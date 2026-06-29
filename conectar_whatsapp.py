import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL")
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = "PetShop_AmigoFiel_Vagner"
NGROK_WEBHOOK = os.getenv("NGROK_URL", "https://ngrok-free.dev") + "/webhook"

def conectar_fluxo_cloud():
    print("=========================================================")
    print(" 🐶 AGENTE DE IA PET SHOP - CONEXÃO CLOUD ESTÁVEL")
    print("=========================================================")
    
    if not API_URL or not API_KEY:
        print("❌ ERRO: EVOLUTION_API_URL ou EVOLUTION_API_KEY não configuradas no .env")
        return

    url_base = API_URL.rstrip('/')
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload_criar = {
        "instanceName": INSTANCE_NAME,
        "token": "petshop_secreto_123",
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
        "webhook": NGROK_WEBHOOK,
        "events": ["MESSAGES_UPSERT"]
    }
    
    # 1. Criação da Instância (Validação simplificada sem o comando 'in')
    try:
        res = requests.post(f"{url_base}/instance/create", json=payload_criar, headers=headers)
        if res.status_code == 200 or res.status_code == 201:
            print("🚀 Instância criada ou validada com sucesso!")
        else:
            print(f"ℹ️ Status da Instância: {res.status_code}")
    except Exception as e:
        print(f"❌ Falha ao contactar servidor: {str(e)}")
        return

    time.sleep(2)

    # 2. Solicitação do Código de Pareamento / QR Code
    try:
        res_qr = requests.get(f"{url_base}/instance/connect/{INSTANCE_NAME}", headers=headers)
        dados = res_qr.json()
        
        if isinstance(dados, dict) and "code" in dados:
            print("\n" + "="*50)
            print("📱 DIGITE ESTE CÓDIGO NO SEU WHATSAPP PARA CONECTAR:")
            print(f"👉 {dados.get('code')} 👈")
            print("="*50 + "\n")
        elif isinstance(dados, dict) and "base64" in dados:
            print("\n📸 QR Code Gerado em Base64 obtido com sucesso.")
            print("Instância aguardando leitura do dispositivo móvel.")
        else:
            print(f"⚠️ Resposta do Servidor: {dados}")
            
    except Exception as e:
        print(f"❌ Erro ao ler dados de conexão: {str(e)}")

if __name__ == "__main__":
    conectar_fluxo_cloud()
