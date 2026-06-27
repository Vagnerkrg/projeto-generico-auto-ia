import sqlite3
from datetime import datetime, timedelta
import subprocess

def simular_agendamento_amanha():
    print("==========================================================")
    print("🧪 SCRIPT DE TESTE: SIMULAÇÃO DE LEMBRETES ATIVOS")
    print("==========================================================")
    
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    
    # Calcula dinamicamente a data de amanhã para o teste
    data_amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 10:00")
    
    cursor.execute("DELETE FROM agendamentos WHERE nome_tutor = 'Roberto Teste'")
    
    print(f"💾 Inserindo agendamento fictício para AMANHÃ ({data_amanha})...")
    cursor.execute("""
        INSERT INTO agendamentos (telefone, nome_tutor, nome_pet, servico, data_horario, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("5511988887777", "Roberto Teste", "Rex", "Tosa Completa", data_amanha, "Pendente"))
    
    conexao.commit()
    conexao.close()
    print("✅ Registro de teste inserido com sucesso no SQLite!\n")
    
    print("🎬 Acionando o motor nativo 'rodar_lembretes.py'...\n")
    subprocess.run(["python", "rodar_lembretes.py"])

if __name__ == "__main__":
    simular_agendamento_amanha()
