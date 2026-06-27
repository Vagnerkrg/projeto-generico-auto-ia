import os
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import buscar_agendamentos_por_data
from services.whatsapp_bot import enviar_mensagem_whatsapp

load_dotenv()
NOME_PETSHOP = os.getenv("NOME_PETSHOP", "Amigo Fiel")

def disparar_lembretes_ativos():
    print("==========================================================")
    print("📢 MOTOR DE LEMBRETES ATIVOS - PET SHOP NATIVO")
    print("==========================================================")
    
    # Calcula dinamicamente a data de amanhã (formato AAAA-MM-DD)
    amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"📅 Buscando agendamentos pendentes para amanhã: {amanha}...")
    
    clientes_alvo = buscar_agendamentos_por_data(amanha)
    total = len(clientes_alvo)
    print(f"📊 Encontrado(s) {total} agendamento(s) para notificar.\n")
    
    if total == 0:
        print("✨ Nenhum lembrete precisa ser enviado hoje. Sistema em espera.")
        return
        
    for cliente in clientes_alvo:
        telefone = cliente["telefone"]
        tutor = cliente["nome_tutor"]
        pet = cliente["nome_pet"]
        servico = cliente["servico"]
        data_bruta = cliente["data_horario"]
        
        # Extração do horário de forma segura contra falhas de índice
        partes = data_bruta.split(" ")
        horario_limpo = partes[1] if len(partes) > 1 else data_bruta
        
        mensagem_lembrete = (
            f"Olá, {tutor}! Passando para lembrar que amanhã, o(a) *{pet}* tem um horário marcado "
            f"para *{servico}* aqui no *{NOME_PETSHOP}* às *{horario_limpo}*. 🐾\n\n"
            f"Confirmado? Se precisar remarcar, basta me avisar por aqui! 😊"
        )
        
        print(f"🚀 Enviando lembrete para {tutor} (Pet: {pet}) no número {telefone}...")
        enviar_mensagem_whatsapp(telefone, mensagem_lembrete)
        
    print("\n✅ Todos os lembretes diários foram processados com sucesso!")

if __name__ == "__main__":
    disparar_lembretes_ativos()
