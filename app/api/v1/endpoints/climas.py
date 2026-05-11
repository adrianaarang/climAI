# app/api/v1/endpoints/climas.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.database import Record as RecordModel
from app.schemas.registro import (
    RecordCreate,
    RecordUpdate,
    Record,
)

router = APIRouter(prefix="/climas", tags=["Mediciones Climáticas"])


# ══════════════════════════════════════════════════════════════
# POST /api/v1/climas/
# ══════════════════════════════════════════════════════════════
@router.post(
    "/",
    response_model=Record,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva medición climática",
)
async def create_record(
    record_in: RecordCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(RecordModel).filter(
        RecordModel.station_id == record_in.station_id,
        RecordModel.timestamp == record_in.timestamp,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un registro para la estación "
                   f"{record_in.station_id} en {record_in.timestamp}."
        )

    db_record = RecordModel(**record_in.model_dump())

    try:
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al guardar en la base de datos."
        )

    return db_record


# ══════════════════════════════════════════════════════════════
# GET /api/v1/climas/
# ══════════════════════════════════════════════════════════════
@router.get(
    "/",
    response_model=list[Record],
    summary="Listar mediciones climáticas",
)
async def list_records(
    station_id: Optional[int] = Query(None, description="Filtrar por estación"),
    limit: int = Query(50, ge=1, le=500, description="Registros por página"),
    page: int = Query(1, ge=1, description="Número de página"),
    db: Session = Depends(get_db),
):
    query = db.query(RecordModel)

    if station_id:
        query = query.filter(RecordModel.station_id == station_id)

    offset = (page - 1) * limit
    records = query.offset(offset).limit(limit).all()

    return records


# ══════════════════════════════════════════════════════════════
# GET /api/v1/climas/{record_id}
# ══════════════════════════════════════════════════════════════
@router.get(
    "/{record_id}",
    response_model=Record,
    summary="Obtener medición por ID",
)
async def get_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    record = db.query(RecordModel).filter(
        RecordModel.record_id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún registro con id={record_id}"
        )

    return record


# ══════════════════════════════════════════════════════════════
# PUT /api/v1/climas/{record_id}
# ══════════════════════════════════════════════════════════════
@router.put(
    "/{record_id}",
    response_model=Record,
    summary="Actualizar medición existente",
)
async def update_record(
    record_id: int,
    record_in: RecordUpdate,
    db: Session = Depends(get_db),
):
    record = db.query(RecordModel).filter(
        RecordModel.record_id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún registro con id={record_id}"
        )

    update_data = record_in.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(record, campo, valor)

    db.commit()
    db.refresh(record)
    return record


# ══════════════════════════════════════════════════════════════
# DELETE /api/v1/climas/{record_id}
# ══════════════════════════════════════════════════════════════
@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar medición",
)
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    record = db.query(RecordModel).filter(
        RecordModel.record_id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún registro con id={record_id}"
        )

    db.delete(record)
    db.commit()