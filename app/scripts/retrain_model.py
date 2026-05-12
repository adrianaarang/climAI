import asyncio
import pandas as pd
import joblib
import logging
import traceback
from pathlib import Path
from sqlalchemy.future import select
from sklearn.linear_model import LinearRegression
from app.models.database import Record
from app.db.session import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def entrenar():
    logger.info("Conectando a BD...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Record).order_by(Record.timestamp.asc()))
        records = result.scalars().all()
        logger.info(f"Registros encontrados: {len(records)}")
        if len(records) < 15:
            logger.warning("Pocos registros, se necesitan al menos 15.")
            return
        df = pd.DataFrame([{
            "temperature": r.temperature,
            "humidity": r.humidity,
            "hour": r.timestamp.hour
        } for r in records])
        model = LinearRegression()
        model.fit(df[["temperature", "humidity", "hour"]], df["temperature"])
        ruta = Path("ml_models/modelo_clima.pkl")
        ruta.parent.mkdir(exist_ok=True)
        joblib.dump(model, ruta)
        logger.info(f"Modelo guardado en {ruta}")

try:
    asyncio.run(entrenar())
except Exception as e:
    traceback.print_exc()