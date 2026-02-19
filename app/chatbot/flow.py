from .data import CATEGORIES
from .state import get_state, set_state, clear_state
from .llm import generate_agro_response


def handle_message(user, text):

    text = text.strip().lower()

    # 🔥 Volver manual al menú principal
    if text == "menu_back":
        clear_state(user)
        return {"type": "menu"}

    # 🔥 Nueva consulta en misma categoría
    if text == "new_question":
        category_key = get_state(user)

        if category_key:
            return {
                "type": "questions",
                "category": category_key
            }
        else:
            return {"type": "menu"}
        
    # 🔥 Despedida
    if text == "goodbye":
        clear_state(user)
        return {"type": "goodbye"}

    # 🔥 Cambio de categoría
    if text.startswith("cat_"):
        category_key = text.replace("cat_", "")

        if category_key in CATEGORIES:
            set_state(user, category_key)
            return {
                "type": "questions",
                "category": category_key
            }

    # 🔥 Si ya hay categoría activa
    category_key = get_state(user)

    if category_key:
        # Pregunta sugerida
        if text.startswith("q_"):
            try:
                _, category_key, index = text.split("_")
                index = int(index)
                question = CATEGORIES[category_key]["questions"][index]
            except:
                question = text
        else:
            question = text

        answer = generate_agro_response(
            CATEGORIES[category_key]["title"],
            question
        )

        return {
            "type": "answer",
            "text": f"📌 *{question}*\n\n{answer}"
        }

    # 🔥 Sin categoría → mostrar menú
    return {"type": "menu"}
