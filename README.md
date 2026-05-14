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

## 🌍  Dashboard Meteorológico
* ** Detección automática de la ubicación del usuario mediante Nominatim, mostrando temperatura, humedad, viento, precipitación y el histórico de las últimas 24h de la estación AEMET más cercana.

## 🧠 Predicción IA
* ** Modelo de Regresión Lineal Multivariable (scikit-learn) que ajusta la temperatura actual, detecta tendencias térmicas (📈 Ascenso, ➖ Estable, 📉 Descenso) y mejora progresivamente con el reentrenamiento automático.

## 📅 Pronóstico inteligente de 5 días
* ** Consumo del endpoint municipal de AEMET con correcciones predictivas aplicadas por nuestro motor de IA.

## 🚨 Alertas climáticas
* Sistema de Alertas por Telegram:** Configuración personalizada de alertas climáticas (temperatura máxima/mínima, lluvia, viento). 
El motor asíncrono evalúa las condiciones y envía notificaciones automáticas al usuario mediante un Bot de Telegram.

## 📊 Estadísticas avanzadas
* ** Visualización interactiva con Chart.js de:
- Temperatura media de todas las provincias españolas
- Ranking climático nacional
- Gráficas comparativas
- Correlación humedad ↔ temperatura
- Tendencias por provincias

## ⚙️ Arquitectura asíncronas
* ** Integración de Celery y Redis para el procesamiento en segundo plano (reentrenamiento del modelo, evaluación de alertas y envío de mensajería) sin bloquear el servidor web.

Celery gestiona procesos en background:

- Reentrenamiento automático del modelo IA
- Evaluación periódica de alertas
- Envío de notificaciones Telegram
- Procesamiento desacoplado de tareas pesadas

## 🔍 Búsqueda por provincia (geolocalización)

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

AEMET OpenData es la principal fuente de datos meteorológicos del proyecto.

La integración funciona en dos pasos:

1. Solicitud de una URL temporal autenticada
2. Descarga y procesamiento del JSON meteorológico

### 📡 Datos consumidos

- Temperatura
- Humedad relativa
- Velocidad del viento
- Precipitación
- Observaciones por estación
- Pronóstico municipal de 5 días

El sistema selecciona automáticamente la estación meteorológica más cercana usando coordenadas geográficas y cálculo Haversine.
---

## 🗺️ Nominatim + OpenStreetMap

OpenStreetMap Nominatim se utiliza para geocodificación inversa.

Transforma:
```text
Latitud + Longitud
        ↓
Provincia / Municipio
```

Esto permite:

- Filtrar estaciones cercanas
- Mostrar la ciudad detectada
- Consultar provincias sin GPS
- Mejorar la experiencia del usuario

  ---
  
## ⚡ Backend y Servidor
## 🚀 FastAPI

FastAPI es el núcleo del backend.

 Motivos de elección
 
- Alto rendimiento
- Soporte nativo async/await
- Documentación automática OpenAPI
- Arquitectura moderna y escalable
- Excelente integración con Pydantic

Gracias al enfoque asíncrono, la aplicación puede manejar múltiples consultas meteorológicas simultáneamente sin bloquear el servidor.
---

## 🌐 Uvicorn

Uvicorn es el servidor ASGI encargado de ejecutar la aplicación FastAPI.

Proporciona:

- Alto rendimiento
- WebSockets
- Compatibilidad ASGI
- Concurrencia eficiente

## 🎨 Jinja2

Jinja2 renderiza HTML dinámico desde el servidor.

Se utiliza para:

- Dashboard meteorológico
- Estadísticas
- Login y autenticación
- Renderizado de vistas dinámicas

## 🗄️ Base de Datos y Persistencia
# 🐘 PostgreSQL

PostgreSQL almacena:

- Usuarios
- Alertas
- Históricos meteorológicos
- Logs
- Predicciones
- Configuración

## 🧩 SQLAlchemy Async

SQLAlchemy permite interactuar con PostgreSQL de forma asíncrona.

Ventajas
- ORM robusto
- Consultas async
- Relaciones complejas
- Escalabilidad
- Integración con Alembic

## 🔄 Alembic

Alembic gestiona el versionado y las migraciones de la base de datos.

Permite:

- Crear nuevas tablas
- Modificar esquemas
- Sincronizar entornos
- Mantener histórico de cambios
  
## 🧠 Inteligencia Artificial y Procesamiento de Datos
# 🤖 scikit-learn

scikit-learn se utiliza para entrenar el modelo predictivo.

Modelo actual
- Regresión Lineal Multivariable
Objetivo

Predecir:

- Temperatura corregida
- Tendencia térmica
  # 📊 Pandas y NumPy

Pandas y NumPy se utilizan para:

- Limpieza de datos
- Transformaciones
- Normalización
- Preparación del dataset
- Ingeniería de variables

# 💾 Joblib

Joblib permite serializar el modelo entrenado en un archivo .pkl.

```text
Entrenamiento
      ↓
modelo_clima.pkl
      ↓
Carga en tiempo real
      ↓
Inferencia IA
```

# 🧱 Arquitectura Técnica

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

# 🧠 Detalles del Modelo IA

## Algoritmo

Modelo de Regresión Lineal Multivariable usando scikit-learn.

--- 

## Features de Entrada
- Temperatura actual
- Humedad relativa
- Hora del día transformada en sinusoide
- Variables temporales derivadas
  
## Target
- Temperatura corregida
- Tendencia térmica
  
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
## Funcionamiento

Cada vez que un usuario consulta el clima:

1. Se almacenan datos meteorológicos reales
2. PostgreSQL acumula histórico
3. Celery puede lanzar reentrenamientos automáticos
4. El modelo .pkl se actualiza
5. Las futuras predicciones mejoran progresivamente
---
# 🔄 Tareas Asíncronas y Mensajería
## Celery

Celery ejecuta tareas pesadas en background.

## Procesos gestionados
- Reentrenamiento automático IA
- Evaluación de alertas
- Envío de notificaciones
- Automatización programada

Esto evita bloquear las peticiones HTTP del usuario.
---

## 🔴 Redis

Redis funciona como broker entre FastAPI y Celery.

Gestiona:

- Cola de tareas
- Mensajería interna
- Caché temporal
- Alertas Personalizas
  
# 📱 Notificaciones y Frontend
## ✈️ Telegram Bot API

Telegram se utiliza para enviar alertas meteorológicas en tiempo real.

Ejemplos
- Riesgo de lluvia
- Temperaturas extremas
- Cambios bruscos
- Alertas personalizadas

## 📈 Chart.js

Chart.js transforma datos climáticos en gráficas interactivas.

- Visualizaciones
- Temperatura histórica
- Rankings provinciales
- Comparativas
- Tendencias climáticas

## 🟨 Vanilla JavaScript + Fetch API

El frontend utiliza JavaScript Vanilla para realizar peticiones asíncronas al backend mediante Fetch API.

Ventajas
- Sin dependencias pesadas
- Mayor rendimiento
- Menor complejidad
- Arquitectura ligera
  
## 🐳 DevOps y Despliegue
## 📦 Docker + Docker Compose

Docker permite contenerizar toda la infraestructura.

Servicios aislados
- FastAPI
- PostgreSQL
- Redis
- Celery Worker
  
Beneficios
- Entorno reproducible
- Fácil despliegue
- Portabilidad
- Escalabilidad
  
## 🔐 Python-dotenv

python-dotenv gestiona variables sensibles mediante archivos .env.

Ejemplos
- API Keys
- JWT Secret
- Credenciales PostgreSQL
- Tokens Telegram
  
## 🔄 Flujo Tecnológico Completo
```text
1. Navegador del usuario
        │
        ▼
2. Geolocalización GPS
        │
        ▼
3. Nominatim (Provincia/Municipio)
        │
        ▼
4. FastAPI
        │
        ├── Consulta AEMET
        │
        ├── Consulta PostgreSQL
        │
        └── Ejecuta ML Engine
                    │
                    ▼
             scikit-learn
                    │
                    ▼
           Predicción IA
                    │
                    ▼
          Respuesta al frontend
                    │
                    ▼
          Chart.js renderiza datos

Procesos paralelos:
Celery + Redis → Alertas → Telegram Bot API

```
## 📁 Estructura del Proyecto
```text
climAI/

├── app/
│   ├──  api/v1/
│   │           ├── endpoints/
│   │           │        ├── predict.py
│   │           │        └── auth_jwt.py
│   │           │        └── climas.py   
│   │           │        └── stats.py    
│   │           └── api_router.py
│   │
│   ├── core/
│   │       ├── resources/
│   │       │           ├── estaciones_madrid.json
│   │       │           └── municipios.json
│   │       ├── celery_app.py
│   │       ├── config.py
│   │       └── security.py
│   │
│   ├── db/
│   │    ├── base_class.py
│   │    ├── base.py
│   │    └── session.py
│   │
│   ├── models/
│   │    └── database.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── provincias.py
│   │   └── views.py
│   │
│   ├── schemas/
│   │   ├── registro.py
│   │   ├── stats.py
│   │   └── token.py
│   │
│   ├── scripts/
│   │   └── retrain_model.py
│   │
│   ├── services/
│   │    ├── aemet_client.py
│   │    ├── alert_service.py
│   │    ├── geo_utils.py
│   │    ├── logging_service.py
│   │    │── ml_engine.py
│   │    ├── normalizer_service.py
│   │    ├── notifier_service.py
│   │    ├── stats_service.py
│   │    ├── telegram_bot.py
│   │    ├── weather_ai_service.py
│   │    └── weather_service.py
│   │
│   ├── static/
│   │    ├── css/
│   │    └── js/
│   │
├── templates/
│
└── main.py
└── logs
│
├── alembic/
│       └── versions/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── ml_models/
│   └── modelo_clima.pkl
│
├── tests/
│   ├── test_api.py
│   └── test_celery.py
│   └── test_normalizer.py
│
├── worker/
│   ├── tasks.py
│
├── .env
├── .env.example
├── .gitignore
└── alembic.ini
└── Dockerfile
└── README.md
└── requirements.txt


```

## 🏛️ Decisiones de Arquitectura

# 📌 Separación de responsabilidades

| Carpeta | Responsabilidad |
|---|---|
| `routers/` | Endpoints y vistas |
| `services/` | Lógica de negocio |
| `db/` | Persistencia |
| `schemas/` | Validación |
| `models/` | Modelos ORM |
| `core/` | Configuración global |

Beneficios
- Código desacoplado
- Testing más sencillo
- Mayor mantenibilidad
- Reutilización de lógica
- Escalabilidad futura
  
## ⚙️ Instalación Local

### 1️⃣ Clonar el repositorio y preparar el entorno

```bash
git clone https://github.com/tuusuario/climAI.git
cd climAI
```

---

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

---

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configurar variables de entorno

```bash
cp .env.example .env
```
---

Importante: Asegúrate de configurar el puerto de la base de datos al 5433 para evitar conflictos con instalaciones locales de PostgreSQL en Windows.

# Base de datos
DATABASE_URL=postgresql+asyncpg://usuario:password@localhost/climai

# API AEMET
AEMET_API_KEY=tu_clave_aqui

# JWT
SECRET_KEY=tu_secret_key_segura

# Telegram
TELEGRAM_BOT_TOKEN=tu_token_de_bot

# Redis
REDIS_URL=redis://localhost:6379/0

---

### 5️⃣ Levantar la Infraestructura (Docker)
Inicia la base de datos y Redis en segundo plano:

Bash
docker compose -f docker/docker-compose.yml up -d 

### 6️⃣ Aplicar migraciones

```bash
alembic upgrade head
```

---

### 7️⃣ Arrancar FastAPI

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### 8 Entrenar el modelo IA

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

### Ejecución

```bash
celery -A app.core.celery_app worker --loglevel=info
```

### Tareas gestionadas

- Reentrenamiento automático del modelo
- Evaluación periódica de alertas
- Notificaciones Telegram
- Procesamiento desacoplado de tareas pesadas

## 🧪 Testing

```bash
pytest tests/
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

climAI prioriza modelos interpretables frente a arquitecturas opacas.

Actualmente:
- Las variables de entrada del modelo son conocidas y documentadas.
- El pipeline ML puede auditarse completamente.
- El flujo de entrenamiento y predicción es reproducible.

Esto facilita:
- Trazabilidad técnica
- Auditoría del sistema
- Mantenimiento del modelo
- Comprensión de las predicciones generadas

---

## ♻️ Escalabilidad y Sostenibilidad Técnica

La arquitectura desacoplada basada en FastAPI, Celery y Docker permite:

- Escalar servicios independientemente
- Optimizar consumo de recursos
- Automatizar tareas de IA de forma eficiente
- Reducir bloqueos y tiempos de respuesta

El diseño modular favorece además la mantenibilidad y evolución futura del sistema.

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
- Sistema de alertas
  
## 🗺️ Roadmap

- Implementar modelos LSTM para series temporales
- Añadir mapa interactivo con Leaflet.js
- Sistema multi-idioma (i18n)
- Aplicación móvil nativa
- Métricas de precisión del modelo
- Panel admin para monitorizar workers Celery

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
- Desarrolladores:  María Isabel Durando, Laura Silva Rubio, Javier CR

---

## ⚠️ Nota Legal

Este proyecto tiene fines educativos y de portfolio.

Los datos meteorológicos pertenecen a AEMET y deben utilizarse respetando las condiciones de uso de su API OpenData.

----
## 📄 Licencia
 Licencia MIT.
