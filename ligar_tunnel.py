import os
import sys
import time
from pyngrok import ngrok, conf
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env de forma segura
load_dotenv()

PORTA_LOCAL = 5000
token_secreto = os.environ.get("NGROK_AUTHTOKEN")

if not token_secreto or "INSIRA_AQUI" in token_secreto:
    print("❌ Erro: NGROK_AUTHTOKEN inválido ou ausente no seu arquivo .env!")
    print("Por favor, cole a sua chave do site do ngrok dentro do arquivo .env antes de rodar.")
    sys.exit(1)

print("🔐 Autenticando com o ngrok usando credenciais seguras do .env...")
conf.get_default().auth_token = token_secreto

print("🌐 Inicializando túnel público seguro via pyngrok...")
try:
    # Cria a conexão na porta do FastAPI
    url_publica = ngrok.connect(PORTA_LOCAL)
    
    print("\n" + "="*60)
    print("🚀 SEU WEBHOOK AGORA ESTÁ ONLINE E 100% PROTEGIDO!")
    print(f"🔗 URL Pública para Webhook: {url_publica.public_url}/webhook")
    print("="*60 + "\n")
    
    print("Mantenha este terminal ativo para não derrubar a conexão.")
    print("Para encerrar o túnel, pressione Ctrl+C.")
    
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n🛑 Túnel encerrado com sucesso.")
except Exception as e:
    print(f"❌ Erro ao abrir o túnel do ngrok: {str(e)}")
