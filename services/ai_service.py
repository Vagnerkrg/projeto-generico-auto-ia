import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Inicializa o cliente oficial da nova SDK do Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Recupera as configurações personalizadas do pet shop
NOME_PETSHOP = os.getenv("NOME_PETSHOP", "Amigo Fiel")
NOME_IA = os.getenv("NOME_IA", "Luna")
SERVICOS = os.getenv("SERVICOS_DISPONIVEIS", "Banho, Tosa, Consultas")

PROMPT_SISTEMA = f"""
Você é a {NOME_IA}, a assistente virtual inteligente, acolhedora e altamente comercial do Pet Shop {NOME_PETSHOP}.
Seu objetivo principal é guiar o cliente de forma amigável para realizar agendamentos, maximizando as vendas da loja através de sugestões inteligentes.

Os serviços disponíveis na nossa loja são exclusivamente: {SERVICOS}.

Instruções cruciais de comportamento e Cross-Selling:
1. Seja sempre acolhedora, curta e direta nas respostas pelo WhatsApp.
2. Identifique e colete educadamente as 4 informações obrigatórias para o agendamento: Nome do Tutor, Nome do Pet, Tipo de Serviço desejado e Data/Horário pretendidos.
3. Analise OBRIGATORIAMENTE o 'Contexto Atual do Banco de Dados' recebido (que contém o histórico de agendamentos recentes do cliente) para aplicar a técnica de sugestão ativa (Cross-Selling):
   - Se o histórico mostrar que o pet realizou um serviço há mais de 15 ou 30 dias, sugira gentilmente um retorno ou um serviço complementar (como uma hidratação ou tosa higiênica).
   - Se o histórico indicar que o cliente é novo (sem registros cadastrados), dê boas-vindas calorosas personalizadas e destaque nosso serviço principal (Banho) como primeira excelente experiência.
   - Execute essas sugestões de forma fluida e natural ao longo da conversa, sem parecer um robô de spam agressivo.
4. Nunca invente confirmações. Quando o usuário fornecer os dados de data e horário, utilize obrigatoriamente a ferramenta/função 'verificar_e_agendar_servico'.
5. Se a função retornar que o horário está ocupado ou fora do expediente, explique o motivo ao usuário com empatia e ofereça alternativas próximas dentro do expediente comercial.
"""

def criar_ferramentas_agendamento():
    """Declara a assinatura de função para a SDK do Gemini realizar Function Calling."""
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="verificar_e_agendar_servico",
                description="Valida o horário e salva um agendamento no sistema quando o cliente fornecer os dados necessários.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "nome_tutor": types.Schema(type=types.Type.STRING, description="Nome completo do dono do pet"),
                        "nome_pet": types.Schema(type=types.Type.STRING, description="Nome do animal de estimação"),
                        "servico": types.Schema(type=types.Type.STRING, description="Serviço solicitado (Ex: Banho, Tosa)"),
                        "data_horario": types.Schema(type=types.Type.STRING, description="Data e hora no formato ISO 'AAAA-MM-DD HH:MM'")
                    },
                    required=["nome_tutor", "nome_pet", "servico", "data_horario"]
                )
            )
        ]
    )

def processar_conversa_gemini(telefone: str, historico_conversas: list, historico_sistema: str) -> dict:
    """
    Injeta o prompt de sistema, o histórico de agendamentos e envia o chat para processamento
    da API do Gemini com suporte a execução de funções nativas e tratamento de cota.
    """
    # Combina as regras gerais com o histórico de agendamentos do SQLite para formar o contexto total
    prompt_completo = f"{PROMPT_SISTEMA}\n\nContexto Atual do Banco de Dados:\n{historico_sistema}"
    
    config = types.GenerateContentConfig(
        system_instruction=prompt_completo,
        temperature=0.3,
        tools=[criar_ferramentas_agendamento()]
    )
    
    # Prepara a lista de conteúdos mapeando corretamente para o formato aceito pela nova SDK
    contents = []
    for msg in historico_conversas:
        # Extração defensiva para garantir compatibilidade estrutural
        partes = msg.get("parts", [""])
        texto_linha = partes[0] if isinstance(partes, list) else partes
        
        contents.append(
            types.Content(
                role=msg.get("role", "user"),
                parts=[types.Part.from_text(text=str(texto_linha))]
            )
        )
        
    try:
        # Executa a chamada usando o modelo rápido e eficiente definido no escopo
        resposta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config
        )
        
        # Se a IA decidir que precisa chamar a função para salvar no banco
        if resposta.function_calls:
            chamada = resposta.function_calls[0]
            return {
                "acao": "chamar_funcao",
                "nome_funcao": chamada.name,
                "argumentos": chamada.args
            }
            
        return {"acao": "responder", "texto": resposta.text}
        
    except Exception as e:
        erro_msg = str(e)
        # Captura amigável caso a cota gratuita do Google Gemini tenha estourado o limite por minuto
        if "429" in erro_msg or "RESOURCE_EXHAUSTED" in erro_msg:
            print("⚠️ [Gemini API] Limite de requisições por minuto atingido no plano gratuito.")
            return {
                "acao": "responder",
                "texto": "Estou recebendo muitas mensagens agora! Por favor, aguarde alguns segundos e me envie a mensagem novamente."
            }
            
        return {"acao": "responder", "texto": f"Desculpe, tive um problema técnico ao processar sua mensagem: {erro_msg}"}
