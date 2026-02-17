from rapidfuzz import fuzz
from app.base import knowledge_base

def find_best_match(user_message: str):

    best_score = 0
    best_answer = "No encontré una respuesta exacta. ¿Puedes reformular la pregunta?"

    for category in knowledge_base.values():
        for question, answer in category.items():
            score = fuzz.ratio(user_message.lower(), question.lower())
            if score > best_score and score > 60:
                best_score = score
                best_answer = answer

    return best_answer
