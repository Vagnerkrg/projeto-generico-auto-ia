from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
# Importa o novo serviço de IA isolado seguindo as boas práticas de arquitetura
from services.ai_service import processar_resposta_gemini

app = FastAPI()

# Define a estrutura exata para liberar os campos de digitação na tela do Swagger Docs
class KeyModel(BaseModel):
    remoteJid: str
    fromMe: bool

class MessageModel(BaseModel):
    conversation: str

class DataModel(BaseModel):
    message: MessageModel
    key: KeyModel

class WebhookPayload(BaseModel):
    data: DataModel

# Rota do Webhook configurada com o modelo estruturado profissional
@app.post("/webhook")
async def receber_mensagem_whatsapp(payload: WebhookPayload):
    print("📩 [Webhook] Nova mensagem recebida do WhatsApp!")
    
    try:
        # Extrai os dados validados com base no modelo criado
        mensagem_texto = payload.data.message.conversation
        numero_cliente = payload.data.key.remoteJid
        from_me = payload.data.key.fromMe
        
        # Ignora mensagens vazias ou mensagens enviadas pelo próprio bot
        if from_me or not mensagem_texto:
            return {"status": "ignorado"}
            
        print(f"📱 De: {numero_cliente} | Mensagem: {mensagem_texto}")
        
        # Envia a mensagem do cliente para o novo serviço de IA isolado
        resposta_ia = processar_resposta_gemini(mensagem_texto)
        print(f"🤖 Resposta do PetBot: {resposta_ia}")
        
        return {"status": "sucesso", "resposta": resposta_ia}
        
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {e}")
        return {"status": "erro", "detalhe": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
