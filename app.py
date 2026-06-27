import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (.env)
load_dotenv()

# Importações locais do projeto
from services.ai_service import processar_resposta_gemini 
# Importa a gravação e a nova função de histórico
from database import salvar_agendamento, buscar_historico_tutor  

app = FastAPI()

class MessageContent(BaseModel):
    conversation: Optional[str] = None

class MessageData(BaseModel):
    message: Optional[MessageContent] = None
    key: Optional[Dict[str, Any]] = None

class WebhookPayload(BaseModel):
    data: Optional[MessageData] = None

@app.post("/webhook")
async def receber_mensagem(payload: WebhookPayload):
    try:
        if not payload.data or not payload.data.message or not payload.data.message.conversation:
            raise HTTPException(status_code=400, detail="Formato de mensagem inválido.")
            
        mensagem_cliente = payload.data.message.conversation
        remote_jid = payload.data.key.get("remoteJid", "000000000") if payload.data.key else "000000000"
        telefone_cliente = remote_jid.split("@")[0]
        
        print(f"📩 Mensagem extraída de {telefone_cliente}: {mensagem_cliente}")
        
        # 1. Recupera o histórico do banco de dados para alimentar o contexto do bot
        historico_contexto = buscar_historico_tutor(telefone_cliente)
        
        # 2. Concatena o histórico junto com a mensagem do cliente de forma inteligível para a IA
        mensagem_com_contexto = f"{historico_contexto}\n\nMensagem Atual do Cliente: {mensagem_cliente}"
        
        # Executa a IA capturando qualquer erro de SDK para não derrubar o Uvicorn
        try:
            resultado_ia = processar_resposta_gemini(mensagem_com_contexto)
        except Exception as error_sdk:
            print(f"❌ Erro na SDK do Gemini: {str(error_sdk)}")
            raise HTTPException(status_code=500, detail=f"Erro na SDK da IA: {str(error_sdk)}")

        # ------------------------------------------------------------------
        # ROTEAMENTO INTELIGENTE E DEFENSIVO (Compatível com google-genai)
        # ------------------------------------------------------------------
        chamadas = getattr(resultado_ia, 'function_calls', None)
        
        if chamadas:
            print(f"📅 [ROTEAMENTO] Detectada Function Calling. Tipo do objeto: {type(chamadas)}")
            
            if isinstance(chamadas, list) and len(chamadas) > 0:
                chamada_principal = chamadas[0]
            else:
                chamada_principal = chamadas
                
            nome_funcao = getattr(chamada_principal, 'name', None)
            argumentos = getattr(chamada_principal, 'args', {})
            
            if hasattr(argumentos, '__dict__'):
                argumentos = dict(argumentos)
            
            print(f"📅 Executando ferramenta '{nome_funcao}' com dados: {argumentos}")
            
            # Salva no SQLite nativo contendo o identificador do telefone
            salvar_agendamento(
                telefone=telefone_cliente,
                nome_tutor=argumentos.get('nome_tutor', 'Não informado'),
                nome_pet=argumentos.get('nome_pet', 'Não informado'),
                servico=argumentos.get('servico', 'Não informado'),
                data_horario=argumentos.get('data_horario', 'Não informado')
            )
            
            resposta_texto = (
                f"🎉 Ótima notícia! O agendamento de **{argumentos.get('servico')}** "
                f"para o pet **{argumentos.get('nome_pet')}** foi realizado com sucesso! 🐾"
            )
            
            return {
                "status": "agendado_com_sucesso",
                "dados_agendamento": argumentos,
                "resposta_para_cliente": resposta_texto
            }
            
        # Fluxo de conversa comum
        print("💬 [ROTEAMENTO] Seguindo fluxo de conversa comum.")
        resposta_texto = getattr(resultado_ia, 'text', str(resultado_ia))
        
        return {
            "status": "conversa_comum",
            "resposta_para_cliente": resposta_texto
        }

    except Exception as e:
        print(f"❌ Erro crítico no endpoint webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
