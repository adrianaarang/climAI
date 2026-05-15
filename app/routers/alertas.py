# app/routers/alertas.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.database import User, Record, Station
from app.routers.auth import obtener_usuario_actual
from app.services.alert_service import AlertService
from app.services.notifier_service import NotifierService

router = APIRouter(prefix="/api/alertas", tags=["alertas"])


@router.get("/activas")
async def get_alertas_activas(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Devuelve las alertas activas basándose en los registros más recientes
    de todas las estaciones.
    """
    try:
        # Obtener los registros más recientes de cada estación
        result = await db.execute(
            select(Record)
            .options(selectinload(Record.station))
            .order_by(Record.timestamp.desc())
            .limit(50)
        )
        records = result.scalars().all()

        service = AlertService()
        alertas_activas = []

        for record in records:
            datos = {
                "temperature": record.temperature,
                "rain": record.rain,
                "humidity": record.humidity,
                "wind": record.wind,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
            }
            alertas = service.evaluar_alertas(datos)

            # Solo incluir si hay algo distinto de VERDE
            if alertas and alertas != ["VERDE"]:
                alertas_activas.append({
                    "station": record.station.name if record.station else "Desconocida",
                    "station_id": record.station_id,
                    "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                    "temperatura": record.temperature,
                    "viento": record.wind,
                    "lluvia": record.rain,
                    "humedad": record.humidity,
                    "alertas": alertas,
                    "nivel_max": _nivel_max(alertas),
                })

        return {"status": "ok", "alertas": alertas_activas, "total": len(alertas_activas)}

    except Exception as e:
        return {"status": "error", "message": str(e), "alertas": []}


@router.get("/resumen")
async def get_resumen_alertas(db: AsyncSession = Depends(get_db)):
    """
    Devuelve conteo de alertas por nivel para el dashboard.
    """
    try:
        result = await db.execute(
            select(Record).order_by(Record.timestamp.desc()).limit(100)
        )
        records = result.scalars().all()

        service = AlertService()
        rojas = naranja = verde = 0

        for record in records:
            datos = {
                "temperature": record.temperature,
                "rain": record.rain,
                "humidity": record.humidity,
                "wind": record.wind,
            }
            alertas = service.evaluar_alertas(datos)
            nivel = _nivel_max(alertas)
            if nivel == "ROJA":
                rojas += 1
            elif nivel == "NARANJA":
                naranja += 1
            else:
                verde += 1

        return {"rojas": rojas, "naranja": naranja, "verde": verde}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/notificar")
async def notificar_alerta(
    datos: dict,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Envía notificación Telegram al usuario autenticado con las alertas dadas.
    """
    user_email = obtener_usuario_actual(request)
    if not user_email:
        return {"status": "error", "message": "No autenticado"}

    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    if not user or not user.telegram_id:
        return {"status": "error", "message": "Usuario sin Telegram vinculado"}

    notifier = NotifierService()
    ok = await notifier.enviar_alerta(
        telegram_id=user.telegram_id,
        estacion=datos.get("station", "Desconocida"),
        alertas=datos.get("alertas", []),
        datos_meteo=datos,
    )
    return {"status": "ok" if ok else "error"}


def _nivel_max(alertas: list) -> str:
    """Determina el nivel máximo de alerta de una lista."""
    if any("ROJA" in a for a in alertas):
        return "ROJA"
    if any("NARANJA" in a for a in alertas):
        return "NARANJA"
    return "VERDE"