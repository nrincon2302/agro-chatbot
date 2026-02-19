import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
load_dotenv()

from app.services.whatsapp_service import send_text, send_buttons, send_list
from app.chatbot.state import get_state
from app.chatbot.flow import handle_message
from app.chatbot.data import CATEGORIES

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app = FastAPI()


@app.get("/")
def health():
    return {"status": "running"}


# --- Verificación webhook ---
@app.get("/webhook")
async def verify_webhook(request: Request):

    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))

    return {"status": "error"}


# --- Recepción mensajes ---
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return {"status": "ok"}

        message = value["messages"][0]
        from_number = message["from"]

        # --- Detectar tipo ---
        if message["type"] == "interactive":
            interactive = message["interactive"]

            if interactive["type"] == "button_reply":
                text = interactive["button_reply"]["id"]
            elif interactive["type"] == "list_reply":
                text = interactive["list_reply"]["id"]
            else:
                return {"status": "ok"}
        else:
            text = message["text"]["body"]

        reply = handle_message(from_number, text)

        # --- Render respuesta ---
        if reply["type"] == "menu":

            rows = []

            for key, cat in CATEGORIES.items():
                rows.append({
                    "id": f"cat_{key}",
                    "title": f"{cat['emoji']} {cat['title']}",
                    "description": "Asesoría técnica especializada"
                })

            sections = [{
                "title": "Áreas disponibles",
                "rows": rows
            }]

            send_list(
                from_number,
                "🌱 *Asistente Agro*\n\n"
                "Soy tu asistente técnico especializado en producción agropecuaria.\n\n"
                "Puedo ayudarte a:\n"
                "• Calcular costos\n"
                "• Mejorar productividad\n"
                "• Resolver dudas técnicas\n\n"
                "Selecciona un área para comenzar 👇",
                "Ver áreas",
                sections
            )


        elif reply["type"] == "questions":

            category_key = reply["category"]
            questions = CATEGORIES[category_key]["questions"]

            rows = []

            for i, q in enumerate(questions):
                rows.append({
                    "id": f"q_{category_key}_{i}",
                    "title": f"Pregunta {i+1}",
                    "description": q[:72]
                })

            rows.append({
                "id": "menu_back",
                "title": "⬅ Volver",
                "description": "Regresar al menú principal"
            })

            sections = [{
                "title": "Consultas sugeridas",
                "rows": rows
            }]

            send_list(
                from_number,
                "📋 Selecciona una pregunta sugerida o escribe la tuya:",
                "Ver preguntas",
                sections
            )


        elif reply["type"] == "answer":

            send_text(from_number, reply["text"])

            send_buttons(
                from_number,
                "¿Deseas hacer otra consulta?",
                [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "new_question",
                            "title": "Nueva consulta"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "menu_back",
                            "title": "Volver al menú"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "goodbye",
                            "title": "Finalizar"
                        }
                    }
                ]
            )

        elif reply["type"] == "goodbye":

            send_text(
                from_number,
                "👋 *Gracias por usar Asistente Agro.*\n\n"
                "Fue un gusto ayudarte.\n"
                "Cuando necesites apoyo técnico, aquí estaré.\n\n"
                "¡Hasta la próxima! 🌾"
            )

    except Exception as e:
        print("ERROR WEBHOOK:", e)

    return {"status": "ok"}
