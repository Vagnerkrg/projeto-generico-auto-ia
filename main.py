import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
# Importa as funções do seu arquivo database.py
from database import inicializar_banco, salvar_agendamento

# Carrega as variáveis do arquivo .env e inicializa o banco local
load_dotenv()
inicializar_banco()

# Inicializa o cliente do Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Prompt de sistema que ensina a IA a usar a ferramenta de agendamento
PROMPT_SISTEMA = """
Você é o "PetBot", o assistente virtual inteligente do Pet Shop "Patas & Pelos". 
Seu objetivo é coletar os dados para agendar serviços (Banho, Tosa ou Consulta).

Diretrizes:
1. Seja sempre cortês, use emojis (🐶, 🐱, 🧼, ✂️) e faça respostas curtas.
2. Pergunte e colete: Nome do Tutor, Nome do Pet, Tipo de Serviço e Horário desejado.
3. Assim que coletar ESSES 4 DADOS, use IMEDIATAMENTE a ferramenta 'registrar_no_banco' para salvar o agendamento de forma automática.
"""

# Cria a ferramenta que o Gemini pode acionar de forma autônoma
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

def enviar_mensagem_ao_petbot(mensagem_cliente):
    # Envia a conversa passando a regra do sistema e a ferramenta criada
    resposta = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=mensagem_cliente,
        config=types.GenerateContentConfig(
            system_instruction=PROMPT_SISTEMA,
            temperature=0.4,
            tools=[ferramenta_banco]
        )
    )
    
    # Captura a chamada de função se a IA decidir registrar no banco
    if resposta.function_calls:
        for chamada in resposta.function_calls:
            if chamada.name == "registrar_no_banco":
                # Converte os argumentos da função para um dicionário Python estável
                args = dict(chamada.args)
                
                # Executa a gravação no arquivo SQL local SQLite
                salvar_agendamento(
                    nome_tutor=str(args.get("nome_tutor")),
                    nome_pet=str(args.get("nome_pet")),
                    servico=str(args.get("servico")),
                    data_horario=str(args.get("data_horario"))
                )
                return "✨ [Sistema] Seu agendamento foi registrado com sucesso em nosso banco de dados! Te esperamos aqui! 🐾"

    return respuesta.text if resposta.text else "Entendido! Como posso ajudar seu Pet hoje?"

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🐾 PETBOT - AGENTE INTELIGENTE COM BANHO E TOSA 🐾")
    print("Digite 'sair' para encerrar.")
    print("="*50 + "\n")
    
    historico_conversa = []
    
    while True:
        mensagem_usuario = input("[Cliente]: ")
        if mensagem_usuario.lower() == 'sair':
            break
        if not mensagem_usuario.strip():
            continue
            
        historico_conversa.append(f"Cliente: {mensagem_usuario}")
        contexto_completo = "\n".join(historico_conversa)
        
        resposta_bot = enviar_mensagem_ao_petbot(contexto_completo)
        historico_conversa.append(f"PetBot: {resposta_bot}")
        
        print(f"[PetBot]: {resposta_bot}\n")
