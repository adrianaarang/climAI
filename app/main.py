# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api_router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="API para el Sistema de Gestión Climática — climAI",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────────
# Permite que el dashboard de Persona 5 consuma la API
# desde un origen distinto (puerto diferente)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rutas ────────────────────────────────────────────────────────
# Todas las rutas bajo /api/v1
app.include_router(api_router, prefix="/api/v1")


# ── Health check ─────────────────────────────────────────────────
# Confirma que el servidor está vivo
# Lo usan Docker y el equipo para verificar que la app arrancó
@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "service": settings.PROJECT_NAME,
    }