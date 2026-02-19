from .data import CATEGORIES
from .state import get_state, set_state
from .llm import generate_agro_response


def handle_message(user, text):

    text = text.strip().lower()
    state = get_state(user)

    # --- Selección categoría ---
    if text.startswith("cat_"):
        category_key = text.replace("cat_", "")

        if category_key not in CATEGORIES:
            return {"type": "menu"}

        set_state(user, {"level": "category", "category": category_key})

        return {"type": "questions", "category": category_key}

    # --- Selección pregunta ---
    if text.startswith("q_"):
        parts = text.split("_")

        if len(parts) != 3:
            return {"type": "menu"}

        _, category_key, index = parts

        if category_key not in CATEGORIES:
            return {"type": "menu"}

        try:
            index = int(index)
        except:
            return {"type": "menu"}

        questions = CATEGORIES[category_key]["questions"]

        if index >= len(questions):
            return {"type": "menu"}

        question = questions[index]

        answer = generate_agro_response(
            CATEGORIES[category_key]["title"],
            question
        )

        return {
            "type": "answer",
            "text": f"📌 *{question}*\n\n{answer}"
        }

    # --- Volver ---
    if text == "menu_back":
        set_state(user, {"level": "menu"})
        return {"type": "menu"}

    # --- Texto libre dentro de categoría ---
    if state["level"] == "category":
        category_key = state["category"]

        answer = generate_agro_response(
            CATEGORIES[category_key]["title"],
            text
        )

        return {
            "type": "answer",
            "text": f"🧠 Respuesta técnica:\n\n{answer}"
        }

    # --- Inicio ---
    return {"type": "menu"}
