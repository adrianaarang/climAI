# climAI 🌤

Aplicación web de meteorología inteligente que combina datos en tiempo real de la API de AEMET con modelos de Machine Learning para ofrecer predicciones climáticas personalizadas por ubicación geográfica.

---
# Más documentación: 
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/adrianaarang/climAI)
# 🚀 Características principales

## 🌍 Dashboard meteorológico en tiempo real

Detecta automáticamente la ubicación del usuario y muestra:

- Temperatura actual
- Humedad relativa
- Velocidad del viento
- Precipitación
- Estación meteorológica AEMET más cercana
- Histórico climático de las últimas 24h

---

## 🧠 Predicción IA

Incluye un modelo de regresión lineal entrenado con datos históricos almacenados en PostgreSQL.

El sistema:

- Ajusta la temperatura actual usando Machine Learning
- Detecta tendencias térmicas:
  - 📈 En ascenso
  - ➖ Estable
  - 📉 En descenso
- Mejora progresivamente conforme se acumulan datos reales

---

## 📅 Pronóstico inteligente de 5 días

Consume el endpoint municipal de predicción de AEMET y aplica una corrección basada en el modelo IA para generar pronósticos más ajustados.

---

## 📊 Estadísticas avanzadas

Visualización en tiempo real de:

- Temperatura media de todas las provincias españolas
- Ranking climático nacional
- Gráficas comparativas
- Correlación humedad ↔ temperatura
- Tendencias por provincias

---

## 🚨 Alertas climáticas

Sistema configurable de alertas personalizadas:

- Temperatura máxima/mínima
- Humedad
- Lluvia
- Viento

Con envío automático de notificaciones mediante Telegram Bot API.

---

## 🔍 Búsqueda por provincia

Permite consultar el tiempo de cualquier provincia española sin necesidad de geolocalización.

---

## ⚙️ Tareas asíncronas

Celery gestiona procesos en background:

- Reentrenamiento automático del modelo IA
- Evaluación periódica de alertas
- Envío de notificaciones Telegram
- Procesamiento desacoplado de tareas pesadas

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

Celery + Redis
     │
     ├── Reentrenamiento automático
     ├── Evaluación de alertas
     └── Notificaciones Telegram
```

## 🧩 Stack Tecnológico

| Backend & APIs | Data & IA | Frontend & DevOps |
|---|---|---|
| ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) | ![PostgreSQL](https://img.shields.io/badge/postgresql-%23336791.svg?style=for-the-badge&logo=postgresql&logoColor=white) | ![HTML5](https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white) |
| ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white) | ![CSS3](https://img.shields.io/badge/css3-1572B6?style=for-the-badge&logo=css3&logoColor=white) |
| ![Uvicorn](https://img.shields.io/badge/Uvicorn-4B8BBE?style=for-the-badge) | ![Alembic](https://img.shields.io/badge/Alembic-222222?style=for-the-badge) | ![JavaScript](https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) |
| ![Celery](https://img.shields.io/badge/celery-37814A?style=for-the-badge&logo=celery&logoColor=white) | ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white) | ![Jinja](https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white) |
| ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white) | ![Pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) | ![Chart.js](https://img.shields.io/badge/chart.js-F5788D?style=for-the-badge&logo=chartdotjs&logoColor=white) |
| ![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens) | ![NumPy](https://img.shields.io/badge/numpy-013243?style=for-the-badge&logo=numpy&logoColor=white) | ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) |
| ![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white) | ![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=for-the-badge&logo=openstreetmap&logoColor=white) | ![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white) |


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
│   logs
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
│   │   │           predict.cpython-313.pyc
│   │   │           
│   │   └───__pycache__
│   │           __init__.cpython-313.pyc
│   │           
│   └───__pycache__
│           __init__.cpython-313.pyc
│           
├───core
│   │   celery_app.py
│   │   config.py
│   │   security.py
│   │   __init__.py
│   │   
│   ├───resources
│   └───__pycache__
│           config.cpython-313.pyc
│           security.cpython-313.pyc
│           __init__.cpython-313.pyc
│           
├───db
│   │   base.py
│   │   base_class.py
│   │   session.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           base_class.cpython-313.pyc
│           session.cpython-313.pyc
│           __init__.cpython-313.pyc
│           
├───models
│   │   database.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           database.cpython-313.pyc
│           __init__.cpython-313.pyc
│           
├───routers
│   │   auth.py
│   │   provincias.py
│   │   views.py
│   │   
│   └───__pycache__
│           auth.cpython-313.pyc
│           provincias.cpython-313.pyc
│           views.cpython-313.pyc
│           
├───schemas
│   │   registro.py
│   │   stats.py
│   │   token.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           registro.cpython-313.pyc
│           token.cpython-313.pyc
│           __init__.cpython-313.pyc
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
│           alert_service.cpython-313.pyc
│           geo_utils.cpython-313.pyc
│           logging_service.cpython-313.pyc
│           stats_service.cpython-313.pyc
│           weather_ai_service.cpython-313.pyc
│           weather_service.cpython-313.pyc
│           __init__.cpython-313.pyc
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
        __init__.cpython-313.pyc
        
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

### 1️⃣ Clonar el repositorio

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

```env
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
```

---

### 5️⃣ Aplicar migraciones

```bash
alembic upgrade head
```

---

### 6️⃣ Arrancar FastAPI

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### 7️⃣ Entrenar el modelo IA

Necesitas al menos 15 registros meteorológicos almacenados.

```bash
python -m app.scripts.retrain_model
```

---

## 🐳 Instalación con Docker

```bash
docker-compose -f docker/docker-compose.yml up --build
```

## 🔌 API REST

| Endpoint | Método | Descripción | Auth |
|---|---|---|---|
| `/api/clima` | GET | Datos actuales + histórico | ❌ |
| `/api/v1/predict` | GET | Predicción IA + pronóstico | ✅ |
| `/api/v1/auth/token` | POST | Login JWT | ❌ |
| `/api/provinces` | GET | Lista provincias | ❌ |
| `/api/alertas/crear` | POST | Crear alerta personalizada | ✅ |

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
  }
}
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
```

## 🧪 Testing

```bash
pytest tests/
```

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
