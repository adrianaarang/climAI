
# climAI 🌤 Predicción Meteorológica Inteligente

**climAI** es una aplicación web de meteorología avanzada que combina datos en tiempo real de la API de **AEMET** con modelos de **Machine Learning** para ofrecer predicciones climáticas personalizadas y un sistema de alertas asíncronas vía Telegram.

---

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

---

## 📺 Demo del Proyecto

> Próximamente

---

## 📚 Documentación Completa

👉 https://deepwiki.com/adrianaarang/climAI

---

## 🚀 Características Principales

### 🌍 Dashboard Meteorológico
Detección automática de la ubicación del usuario mediante Nominatim, mostrando temperatura, humedad, viento, precipitación y el histórico de las últimas 24h de la estación AEMET más cercana.

### 🧠 Predicción IA
Modelo de Regresión Lineal Multivariable (scikit-learn) que ajusta la temperatura actual, detecta tendencias térmicas (📈 Ascenso, ➖ Estable, 📉 Descenso) y mejora progresivamente con el reentrenamiento automático.

### 📅 Pronóstico Inteligente de 5 Días
Consumo del endpoint municipal de AEMET con correcciones predictivas aplicadas por el motor de IA.

### 🚨 Sistema de Alertas Climáticas
Centro de alertas en tiempo real con tres niveles de severidad:

| Nivel | Color | Condiciones |
|---|---|---|
| Alerta Roja | 🔴 | Temp ≥ 40°C, temp ≤ -5°C, viento > 70 km/h, lluvia > 30 mm |
| Alerta Naranja | 🟠 | Temp ≥ 35°C, temp ≤ 0°C, viento > 40 km/h, lluvia > 10 mm |
| Sin alerta | 🟢 | Condiciones dentro de parámetros normales |

La interfaz se actualiza automáticamente cada 60 segundos y permite filtrar por nivel y tipo de fenómeno.

### ✈️ Notificaciones Telegram
Recibe alertas climáticas directamente en Telegram sin configuración adicional:

1. Abre Telegram y escríbele a **@userinfobot**
2. Copia el número de tu `Id`
3. Ve a climAI → Vincular Telegram → pega el ID y pulsa **Vincular**
4. Recibirás un mensaje de confirmación al instante

> No requiere ngrok ni instalaciones externas.

### 📊 Estadísticas Avanzadas
Visualización interactiva con Chart.js de temperatura media por provincias, ranking climático nacional, correlación humedad ↔ temperatura y tendencias comparativas.

### ⚙️ Arquitectura Asíncrona
Integración de Celery y Redis para el procesamiento en segundo plano sin bloquear el servidor web.

### 🔍 Búsqueda por Provincia
Permite consultar el tiempo de cualquier provincia española sin necesidad de geolocalización.

---

## 🧩 Stack Tecnológico

| Capa | Tecnologías |
|:---|:---|
| **Backend & API** | FastAPI, Uvicorn, SQLAlchemy Async, Alembic, Python-dotenv |
| **Data & IA** | PostgreSQL, scikit-learn, Pandas, NumPy, Joblib |
| **Tareas Async** | Celery, Redis |
| **Integraciones** | AEMET OpenData API, Telegram Bot API, OpenStreetMap (Nominatim) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Jinja2, Chart.js |
| **Infraestructura** | Docker, Docker Compose |

---

## 🏗️ Arquitectura del Sistema

### Flujo de Datos

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

### Pipeline ML

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

### Separación de Responsabilidades

| Carpeta | Responsabilidad |
|---|---|
| `routers/` | Endpoints y vistas |
| `services/` | Lógica de negocio |
| `db/` | Persistencia |
| `schemas/` | Validación |
| `models/` | Modelos ORM |
| `core/` | Configuración global |

---

## 🔌 API REST

| Endpoint | Método | Descripción | Auth |
|---|---|---|---|
| `/api/clima` | `GET` | Datos actuales + histórico | ❌ |
| `/api/v1/predict` | `GET` | Predicción IA + pronóstico | ✅ |
| `/api/v1/auth/token` | `POST` | Login JWT | ❌ |
| `/api/provinces` | `GET` | Lista de provincias | ❌ |
| `/api/alertas/activas` | `GET` | Alertas activas en tiempo real | ✅ |
| `/api/alertas/resumen` | `GET` | Conteo por nivel (roja / naranja / verde) | ❌ |
| `/api/alertas/notificar` | `POST` | Enviar alerta por Telegram | ✅ |
| `/api/telegram/vincular-manual` | `POST` | Vincular cuenta Telegram por `chat_id` | ✅ |
| `/api/telegram/desvincular` | `POST` | Desvincular Telegram | ✅ |
| `/api/telegram/estado` | `GET` | Estado de vinculación | ✅ |

### 📦 Ejemplo de Respuesta

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

## ⚙️ Tareas Gestionadas con Celery

| Tarea | Descripción |
|---|---|
| 🔄 Reentrenamiento del modelo | Reentrena automáticamente con el histórico disponible |
| 🔔 Evaluación de alertas | Revisión periódica del nivel de riesgo meteorológico |
| 📲 Notificaciones Telegram | Envío de alertas a usuarios vinculados |
| ⚡ Procesamiento desacoplado | Gestión asíncrona de tareas pesadas sin bloquear la API |

---

## 🔌 APIs Externas y Servicios Integrados

### 🌦️ AEMET OpenData API

Principal fuente de datos meteorológicos. La integración funciona en dos pasos:

1. Solicitud de una URL temporal autenticada
2. Descarga y procesamiento del JSON meteorológico

Datos consumidos: temperatura, humedad relativa, velocidad del viento, precipitación, observaciones por estación y pronóstico municipal de 5 días.

El sistema selecciona automáticamente la estación meteorológica más cercana usando coordenadas geográficas y cálculo Haversine.

### 🗺️ Nominatim + OpenStreetMap

Transforma coordenadas en provincia/municipio para filtrar estaciones y mejorar la experiencia del usuario.

---

## 📁 Estructura del Proyecto

```text
climAI/
├── main.py
├── api/
│   └── v1/
│       ├── api_router.py
│       └── endpoints/
│           ├── auth_jwt.py
│           ├── climas.py
│           ├── predict.py
│           └── stats.py
├── core/
│   ├── celery_app.py
│   ├── config.py
│   ├── security.py
│   └── resources/
│       ├── estaciones_madrid.json
│       └── municipios.json
├── db/
│   ├── base.py
│   ├── base_class.py
│   └── session.py
├── models/
│   └── database.py
├── routers/
│   ├── alertas.py
│   ├── auth.py
│   ├── provincias.py
│   ├── telegram_bot.py
│   └── views.py
├── schemas/
│   ├── registro.py
│   ├── stats.py
│   └── token.py
├── scripts/
│   └── retrain_model.py
├── services/
│   ├── aemet_client.py
│   ├── alert_service.py
│   ├── geo_utils.py
│   ├── logging_service.py
│   ├── ml_engine.py
│   ├── normalizer_service.py
│   ├── notifier_service.py
│   ├── stats_service.py
│   ├── weather_ai_service.py
│   └── weather_service.py
├── static/
│   ├── css/
│   │   ├── alertas.css
│   │   ├── auth.css
│   │   ├── base.css
│   │   ├── index.css
│   │   ├── prediccion.css
│   │   ├── stats.css
│   │   └── vincular_telegram.css
│   └── js/
│       ├── alertas.js
│       ├── auth.js
│       ├── base.js
│       ├── index.js
│       ├── prediccion.js
│       ├── stats.js
│       ├── vincular_telegram.js
│       └── weather_province.js
└── templates/
    ├── alertas.html
    ├── base.html
    ├── index.html
    ├── login.html
    ├── prediccion_ia.html
    ├── registro_usuario.html
    ├── stats.html
    ├── vincular_telegram.html
    └── weather_province.html
```

---

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 14+
- Redis
- Clave API de AEMET
- Token de Telegram Bot
- `libpq-dev` (o `libpq-devel` en sistemas RPM)

> Asegúrate de tener un archivo `.env` configurado con tus credenciales antes de ejecutar la aplicación.

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

---

## 🔎 Transparencia y Explicabilidad

climAI prioriza modelos interpretables frente a arquitecturas opacas:

- Las variables de entrada son conocidas y están documentadas.
- El pipeline de ML es completamente auditable.
- El flujo de entrenamiento y predicción es reproducible.

---

## ⚖️ Limitaciones del Modelo Predictivo

El modelo actual utiliza una aproximación basada en **Regresión Lineal Multivariable**, por lo que:

- Las predicciones pueden desviarse en fenómenos meteorológicos extremos.
- El rendimiento depende directamente de la calidad y volumen del histórico disponible.
- El sistema no sustituye a los servicios meteorológicos oficiales como [AEMET](https://www.aemet.es).

> Las futuras versiones incluirán métricas de evaluación, monitorización de precisión y modelos más avanzados (LSTM / series temporales).

---

## 📊 Gobernanza y Calidad del Dato

Los datos meteorológicos provienen de fuentes oficiales y públicas:

- [AEMET OpenData API](https://opendata.aemet.es)
- [OpenStreetMap / Nominatim](https://nominatim.openstreetmap.org)

Para garantizar calidad y consistencia:

- Los datos se normalizan y validan antes de su uso.
- El modelo se reentrena exclusivamente con histórico almacenado localmente.
- El procesamiento se desacopla mediante **Celery** para evitar corrupción por concurrencia.
- **PostgreSQL** garantiza persistencia estructurada y trazabilidad de registros.

---

## 🔐 Privacidad y Protección de Datos

La aplicación aplica principios de **minimización de datos**:

- No se almacenan coordenadas GPS de forma persistente salvo necesidad funcional explícita.
- Las alertas de Telegram utilizan únicamente los identificadores mínimos necesarios para el envío.
- Las credenciales y secretos se gestionan mediante variables de entorno (`.env`).
- El acceso autenticado se protege mediante **JWT** y políticas de autenticación seguras.

> El proyecto evita el tratamiento de categorías especiales de datos personales y limita la persistencia de información identificable.

---

## 🛡️ Evaluación Ética y Gobernanza del Dato

### 🌱 Uso Responsable de la Inteligencia Artificial

climAI ha sido diseñado siguiendo principios de **IA responsable**, transparencia y minimización de riesgos en el tratamiento de datos meteorológicos y de geolocalización.

> ⚠️ El sistema predictivo tiene una finalidad exclusivamente **informativa** y no debe utilizarse para la toma de decisiones críticas relacionadas con seguridad, emergencias o actividades profesionales sensibles.

---

## 🗺️ Roadmap

### Corto plazo
- [ ] Webhook Telegram con dominio propio
- [ ] Panel admin para monitorizar workers Celery
- [ ] Métricas de precisión del modelo

### Medio plazo
- [ ] Mapa interactivo con Leaflet.js
- [ ] Sistema multi-idioma (i18n)

### Largo plazo
- [ ] Modelos LSTM para predicción de series temporales
- [ ] Aplicación móvil nativa

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

