import requests
import sys

# URL oficial do endpoint local do FastAPI
URL_WEBHOOK = "http://localhost:5000/webhook"

# Payload estruturado ajustado para 23h da noite (Força o bloqueio de expediente!)
payload_teste = {
    "dados_testes": {
        "nome_tutor": "Carlos",
        "nome_pet": "Bob",
        "servico": "Banho",
        "data_horario": "2026-06-29 23:00"  # <--- Horário fora do expediente (Pet shop fechado!)
    }
}

def executar_teste_local():
    print("🚀 Disparando carga de teste estruturada para o FastAPI...")
    
    try:
        # Envia a requisição POST tratando falhas de conexão de rede
        resposta = requests.post(URL_WEBHOOK, json=payload_teste, timeout=10)
        
        print(f"🔹 Status HTTP do Servidor: {resposta.status_code}")
        
        # Se o servidor responder com erro (Ex: 400 ou 500), exibe o log de erro
        if resposta.status_code != 200:
            print(f"❌ Falha no processamento do servidor: {resposta.text}")
            return
            
        print(f"📦 Payload de Resposta Recebido: {resposta.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de Conexão: Certifique-se de que o Uvicorn está rodando na porta 5000!")
    except Exception as erro_inesperado:
        print(f"❌ Ocorreu um erro inesperado durante o teste: {str(erro_inesperado)}")

if __name__ == "__main__":
    executar_teste_local()
