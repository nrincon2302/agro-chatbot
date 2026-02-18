from .llm import generate_agro_response
from .data import CATEGORIES
from .state import get_state, set_state
import re

def build_main_menu():
    text = "🌱 *Asistente Agro*\n\nSelecciona una categoría:\n\n"
    for i, key in enumerate(CATEGORIES.keys(), start=1):
        cat = CATEGORIES[key]
        text += f"{i}️⃣ {cat['emoji']} {cat['title']}\n"
    text += "\nResponde con el número."
    return text


def build_questions_menu(category_key):
    cat = CATEGORIES[category_key]
    text = f"{cat['emoji']} *{cat['title']}*\n\nSelecciona una pregunta:\n\n"
    
    for i, q in enumerate(cat["questions"], start=1):
        text += f"{i}. {q}\n"
    
    text += "\nEscribe el número o escribe 'menu' para volver."
    return text


def handle_message(user, incoming):

    state = get_state(user)
    text = incoming.strip().lower()

    match = re.search(r"\d+", text)
    if match:
        text = match.group()

    # VOLVER AL MENÚ
    if text == "menu":
        set_state(user, {"level": "menu"})
        return build_main_menu()

    # MENÚ PRINCIPAL
    if state["level"] == "menu":
        try:
            index = int(text) - 1
            category_key = list(CATEGORIES.keys())[index]
            set_state(user, {"level": "category", "category": category_key})
            return build_questions_menu(category_key)
        except:
            return build_main_menu()

    # DENTRO DE CATEGORÍA
    if state["level"] == "category":
        category_key = state["category"]
        category_title = CATEGORIES[category_key]["title"]
        questions = CATEGORIES[category_key]["questions"]

        try:
            index = int(text) - 1
            question = questions[index]

            answer = generate_agro_response(category_title, question)

            return (
                f"📌 *{question}*\n\n"
                f"{answer}\n\n"
                f"Escribe 'menu' para volver."
            )
        except:
            return build_questions_menu(category_key)

    return build_main_menu()
