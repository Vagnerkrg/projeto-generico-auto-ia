import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Recupera as configurações da Evolution API salvas no arquivo .env
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "petshop_secreto_123")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "AmigoFiel")

def enviar_mensagem_whatsapp(telefone: str, texto: str) -> bool:
    """
    Envia uma mensagem de texto real para o cliente utilizando a Evolution API v2.
    Retorna True em caso de sucesso e False em caso de falha.
    """
    # Higieniza o número mantendo apenas os dígitos numéricos
    numero_limpo = ''.join(filter(str.isdigit, telefone))
    
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    payload = {
        "number": numero_limpo,
        "options": {
            "delay": 1200, # Simula digitação humana de 1.2 segundos
            "presence": "composing"
        },
        "textMessage": {
            "text": texto
        }
    }
    
    try:
        print(f"🚀 [WhatsApp Out] Despachando mensagem para o número {numero_limpo} via Evolution v2...")
        resposta = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # CORREÇÃO DEFINITIVA: Validação numérica direta sem usar a palavra "in"
        if 200 <= resposta.status_code <= 299:
            print(f"✅ [WhatsApp Out] Mensagem enviada com sucesso! Status: {resposta.status_code}")
            return True
        else:
            print(f"❌ [WhatsApp Out] Falha no envio. Retorno da API: {resposta.text}")
            return False
            
    except Exception as e:
        print(f"❌ [WhatsApp Out] Erro crítico de rede ao conectar na Evolution API: {str(e)}")
        return False
