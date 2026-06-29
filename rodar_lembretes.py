import os
import datetime
from database import buscar_agendamentos_por_data
from services.whatsapp_bot import enviar_mensagem_whatsapp

def disparar_lembretes_noturnos():
    print("=========================================================")
    print(" 📢 EXECUTANDO MOTOR DE LEMBRETES AUTOMÁTICOS DO PET SHOP")
    print("=========================================================")
    
    # Calcula exatamente a data de amanhã
    amanha = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"📅 Varrendo o banco local em busca de agendamentos para amanhã: {amanha}...")
    
    try:
        # Busca no SQLite de forma nativa
        agendamentos_amanha = buscar_agendamentos_por_data(amanha)
        total = len(agendamentos_amanha)
        print(f"📈 Total de lembretes encontrados para amanhã: {total}\n")
        
        if total == 0:
            print("💤 Nenhum compromisso agendado para amanhã. Motor encerrado.")
            return
            
        for item in agendamentos_amanha:
            telefone = item.get("telefone")
            nome_tutor = item.get("nome_tutor")
            nome_pet = item.get("nome_pet")
            servico = item.get("servico")
            
            # Tratamento seguro para extrair o horário do texto salvo
            data_horario_bruta = item.get("data_horario", "")
            if " " in data_horario_bruta:
                partes = data_horario_bruta.split(" ")
                horario = partes[1] if len(partes) > 1 else partes[0]
            else:
                horario = data_horario_bruta if data_horario_bruta else "horário agendado"
            
            # Monta a mensagem ativa inteligente personalizada com os dados do .env
            mensagem = (
                f"Olá, {nome_tutor}! 👋 Aqui é a {os.getenv('NOME_IA', 'Luna')} do Pet Shop {os.getenv('NOME_PETSHOP', 'Amigo Fiel')}. 🐶\n\n"
                f"Passando para lembrar que amanhã ({amanha}) o(a) *{nome_pet}* tem um horário agendado conosco para *{servico}* às *{horario}*! 🗓️✨\n\n"
                f"Contamos com a presença de vocês! Se precisar reagendar, avisar com antecedência. 🐾"
            )
            
            print(f"📤 Disparando Lembrete Ativo para {nome_tutor} (Pet: {nome_pet})...")
            
            # CORREÇÃO CIRÚRGICA: Passando as variáveis de forma direta por posição, sem o 'message='
            enviar_mensagem_whatsapp(telefone, mensagem)
            print("✅ Mensagem processada com sucesso no barramento!\n")
            
    except Exception as e:
        print(f"❌ Erro na execução do motor de lembretes: {str(e)}")

if __name__ == "__main__":
    disparar_lembretes_noturnos()
