# climAI 🌤  Predicción Meteorológica Inteligente

**climAI** es una aplicación web de meteorología avanzada que combina datos en tiempo real de la API de **AEMET** con modelos de **Machine Learning** para ofrecer predicciones climáticas personalizadas y un sistema de alertas asíncronas vía Telegram.

---

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

---

# 🚀 Características principales

## 🌍 Dashboard Meteorológico
Detección automática de la ubicación del usuario mediante Nominatim, mostrando temperatura, humedad, viento, precipitación y el histórico de las últimas 24h de la estación AEMET más cercana.

## 🧠 Predicción IA
Modelo de Regresión Lineal Multivariable (scikit-learn) que ajusta la temperatura actual, detecta tendencias térmicas (📈 Ascenso, ➖ Estable, 📉 Descenso) y mejora progresivamente con el reentrenamiento automático.

## 📅 Pronóstico inteligente de 5 días
Consumo del endpoint municipal de AEMET con correcciones predictivas aplicadas por nuestro motor de IA.

## 🚨 Sistema de Alertas Climáticas
Centro de alertas en tiempo real con tres niveles de severidad:

| Nivel | Color | Condiciones |
|---|---|---|
| Alerta Roja | 🔴 | Temp ≥ 40°C, temp ≤ -5°C, viento > 70 km/h, lluvia > 30 mm |
| Alerta Naranja | 🟠 | Temp ≥ 35°C, temp ≤ 0°C, viento > 40 km/h, lluvia > 10 mm |
| Sin alerta | 🟢 | Condiciones dentro de parámetros normales |

La interfaz se actualiza automáticamente cada 60 segundos y permite filtrar por nivel y tipo de fenómeno.

## ✈️ Notificaciones Telegram
Recibe alertas climáticas directamente en Telegram sin configuración adicional:

1. Abre Telegram y escríbele a **@userinfobot**
2. Copia el número de tu `Id`
3. Ve a ClimAI → Vincular Telegram → pega el ID y pulsa **Vincular**
4. Recibirás un mensaje de confirmación al instante

> No requiere ngrok ni instalaciones externas.

## 📊 Estadísticas avanzadas
Visualización interactiva con Chart.js de temperatura media por provincias, ranking climático nacional, correlación humedad ↔ temperatura y tendencias comparativas.

## ⚙️ Arquitectura asíncrona
Integración de Celery y Redis para el procesamiento en segundo plano sin bloquear el servidor web:
- Reentrenamiento automático del modelo IA
- Evaluación periódica de alertas
- Envío de notificaciones Telegram
- Procesamiento desacoplado de tareas pesadas

## 🔍 Búsqueda por provincia
Permite consultar el tiempo de cualquier provincia española sin necesidad de geolocalización.

---

## 🧩 Stack Tecnológico

| Capa | Tecnologías |
| :--- | :--- |
| **Backend & API** | FastAPI, Uvicorn, SQLAlchemy Async, Alembic, Python-dotenv |
| **Data & IA** | PostgreSQL, scikit-learn, Pandas, NumPy, Joblib |
| **Tareas Async** | Celery, Redis |
| **Integraciones** | AEMET OpenData API, Telegram Bot API, OpenStreetMap (Nominatim) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Jinja2, Chart.js |
| **Infraestructura** | Docker, Docker Compose |

---

# 🏗️ Arquitectura del Sistema

## Flujo de Datos

```text
Frontend (HTML/CSS/JS)
        │
        ▼
FastAPI (API REST + Views)
        │
 ┌──────┴──────┐
 ▼             ▼
AEMET API   PostgreSQL
 │             │
 ▼             ▼
Weather Service ──► ML Engine
                     │
                     ▼
              modelo_clima.pkl
                     │
                     ▼
             Predicción IA
```

---

# 🔌 APIs Externas y Servicios Integrados

## 🌦️ AEMET OpenData API

Principal fuente de datos meteorológicos. La integración funciona en dos pasos:

1. Solicitud de una URL temporal autenticada
2. Descarga y procesamiento del JSON meteorológico

### Datos consumidos
- Temperatura, humedad relativa, velocidad del viento, precipitación
- Observaciones por estación
- Pronóstico municipal de 5 días

El sistema selecciona automáticamente la estación meteorológica más cercana usando coordenadas geográficas y cálculo Haversine.

---

## 🗺️ Nominatim + OpenStreetMap

Transforma coordenadas en provincia/municipio para filtrar estaciones y mejorar la experiencia del usuario.

---

## ⚡ Backend y Servidor

### 🚀 FastAPI
Núcleo del backend. Alto rendimiento, soporte nativo async/await, documentación automática OpenAPI y excelente integración con Pydantic.

### 🌐 Uvicorn
Servidor ASGI que ejecuta FastAPI con alto rendimiento y soporte WebSockets.

### 🎨 Jinja2
Renderiza HTML dinámico para el dashboard, estadísticas, login y vistas de alertas.

---

## 🗄️ Base de Datos y Persistencia

### 🐘 PostgreSQL
Almacena usuarios, alertas, históricos meteorológicos, logs, predicciones y configuración.

### 🧩 SQLAlchemy Async
ORM robusto con consultas async y soporte para relaciones complejas.

### 🔄 Alembic
Gestiona el versionado y las migraciones de la base de datos.

---

## 🧠 Inteligencia Artificial

### 🤖 scikit-learn
Regresión Lineal Multivariable para predecir temperatura corregida y tendencia térmica.

### 📊 Pandas y NumPy
Limpieza, transformación y normalización de datos meteorológicos.

### 💾 Joblib
Serializa el modelo entrenado en `.pkl` para inferencia en tiempo real.

---

## 🧱 Arquitectura Técnica

| Capa | Tecnología |
|---|---|
| Backend | FastAPI + SQLAlchemy Async |
| Base de Datos | PostgreSQL + Alembic |
| Machine Learning | scikit-learn + joblib |
| Tareas Async | Celery + Redis |
| Datos meteorológicos | API AEMET OpenData |
| Geocodificación | Nominatim (OpenStreetMap) |
| Frontend | Jinja2 + HTML/CSS/JS Vanilla |
| Gráficas | Chart.js |
| Autenticación | Cookies de sesión + JWT |
| Notificaciones | Telegram Bot API |
| Contenedores | Docker + Docker Compose |

---

## 🧠 Pipeline ML

```text
Datos AEMET
    │
    ▼
PostgreSQL
    │
    ▼
Normalización (StandardScaler)
    │
    ▼
LinearRegression
    │
    ▼
modelo_clima.pkl
    │
    ▼
Predicción IA
```

---

## 📁 Estructura del Proyecto

```text
│climAI
│ logs                  
│   main.py                                                                   
│   __init__.py
│                                                                                           
├───api                                                  
│   │   __init__.py
│   │   
│   ├───v1
│   │   │   api_router.py
│   │   │   __init__.py
│   │   │   
│   │   ├───endpoints
│   │   │   │   auth_jwt.py
│   │   │   │   climas.py
│   │   │   │   predict.py
│   │   │   │   stats.py
│   │   │   │   
│   │   │   └───__pycache__
│   │   │           auth_jwt.cpython-313.pyc
│   │   │           auth_jwt.cpython-314.pyc
│   │   │           predict.cpython-313.pyc
│   │   │           predict.cpython-314.pyc
│   │   │           
│   │   └───__pycache__
│   │           __init__.cpython-313.pyc
│   │           __init__.cpython-314.pyc
│   │           
│   └───__pycache__
│           __init__.cpython-313.pyc
│           __init__.cpython-314.pyc
│           
├───core
│   │   celery_app.py
│   │   config.py
│   │   security.py
│   │   __init__.py
│   │   
│   ├───resources
│   │       estaciones_madrid.json
│   │       municipios.json
│   │       
│   └───__pycache__
│           config.cpython-313.pyc
│           config.cpython-314.pyc
│           security.cpython-313.pyc
│           security.cpython-314.pyc
│           __init__.cpython-313.pyc
│           __init__.cpython-314.pyc
│           
├───db
│   │   base.py
│   │   base_class.py
│   │   session.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           base_class.cpython-313.pyc
│           base_class.cpython-314.pyc
│           session.cpython-313.pyc
│           session.cpython-314.pyc
│           __init__.cpython-313.pyc
│           __init__.cpython-314.pyc
│           
├───models
│   │   database.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           database.cpython-313.pyc
│           database.cpython-314.pyc
│           __init__.cpython-313.pyc
│           __init__.cpython-314.pyc
│           
├───routers
│   │   alertas.py
│   │   auth.py
│   │   provincias.py
│   │   telegram_bot.py
│   │   views.py
│   │   
│   └───__pycache__
│           alertas.cpython-314.pyc
│           auth.cpython-313.pyc
│           auth.cpython-314.pyc
│           provincias.cpython-313.pyc
│           provincias.cpython-314.pyc
│           telegram_bot.cpython-314.pyc
│           views.cpython-313.pyc
│           views.cpython-314.pyc
│           
├───schemas
│   │   registro.py
│   │   stats.py
│   │   token.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           registro.cpython-313.pyc
│           registro.cpython-314.pyc
│           token.cpython-313.pyc
│           token.cpython-314.pyc
│           __init__.cpython-313.pyc
│           __init__.cpython-314.pyc
│           
├───scripts
│   │   retrain_model.py
│   │   
│   └───__pycache__
│           retrain_model.cpython-313.pyc
│           
├───services
│   │   aemet_client.py
│   │   alert_service.py
│   │   geo_utils.py
│   │   logging_service.py
│   │   ml_engine.py
│   │   normalizer_service.py
│   │   notifier_service.py
│   │   stats_service.py
│   │   weather_ai_service.py
│   │   weather_service.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           aemet_client.cpython-313.pyc
│           aemet_client.cpython-314.pyc
│           alert_service.cpython-313.pyc
│           alert_service.cpython-314.pyc
│           geo_utils.cpython-313.pyc
│           geo_utils.cpython-314.pyc
│           logging_service.cpython-313.pyc
│           logging_service.cpython-314.pyc
│           notifier_service.cpython-313.pyc
│           notifier_service.cpython-314.pyc
│           stats_service.cpython-313.pyc
│           stats_service.cpython-314.pyc
│           weather_ai_service.cpython-313.pyc
│           weather_ai_service.cpython-314.pyc
│           weather_service.cpython-313.pyc
│           weather_service.cpython-314.pyc
│           __init__.cpython-313.pyc
│           __init__.cpython-314.pyc
│           
├───static
│   ├───css
│   │       alertas.css
│   │       auth.css
│   │       base.css
│   │       index.css
│   │       prediccion.css
│   │       stats.css
│   │       vincular_telegram.css
│   │       
│   └───js
│           alertas.js
│           auth.js
│           base.js
│           index.js
│           prediccion.js
│           stats.js
│           vincular_telegram.js
│           weather_province.js
│           
├───templates
│       alertas.html
│       base.html
│       index.html
│       login.html
│       prediccion_ia.html
│       registro_usuario.html
│       stats.html
│       vincular_telegram.html
│       weather_province.html
│       
└───__pycache__
        main.cpython-313.pyc
        main.cpython-314.pyc
        __init__.cpython-313.pyc
        __init__.cpython-314.pyc
```

---

## 🏛️ Decisiones de Arquitectura

### 📌 Separación de responsabilidades

| Carpeta | Responsabilidad |
|---|---|
| `routers/` | Endpoints y vistas |
| `services/` | Lógica de negocio |
| `db/` | Persistencia |
| `schemas/` | Validación |
| `models/` | Modelos ORM |
| `core/` | Configuración global |

Beneficios:
- Código desacoplado
- Testing más sencillo
- Mayor mantenibilidad
- Reutilización de lógica
- Escalabilidad futura

---

## ⚙️ Instalación Local

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/tuusuario/climAI.git
cd climAI
```

### 2️⃣ Crear entorno virtual

**Windows**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / Mac**
```bash
python -m venv venv
source venv/bin/activate
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el `.env` con tus valores:

```env
# Base de datos
DATABASE_URL=postgresql+asyncpg://usuario:password@localhost:5433/climai

# API AEMET (regístrate en opendata.aemet.es)
AEMET_API_KEY=tu_clave_aqui

# JWT
SECRET_KEY=tu_secret_key_segura

# Telegram (opcional — obtén el token con @BotFather)
TELEGRAM_BOT_TOKEN=tu_token_de_bot

# Redis
REDIS_URL=redis://localhost:6379/0
```

> ⚠️ Usa el puerto `5433` en Windows para evitar conflictos con instalaciones locales de PostgreSQL.

### 5️⃣ Levantar la infraestructura (Docker)

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 6️⃣ Aplicar migraciones

```bash
alembic upgrade head
```

### 7️⃣ Arrancar FastAPI

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 8️⃣ Entrenar el modelo IA

Necesitas al menos 15 registros meteorológicos almacenados.

```bash
python -m app.scripts.retrain_model
```

---

## 🐳 Instalación con Docker

```bash
docker-compose -f docker/docker-compose.yml up --build
```

---

## ⚡ Celery Worker

```bash
celery -A app.core.celery_app worker --loglevel=info
```

### Tareas gestionadas
- Reentrenamiento automático del modelo
- Evaluación periódica de alertas
- Notificaciones Telegram
- Procesamiento desacoplado de tareas pesadas

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 🔌 API REST

| Endpoint | Método | Descripción | Auth |
|---|---|---|---|
| `/api/clima` | GET | Datos actuales + histórico | ❌ |
| `/api/v1/predict` | GET | Predicción IA + pronóstico | ✅ |
| `/api/v1/auth/token` | POST | Login JWT | ❌ |
| `/api/provinces` | GET | Lista provincias | ❌ |
| `/api/alertas/activas` | GET | Alertas activas en tiempo real | ✅ |
| `/api/alertas/resumen` | GET | Conteo por nivel (roja/naranja/verde) | ❌ |
| `/api/alertas/notificar` | POST | Enviar alerta por Telegram | ✅ |
| `/api/telegram/vincular-manual` | POST | Vincular cuenta Telegram por chat_id | ✅ |
| `/api/telegram/desvincular` | POST | Desvincular Telegram | ✅ |
| `/api/telegram/estado` | GET | Estado de vinculación | ✅ |

---

## 📦 Ejemplo de Respuesta

```bash
curl "http://localhost:8000/api/clima?lat=40.4168&lon=-3.7038"
```

```json
{
  "temperatura": 22.4,
  "humedad": 58.0,
  "viento": 12.3,
  "precipitacion": 0.0,
  "estacion_nombre": "Madrid, Retiro",
  "ciudad_buscada": "madrid",
  "es_noche": false,
  "pronostico_ia": {
    "temperatura": 23.1,
    "tendencia": "En ascenso"
  },
  "alertas": ["VERDE"]
}
```

---

# 🛡️ Evaluación Ética y Gobernanza del Dato

## 🌱 Uso Responsable de la Inteligencia Artificial

climAI ha sido diseñado siguiendo principios básicos de IA responsable, transparencia y minimización de riesgos asociados al tratamiento de datos meteorológicos y de geolocalización.

El sistema predictivo tiene una finalidad exclusivamente informativa y no debe utilizarse para la toma de decisiones críticas relacionadas con seguridad, emergencias o actividades profesionales sensibles.

---

## 🔐 Privacidad y Protección de Datos

La aplicación aplica principios de minimización de datos:

- No se almacenan coordenadas GPS persistentes salvo necesidad funcional explícita.
- Las alertas de Telegram utilizan únicamente los identificadores necesarios para el envío de notificaciones.
- Las credenciales y secretos se gestionan mediante variables de entorno (`.env`).
- El acceso autenticado se protege mediante JWT y políticas de autenticación seguras.

El proyecto evita el tratamiento de categorías especiales de datos personales y limita la persistencia de información identificable.

---

## 📊 Gobernanza y Calidad del Dato

Los datos meteorológicos utilizados provienen de fuentes oficiales y públicas:

- AEMET OpenData API
- OpenStreetMap / Nominatim

Para garantizar calidad y consistencia:

- Se aplican procesos de normalización y validación de datos.
- El modelo IA se reentrena únicamente con datos históricos almacenados localmente.
- Se desacopla el procesamiento mediante Celery para evitar corrupción de estados concurrentes.
- PostgreSQL mantiene persistencia estructurada y trazabilidad de registros.

---

## ⚖️ Limitaciones del Modelo Predictivo

El modelo actual utiliza una aproximación basada en Regresión Lineal Multivariable, por lo que:

- Las predicciones pueden contener desviaciones respecto a fenómenos meteorológicos extremos.
- El rendimiento depende directamente de la calidad y volumen del histórico disponible.
- El sistema no sustituye servicios meteorológicos oficiales.

Las futuras versiones incluirán métricas de evaluación del modelo, monitorización de precisión y modelos temporales más avanzados (LSTM / series temporales).

---

## 🔎 Transparencia y Explicabilidad

climAI prioriza modelos interpretables frente a arquitecturas opacas:

- Las variables de entrada del modelo son conocidas y documentadas.
- El pipeline ML puede auditarse completamente.
- El flujo de entrenamiento y predicción es reproducible.

---

## ♻️ Escalabilidad y Sostenibilidad Técnica

La arquitectura desacoplada basada en FastAPI, Celery y Docker permite escalar servicios independientemente, optimizar consumo de recursos y automatizar tareas de IA de forma eficiente.

---

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 14+
- Redis
- Clave API de AEMET
- Token Telegram Bot (opcional)

---

## 📸 Capturas

- Dashboard principal en tiempo real
- Pronóstico inteligente IA
- Estadísticas de provincias
- Gráficas históricas
- Centro de alertas climáticas
- Vinculación Telegram

---

## 🗺️ Roadmap

- Implementar modelos LSTM para series temporales
- Añadir mapa interactivo con Leaflet.js
- Sistema multi-idioma (i18n)
- Aplicación móvil nativa
- Métricas de precisión del modelo
- Panel admin para monitorizar workers Celery
- Webhook Telegram con dominio propio

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!

```bash
# 1. Haz un Fork del proyecto

# 2. Crea una rama
git checkout -b feature/AmazingFeature

# 3. Haz commit
git commit -m "Add some AmazingFeature"

# 4. Haz push
git push origin feature/AmazingFeature

# 5. Abre un Pull Request 🚀
```

---

## 👤 Autores

- Scrum: Adriana Aránguez
- Product: María Roldán
- Desarrolladores: María Isabel Durando, Laura Silva Rubio, Javier CR

---

## ⚠️ Nota Legal

Este proyecto tiene fines educativos y de portfolio.

Los datos meteorológicos pertenecen a AEMET y deben utilizarse respetando las condiciones de uso de su API OpenData.


----
## 📄 Licencia
 Licencia MIT.

