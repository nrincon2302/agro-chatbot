from fastapi import FastAPI, Form
from dotenv import load_dotenv
from app.services.twilio_service import send_text
from app.chatbot.flow import handle_message

load_dotenv()

app = FastAPI()

@app.post("/webhook")
async def webhook(
    From: str = Form(...),
    Body: str = Form(None),
    ButtonText: str = Form(None)
):
    incoming = Body or ButtonText or ""
    
    reply = handle_message(From, incoming)
    send_text(From, reply)

    return {"status": "ok"}
