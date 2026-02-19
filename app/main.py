import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

from app.services.whatsapp_service import send_text
from app.chatbot.flow import handle_message

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            text = message["text"]["body"]

            print("MENSAJE ENTRANTE:", text)

            reply = handle_message(from_number, text)

            send_text(from_number, reply)

    except Exception as e:
        print("ERROR WEBHOOK:", e)

    return {"status": "ok"}


VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))

    return {"status": "error"}
