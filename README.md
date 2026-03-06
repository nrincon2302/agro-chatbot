# 🌱 Asistente Agro — Chatbot WhatsApp para Productores Agropecuarios

> **Estado actual: MVP funcional (prototipo en fase piloto)**
>
> Este sistema es un prototipo operativo construido para validar el concepto en un entorno de pruebas controlado (sandbox de Meta). Está desplegado y funciona de extremo a extremo, pero varias funcionalidades avanzadas descritas en la propuesta técnica del proyecto están identificadas como trabajo futuro. Ver sección [Alcance del MVP y trabajo futuro](#-alcance-del-mvp-y-trabajo-futuro).

---

## ¿Qué hace el sistema?

Asistente Agro es un chatbot técnico para productores agropecuarios latinoamericanos que opera a través de WhatsApp. Permite al productor seleccionar su línea productiva, explorar preguntas sugeridas o escribir las propias, y recibir orientación técnica generada por un modelo de lenguaje de última generación.

El flujo completo es:

1. El productor escribe al número de WhatsApp configurado.
2. El webhook recibe el mensaje en el servidor FastAPI.
3. El sistema determina el estado de la conversación y la acción correspondiente.
4. Si corresponde una consulta técnica, el módulo LLM genera una respuesta.
5. Antes de enviar la respuesta, un filtro automático evalúa si contiene contenido sensible.
6. Se envía la respuesta al usuario junto con el disclaimer obligatorio.
7. La interacción queda registrada en el log en memoria.

---

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Backend / Webhook | FastAPI + Uvicorn |
| Mensajería | WhatsApp Cloud API (Meta) |
| Modelo de lenguaje | Google Gemini 2.0 Flash |
| Filtro de contenido | Google Gemini 2.0 Flash (segundo llamado) |
| Contenerización | Docker |
| Despliegue | Render (plan gratuito) |
| Soporte alternativo (preparado) | OpenAI GPT, Twilio |

---

## Líneas productivas implementadas

El sistema cubre las siguientes cinco categorías, cada una con preguntas sugeridas:

| Categoría | Emoji | Preguntas sugeridas |
|---|---|---|
| Ganadería | 🐄 | Ordeño, mastitis, costos por litro, registros productivos |
| Avicultura | 🐔 | Bioseguridad, vacunas, mortalidad, costo por huevo |
| Cunicultura | 🐰 | Reproducción, alimentación, mixomatosis, mortalidad |
| Hortalizas | 🥬 | pH del suelo, rotación de cultivos, Fusarium, reducción de costos |
| Transformación y Postcosecha | 🧺 | BPM lácteos, acondicionamiento de papa, inocuidad, almacenamiento |

---

## Funcionalidades implementadas en este MVP

### ✅ Flujo conversacional interactivo

Menús tipo lista, botones de respuesta rápida y manejo de estado por usuario, todo mediante la WhatsApp Cloud API oficial de Meta. Incluye navegación entre categorías, nueva consulta en la misma categoría y cierre de sesión.

### ✅ Generación de respuestas con LLM (Gemini)

Cada consulta técnica es procesada por Google Gemini 2.0 Flash con un prompt especializado en producción rural latinoamericana. Las respuestas están limitadas a 8 líneas, en lenguaje práctico y con pasos accionables. La temperatura está configurada en 0.4 para balancear precisión y naturalidad.

### ✅ Filtro automático de contenido sensible

Implementado en `app/chatbot/filter.py`. Antes de enviar cada respuesta técnica al usuario, el sistema realiza un segundo llamado a Gemini que evalúa si la respuesta contiene:

- Dosificaciones específicas de agroquímicos o pesticidas
- Prescripciones veterinarias o medicamentos con dosis concretas
- Diagnósticos clínicos de enfermedades animales o vegetales
- Recomendaciones con potencial de causar daño sanitario, ambiental o económico

Si el filtro detecta contenido sensible, **bloquea la respuesta** y la reemplaza por un mensaje estándar que redirige al productor hacia asistencia técnica profesional en campo. Si el filtro falla por cualquier razón técnica (error de red, cuota de API), la respuesta pasa de todas formas para no interrumpir el servicio.

El porcentaje de bloqueos queda registrado en el log de indicadores.

### ✅ Disclaimer obligatorio en cada respuesta

Todas las respuestas técnicas incluyen al final el siguiente texto, tal como lo requiere el documento de propuesta:

> *"La información suministrada es orientativa y no reemplaza la asistencia técnica profesional en campo."*

Este disclaimer no aparece en mensajes de navegación (menús, botones), solo en las respuestas generadas por el LLM.

### ✅ Log de interacciones en memoria

Implementado en `app/chatbot/logger.py`. Cada consulta técnica queda registrada con los siguientes campos:

| Campo | Descripción |
|---|---|
| `timestamp` | Fecha y hora UTC de la interacción |
| `user_id` | Número de teléfono anonimizado (solo últimos 4 dígitos) |
| `category` | Línea productiva seleccionada |
| `question` | Texto de la consulta (máximo 300 caracteres) |
| `blocked` | `Sí` o `No` — indica si el filtro bloqueó la respuesta |

> ⚠️ **Limitación actual:** los logs se almacenan en memoria del proceso. Se pierden cuando el servidor se reinicia. En el plan gratuito de Render, el servidor se reinicia por inactividad (~15 minutos sin solicitudes). Ver [Trabajo futuro](#-alcance-del-mvp-y-trabajo-futuro) para la migración a base de datos.

### ✅ Endpoints de administración

El sistema expone dos endpoints protegidos por token para consulta y exportación de datos. Para usarlos se requiere el header `x-admin-token` con el valor configurado en la variable de entorno `ADMIN_TOKEN`.

**`GET /admin/stats`** — Resumen de indicadores en JSON:

```json
{
  "total": 42,
  "blocked": 3,
  "by_category": {
    "ganaderia": 18,
    "hortalizas": 12,
    "avicultura": 8,
    "transformacion": 4
  }
}
```

**`GET /admin/export`** — Descarga el log completo en formato CSV:

```bash
curl https://TU-DOMINIO.onrender.com/admin/export \
  -H "x-admin-token: TU_TOKEN" \
  -o log_asistente_agro.csv
```

---

## Estructura del proyecto

```
app/
├── main.py                    # Punto de entrada FastAPI, webhook, endpoints admin
│
├── chatbot/
│   ├── flow.py                # Lógica del flujo conversacional
│   ├── state.py               # Estado en memoria por usuario
│   ├── data.py                # Categorías y preguntas sugeridas (5 líneas)
│   ├── llm.py                 # Integración con Gemini (y código preparado para OpenAI)
│   ├── filter.py              # Filtro automático de contenido sensible ← NUEVO
│   └── logger.py              # Log de interacciones + exportación CSV ← NUEVO
│
└── services/
    ├── whatsapp_service.py    # Llamadas a WhatsApp Cloud API (Meta)
    └── twilio_service.py      # Servicio alternativo Twilio (preparado, no activo)
```

---

## Variables de entorno

Copie `.env.example` a `.env` y complete cada valor:

```bash
cp .env.example .env
```

| Variable | Descripción | Dónde obtenerla |
|---|---|---|
| `ACCESS_TOKEN` | Token de acceso a WhatsApp Cloud API | Meta for Developers → API Setup |
| `PHONE_NUMBER_ID` | ID del número de teléfono de WhatsApp | Meta for Developers → API Setup |
| `VERIFY_TOKEN` | Token para verificación del webhook (lo define usted) | Cualquier cadena sin espacios |
| `VERSION` | Versión de la API de Meta | `v22.0` (ajustar según consola) |
| `APP_ID` | ID de la aplicación en Meta | Meta for Developers → Configuración → Básica |
| `APP_SECRET` | Clave secreta de la app en Meta | Meta for Developers → Configuración → Básica |
| `GEMINI_API_KEY` | API Key de Google Gemini | aistudio.google.com |
| `ADMIN_TOKEN` | Token para proteger los endpoints `/admin/*` | Generar con el comando de abajo |
| `OPENAI_API_KEY` | API Key de OpenAI (opcional) | platform.openai.com |

Para generar el `ADMIN_TOKEN`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Ejecución local

### Con Docker

```bash
# Construir la imagen
docker build -t asistente-agro .

# Ejecutar el contenedor
docker run --env-file .env -p 8000:8000 asistente-agro
```

### Con Python directo

```bash
python -m venv venv
source venv/bin/activate       # Linux / Mac
venv\Scripts\activate          # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verificar que responde:

```bash
curl http://localhost:8000
# → {"status": "running"}
```

### Pruebas locales con ngrok

Para recibir mensajes reales de WhatsApp en local, se necesita exponer el puerto 8000 públicamente con ngrok:

```bash
ngrok http 8000
```

Copie la URL `https://xxxx.ngrok-free.app` y actualícela en el webhook de Meta (WhatsApp → Configuración → Webhooks). Recuerde que esta URL cambia cada vez que reinicia ngrok.

---

## Despliegue en Render

El proyecto incluye un `Dockerfile` listo para despliegue. En Render:

1. Crear un nuevo **Web Service** conectado al repositorio.
2. Seleccionar **Runtime: Docker**.
3. Agregar las variables de entorno en la sección Environment.
4. El despliegue es automático con cada `git push` a la rama principal.

URL de prueba actual: [https://agro-chatbot-zkci.onrender.com](https://agro-chatbot-zkci.onrender.com)

> ⚠️ En el plan gratuito, el servidor se suspende tras 15 minutos de inactividad. El primer mensaje después de una pausa puede tardar hasta 60 segundos.

---

## 🗺 Alcance del MVP y trabajo futuro

Esta tabla distingue claramente lo que está implementado en el MVP actual de lo que está especificado en la propuesta técnica del proyecto pero pendiente de desarrollo:

| Funcionalidad | Estado en este MVP |
|---|---|
| Flujo conversacional interactivo (menús, listas, botones) | ✅ Implementado |
| Generación de respuestas con Gemini | ✅ Implementado |
| Filtro automático de contenido sensible | ✅ Implementado |
| Disclaimer obligatorio en cada respuesta | ✅ Implementado |
| Log de interacciones con exportación CSV | ✅ Implementado |
| Indicadores básicos por categoría | ✅ Implementado |
| 5 líneas productivas (incluye Transformación/Postcosecha) | ✅ Implementado |
| Soporte para OpenAI como proveedor alternativo de LLM | ✅ Preparado (código comentado en `llm.py`) |
| Soporte para Twilio como canal alternativo | ✅ Preparado (con limitaciones de interactividad) |
| **Persistencia de estado y logs en base de datos** | ⏳ Trabajo futuro |
| **RAG con corpus técnico validado** | ⏳ Trabajo futuro |
| **Historial de conversaciones por productor** | ⏳ Trabajo futuro |
| **Panel administrativo web** | ⏳ Trabajo futuro |
| **Reportes automáticos mensuales/trimestrales** | ⏳ Trabajo futuro |
| **Entrenamiento o ajuste fino del modelo con datos propios** | ⏳ Trabajo futuro |
| **Multi-tenant para múltiples organizaciones** | ⏳ Trabajo futuro |
| **Acceso de producción (cualquier usuario puede escribir)** | ⏳ Requiere aprobación de Meta |

### Sobre el RAG (Generación Asistida por Recuperación)

La propuesta técnica especifica que el sistema debe operar bajo un esquema RAG, consultando un repositorio de documentos técnicos validados antes de generar cada respuesta. **Esta funcionalidad no está implementada en el MVP.** El LLM responde desde su conocimiento de entrenamiento general con el prompt especializado.

La implementación de RAG requiere: definir y recopilar el corpus documental, procesarlo en fragmentos, generar embeddings, almacenarlos en una base de datos vectorial (como pgvector en Supabase) y modificar el módulo `llm.py` para recuperar contexto relevante antes de cada generación. Esto representa la evolución más estructural del sistema y la de mayor impacto en la calidad de las respuestas.

---

## Limitaciones conocidas del MVP

- **Estado en memoria:** el estado de conversación de cada usuario se pierde si el servidor se reinicia.
- **Logs en memoria:** el historial de consultas se pierde con cada reinicio del servidor.
- **Sin autenticación de usuarios:** cualquier número autorizado como tester puede usar el sistema.
- **Modo sandbox de Meta:** en el estado actual, solo números registrados manualmente en el panel de Meta pueden enviar mensajes al chatbot. Pasar a producción requiere solicitar y recibir aprobación de Meta para el permiso `whatsapp_business_messaging`.
- **Sin validación del corpus:** las respuestas se generan con el conocimiento general de Gemini, sin consultar fuentes técnicas validadas institucionalmente.