import asyncio
from celery.utils.log import get_task_logger
from app.core.celery_app import celery_app
from app.services.weather_service import obtener_clima_cercano
from app.db.session import AsyncSessionLocal

logger = get_task_logger(__name__)

@celery_app.task
def actualizar_clima(lat: float, lon: float):
    async def run_task():
        async with AsyncSessionLocal() as db:
            try:
                logger.info(f"Worker iniciando petición: Lat({lat}), Lon({lon})")
                data = await obtener_clima_cercano(
                    lat=lat,
                    lon=lon,
                    db=db
                )
                logger.info(f"Datos procesados correctamente: {data}")
                return data
            except Exception as e:
                logger.error(f"Error crítico en el Worker: {str(e)}")
                raise e

    return asyncio.run(run_task())