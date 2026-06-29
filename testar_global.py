import asyncio
import httpx
import time
import sqlite3
from database import listar_todos_agendamentos

URL_WEBHOOK = "http://localhost:5000/webhook"

async def enviar_requisicao_estresse(client, id_teste, telefone, texto):
    """Dispara uma mensagem simulando concorrência em tempo real."""
    payload = {"telefone": telefone, "texto": texto}
    print(f"🚀 [Thread-{id_teste}] Enviando: '{texto}' para o telefone {telefone}...")
    try:
        resposta = await client.post(URL_WEBHOOK, json=payload, timeout=30.0)
        print(f"📥 [Thread-{id_teste}] Resposta recebida (Status: {resposta.status_code})")
        return resposta.json()
    except Exception as e:
        print(f"❌ [Thread-{id_teste}] Falha na requisição: {str(e)}")
        return None

async def rodar_teste_estresse():
    print("\n" + "💥" * 35)
    print(" 🔥 INICIANDO TESTE DE ESTRESSE BRUTO E CONCORRÊNCIA MÁXIMA")
    print("💥" * 35 + "\n")
    
    # Lista de cenários agressivos sendo disparados ao mesmo tempo
    cenarios = [
        # Disparos Simultâneos (Cenário de pico de mensagens)
        (1, "5511911112222", "Quero agendar um Banho para o meu gato Simba amanhã às 14:00 por favor"),
        (2, "5511933334444", "Luna, marca uma Tosa para o Thor amanhã às 14:00 sem falta"), # Teste de Choque Simétrico
        (3, "5511955556666", "Olá, gostaria de agendar uma Consulta Veterinária pro meu cachorro Bob amanhã às 14:00"), # Terceiro choque
        
        # Cenários de Horário Proibido e Madrugada
        (4, "5511977778888", "Preciso de um Banho pro Fred hoje às 23:30 da noite, pode ser?"), 
        (5, "5511999990000", "Quero agendar uma consulta pro meu pet domingo às 03:00 da manhã"),
        
        # Mensagens sem sentido ou Dados Incompletos
        (6, "5511922223333", "Quero agendar algo para o meu bicho de estimação amanhã"),
        (7, "5511944445555", "Qual o valor dos serviços e o horário de funcionamento de vocês?")
    ]
    
    start_time = time.time()
    
    # Abre uma única sessão HTTP asssíncrona para bombardear o servidor FastAPI
    async with httpx.AsyncClient() as client:
        tarefas = [enviar_requisicao_estresse(client, *cenario) for cenario in cenarios]
        # Executa todas as 7 requisições EXATAMENTE AO MESMO TEMPO
        resultados = await asyncio.gather(*tarefas)
        
    end_time = time.time()
    
    print("\n" + "="*70)
    print(f"📊 RESUMO DO TESTE DE ESTRESSE")
    print(f"⏱️ Tempo total para processar {len(cenarios)} requisições pesadas de IA: {end_time - start_time:.2f} segundos")
    print("="*70)
    
    print("\n🔎 Verificando integridade do banco SQLite pós-bombardeio...")
    try:
        dados = listar_todos_agendamentos()
        print(f"📈 Total de registros persistidos com segurança no banco: {len(dados)}")
    except Exception as e:
        print(f"❌ Erro ao acessar o banco de dados: {str(e)}")

if __name__ == "__main__":
    # Inicializa o loop assíncrono do Python de forma nativa
    asyncio.run(rodar_teste_estresse())
