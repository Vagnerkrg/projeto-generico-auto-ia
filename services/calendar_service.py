import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define as permissões necessárias (Acesso de leitura e escrita na agenda)
SCOPES = ["https://googleapis.com"]

def obter_servico_calendario():
    """
    Gerencia o fluxo de autenticação OAuth2 do Google de forma nativa.
    Gera localmente o token de acesso de modo 100% gratuito.
    """
    creds = None
    token_path = "config/token.json"
    credentials_path = "config/credentials.json"

    # Se o token já existir localmente, reutiliza para não pedir login toda vez
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # Se não houver credenciais válidas, realiza o fluxo de login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"⚠️ Arquivo '{credentials_path}' não encontrado. Crie a pasta 'config/' e coloque as credenciais do Google lá.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Salva o token gerado para as próximas execuções
        os.makedirs("config", exist_ok=True)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        # Constrói o cliente de serviço oficial da API do Google Calendar
        servico = build("calendar", "v3", credentials=creds)
        return servico
    except HttpError as erro:
        print(f"❌ Erro ao conectar na API do Google Calendar: {erro}")
        return None

def criar_evento_agenda(summary, description, start_time_str, duration_minutes=60):
    """
    Cria um evento na agenda principal do Google.
    start_time_str deve vir no formato: 'YYYY-MM-DD HH:MM'
    """
    servico = obter_servico_calendario()
    if not servico:
        return {"status": "erro", "mensagem": "Não foi possível autenticar no Google Calendar."}

    try:
        # Converte a string de data/hora para o formato ISO exigido pelo Google
        data_hora_inicio = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        data_hora_fim = data_hora_inicio + datetime.timedelta(minutes=duration_minutes)
        
        # Estrutura do payload oficial do Google Event
        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": data_hora_inicio.isoformat(),
                "timeZone": "America/Sao_Paulo",
            },
            "end": {
                "dateTime": data_hora_fim.isoformat(),
                "timeZone": "America/Sao_Paulo",
            },
        }

        # Insere o evento na agenda padrão ('primary') do usuário autenticado
        evento_criado = servico.events().insert(calendarId="primary", body=event).execute()
        print(f"📅 [Google Calendar] Evento criado: {evento_criado.get('htmlLink')}")
        
        return {"status": "sucesso", "id_evento": evento_criado.get("id")}
        
    except Exception as e:
        print(f"❌ [Google Calendar] Erro ao criar evento: {str(e)}")
        return {"status": "erro", "mensagem": str(e)}

# --- BLOCO DE TESTE LOCAL ---
if __name__ == "__main__":
    print("🤖 Iniciando teste do módulo de calendário...")
    # Executa apenas a tentativa de carregar o serviço básico
    obter_servico_calendario()
