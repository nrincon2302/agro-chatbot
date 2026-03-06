import os
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import Response
from dotenv import load_dotenv
load_dotenv()

from app.services.whatsapp_service import send_text, send_buttons, send_list
from app.chatbot.state import get_state
from app.chatbot.flow import handle_message
from app.chatbot.data import CATEGORIES
from app.chatbot.filter import apply_filter
from app.chatbot import logger

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

DISCLAIMER = (
    "\n\n─────────────────────\n"
    "ℹ️ _La información suministrada es orientativa y no reemplaza "
    "la asistencia técnica profesional en campo._"
)

app = FastAPI()


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {"status": "running"}


# ── Verificación webhook ───────────────────────────────────────────────────────

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))
    return {"status": "error"}


# ── Recepción de mensajes ──────────────────────────────────────────────────────

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

        # Detectar tipo de mensaje
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

        # ── Render respuesta ───────────────────────────────────────────────────

        if reply["type"] == "menu":
            rows = [
                {
                    "id": f"cat_{key}",
                    "title": f"{cat['emoji']} {cat['title']}",
                    "description": "Asesoría técnica especializada"
                }
                for key, cat in CATEGORIES.items()
            ]
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
                [{"title": "Áreas disponibles", "rows": rows}]
            )

        elif reply["type"] == "questions":
            category_key = reply["category"]
            questions = CATEGORIES[category_key]["questions"]
            rows = [
                {
                    "id": f"q_{category_key}_{i}",
                    "title": f"Pregunta {i+1}",
                    "description": q[:72]
                }
                for i, q in enumerate(questions)
            ]
            rows.append({
                "id": "menu_back",
                "title": "⬅ Volver",
                "description": "Regresar al menú principal"
            })
            send_list(
                from_number,
                "📋 Selecciona una pregunta sugerida o escribe la tuya:",
                "Ver preguntas",
                [{"title": "Consultas sugeridas", "rows": rows}]
            )

        elif reply["type"] == "answer":
            raw_text = reply["text"]
            category_key = get_state(from_number) or "desconocido"

            # Extraer la pregunta del texto (está en la primera línea tras el emoji 📌)
            lines = raw_text.split("\n")
            question_line = lines[0].replace("📌", "").replace("*", "").strip()

            # Aplicar filtro de contenido sensible
            filtered_text, was_blocked = apply_filter(raw_text)

            # Registrar interacción
            logger.log_interaction(
                user=from_number,
                category=category_key,
                question=question_line,
                was_blocked=was_blocked,
            )

            # Agregar disclaimer si la respuesta no fue bloqueada
            final_text = (
                filtered_text
                if was_blocked
                else filtered_text + DISCLAIMER
            )

            send_text(from_number, final_text)
            send_buttons(
                from_number,
                "¿Deseas hacer otra consulta?",
                [
                    {"type": "reply", "reply": {"id": "new_question", "title": "Nueva consulta"}},
                    {"type": "reply", "reply": {"id": "menu_back",    "title": "Volver al menú"}},
                    {"type": "reply", "reply": {"id": "goodbye",      "title": "Finalizar"}},
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


# ── Admin: resumen de indicadores ──────────────────────────────────────────────

@app.get("/admin/stats")
async def admin_stats(x_admin_token: str = Header(default="")):
    _check_admin_token(x_admin_token)
    return logger.get_summary()


# ── Admin: exportar logs en CSV ────────────────────────────────────────────────

@app.get("/admin/export")
async def admin_export(x_admin_token: str = Header(default="")):
    _check_admin_token(x_admin_token)
    csv_content = logger.export_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=asistente_agro_logs.csv"}
    )


# ── Helper ─────────────────────────────────────────────────────────────────────

def _check_admin_token(token: str):
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Token de administrador inválido.")