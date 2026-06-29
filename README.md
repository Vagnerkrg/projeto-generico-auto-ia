# 🐶 Agente de IA para Pet Shops – Luna 🐾

Agente de atendimento e agendamento inteligente automatizado construído 100% em **Python nativo e FastAPI**, operando de forma totalmente independente de plataformas no-code (como n8n) e estruturado em arquitetura gratuita de alta performance.

## 🚀 Principais Funcionalidades
* **Atendimento Inteligente**: Integração direta via código com o simulador Evolution API v2 para leitura de payloads flexíveis do WhatsApp.
* **Motor Cognitivo Estável**: Motor conversacional baseado no Google Gemini API (`gemini-2.5-flash`), com persistência de memória comercial de longo prazo e cross-selling de serviços.
* **Sincronização em Nuvem**: Injeção e espelhamento assíncrono de agendamentos diretamente na Google Calendar API de forma nativa via OAuth2.
* **Persistência Relacional**: Banco de dados SQLite local (`database/petshop.db`) com travas comerciais rígidas contra choque de horários duplicados e validação de expediente.
* **Painel Administrativo**: Script complementar `exibir_dashboard.py` para gerenciamento tabular instantâneo dos atendimentos via terminal.

## 📂 Arquitetura do Projeto
```text
├── database/
│   └── petshop.db          # Banco de dados relacional SQLite
├── services/
│   ├── ai_service.py       # Pipeline cognitivo do Gemini
│   ├── calendar_service.py # Integração nativa Google Calendar API
│   └── whatsapp_bot.py     # Simulador integrado Evolution API v2
├── app.py                  # Servidor principal FastAPI e rotas webhook
├── exibir_dashboard.py     # Painel de controle administrativo tabular
├── ligar_tunnel.py         # Inicializador automatizado do túnel pyngrok
├── testar_bot.py           # Script de simulação conversacional automatizada
└── .gitignore              # Blindagem de segurança de chaves locais
```

## ⚙️ Instruções de Reinicialização (Modo de Recuperação Rápida)
Caso o ecossistema seja desligado ou a máquina reiniciada, execute os comandos abaixo no terminal PowerShell exatamente nesta ordem:

### Terminal 1: Servidor Web FastAPI
```powershell
.\venv\Scripts\Activate.ps1
\$env:OAUTHLIB_INSECURE_TRANSPORT="1"
uvicorn app:app --reload --port 5000
```

### Terminal 2: Túnel de Rede Externa
```powershell
.\venv\Scripts\Activate.ps1
python ligar_tunnel.py
```

### Terminal 3: Consultas e Dashboard
```powershell
.\venv\Scripts\Activate.ps1
python exibir_dashboard.py
```

## 📊 Histórico de Engenharia e Panes Mitigadas
1. **PANE 01 (OAuth2 Web)**: Correção do ID de cliente de Desktop para Aplicativo Web, configurando URIs estáveis para localhost.
2. **PANE 02 (Escopo Google)**: Resolução do erro `invalid_scope` alinhando a URL oficial completa no GCP.
3. **PANE 03 (Transporte Inseguro)**: Forçamento da variável `OAUTHLIB_INSECURE_TRANSPORT="1"` direto na raiz do terminal.
4. **PANE 04 (PKCE Bypass)**: Captura e persistência dinâmica do parâmetro `flow.code_verifier` contornando a ausência de chaves de verificação.
5. **PANE 05 (Autenticação 401)**: Mitigação do erro `ACCESS_TOKEN_TYPE_UNSUPPORTED` substituindo tokens dinâmicos por chaves estruturadas no Google AI Studio.
6. **PANE 06 (GitHub Push Protection)**: Aplicação profunda de `git filter-branch` para expurgar retroativamente arquivos `.env` e segredos sensíveis do histórico remoto, blindando o repositório via SSH.
