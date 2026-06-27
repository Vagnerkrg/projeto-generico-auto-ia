import requests
import sys

URL_WEBHOOK = "http://localhost:5000/webhook"

# Dicionário com cenários prontos de teste comercial
CENARIOS = {
    "expediente": {
        "nome_tutor": "Carlos",
        "nome_pet": "Bob",
        "servico": "Banho",
        "data_horario": "2026-06-29 23:00"  # Bloqueio: 23h da noite
    },
    "sucesso": {
        "nome_tutor": "Mariana",
        "nome_pet": "Mel",
        "servico": "Tosa",
        "data_horario": "2026-06-30 10:00"  # Sucesso: Terça às 10h da manhã
    },
    "conflito": {
        "nome_tutor": "Rodrigo",
        "nome_pet": "Thor",
        "servico": "Consulta",
        "data_horario": "2026-06-30 10:00"  # Conflito: Mesmo horário da Mel
    }
}

def disparar_teste(tipo_cenario: str):
    dados = CENARIOS.get(tipo_cenario)
    if not dados:
        print(f"⚠️ Cenário '{tipo_cenario}' não encontrado. Use: expediente, sucesso ou conflito.")
        return

    print(f"🚀 [TESTE MOCK] Disparando cenário '{tipo_cenario.upper()}' para o FastAPI...")
    print(f"📅 Dados enviados: {dados['data_horario']} | Pet: {dados['nome_pet']}")
    
    try:
        resposta = requests.post(URL_WEBHOOK, json={"dados_testes": dados}, timeout=10)
        print(f"🔹 Status HTTP do Servidor: {resposta.status_code}")
        
        if resposta.status_code == 200:
            print(f"📦 Resposta do Servidor: {resposta.json()}\n")
        else:
            print(f"❌ Erro Interno: {resposta.text}\n")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: O Uvicorn está desligado na porta 5000!\n")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}\n")

if __name__ == "__main__":
    # Se passar argumento (ex: python testar_bot.py sucesso), roda apenas aquele cenário
    if len(sys.argv) > 1:
        disparar_teste(sys.argv[1])
    else:
        # Se rodar sem argumentos, executa a bateria completa de testes automaticamente
        print("🔥 Iniciando Bateria Automática de Testes Locais do Banco de Dados...\n")
        disparar_teste("expediente")
        disparar_teste("sucesso")
        disparar_teste("conflito")
