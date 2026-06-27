import requests

# Endereço local do seu servidor FastAPI
url = "http://localhost:5000/webhook"
# Dados simulando o envio de uma mensagem do WhatsApp
payload = {
    "data": {
        "message": {
            "conversation": "Olá, sou o Carlos e queria agendar um banho para o meu cachorro Bob amanhã às 14h"
        },
        "key": {
            "remoteJid": "5521999999999@s.whatsapp.net",
            "fromMe": False
        }
    }
}

print("🚀 Enviando mensagem simulada para o servidor FastAPI...")
try:
    resposta = requests.post(url, json=payload)
    print(f"📡 Status do Servidor: {resposta.status_code}")
    print(f"📦 Resposta recebida: {resposta.json()}")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
