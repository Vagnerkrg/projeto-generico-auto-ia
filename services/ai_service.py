import os
from google import genai
from google.genai import types

# Inicializa o cliente do Gemini usando a API Key do ambiente
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

PROMPT_SISTEMA = """
Você é o "PetBot", o assistente virtual inteligente do Pet Shop "Patas & Pelos". 
Seu objetivo é coletar os dados para agendar serviços (Banho, Tosa ou Consulta).

Diretrizes:
1. Seja sempre cortês, use emojis (🐶, 🐱, 🧼, ✂️) e faça respostas curtas.
2. Pergunte e colete: Nome do Tutor, Nome do Pet, Tipo de Serviço e Horário desejado.
3. Assim que coletar ESSES 4 DADOS, use IMEDIATAMENTE a ferramenta 'registrar_no_banco' para salvar o agendamento de forma automática.
"""

# Declaração da ferramenta de banco de dados para a IA
ferramenta_banco = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="registrar_no_banco",
            description="Salva o agendamento concluído no banco de dados do Pet Shop.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "nome_tutor": types.Schema(type=types.Type.STRING, description="Nome do dono do pet"),
                    "nome_pet": types.Schema(type=types.Type.STRING, description="Nome do animal de estimação"),
                    "servico": types.Schema(type=types.Type.STRING, description="Serviço solicitado (Banho, Tosa ou Consulta)"),
                    "data_horario": types.Schema(type=types.Type.STRING, description="Data e horário combinado")
                },
                required=["nome_tutor", "nome_pet", "servico", "data_horario"]
            )
        )
    ]
)

def processar_resposta_gemini(mensagem_cliente: str):
    """Envia a mensagem ao Gemini e retorna o objeto bruto de resposta para o roteamento do app.py."""
    resposta = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=mensagem_cliente,
        config=types.GenerateContentConfig(
            system_instruction=PROMPT_SISTEMA,
            temperature=0.4,
            tools=[ferramenta_banco]
        )
    )
    return resposta
