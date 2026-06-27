import requests
import os

def enviar_mensagem_whatsapp(telefone: str, texto: str):
    """
    Função nativa para disparar a resposta de volta para o cliente.
    Mapeada para funcionar de forma flexível com APIs de integração.
    """
    # Exibe no terminal local para auditoria de testes
    print(f"📤 [WhatsApp Out] Enviando mensagem para {telefone}...")
    print(f"💬 Conteúdo: {texto}")
    
    # ------------------------------------------------------------------
    # GABARITO DE INTEGRAÇÃO (Pronto para plugar em Gateways/APIs)
    # ------------------------------------------------------------------
    # Quando você for rodar no cliente final, basta preencher essas variáveis no .env
    # URL_API = os.environ.get("URL_API_WHATSAPP")
    # TOKEN_API = os.environ.get("TOKEN_API_WHATSAPP")
    
    # payload = {
    #     "number": telefone,
    #     "text": texto
    # }
    # headers = {"Authorization": f"Bearer {token_api}"}
    # requests.post(f"{url_api}/messages/send", json=payload, headers=headers)
    
    return True
