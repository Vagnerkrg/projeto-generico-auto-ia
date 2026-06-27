import sqlite3

def inicializar_banco():
    # Cria ou conecta ao arquivo do banco de dados dentro da pasta correta
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    
    # Cria a tabela de agendamentos atualizada com a coluna telefone
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telefone TEXT,
        nome_tutor TEXT,
        nome_pet TEXT,
        servico TEXT,
        data_horario TEXT,
        status TEXT DEFAULT 'Pendente'
    )
    """)
    conexao.commit()
    conexao.close()
    print("📋 [Banco de Dados] Tabela inicializada com sucesso!")

def salvar_agendamento(telefone, nome_tutor, nome_pet, servico, data_horario):
    # Conecta ao arquivo do banco de dados dentro da pasta correta
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    
    cursor.execute("""
    INSERT INTO agendamentos (telefone, nome_tutor, nome_pet, servico, data_horario)
    VALUES (?, ?, ?, ?, ?)
    """, (telefone, nome_tutor, nome_pet, servico, data_horario))
    
    conexao.commit()
    conexao.close()
    print("💾 [Banco de Dados] Agendamento salvo com sucesso localmente!")

def buscar_historico_tutor(telefone: str) -> str:
    """
    Busca os agendamentos recentes do cliente pelo número de telefone
    para servir de contexto de memória para o Gemini.
    """
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    
    try:
        # Busca os 3 agendamentos mais recentes daquele número
        cursor.execute("""
            SELECT nome_tutor, nome_pet, servico, data_horario, status 
            FROM agendamentos 
            WHERE telefone = ? 
            ORDER BY id DESC LIMIT 3
        """, (telefone,))
        
        registros = cursor.fetchall()
        conexao.close()
        
        if not registros:
            return "Histórico: Este é um cliente novo, sem agendamentos cadastrados."
            
        # Formata os dados para o prompt do Gemini compreender
        historico_texto = "Histórico de agendamentos recentes deste cliente no sistema:\n"
        for reg in registros:
            historico_texto += f"- Tutor: {reg[0]} | Pet: {reg[1]} | Serviço: {reg[2]} | Horário: {reg[3]} | Status: {reg[4]}\n"
            
        return historico_texto
        
    except sqlite3.OperationalError:
        conexao.close()
        return "Histórico: Não foi possível ler os registros anteriores."
