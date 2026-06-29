import requests

# Bate na rota GET do seu servidor FastAPI ativo
URL_AGENDAMENTOS = "http://localhost:5000/agendamentos"

def consultar_painel_petshop():
    print("=========================================================")
    print(" 📊 CONSULTANDO AGENDAMENTOS SALVOS NO SQLITE - DASHBOARD")
    print("=========================================================")
    
    try:
        res = requests.get(URL_AGENDAMENTOS)
        if res.status_code == 200:
            dados = res.json()
            print(f"✅ Conexão com o Banco: SUCESSO")
            print(f"📈 Total de Agendamentos Cadastrados: {dados.get('total_agendamentos')}\n")
            
            # Varre e exibe cada pet agendado de forma organizada
            for item in dados.get("dados", []):
                print(f"🐾 Pet: {item.get('nome_pet')} | 🤵 Tutor: {item.get('nome_tutor')}")
                print(f"✂️ Serviço: {item.get('servico')} | 📅 Data/Horário: {item.get('data_horario')}")
                print("-" * 40)
        else:
            print(f"❌ Falha ao ler banco: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Erro de rede: {str(e)}")

if __name__ == "__main__":
    consultar_painel_petshop()
