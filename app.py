import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (.env)
load_dotenv()

# Importações locais do projeto
from services.ai_service import processar_resposta_gemini 
# Importa todas as funções nativas de persistência e validações do SQLite
from database import (
    salvar_agendamento, 
    buscar_historico_tutor, 
    verificar_disponibilidade_horario,
    salvar_mensagem_historico,
    recuperar_contexto_conversa,
    validar_horario_funcionamento  # <--- IMPORTAÇÃO DA NOVA TRAVA INTEGRADA
)  
from services.whatsapp_bot import enviar_mensagem_whatsapp  

app = FastAPI()

class MessageContent(BaseModel):
    conversation: Optional[str] = None

class MessageData(BaseModel):
    message: Optional[MessageContent] = None
    key: Optional[Dict[str, Any]] = None

class WebhookPayload(BaseModel):
    data: Optional[MessageData] = None
    dados_testes: Optional[Dict[str, Any]] = None  # Habilita testes livres sem gastar cota 429

@app.post("/webhook")
async def receber_mensagem(payload: WebhookPayload):
    try:
        # ------------------------------------------------------------------
        # 🧪 MOCK: CAMINHO ULTRA-RÁPIDO E GRATUITO PARA INJEÇÃO DE TESTES
        # ------------------------------------------------------------------
        if payload.dados_testes:
            print("🧪 [TESTE INTERNO] Ignorando chamada do Gemini para isolar testes do SQLite.")
            argumentos = payload.dados_testes
            telefone_cliente = "5521999999999"
            horario_solicitado = argumentos.get('data_horario', 'Não informado')
            
            # ⏰ VALIDAÇÃO 1: HORÁRIO DE EXPEDIENTE COMERCIAL (NOVA TRAVA ATIVADA)
            dentro_expediente = validar_horario_funcionamento(horario_solicitado)
            if not dentro_expediente:
                print(f"⚠️ [EXPEDIENTE] Horário '{horario_solicitado}' recusado por estar fora do expediente!")
                resposta_erro = "Desculpe, o horário solicitado está fora do nosso expediente comercial. 🐾"
                return {"status": "erro_expediente", "resposta_para_cliente": resposta_erro}
            
            # 📅 VALIDAÇÃO 2: HORÁRIO JÁ OCUPADO (TRAVA DE CONFLITOS)
            horario_livre = verificar_disponibilidade_horario(horario_solicitado)
            if not horario_livre:
                print(f"⚠️ [CONFLITO] Horário '{horario_solicitado}' ocupado no banco local!")
                resposta_conflito = f"Desculpe, o horário {horario_solicitado} já está preenchido por outro pet. 🐾"
                return {"status": "conflito_horario", "resposta_para_cliente": resposta_conflito}
                
            # Se passou pelas duas travas, salva com total segurança
            salvar_agendamento(
                telefone=telefone_cliente,
                nome_tutor=argumentos.get('nome_tutor', 'Não informado'),
                nome_pet=argumentos.get('nome_pet', 'Não informado'),
                servico=argumentos.get('servico', 'Não informado'),
                data_horario=horario_solicitado
            )
            return {"status": "agendado_com_sucesso", "dados_agendamento": argumentos}

        # ------------------------------------------------------------------
        # 📲 FLUXO DO WHATSAPP REAL (PRODUÇÃO COM MEMÓRIA SEQUENCIAL)
        # ------------------------------------------------------------------
        if not payload.data or not payload.data.message or not payload.data.message.conversation:
            raise HTTPException(status_code=400, detail="Formato de mensagem inválido.")
            
        mensagem_cliente = payload.data.message.conversation
        remote_jid = payload.data.key.get("remoteJid", "000000000") if payload.data.key else "000000000"
        telefone_cliente = remote_jid.split("@")[0]
        
        print(f"📩 Mensagem extraída de {telefone_cliente}: {mensagem_cliente}")
        
        salvar_mensagem_historico(telefone=telefone_cliente, papel="user", texto=mensagem_cliente)
        historico_cadastros = buscar_historico_tutor(telefone_cliente)
        historico_chat_recente = recuperar_contexto_conversa(telefone_cliente)
        
        contexto_formatado = f"{historico_cadastros}\n\nHistórico Recente de Diálogo: {historico_chat_recente}\n\nMensagem Atual: {mensagem_cliente}"
        
        try:
            resultado_ia = processar_resposta_gemini(contexto_formatado)
        except Exception as error_sdk:
            print(f"❌ Erro na SDK do Gemini: {str(error_sdk)}")
            raise HTTPException(status_code=500, detail=f"Erro na SDK da IA: {str(error_sdk)}")

        chamadas = getattr(resultado_ia, 'function_calls', None)
        
        if chamadas:
            print(f"📅 [ROTEAMENTO] Detectada Function Calling.")
            
            if isinstance(chamadas, list) and len(chamadas) > 0:
                chamada_principal = chamadas[0]
            else:
                chamada_principal = chamadas
                
            nome_funcao = getattr(chamada_principal, 'name', None)
            argumentos = getattr(chamada_principal, 'args', {})
            
            if hasattr(argumentos, '__dict__'):
                argumentos = dict(argumentos)
            
            horario_solicitado = argumentos.get('data_horario', 'Não informado')
            print(f"📅 Executando ferramenta '{nome_funcao}' para o horário: {horario_solicitado}")
            
            # --- TRAVA 1: HORÁRIO DE EXPEDIENTE ---
            dentro_expediente = validar_horario_funcionamento(horario_solicitado)
            if not dentro_expediente:
                resposta_erro = "Desculpe, o horário solicitado está fora do nosso expediente comercial. 🐾"
                salvar_mensagem_historico(telefone=telefone_cliente, papel="model", texto=resposta_erro)
                enviar_mensagem_whatsapp(telefone=telefone_cliente, texto=resposta_erro)
                return {"status": "erro_expediente", "resposta_para_cliente": resposta_erro}
            
            # --- TRAVA 2: HORÁRIO JÁ OCUPADO ---
            horario_livre = verificar_disponibilidade_horario(horario_solicitado)
            if not horario_livre:
                print(f"⚠️ [CONFLITO] Horário '{horario_solicitado}' ocupado!")
                resposta_conflito = (
                    f"Desculpe, acabei de checar no sistema da {os.environ.get('NOME_PETSHOP', 'Amigo Fiel')} e o horário "
                    f"**{horario_solicitado}** infelizmente já está ocupado. 🐾\nPoderia sugerir outro horário?"
                )
                salvar_mensagem_historico(telefone=telefone_cliente, papel="model", texto=resposta_conflito)
                enviar_mensagem_whatsapp(telefone=telefone_cliente, texto=resposta_conflito)
                return {"status": "conflito_horario", "resposta_para_cliente": resposta_conflito}
            
            salvar_agendamento(
                telefone=telefone_cliente,
                nome_tutor=argumentos.get('nome_tutor', 'Não informado'),
                nome_pet=argumentos.get('nome_pet', 'Não informado'),
                servico=argumentos.get('servico', 'Não informado'),
                data_horario=horario_solicitado
            )
            
            resposta_texto = (
                f"🎉 Ótima notícia! O agendamento de **{argumentos.get('servico')}** "
                f"para o pet **{argumentos.get('nome_pet')}** foi realizado com sucesso! 🐾"
            )
            
            salvar_mensagem_historico(telefone=telefone_cliente, papel="model", texto=resposta_texto)
            enviar_mensagem_whatsapp(telefone=telefone_cliente, texto=resposta_texto)
            return {"status": "agendado_com_sucesso", "dados_agendamento": argumentos, "resposta_para_cliente": resposta_texto}
            
        print("💬 [ROTEAMENTO] Seguindo fluxo de conversa comum.")
        resposta_texto = resultado_ia.text if hasattr(resultado_ia, 'text') else str(resultado_ia)
        
        salvar_mensagem_historico(telefone=telefone_cliente, papel="model", texto=resposta_texto)
        enviar_mensagem_whatsapp(telefone=telefone_cliente, texto=resposta_texto)
        
        return {"status": "conversa_comum", "resposta_para_cliente": resposta_texto}

    except Exception as e:
        print(f"❌ Erro crítico no endpoint webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
