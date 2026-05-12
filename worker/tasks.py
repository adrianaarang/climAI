import asyncio

from app.core.celery_app import celery_app
from app.services.weather_service import obtener_clima_cercano
from app.db.session import AsyncSessionLocal


@celery_app.task
def actualizar_clima(lat: float, lon: float):

    async def run_task():

        async with AsyncSessionLocal() as db:

            data = await obtener_clima_cercano(
                lat=lat,
                lon=lon,
                db=db
            )

            print(data)

            return data

    return asyncio.run(run_task())