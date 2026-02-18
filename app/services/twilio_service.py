import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)
FROM_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

def send_text(to, body):
    client.messages.create(
        from_=FROM_NUMBER,
        to=to,
        body=body
    )

def send_menu(to):
    body = (
        "🌱 *Asistente Agro*\n\n"
        "Selecciona una categoría:\n\n"
        "1️⃣ Ganadería\n"
        "2️⃣ Avicultura\n"
        "3️⃣ Cunicultura\n"
        "4️⃣ Hortalizas\n\n"
        "Responde con el número."
    )

    client.messages.create(
        from_=FROM_NUMBER,
        to=to,
        body=body
    )
