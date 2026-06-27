import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from services.ai_service import processar_resposta_gemini 

app = FastAPI()

# Nova estrutura Pydantic para capturar o payload real do WhatsApp
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
        # Extrai os dados de forma segura tratando dados ausentes
        if not payload.data or not payload.data.message or not payload.data.message.conversation:
            raise HTTPException(status_code=400, detail="Formato de mensagem inválido ou texto vazio.")
            
        mensagem_cliente = payload.data.message.conversation
        
        # Extrai o telefone de forma segura removendo o sufixo do WhatsApp
        remote_jid = payload.data.key.get("remoteJid", "000000000") if payload.data.key else "000000000"
        telefone_cliente = remote_jid.split("@")[0]
        nome_usuario = "Cliente"  # Opcional: extrair de profiles mais tarde se disponível
        
        print(f"📩 Mensagem extraída de {telefone_cliente}: {mensagem_cliente}")
        
        # 1. Envia a mensagem extraída para o Gemini 2.5 Flash
        resultado_ia = processar_resposta_gemini(mensagem_cliente)
        
        # 2. ROTEAMENTO: Analisa o que a IA decidiu fazer
        if hasattr(resultado_ia, 'function_calls') and resultado_ia.function_calls:
            chamada_funcao = resultado_ia.function_calls
            nome_funcao = chamada_funcao.name
            argumentos = llamada_funcao.args
            
            print(f"📅 [CAMINHO AGENDAMENTO] IA ativou a função: {nome_funcao} com os dados: {argumentos}")
            
            resposta_texto = (
                f"🎉 Ótima notícia! O agendamento de **{argumentos.get('servico')}** "
                f"para o pet **{argumentos.get('nome_pet')}** foi realizado com sucesso para o dia/horário {argumentos.get('data_horario')}! 🐾"
            )
            
            return {
                "status": "agendado_com_sucesso",
                "dados_agendamento": argumentos,
                "resposta_para_cliente": resposta_texto
            }
        
        # 3. [CAMINHO CONVERSA COMUM]
        else:
            print("💬 [CAMINHO CONVERSA] IA apenas respondeu o cliente.")
            resposta_texto = resultado_ia.text if hasattr(resultado_ia, 'text') else str(resultado_ia)
            
            return {
                "status": "conversa_comum",
                "resposta_para_cliente": resposta_texto
            }

    except Exception as e:
        print(f"❌ Erro ao processar fluxo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no processamento do bot")
