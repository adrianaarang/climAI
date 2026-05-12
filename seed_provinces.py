import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.models.database import Province
from app.db.session import engine

# Lista de provincias
NOMBRES_PROVINCIAS = [
    "Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Barcelona",
    "Burgos", "Cáceres", "Cádiz", "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca",
    "Gerona", "Granada", "Guadalajara", "Guipúzcoa", "Huelva", "Huesca", "Islas Baleares",
    "Jaén", "La Coruña", "La Rioja", "Las Palmas", "León", "Lérida", "Lugo", "Madrid", "Málaga",
    "Murcia", "Navarra", "Orense", "Palencia", "Pontevedra", "Salamanca", "Santa Cruz de Tenerife",
    "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo", "Valencia", "Valladolid",
    "Vizcaya", "Zamora", "Zaragoza"
]

async def seed():
    # En SQLAlchemy 2.0 se usa async_sessionmaker
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        print("Conectado a la base de datos. Insertando provincias...")
        for nombre in NOMBRES_PROVINCIAS:
            nueva_provincia = Province(name=nombre)
            session.add(nueva_provincia)
        
        await session.commit()
        print(f"¡Éxito! Se han cargado {len(NOMBRES_PROVINCIAS)} provincias.")

if __name__ == "__main__":
    asyncio.run(seed())