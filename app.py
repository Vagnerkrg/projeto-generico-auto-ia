import os
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

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

app = FastAPI(
    title="Agente de IA para Pet Shop",
    description="API nativa integrada para atendimento e agendamento inteligente",
    version="1.1.0"
)

# Mantido no código para documentação automática no Swagger UI (/docs)
class MensagemWhatsApp(BaseModel):
    telefone: str
    texto: str
    is_mock: Optional[bool] = False

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
    """
    Endpoint unificado corrigido que aceita payloads flexíveis (dados reais ou mocks de teste),
    processa o histórico no SQLite e gerencia o pipeline do Gemini com travas comerciais.
    """
    try:
        # Captura o JSON bruto enviado para evitar erros 422 de validação rígida
        payload_bruto = await request.json()
        print(f"📥 [Webhook] Payload recebido: {payload_bruto}")
        
        # --- CASO A: Compatibilidade com dicionários estáticos de teste antigos ---
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
            
        # --- CASO B: Fluxo Conversacional Real (Humano ou novo script testar_bot.py) ---
        telefone = payload_bruto.get("telefone")
        texto_cliente = payload_bruto.get("texto")
        
        if not telefone or not texto_cliente:
            raise HTTPException(status_code=400, detail="Os campos 'telefone' e 'texto' são obrigatórios no JSON.")
        
        # 1. Registra de forma nativa a entrada do cliente no banco
        salvar_mensagem_historico(telefone, "user", texto_cliente)
        
        # 2. Resgata contexto (últimas 6 mensagens) e o histórico de longo prazo (últimos 3 agendamentos)
        contexto_conversas = recuperar_contexto_conversa(telefone)
        historico_sistema = buscar_historico_tutor(telefone)
        
        # 3. Dispara para o Gemini avaliar o diálogo e decidir a ação
        resultado_ia = processar_conversa_gemini(telefone, contexto_conversas, historico_sistema)
        
        texto_resposta = ""
        
        # Cenário A: A IA identificou que todos os dados foram coletados e chamou a Função de Agendamento
        if resultado_ia.get("acao") == "chamar_funcao" and resultado_ia.get("nome_funcao") == "verificar_e_agendar_servico":
            args = resultado_ia.get("argumentos", {})
            nome_tutor = args.get("nome_tutor")
            nome_pet = args.get("nome_pet")
            servico = args.get("servico")
            data_horario = args.get("data_horario")
            
            # Executa a trava de validação de horário comercial
            if not validar_horario_funcionamento(data_horario):
                texto_resposta = f"Desculpe, mas não funcionamos neste horário informado ({data_horario}). Que tal escolher outro momento dentro do expediente comercial?"
            
            # Executa a trava de choque/conflito de horários duplicados
            elif not verificar_disponibilidade_horario(data_horario):
                texto_resposta = f"Opa! Verifiquei aqui no meu sistema que o horário de {data_horario} já está preenchido para outro pet. Teria outro horário de sua preferência?"
            
            # Passou nas duas travas: salva com sucesso no SQLite
            else:
                salvar_agendamento(telefone, nome_tutor, nome_pet, servico, data_horario)
                texto_resposta = f"Perfeito, tudo certo! 🎉 Agendamento confirmado para o(a) {nome_pet} (Serviço: {servico}) no dia e horário: {data_horario}. Esperamos vocês!"
        
        # Cenário B: A IA decidiu apenas continuar conversando ou coletando os dados restantes
        else:
            texto_resposta = resultado_ia.get("texto", "Não consegui processar sua mensagem no momento.")
            
        # 4. Registra nativamente a resposta gerada para o robô lembrar na próxima iteração
        salvar_mensagem_historico(telefone, "model", texto_resposta)
        
        # 5. Dispara o envio de volta para o cliente de forma assíncrona (não trava o servidor)
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
    """Simula perfeitamente a rota de criação de instâncias da Evolution API."""
    try:
        payload = await request.json()
        print(f"📦 [Simulador] Criando instância fictícia: {payload.get('instanceName')}")
        return {
            "status": "SUCCESS",
            "message": "Instância simulada criada com sucesso no cluster local.",
            "instance": {
                "instanceName": payload.get("instanceName"),
                "status": "created"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mock-api/instance/connect/{instance_name}", tags=["Simulador Evolution"])
async def mock_conectar_instancia(instance_name: str):
    """Simula a rota de captura de dados de conexão, devolvendo o código de pareamento."""
    print(f"🔍 [Simulador] Gerando código de pareamento para a instância: {instance_name}")
    return {
        "status": "SUCCESS",
        "code": "LUNA-PET-2026",
        "message": "Código gerado com sucesso. Digite-o no seu WhatsApp."
    }

@app.post("/mock-api/message/sendText/{instance_name}", tags=["Simulador Evolution"])
async def mock_enviar_mensagem(instance_name: str, request: Request):
    """Simula o disparo de mensagens de volta para o cliente sem gastar com APIs."""
    payload = await request.json()
    print(f"📤 [Simulador - {instance_name}] Mensagem ativa enviada para {payload.get('number')}: {payload.get('text')}")
    return {"status": "SUCCESS", "message": "Mensagem enviada com sucesso de forma simulada."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
