from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.database import Province

router = APIRouter(prefix="/api", tags=["provincias"])

@router.get("/provinces")
async def get_provinces(db: AsyncSession = Depends(get_db)):
    try:
        # Usamos tu modelo Province
        result = await db.execute(select(Province).order_by(Province.name))
        provinces = result.scalars().all()
        # Mapeamos a los nombres que el JS entenderá
        return [{"id": p.province_id, "name": p.name} for p in provinces]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en BBDD: {e}")