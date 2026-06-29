import os
import datetime
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional

# Habilita o tráfego HTTP local para contornar a trava de segurança do OAuth2 em testes
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Importações nativas de banco de dados
from database import (
    salvar_agendamento,
    buscar_historico_tutor,
    verificar_disponibilidade_horario,
    salvar_mensagem_historico,
    recuperar_contexto_conversa,
    validar_horario_funcionamento,
    listar_todos_agendamentos
)

# Importação do serviço de Inteligência Artificial nativo
from services.ai_service import processar_conversa_gemini
# Importação do envio de mensagens de volta ao cliente
from services.whatsapp_bot import enviar_mensagem_whatsapp
# Importação do fluxo de autenticação do Google Calendar
from services.calendar_service import obter_fluxo_autenticacao, criar_evento_petshop

app = FastAPI(
    title="Agente de IA para Pet Shop",
    description="API nativa integrada para atendimento e agendamento inteligente",
    version="1.2.0"
)

class MensagemWhatsApp(BaseModel):
    telefone: str
    texto: str
    is_mock: Optional[bool] = False

# ------------------------------------------------------------------
# 🔑 ROTAS DE AUTENTICAÇÃO DO GOOGLE CALENDAR
# ------------------------------------------------------------------
@app.get("/login-google", tags=["Google Calendar"])
def login_google():
    """Rota para iniciar a autenticação salvando os parâmetros necessários."""
    flow = obter_fluxo_autenticacao()
    # Gera a URL de autorização obtendo o code_verifier gerado na hora
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    
    # Salvamos o code_verifier gerado na memória do próprio objeto temporário para uso posterior
    os.environ[f"GOOGLE_PKCE_{state}"] = flow.code_verifier
    return RedirectResponse(authorization_url)

@app.get("/oauth2callback", tags=["Google Calendar"])
async def oauth2callback(request: Request):
    """Rota de retorno do Google que recupera o PKCE correto e gera o token.json."""
    flow = obter_fluxo_autenticacao()
    
    # Recupera o parâmetro 'state' enviado pelo Google na URL
    state = request.query_params.get("state")
    
    # Busca o code_verifier original associado àquele estado
    saved_verifier = os.environ.get(f"GOOGLE_PKCE_{state}")
    
    if saved_verifier:
        flow.code_verifier = saved_verifier
    else:
        # Fallback de segurança caso a memória expire
        flow.code_verifier = None
        
    str_url = str(request.url)
    
    if "http://" in str_url and not "localhost" in str_url:
        str_url = str_url.replace("http://", "https://")
        
    flow.fetch_token(authorization_response=str_url)
    creds = flow.credentials
    
    with open('services/token.json', 'w') as token:
        token.write(creds.to_json())
        
    # Limpa a variável temporária do ambiente
    if f"GOOGLE_PKCE_{state}" in os.environ:
        del os.environ[f"GOOGLE_PKCE_{state}"]
        
    return {"status": "Sucesso", "mensagem": "Luna está conectada com sucesso ao seu Google Calendar!"}

# ------------------------------------------------------------------
# 📊 ROTA DASHBOARD: LISTAR TODOS OS AGENDAMENTOS
# ------------------------------------------------------------------
@app.get("/agendamentos", tags=["Dashboard"])
async def get_agendamentos():
    """Retorna a lista completa de agendamentos para o painel do dono do pet shop."""
    try:
        dados_agendamentos = listar_todos_agendamentos()
        return {
            "status": "sucesso",
            "total_agendamentos": len(dados_agendamentos),
            "dados": dados_agendamentos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ------------------------------------------------------------------
# 📲 ROTA PRINCIPAL: WEBHOOK INTEGRADO COM TRATAMENTO DINÂMICO
# ------------------------------------------------------------------
@app.post("/webhook", tags=["Webhook"])
async def receber_mensagem(request: Request, background_tasks: BackgroundTasks):
    """Endpoint unificado que processa o Gemini e gerencia o pipeline com travas comerciais."""
    try:
        payload_bruto = await request.json()
        print(f"📥 [Webhook] Payload recebido: {payload_bruto}")
        
        if "dados_testes" in payload_bruto:
            dados = payload_bruto["dados_testes"]
            telefone = payload_bruto.get("telefone", "5511999998888")
            nome_tutor = dados.get("nome_tutor")
            nome_pet = dados.get("nome_pet")
            servico = dados.get("servico")
            data_horario = dados.get("data_horario")
            
            if not validar_horario_funcionamento(data_horario):
                texto_resposta = f"Desculpe, mas não funcionamos neste horário informado ({data_horario})."
                return {"status": "erro", "resposta_enviada": texto_resposta}
                
            if not verificar_disponibilidade_horario(data_horario):
                texto_resposta = f"Opa! Verifiquei aqui no meu sistema que o horário de {data_horario} já está preenchido."
                return {"status": "erro", "resposta_enviada": texto_resposta}
                
            salvar_agendamento(telefone, nome_tutor, nome_pet, servico, data_horario)
            return {"status": "sucesso", "resposta_enviada": f"Agendamento de teste para {nome_pet} salvo com sucesso!"}
            
        telefone = payload_bruto.get("telefone")
        texto_cliente = payload_bruto.get("texto")
        
        if not telefone or not texto_cliente:
            raise HTTPException(status_code=400, detail="Os campos 'telefone' e 'texto' são obrigatórios no JSON.")
        
        salvar_mensagem_historico(telefone, "user", texto_cliente)
        contexto_conversas = recuperar_contexto_conversa(telefone)
        historico_sistema = buscar_historico_tutor(telefone)
        
        resultado_ia = processar_conversa_gemini(telefone, contexto_conversas, historico_sistema)
        texto_resposta = ""
        
        if resultado_ia.get("acao") == "chamar_funcao" and resultado_ia.get("nome_funcao") == "verificar_e_agendar_servico":
            args = resultado_ia.get("argumentos", {})
            nome_tutor = args.get("nome_tutor")
            nome_pet = args.get("nome_pet")
            servico = args.get("servico")
            data_horario = args.get("data_horario")
            
            if not validar_horario_funcionamento(data_horario):
                erro_contexto = f"[SISTEMA]: Erro ao executar verificar_e_agendar_servico. Motivo: O horário {data_horario} está fora do expediente comercial do pet shop."
                contexto_conversas.append({"role": "user", "parts": [erro_contexto]})
                reprocesso = processar_conversa_gemini(telefone, contexto_conversas, historico_sistema)
                texto_resposta = reprocesso.get("texto", f"Desculpe, mas não funcionamos neste horário ({data_horario}). Que tal escolher outro momento no horário comercial?")
            
            elif not verificar_disponibilidade_horario(data_horario):
                erro_contexto = f"[SISTEMA]: Erro ao executar verificar_e_agendar_servico. Motivo: O horário {data_horario} já está ocupado por outro animal de estimação."
                contexto_conversas.append({"role": "user", "parts": [erro_contexto]})
                reprocesso = processar_conversa_gemini(telefone, contexto_conversas, historico_sistema)
                texto_resposta = reprocesso.get("texto", f"Opa, acabei de ver que o horário {data_horario} já está preenchido. Teria outro de sua preferência?")
            
            else:
                salvar_agendamento(telefone, nome_tutor, nome_pet, servico, data_horario)
                try:
                    resumo_evento = f"🐾 {nome_pet} - {servico}"
                    descricao_evento = f"Tutor: {nome_tutor}\nTelefone: {telefone}\nAgendado via IA Luna"
                    criar_evento_petshop(resumo_evento, descricao_evento, data_horario)
                except Exception as e_cal:
                    print(f"⚠️ [Aviso Google Calendar]: Falha ao espelhar evento na agenda: {e_cal}")
                
                texto_resposta = f"Perfeito, tudo certo! 🎉 Agendamento confirmado para o(a) {nome_pet} (Serviço: {servico}) no dia e horário: {data_horario}. Esperamos vocês!"
        else:
            texto_resposta = resultado_ia.get("texto", "Não consegui processar sua mensagem no momento.")
            
        salvar_mensagem_historico(telefone, "model", texto_resposta)
        background_tasks.add_task(enviar_mensagem_whatsapp, telefone, texto_resposta)
        
        return {
            "status": "sucesso",
            "fluxo_executado": resultado_ia.get("acao"),
            "resposta_enviada": texto_resposta
        }
    except Exception as e:
        print(f"❌ [Erro Webhook]: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno no pipeline do agente: {str(e)}")

# ------------------------------------------------------------------
# 🤖 SIMULADOR INTEGRADO DA EVOLUTION API (100% GRATUITO E NATIVO)
# ------------------------------------------------------------------
@app.post("/mock-api/instance/create", tags=["Simulador Evolution"])
async def mock_criar_instancia(request: Request):
    """Simula a rota de criação de instâncias da Evolution API."""
    try:
        payload = await request.json()
        print(f"📦 [Simulador] Criando instância fictícia: {payload.get('instanceName')}")
        return {
            "status": "SUCCESS",
            "message": "Instância simulada criada com sucesso no cluster local.",
            "instance": {"instanceName": payload.get("instanceName"), "status": "created"}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mock-api/instance/connect/{instance_name}", tags=["Simulador Evolution"])
async def mock_conectar_instancia(instance_name: str):
    """Simula a rota de captura de dados de conexão, devolvendo o código de pareamento estável."""
    print(f"🔍 [Simulador] Gerando código de pareamento para a instância: {instance_name}")
    return {
        "status": "SUCCESS",
        "pairingCode": "LUNA-PET-2026",
        "message": "Código de pareamento gerado localmente pelo simulador com sucesso."
    }
