import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Importaciones de Base de Datos
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, get_db
from app.db.base_class import Base

# Importaciones de Routers (ajustado a tu archivo auth.py)
from app.routers.auth import router as auth_router, obtener_usuario_actual

load_dotenv()

app = FastAPI(title="ClimAI", version="1.0.0")

# --- BASE DE DATOS: Creación automática de tablas ---
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ARCHIVOS ESTÁTICOS Y TEMPLATES ---
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# --- SERVICIOS ---
try:
    from app.services.weather_service import obtener_clima_cercano
except ImportError as e:
    print(f"Error crítico: No se pudo importar weather_service: {e}")
    async def obtener_clima_cercano(lat, lon, db): return None

# --- REGISTRO DE ROUTERS ---
# Incluye las rutas de login, registro y logout definidas en routers/auth.py
app.include_router(auth_router)

# --- RUTAS DE NAVEGACIÓN ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Verificamos si hay sesión activa para mostrar el nombre del usuario en el header
    user = obtener_usuario_actual(request)
    return templates.TemplateResponse("index.html", {"request": request, "usuario": user})

# --- API ENDPOINTS ---

@app.get("/api/clima")
async def get_weather_data(
    lat: float, 
    lon: float, 
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint que devuelve el clima actual y el histórico.
    Ahora requiere 'db' para consultar provincias y guardar registros.
    """
    try:
        # Llamada al servicio pasando la sesión de DB
        raw = await obtener_clima_cercano(lat, lon, db)
        
        if not raw:
            return {"error": "No se pudieron obtener datos de clima"}

        # Devolvemos el JSON estructurado para el frontend (JS)
        return {
            "temperature":     raw.get("temperatura", 0),
            "humidity":        raw.get("humedad", 0),
            "wind_speed":      raw.get("viento", 0),
            "precipitation":   raw.get("precipitacion", 0.0),
            "estacion_nombre": raw.get("estacion_nombre", "Estación Desconocida"),
            "ciudad_buscada":  raw.get("ciudad_buscada", "Ubicación detectada"),
            "es_noche":        raw.get("es_noche", False),
            "historico":       raw.get("historico")
        }

    except Exception as e:
        print(f"Error en el endpoint de clima: {e}")
        return {"error": "Error interno al procesar la solicitud de clima"}