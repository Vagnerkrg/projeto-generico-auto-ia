import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = "http://localhost:5000/webhook"
TELEFONE_TESTE = "5511999998888"

def simular_mensagem_cliente(texto):
    print(f"\n💬 [Cliente]: {texto}")
    payload = {
        "telefone": TELEFONE_TESTE,
        "texto": texto
    }
    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        if res.status_code == 200:
            dados = res.json()
            print(f"🤖 [{os.getenv('NOME_IA', 'Luna')}]: {dados.get('resposta_enviada')}")
        else:
            print(f"❌ Erro no servidor: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Falha de rede: {str(e)}")

if __name__ == "__main__":
    print("=========================================================")
    print(" 🐶 CONCLUINDO SIMULAÇÃO DE ATENDIMENTO - ROBÔ LUNA")
    print("=========================================================")
    
    # Cliente fornece a resposta com o formato estruturado que a IA exigiu
    simular_mensagem_cliente("Perfeito! A data completa de amanhã é 30/06/2026 às 14:00.")
