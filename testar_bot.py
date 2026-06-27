import requests

url = "http://localhost:5000/webhook"

# Dados simulados idênticos ao do WhatsApp (Dribla o limite 429 da API do Gemini)
payload = {
    "dados_testes": {
        "nome_tutor": "Carlos",
        "nome_pet": "Bob",
        "servico": "Banho",
        "data_horario": "Amanhã às 14h"
    }
}

print("🚀 Enviando dados de teste isolados para o servidor FastAPI...")
resposta = requests.post(url, json=payload)

print(f"🔹 Status do Servidor: {resposta.status_code}")
print(f"📦 Resposta recebida: {resposta.json()}")
