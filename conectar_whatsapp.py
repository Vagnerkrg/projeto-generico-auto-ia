import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Parâmetros locais configurados no .env e sincronizados com o Docker v2
API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
API_KEY = os.getenv("EVOLUTION_API_KEY", "petshop_secreto_123")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE", "AmigoFiel")

def inicializar_e_conectar_instancia():
    print("==========================================================")
    print("🔌 INICIALIZADOR DE INSTÂNCIA - EVOLUTION API V2")
    print("==========================================================")
    
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }
    
    # 1. Criação da Instância de forma nativa na Evolution v2
    print(f"🚀 Criando a instância '{INSTANCE_NAME}' no Docker local...")
    url_criar = f"{API_URL}/instance/create"
    payload_criar = {
        "instanceName": INSTANCE_NAME,
        "token": API_KEY,
        "number": "",
        "qrcode": True
    }
    
    try:
        res_criar = requests.post(url_criar, json=payload_criar, headers=headers, timeout=15)
        # CORREÇÃO DEFINITIVA: Validação por intervalo numérico direto (sem usar "in")
        if 200 <= res_criar.status_code <= 299:
            print(f"✅ Instância '{INSTANCE_NAME}' registrada com sucesso no painel!")
        else:
            print("ℹ️ A instância já está registrada ou inicializada. Prosseguindo...")
            
    except Exception as e:
        print(f"❌ Erro de rede ao tentar criar instância: {str(e)}")
        return

    # Pequena pausa para garantir a sincronização interna do container
    time.sleep(2)

    # 2. Captura do QR Code para pareamento
    print(f"🔍 Solicitando QR Code de pareamento para a instância '{INSTANCE_NAME}'...")
    url_qrcode = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
    
    try:
        res_qr = requests.get(url_qrcode, headers=headers, timeout=15)
        
        # CORREÇÃO DEFINITIVA: Validação por intervalo numérico direto na leitura do QR
        if 200 <= res_qr.status_code <= 299:
            dados_qr = res_qr.json()
            if isinstance(dados_qr, dict) and "code" in dados_qr:
                print("\n🚨 INSTÂNCIA PRONTA! ESCANEIE O QR CODE ABAIXO NO SEU WHATSAPP:")
                print("👉 Vá em: Aparelhos Conectados -> Conectar um Aparelho\n")
                print(dados_qr.get("code"))
                print("\n💡 Se o terminal não renderizar o desenho, use a string acima ou acesse o painel local.")
            elif isinstance(dados_qr, dict) and (dados_qr.get("status") == "CONNECTED" or dados_qr.get("instance", {}).get("status") == "CONNECTED"):
                print("🎉 Excelente! Seu WhatsApp já está conectado e autenticado nesta instância!")
            else:
                print(f"⚠️ Resposta da API: {dados_qr}")
        else:
            print(f"❌ Falha ao buscar QR Code. Status HTTP: {res_qr.status_code}")
                
    except Exception as e:
        print(f"❌ Erro de rede ao buscar o QR Code: {str(e)}")

if __name__ == "__main__":
    inicializar_e_conectar_instancia()
