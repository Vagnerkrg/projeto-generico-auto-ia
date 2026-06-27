import json
import time
import requests
import sqlite3

BASE_URL = "http://127.0.0.1:5000"
TELEFONE_TESTE = "5511999998888"

def limpar_banco_para_teste():
    """Limpa os agendamentos e o histórico de conversas antigos para começar do zero absoluto."""
    print("🧹 [MOCK] Limpando agendamentos e histórico de conversas antigos do SQLite...")
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM agendamentos")
        cursor.execute("DELETE FROM historico_conversas")
        conexao.commit()
        print("✅ [Banco de Dados] Tabelas limpas com sucesso!")
    except sqlite3.OperationalError as e:
        print(f"⚠️ [Banco de Dados] Erro ao limpar tabelas: {str(e)}")
    conexao.close()

def formatar_json(dados):
    return json.dumps(dados, indent=4, ensure_ascii=False)

def enviar_mensagem(telefone, texto):
    """Envia um payload POST simulando o webhook do WhatsApp."""
    url = f"{BASE_URL}/webhook"
    payload = {
        "telefone": telefone,
        "texto": texto,
        "is_mock": False
    }
    try:
        resposta = requests.post(url, json=payload, timeout=15)
        return resposta.status_code, resposta.json()
    except requests.exceptions.ConnectionError:
        print("❌ [ERRO] O servidor FastAPI não está rodando na porta 5000!")
        exit(1)

def consultar_dashboard():
    """Consulta a rota GET /agendamentos para verificar o banco de dados."""
    url = f"{BASE_URL}/agendamentos"
    resposta = requests.get(url, timeout=10)
    return resposta.json()

def ejecutar_suite_testes():
    print("==========================================================")
    print("🚀 INICIANDO SUÍTE DE TESTES DO AGENTE DE IA DO PET SHOP")
    print("==========================================================\n")

    # Limpa os dados de agendamentos e conversas antigas
    limpar_banco_para_teste()

    # --- CENÁRIO 1: Saudação e Coleta de Dados ---
    print("\n📝 [CENÁRIO 1] Iniciando conversa com a Luna...")
    status, res = enviar_mensagem(TELEFONE_TESTE, "Olá, gostaria de agendar um serviço por favor.")
    print(f"Status: {status}")
    print(f"Resposta da IA:\n{res.get('resposta_enviada')}\n")
    time.sleep(8)  # Tempo estendido para respeitar a cota gratuita do Google

    # --- CENÁRIO 2: Fornecendo dados parciais ---
    print("📝 [CENÁRIO 2] Fornecendo o nome do tutor e do pet...")
    status, res = enviar_mensagem(TELEFONE_TESTE, "Meu nome é Carlos e o meu cachorro se chama Floquinho.")
    print(f"Status: {status}")
    print(f"Resposta da IA:\n{res.get('resposta_enviada')}\n")
    time.sleep(8)  # Tempo estendido para respeitar a cota gratuita do Google

    # --- CENÁRIO 3: Fornecendo serviço e data com Sucesso ---
    print("📝 [CENÁRIO 3] Solicitando Banho em horário comercial válido...")
    status, res = enviar_mensagem(TELEFONE_TESTE, "Quero um Banho para o Floquinho na próxima segunda-feira, dia 29/06/2026 às 14:00.")
    print(f"Status: {status}")
    print(f"Resposta da IA:\n{res.get('resposta_enviada')}\n")
    time.sleep(8)  # Tempo estendido para respeitar a cota gratuita do Google

    # --- CONSULTA FINAL AO DASHBOARD ---
    print("==========================================================")
    print("📊 CONSULTANDO REGISTROS GRAVADOS NO DASHBOARD (GET)")
    print("==========================================================")
    dados_finais = consultar_dashboard()
    print(formatar_json(dados_finais))

if __name__ == "__main__":
    ejecutar_suite_testes()
