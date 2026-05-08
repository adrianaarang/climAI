from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crear el motor asíncrono
# Activar consultas en la consola (echo=True)
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Crear generador de sesiones asíncronas
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependencia para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()