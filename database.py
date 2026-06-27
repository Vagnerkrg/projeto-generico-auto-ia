import sqlite3
from datetime import datetime

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

def verificar_disponibilidade_horario(data_horario: str) -> bool:
    """
    Consulta o banco de dados para verificar se o horário solicitado já está ocupado.
    Retorna True se estiver disponível, e False se estiver ocupado.
    """
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    
    try:
        # Busca se existe algum agendamento ativo no mesmo horário
        cursor.execute("""
            SELECT id FROM agendamentos 
            WHERE data_horario = ? AND status != 'Cancelado'
        """, (data_horario,))
        
        conflito = cursor.fetchone()
        conexao.close()
        
        # Se encontrou algum registro, o horário NÃO está disponível (False)
        if conflito:
            return False
            
        return True
    except sqlite3.OperationalError:
        conexao.close()
        return True  # Retorno seguro caso a tabela mude

# ------------------------------------------------------------------
# 🧠 FUNÇÕES PARA GESTÃO DE MEMÓRIA DA CONVERSA (PASSOS 2 E 3)
# ------------------------------------------------------------------

def salvar_mensagem_historico(telefone: str, papel: str, texto: str):
    """Grava cada mensagem enviada (user) ou recebida (model) no banco de dados SQLite."""
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO historico_conversas (telefone, papel, texto) 
        VALUES (?, ?, ?)
    """, (telefone, papel, texto))
    conexao.commit()
    conexao.close()
    print(f"💾 [Memória] Mensagem do papel '{papel}' salva para o número {telefone}.")

def recuperar_contexto_conversa(telefone: str) -> list:
    """Recupera os últimos 6 diálogos do cliente para injetar como histórico nativo na SDK do Gemini."""
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT papel, texto FROM historico_conversas 
        WHERE telefone = ? 
        ORDER BY id DESC LIMIT 6
    """, (telefone,))
    linhas = cursor.fetchall()
    conexao.close()
    
    # Inverte para manter a ordem cronológica correta da conversa (mais antiga para mais recente)
    conversas = []
    for papel, texto in reversed(linhas):
        conversas.append({"role": papel, "parts": [texto]})
    return conversas

# ------------------------------------------------------------------
# ⏰ NOVA TRAVA: VALIDAÇÃO DE HORÁRIO DE EXPEDIENTE COMERCIAL
# ------------------------------------------------------------------

def validar_horario_funcionamento(data_horario_texto: str) -> bool:
    """
    Verifica se a data e horário informados estão dentro do horário comercial.
    Funcionamento padrão: Segunda a Sexta das 08h às 18h | Sábado das 08h às 12h.
    """
    try:
        # Se o formato for puramente textual (como 'Amanhã às 14h'), liberamos para teste
        if "às" in data_horario_texto or "amanhã" in data_horario_texto.lower():
            return True
            
        # Para validações em formatos reais estruturados (ex: '2026-06-29 23:00')
        data_hora = datetime.strptime(data_horario_texto, "%Y-%m-%d %H:%M")
        dia_semana = data_hora.weekday() # 0 = Segunda, 5 = Sábado, 6 = Domingo
        hora = data_hora.hour
        
        # 1. Bloqueia Domingos completamente
        if dia_semana == 6:
            print("⚠️ [EXPEDIENTE] Recusado: Pet shop fechado aos domingos.")
            return False
            
        # 2. Valida Sábados (Apenas das 08h às 12h)
        if dia_semana == 5:
            if hora < 8 or hora >= 12:
                print("⚠️ [EXPEDIENTE] Recusado: Fora do horário de sábado (08h às 12h).")
                return False
                
        # 3. Valida Dias de Semana normais (Das 08h às 18h)
        if hora < 8 or hora >= 18:
            print("⚠️ [EXPEDIENTE] Recusado: Fora do expediente semanal (08h às 18h).")
            return False
            
        return True
    except Exception:
        # Retorno defensivo: se houver falha na conversão da string, permite para não quebrar a IA
        return True

# ------------------------------------------------------------------
# 📊 NOVA FUNÇÃO: LISTAGEM DE AGENDAMENTOS PARA O DASHBOARD
# ------------------------------------------------------------------

def listar_todos_agendamentos() -> list:
    """
    Busca todos os agendamentos registrados no SQLite.
    Retorna uma lista de dicionários organizada cronologicamente.
    """
    conexao = sqlite3.connect("database/petshop.db")
    cursor = conexao.cursor()
    
    try:
        cursor.execute("""
            SELECT id, telefone, nome_tutor, nome_pet, servico, data_horario, status 
            FROM agendamentos 
            ORDER BY data_horario ASC
        """)
        linhas = cursor.fetchall()
        conexao.close()
        
        agendamentos = []
        for linha in linhas:
            agendamentos.append({
                "id": linha[0],
                "telefone": linha[1],
                "nome_tutor": linha[2],
                "nome_pet": linha[3],
                "servico": linha[4],
                "data_horario": linha[5],
                "status": linha[6]
            })
            
        return agendamentos
    except sqlite3.OperationalError:
        conexao.close()
        return []
