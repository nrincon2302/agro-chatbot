import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SENSITIVE_TOPICS = [
    "dosificaciones específicas de agroquímicos o pesticidas",
    "prescripciones veterinarias o medicamentos con dosis",
    "diagnósticos clínicos de enfermedades animales o vegetales",
    "indicaciones que puedan causar daño sanitario, ambiental o económico",
]

FILTER_PROMPT = """
Eres un evaluador de contenido técnico agropecuario.

Analiza el siguiente texto y determina si contiene alguno de estos elementos sensibles:
- Dosificaciones específicas de agroquímicos o pesticidas
- Prescripciones veterinarias o medicamentos con dosis concretas
- Diagnósticos clínicos de enfermedades animales o vegetales
- Recomendaciones que puedan causar daño sanitario, ambiental o económico directo

Responde ÚNICAMENTE con una de estas dos palabras:
SEGURO
SENSIBLE
"""

REDIRECT_MESSAGE = (
    "⚠️ Esta consulta requiere atención de un profesional técnico en campo.\n\n"
    "El asistente no puede brindar dosificaciones, prescripciones veterinarias "
    "ni diagnósticos clínicos específicos.\n\n"
    "Te recomendamos contactar directamente a tu asistente técnico o a las "
    "entidades de apoyo del sector agropecuario en tu territorio."
)


def is_safe_response(response_text: str) -> bool:
    """
    Returns True if the response is safe to send, False if it should be blocked.
    """
    try:
        result = client.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=f"{FILTER_PROMPT}\n\nTexto a evaluar:\n{response_text}",
            config={
                "temperature": 0.0,
                "max_output_tokens": 10,
            }
        )
        verdict = result.text.strip().upper()
        return verdict == "SEGURO"

    except Exception as e:
        print(f"FILTER ERROR: {e}")
        # Si el filtro falla, dejamos pasar para no romper el flujo
        return True


def apply_filter(response_text: str) -> tuple[str, bool]:
    """
    Returns (final_text, was_blocked).
    """
    if is_safe_response(response_text):
        return response_text, False
    else:
        return REDIRECT_MESSAGE, True