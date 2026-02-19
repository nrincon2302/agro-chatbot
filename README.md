# 🌱 Asistente Agro – WhatsApp Chatbot para Productores

Asistente Agro es un chatbot técnico orientado a productores agropecuarios latinoamericanos.
Permite resolver dudas técnicas, sugerir consultas frecuentes y generar respuestas especializadas usando modelos LLM.

Está construido con:

* **FastAPI**
* **WhatsApp Cloud API (Meta)**
* **Google Gemini (por defecto)**
* Soporte preparado para **OpenAI**
* Servicio alternativo preparado para **Twilio**

Actualmente está desplegado para pruebas en:

👉 [https://agro-chatbot-zkci.onrender.com](https://agro-chatbot-zkci.onrender.com)



# 🚀 ¿Qué hace el sistema?

El flujo general es:

1. El productor escribe al número de WhatsApp.
2. El webhook recibe el mensaje en FastAPI.
3. Se procesa el estado de conversación.
4. Se envía:

   * Menú interactivo de categorías
   * Lista de preguntas sugeridas
   * Respuesta técnica generada por LLM
   * Botones para continuar o finalizar

El asistente responde como ingeniero agrónomo, en lenguaje práctico y con pasos accionables.



# 📁 Estructura del Proyecto

```
app/
│
├── main.py
│
├── chatbot/
│   ├── flow.py
│   ├── state.py
│   ├── data.py
│   └── llm.py
│
├── services/
│   ├── twilio_service.py
│   └── whatsapp_service.py
│
├── requirements.txt
└── .env
```



## 🔹 `main.py`

* Punto de entrada FastAPI.
* Define:

  * Health check (`/`)
  * Verificación del webhook (`GET /webhook`)
  * Recepción de mensajes (`POST /webhook`)
* Renderiza:

  * Menús interactivos
  * Listas
  * Botones
  * Mensajes de despedida



## 🔹 `flow.py`

Contiene la lógica de conversación.

* Decide qué tipo de respuesta enviar:

  * `menu`
  * `questions`
  * `answer`
  * `goodbye`
* Interpreta los IDs de botones y listas.
* Controla el flujo conversacional.



## 🔹 `state.py`

Gestión simple de estado en memoria:

```python
user_states = {}
```

Permite:

* Guardar categoría seleccionada
* Consultar estado
* Limpiar sesión



## 🔹 `llm.py`

Módulo encargado de generar respuestas técnicas.

Por defecto usa **Google Gemini**:

```python
model = "models/gemini-2.0-flash"
```

Incluye:

* Prompt de sistema especializado en producción rural.
* Control de temperatura.
* Límite de tokens.
* Manejo de errores.

También incluye código comentado para usar **OpenAI (GPT)** en lugar de Gemini si se desea cambiar el proveedor.

Solo habría que:

* Activar el bloque de OpenAI
* Configurar `OPENAI_API_KEY`
* Ajustar el modelo deseado



## 🔹 `whatsapp_service.py`

Encapsula las llamadas a la **WhatsApp Cloud API (Meta)**.

Funciones principales:

* `send_text()`
* `send_buttons()`
* `send_list()`

Aquí se construyen los payloads interactivos:

* Menús tipo lista
* Botones rápidos
* Texto plano



# 🔄 Servicio preparado para Twilio

El proyecto incluye estructura preparada para integrar **Twilio** como proveedor alternativo.

⚠️ Importante:

Si se usa Twilio:

* No están disponibles los menús interactivos tipo lista
* No están disponibles selectores avanzados nativos de Meta
* Solo se podrían usar botones simples o texto plano

La integración está pensada para adaptarse si se requiere cambiar proveedor, pero la experiencia interactiva completa está optimizada para WhatsApp Cloud API oficial.



# ⚙️ Variables de Entorno

Ejemplo de `.env`:

```
ACCESS_TOKEN=...
PHONE_NUMBER_ID=...
VERIFY_TOKEN=...
VERSION=v22.0

GEMINI_API_KEY=...
OPENAI_API_KEY=...   # opcional
```



# 🖥️ Ejecutar en Local

### 1️⃣ Crear entorno

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 2️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3️⃣ Ejecutar servidor

```bash
uvicorn app.main:app --reload --port 8000
```

Servidor disponible en:

```
http://localhost:8000
```



# 🌍 Despliegue

Actualmente desplegado en **Render**:

[https://agro-chatbot-zkci.onrender.com](https://agro-chatbot-zkci.onrender.com)

El despliegue funciona mediante:

* Conexión automática al repositorio
* Variables de entorno configuradas en Render
* Webhook apuntando al dominio público



# 📌 Limitaciones actuales

* Estado en memoria (se reinicia al reiniciar servidor)
* No hay base de datos persistente
* No hay autenticación de usuarios
* Solo testers autorizados pueden escribir al número si está en modo sandbox



# 🧠 Posibles mejoras futuras

* Persistencia con Redis
* Registro de consultas en base de datos
* Panel web administrativo
* Métricas de uso
* Multi-tenant para diferentes asociaciones de productores
* Versionado de prompts



# 🧪 Estado actual

✔ Funciona en local
✔ Funciona desplegado en Render
✔ Integra LLM (Gemini)
✔ Permite migrar a OpenAI
✔ Preparado para Twilio (con limitaciones)
