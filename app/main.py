# app/main.py-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import engine, get_db
from app.db.base_class import Base
from app.models.database import User

# Routers
from app.routers.auth import router as auth_router, obtener_usuario_actual
from app.api.v1.endpoints.auth_jwt import router as auth_jwt_router
from app.routers.provincias import router as provincias_router

load_dotenv()

app = FastAPI(title="ClimAI", version="1.0.0")


# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Estáticos y Templates ──────────────────────────────────────────────────────
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


# ── Servicios ──────────────────────────────────────────────────────────────────
try:
    from app.services.weather_service import obtener_clima_cercano
except ImportError as e:
    print(f"[main] Error importando weather_service: {e}")
    obtener_clima_cercano = None

try:
    from app.services.alert_service import AlertService
except ImportError as e:
    print(f"[main] Error importando alert_service: {e}")
    AlertService = None


# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)                        # /login, /registro_usuario, /logout
app.include_router(auth_jwt_router, prefix="/api/v1")  # /api/v1/auth/token
app.include_router(provincias_router)


# ── Páginas ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = obtener_usuario_actual(request)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"usuario": user}
    )


@app.get("/weather-province", response_class=HTMLResponse)
async def interface_provincias(request: Request):
    user = obtener_usuario_actual(request)
    return templates.TemplateResponse(
        "weather_province.html",
        {"request": request, "usuario": user}
    )


@app.get("/alertas", response_class=HTMLResponse)
async def pagina_alertas(request: Request):
    user = obtener_usuario_actual(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "alertas.html",
        {"request": request, "usuario": user}
    )


# ── API Clima ──────────────────────────────────────────────────────────────────
@app.get("/api/clima")
async def get_weather_data(
    lat: float = None,
    lon: float = None,
    db: AsyncSession = Depends(get_db),
):
    if lat is None or lon is None:
        return {"error": "Se requiere lat y lon"}
    try:
        raw = await obtener_clima_cercano(lat, lon, db)
        if not raw:
            return {"error": "No hay datos disponibles para esta selección"}
        return {
            "temperatura": raw.get("temperatura", 0),
            "humedad": raw.get("humedad", 0),
            "viento": raw.get("viento", 0),
            "precipitacion": raw.get("precipitacion", 0.0),
            "estacion_nombre": raw.get("estacion_nombre", "Desconocida"),
            "ciudad_buscada": raw.get("ciudad_buscada", "Ubicación detectada"),
            "es_noche": raw.get("es_noche", False),
            "historico": raw.get("historico"),
            "pronostico_ia": raw.get("pronostico_ia")
        }
    except Exception as e:
        print(f"[main /api/clima] Error: {e}")
        return {"error": "Error interno del servidor"}


# ── API Alertas ────────────────────────────────────────────────────────────────
@app.post("/api/alertas/crear")
async def api_crear_alerta(
    datos: dict,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_email = obtener_usuario_actual(request)
    if not user_email:
        return {"status": "error", "message": "Debes estar logueado"}
    if not AlertService:
        return {"status": "error", "message": "Servicio de alertas no disponible"}
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    if user:
        service = AlertService(db)
        return await service.registrar_alerta_usuario(user.user_id, datos)
    return {"status": "error", "message": "Usuario no encontrado"}


# ── Ejecución ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
