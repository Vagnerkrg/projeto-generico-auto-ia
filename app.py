from fastapi import FastAPI, Request
import uvicorn
from main import enviar_mensagem_ao_petbot

app = FastAPI()

# Rota obrigatória que a Evolution API vai disparar a cada mensagem recebida no WhatsApp
@app.post("/webhook")
async def receber_mensagem_whatsapp(request: Request):
    dados = await request.json()
    print("📩 [Webhook] Nova mensagem recebida do WhatsApp!")
    
    try:
        # Extrai os dados básicos enviados pela Evolution API
        mensagem_texto = dados.get("data", {}).get("message", {}).get("conversation", "")
        numero_cliente = dados.get("data", {}).get("key", {}).get("remoteJid", "")
        
        # Ignora mensagens vazias ou mensagens enviadas pelo próprio bot
        from_me = dados.get("data", {}).get("key", {}).get("fromMe", False)
        if from_me or not mensagem_texto:
            return {"status": "ignorado"}
            
        print(f"📱 De: {numero_cliente} | Mensagem: {mensagem_texto}")
        
        # Envia a mensagem do cliente para a inteligência do nosso PetBot
        resposta_ia = enviar_mensagem_ao_petbot(mensagem_texto)
        print(f"🤖 Resposta do PetBot: {resposta_ia}")
        
        # TODO: Aqui colocaremos a função HTTP Request para disparar a 'resposta_ia' 
        # de volta para o WhatsApp do cliente usando a Evolution API.
        
        return {"status": "sucesso", "resposta": resposta_ia}
        
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {e}")
        return {"status": "erro", "detalhe": str(e)}

if __name__ == "__main__":
    # Roda o servidor local na porta 5000
    uvicorn.run(app, host="0.0.0.0", port=5000)
