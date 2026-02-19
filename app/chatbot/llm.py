import os
from openai import OpenAI
from google import genai

# Configuración
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

model = "models/gemini-2.0-flash"

SYSTEM_PROMPT = """
Eres un ingeniero agrónomo especializado en producción rural latinoamericana.

Responde:
- Máximo 8 líneas
- En lenguaje claro y práctico
- Incluye pasos accionables
- No uses lenguaje académico complejo
- No menciones que eres IA
"""

def generate_agro_response(category, question):
    try:
        print("LLAMANDO A GEMINI...")

        prompt = f"""
{SYSTEM_PROMPT}

Categoría productiva: {category}

Pregunta del productor:
{question}
"""

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0.4,
                "max_output_tokens": 250
            }
        )

        print("RESPUESTA RECIBIDA")

        return response.text.strip()

    except Exception as e:
        return "⚠️ El asistente técnico está temporalmente no disponible."


# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def generate_agro_response(category, question):
#     try:
#         print("LLAMANDO A OPENAI...")

#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "Responde como ingeniero agrónomo en máximo 6 líneas."
#                 },
#                 {
#                     "role": "user",
#                     "content": f"Categoría: {category}\nPregunta: {question}"
#                 }
#             ],
#             temperature=0.4
#         )

#         print("RESPUESTA RECIBIDA")

#         return response.choices[0].message.content

#     except Exception as e:
#         return "Error generando respuesta técnica."
