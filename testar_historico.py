import os
import requests
import sqlite3
import time
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = "http://localhost:5000/webhook"
TELEFONE_TESTE = "5511999998888"

def injetar_agendamento_antigo():
    """Insere um agendamento de 35 dias atrás no banco para simular cliente antigo."""
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    
    # Insere um registro antigo para forçar a regra de Cross-Selling da Luna
    cursor.execute("""
        INSERT INTO agendamentos (telefone, nome_tutor, nome_pet, servico, data_horario, status)
        VALUES (?, 'Vagner', 'Rex', 'Banho', '2026-05-25 10:00', 'Concluido')
    """, (TELEFONE_TESTE,))
    
    conexao.commit()
    conexao.close()
    print("💾 [Teste] Agendamento de 35 dias atrás injetado no SQLite com sucesso!")

def simular_mensagem_cliente(texto):
    print(f"\n💬 [Cliente]: {texto}")
    payload = {"telefone": TELEFONE_TESTE, "texto": texto}
    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        if res.status_code == 200:
            dados = res.json()
            print(f"🤖 [{os.getenv('NOME_IA', 'Luna')}]: {dados.get('resposta_enviada')}")
        else:
            print(f"❌ Erro no servidor: {res.status_code}")
    except Exception as e:
        print(f"❌ Falha de rede: {str(e)}")

if __name__ == "__main__":
    print("=========================================================")
    print(" 🐾 SIMULANDO CLIENTE ANTIGO - TESTE DE CROSS-SELLING")
    print("=========================================================")
    
    # 1. Injeta o dado antigo no banco
    injetar_agendamento_antigo()
    
    # 2. Cliente entra em contato demonstrando interesse em voltar
    simular_mensagem_cliente("Oi, queria marcar um banho pro Rex essa semana.")
