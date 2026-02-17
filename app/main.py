from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.chatbot import find_best_match
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    incoming_msg = form.get("Body")

    response_text = find_best_match(incoming_msg)

    twilio_response = MessagingResponse()
    twilio_response.message(response_text)

    return JSONResponse(content=str(twilio_response), media_type="application/xml")

@app.post("/chat")
async def chat_web(message: dict):
    user_message = message["message"]
    response_text = find_best_match(user_message)
    return {"response": response_text}

@app.get("/")
async def root():
    return {"message": "¡Bienvenido al Agro-Chatbot! Envíame un mensaje para obtener información sobre agricultura."}
