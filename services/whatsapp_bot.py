import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Recupera a URL calibrada no .env (http://localhost:5000/mock-api)
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:5000/mock-api")
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "AmigoFiel")
API_KEY = os.getenv("EVOLUTION_API_KEY", "42a83c93-60ae-432d-862d-a2f07297b83d")

def enviar_mensagem_whatsapp(telefone: str, texto: str):
    """
    Despacha a mensagem de resposta utilizando a URL configurada no ambiente.
    Direciona automaticamente para o simulador interno na porta 5000.
    """
    # Remove caracteres não numéricos do telefone por segurança
    numero_limpo = "".join(filter(str.isdigit, telefone))
    
    # Monta a rota apontando dinamicamente para o barramento correto
    url_final = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }
    
    payload = {
        "number": numero_limpo,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": texto
        }
    }
    
    try:
        print(f"🚀 [WhatsApp Out] Enviando via: {url_final}")
        resposta = requests.post(url_final, json=payload, headers=headers, timeout=10)
        
        # Correção matemática definitiva: evita colchetes/parênteses e aceita qualquer HTTP 2xx de sucesso
        if 200 <= resposta.status_code < 300:
            print(f"✅ [WhatsApp Out] Mensagem entregue com sucesso para {numero_limpo}.")
            return True
        else:
            print(f"⚠️ [WhatsApp Out] Resposta inesperada do barramento: {resposta.status_code} - {resposta.text}")
            return False
            
    except Exception as e:
        print(f"❌ [WhatsApp Out] Erro crítico de rede ao conectar na Evolution API: {str(e)}")
        return False
