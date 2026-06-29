# 🐶 Agente de IA para Pet Shops – Luna 🐾

Transforme Seu Pet Shop com Automação Inteligente e Código Nativo! 🚀

Otimize o atendimento ao cliente e agilize processos com este Agente de IA construído 100% em **Python nativo e FastAPI**. 📲🐾 Automatize interações, agendamentos e recomendações de serviços diretamente pelo VS Code — com infraestrutura robusta, totalmente gratuita e independente de plataformas no-code!

## 🔹 Principais Funcionalidades
* **✅ Atendimento automático no WhatsApp**: Integração direta via código com o simulador Evolution API v2 para leitura de payloads flexíveis. 💬
* **✅ Agendamento de serviços automatizado**: Motor cognitivo baseado no Google Gemini API (`gemini-2.5-flash`), com persistência de memória de longo prazo. 📅✂️
* **✅ Sincronização em Nuvem**: Injeção automática de agendamentos diretamente na Google Calendar API de forma assíncrona via OAuth2. 📢🐾
* **✅ Persistência de Dados Local**: Banco SQLite nativo para controle de histórico de longo prazo e segurança dos dados. 📊📁
* **✅ Sugestão de produtos e serviços**: Algoritmos comerciais integrados para cross-selling dinâmico de forma contextualizada. 🎁🐶

## 📌 Como Funciona
1. **O Webhook do FastAPI** recebe payloads flexíveis contendo as mensagens dos clientes via WhatsApp.
2. **A IA Luna** resgata o histórico do SQLite, analisa os dados e processa o diálogo fornecendo as opções ideais.
3. **O cliente confirma** as informações e o script dispara a validação de horários duplicados e expediente comercial.
4. **O agendamento** é consolidado no banco local e espelhado automaticamente no Google Agenda.
5. **Lembretes nativos** e automáticos garantem o controle completo de faltas do pet shop.

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
├── rodar_lembretes.py      # Motor de busca e envio de notificações ativas
└── testar_global.py        # Motor bruto de testes de estresse concorrentes
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
7. **PANE 07 (Exclusão Acidental de Configurações)**: Reconstruído arquivo `.env` do absoluto zero contornando colagens lineares incorretas do Windows.
8. **PANE 08 (Vazamento de Dados Binários)**: Desvinculação do arquivo relacional `database/petshop.db` do rastreamento do repositório remoto.
9. **PANE 09 (Erro 404 de Barramento)**: Acoplamento da rota `POST /mock-api/message/sendText/{instance_name}` dando suporte às respostas do motor de lembretes ativos.
10. **PANE 10 (Estouro de RPM - Rate Limit)**: Interceptação preventiva do estouro de cota do plano gratuito do Gemini sob bombardeio de requisições paralelas simultâneas, mantendo a resposta do webhook com sucesso 200 OK.

---

## 👨‍💻 Autor e Desenvolvedor Principal
Este ecossistema foi projetado, desenvolvido e homologado do absoluto zero por:

* **Vagner** — *Engenheiro de Software & Desenvolvedor de Soluções de IA*
* 💻 **GitHub**: [Vagnerkrg](https://github.com)
* 🚀 **LinkedIn**: [Seu Perfil Aqui] *(Dica: substitua essa frase pelo link do seu perfil se quiser)*

---
*Propriedade intelectual protegida de forma local. Desenvolvido para fins de otimização de negócios e portfólio sênior.*
