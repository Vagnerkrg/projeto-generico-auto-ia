import sqlite3

def inicializar_banco():
    # Cria ou conecta ao arquivo do banco de dados local
    conexao = sqlite3.connect("petshop.db")
    cursor = conexao.cursor()
    
    # Cria a tabela de agendamentos caso ela não exista
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_tutor TEXT,
        nome_pet TEXT,
        servico TEXT,
        data_horario TEXT,
        status TEXT DEFAULT 'Pendente'
    )
    """)
    conexao.commit()
    conexao.close()

def salvar_agendamento(nome_tutor, nome_pet, servico, data_horario):
    conexao = sqlite3.connect("petshop.db")
    cursor = conexao.cursor()
    
    cursor.execute("""
    INSERT INTO agendamentos (nome_tutor, nome_pet, servico, data_horario)
    VALUES (?, ?, ?, ?)
    """, (nome_tutor, nome_pet, servico, data_horario))
    
    conexao.commit()
    conexao.close()
    print("💾 [Banco de Dados] Agendamento salvo com sucesso localmente!")
