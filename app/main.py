# app/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dotenv import load_dotenv

from app.db.session import engine, get_db
from app.db.base_class import Base
from app.models.database import User
from app.routers.auth import obtener_usuario_actual

from app.routers.auth import router as auth_router
from app.routers.views import router as views_router
from app.routers.provincias import router as provincias_router
from app.api.v1.endpoints.auth_jwt import router as auth_jwt_router
from app.api.v1.endpoints.predict import router as predict_router

load_dotenv()

# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="ClimAI", version="1.0.0", lifespan=lifespan)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Estáticos ──────────────────────────────────────────────────────────────────
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(auth_jwt_router, prefix="/api/v1")
app.include_router(predict_router,  prefix="/api/v1")
app.include_router(provincias_router)
app.include_router(views_router)

# ── API Clima (index.html) ─────────────────────────────────────────────────────
# Este endpoint lo usa el dashboard principal — devuelve datos actuales + histórico + IA
try:
    from app.services.weather_service import obtener_clima_cercano
    from app.services.weather_ai_service import WeatherAIService

    @app.get("/api/clima")
    async def get_weather_data(
        lat: float = None,
        lon: float = None,
        db: AsyncSession = Depends(get_db)
    ):
        if lat is None or lon is None:
            return {"error": "Se requiere lat y lon"}
        try:
            raw = await obtener_clima_cercano(lat, lon, db)
            if not raw:
                return {"error": "No hay datos"}

            # La IA se llama aquí igual que en predict.py
            ai = WeatherAIService()
            pronostico_ia = ai.obtener_prediccion(
                temp=raw.get("temperatura", 0),
                humedad=raw.get("humedad", 0)
            )

            return {
                "temperatura":     raw.get("temperatura", 0),
                "humedad":         raw.get("humedad", 0),
                "viento":          raw.get("viento", 0),
                "precipitacion":   raw.get("precipitacion", 0.0),
                "estacion_nombre": raw.get("estacion_nombre", "Desconocida"),
                "ciudad_buscada":  raw.get("ciudad_buscada", "Ubicación detectada"),
                "es_noche":        raw.get("es_noche", False),
                "historico":       raw.get("historico"),
                "pronostico_ia":   pronostico_ia,
            }
        except Exception as e:
            print(f"[main /api/clima] Error: {e}")
            return {"error": "Error interno"}

except ImportError as e:
    print(f"[main] weather_service no disponible: {e}")

# ── API Alertas ────────────────────────────────────────────────────────────────
try:
    from app.services.alert_service import AlertService

    @app.post("/api/alertas/crear")
    async def api_crear_alerta(datos: dict, request: Request, db: AsyncSession = Depends(get_db)):
        user_email = obtener_usuario_actual(request)
        if not user_email:
            return {"status": "error", "message": "No logueado"}
        result = await db.execute(select(User).where(User.email == user_email))
        user = result.scalar_one_or_none()
        if user:
            service = AlertService(db)
            return await service.crear_alerta(user, datos)

except ImportError as e:
    print(f"[main] alert_service no disponible: {e}")
