import requests

URL_DASHBOARD = "http://localhost:5000/agendamentos"

def renderizar_painel_petshop():
    print("\n" + "="*80)
    print(" 📊 PAINEL ADMINISTRATIVO DE CONTROLE - PET SHOP AMIGO FIEL")
    print("="*80)
    
    try:
        # Consulta a rota GET do servidor FastAPI
        resposta = requests.get(URL_DASHBOARD, timeout=5)
        
        if resposta.status_code == 200:
            dados_api = resposta.json()
            total = dados_api.get("total_agendamentos", 0)
            registros = dados_api.get("dados", [])
            
            print(f"📈 Total de Serviços Agendados no Sistema: {total}")
            print("-"*80)
            
            # Cabeçalho da Tabela formatado por espaçamento fixo
            print(f"{'ID':<4} | {'TELEFONE':<13} | {'TUTOR':<12} | {'PET':<10} | {'SERVIÇO':<12} | {'DATA/HORÁRIO':<16}")
            print("-"*80)
            
            # Loop para renderizar cada linha do banco SQLite
            for agendamento in registros:
                print(
                    f"{agendamento.get('id'):<4} | "
                    f"{agendamento.get('telefone'):<13} | "
                    f"{agendamento.get('nome_tutor'):<12} | "
                    f"{agendamento.get('nome_pet'):<10} | "
                    f"{agendamento.get('servico'):<12} | "
                    f"{agendamento.get('data_horario'):<16}"
                )
            print("="*80 + "\n")
            
        else:
            print(f"❌ Erro ao acessar a API do Painel: Código HTTP {resposta.status_code}")
            
    except Exception as e:
        print(f"❌ Falha de conexão com o servidor do Dashboard: {str(e)}")

if __name__ == "__main__":
    renderizar_painel_petshop()
