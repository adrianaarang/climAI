# app/schemas/registro.py
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
import math


# ── Schema base compartido ──────────────────────────────────────
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Schemas de ESTACIONES (necesarios para mostrar info) ────────
class StationBase(BaseModel):
    idema: str
    name: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    province_id: int

class StationCreate(StationBase):
    pass

class Station(StationBase, BaseSchema):
    station_id: int


# ── Schemas de REGISTROS (tu responsabilidad principal) ─────────

class RecordBase(BaseModel):
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rain: Optional[float] = None
    station_id: int

    # Validación: temperatura dentro de límites físicos reales
    @field_validator("temperature")
    @classmethod
    def temperatura_valida(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if math.isnan(v) or math.isinf(v):
            raise ValueError("La temperatura no puede ser NaN o infinito")
        if v < -50.0 or v > 60.0:
            raise ValueError("Temperatura fuera de rango físico (-50 a 60°C)")
        return round(v, 2)

    # Validación: humedad entre 0 y 100
    @field_validator("humidity")
    @classmethod
    def humedad_valida(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0.0 or v > 100.0:
            raise ValueError("Humedad debe estar entre 0 y 100%")
        return round(v, 2)

    # Validación: lluvia no puede ser negativa
    @field_validator("rain")
    @classmethod
    def lluvia_valida(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0.0:
            raise ValueError("La lluvia no puede ser negativa")
        return round(v, 2)


# ── ENTRADA: lo que el cliente envía al crear ───────────────────
class RecordCreate(RecordBase):
    pass


# ── ACTUALIZACIÓN: campos opcionales ───────────────────────────
class RecordUpdate(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rain: Optional[float] = None


# ── SALIDA: lo que el servidor devuelve ─────────────────────────
class Record(RecordBase, BaseSchema):
    record_id: int


# ── SALIDA con datos de estación incluidos ──────────────────────
# Útil para cuando el cliente quiere ver el nombre de la estación
# sin hacer una segunda petición
class RecordWithStation(Record):
    station: Optional[Station] = None