import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ['https://googleapis.auth']
CREDENTIALS_FILE = 'services/credentials.json'
TOKEN_FILE = 'services/token.json'

def obter_fluxo_autenticacao():
    """Configura o fluxo OAuth2 apontando para o redirecionamento correto da porta 5000."""
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:5000/oauth2callback'
    )
    return flow

def obter_servico_calendario():
    """Retorna o serviço do Google Calendar se o token.json existir e for válido."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        else:
            return None # Requer nova autenticação via rota web
            
    return build('calendar', 'v3', credentials=creds)

def criar_evento_petshop(resumo, descricao, data_hora_inicio, duracao_minutos=60):
    """Insere um agendamento diretamente na agenda do Google."""
    service = obter_servico_calendario()
    if not service:
        print("[ERRO] Token inválido ou inexistente. Luna precisa de reautenticação.")
        return None
        
    inicio = datetime.datetime.fromisoformat(data_hora_inicio)
    fim = inicio + datetime.timedelta(minutes=duracao_minutos)
    
    evento = {
        'summary': resumo,
        'description': descricao,
        'start': {'dateTime': inicio.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': fim.isoformat(), 'timeZone': 'America/Sao_Paulo'},
    }
    
    evento_criado = service.events().insert(calendarId='primary', body=evento).execute()
    print(f"[SUCESSO] Evento criado no Google Calendar: {evento_criado.get('htmlLink')}")
    return evento_criado
