import requests

# URL Pública com o link exato do seu print, sem quebras de linha
URL_PUBLICA_NGROK = "https://hardcore-daytime-paramedic.ngrok-free.dev/webhook"

# Estrutura real de payload de mensagem do WhatsApp
payload_whatsapp_real = {
    "data": {
        "key": {
            "remoteJid": "5521988888888@s.whatsapp.net",
            "fromMe": False,
            "id": "ABC123XYZ"
        },
        "message": {
            "conversation": "Olá! Gostaria de saber quais são os serviços e valores de vocês."
        }
    }
}

print("🌍 Disparando mensagem externa para o túnel público do ngrok...")
print(f"🔗 Destino Oficial: {URL_PUBLICA_NGROK}\n")

try:
    # Dispara a requisição POST pela internet
    resposta = requests.post(URL_PUBLICA_NGROK, json=payload_whatsapp_real, timeout=15)
    
    print(f"🔹 Status HTTP retornado pelo servidor: {resposta.status_code}")
    
    if resposta.status_code == 200:
        print("📦 Resposta da IA Luna recebida com sucesso de volta:\n")
        print(resposta.json().get("resposta_para_cliente"))
    else:
        print(f"❌ O servidor retornou um erro: {resposta.text}")
    
except requests.exceptions.Timeout:
    print("❌ Erro: Tempo limite estourado. Verifique se o ligar_tunnel.py continua ativo.")
except Exception as e:
    print(f"❌ Falha crítica ao conectar: {str(e)}")
