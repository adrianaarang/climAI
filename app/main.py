# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.api_router import api_router
from app.routers import auth as auth_frontend
from app.routers import provincias

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="API para el Sistema de Gestión Climática — climAI",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Archivos estáticos (CSS, JS) ─────────────────────────────
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ── Rutas API REST ───────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")

# ── Rutas Frontend ───────────────────────────────────────────
app.include_router(auth_frontend.router)
app.include_router(provincias.router)


# ── Health check ─────────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "service": settings.PROJECT_NAME,
    }
