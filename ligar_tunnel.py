import os
import sys
import time
from pyngrok import ngrok
from dotenv import load_dotenv

load_dotenv()

PORTA_LOCAL = 5000

print("🌐 Inicializando túnel público seguro via pyngrok...")
try:
    # Cria a conexão na porta do FastAPI
    url_publica = ngrok.connect(PORTA_LOCAL)
    
    print("\n" + "="*60)
    print("🚀 SEU WEBHOOK AGORA ESTÁ ONLINE PARA O MUNDO REAL!")
    print(f"🔗 URL Pública para Webhook: {url_publica.public_url}/webhook")
    print("="*60 + "\n")
    
    print("Mantenha este terminal ativo para não derrubar a conexão.")
    print("Para encerrar o túnel, pressione Ctrl+C.")
    
    # Mantém o processo ativo nativamente sem gerar erros de atributo
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n🛑 Túnel encerrado com sucesso.")
except Exception as e:
    print(f"❌ Erro ao abrir o túnel do ngrok: {str(e)}")
