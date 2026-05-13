import os
import logging
import httpx
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import Province, Station, Record
from app.services.geo_utils import get_province_name
from app.services.alert_service import AlertService
from app.services.aemet_client import (
    fetch_observaciones,
    find_nearest_station,
    format_history,
    fetch_pronostico_dias,
)

logger = logging.getLogger(__name__)


class WeatherAPIService:
    """
    Orquestador principal — coordina geo_utils, aemet_client, alert_service y la BD.
    No contiene lógica de negocio propia, solo une las piezas.
    """

    def __init__(self, db: AsyncSession):
        self.db            = db
        self.api_key       = os.getenv("AEMET_API_KEY")
        self.headers       = {"api_key": self.api_key, "cache-control": "no-cache"}
        self.alert_service = AlertService()  # Evalúa si los datos actuales generan alertas

    async def obtener_clima_por_coordenadas(self, lat: float, lon: float) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            try:
                # PASO 1: provincia por coordenadas (Nominatim)
                p_name = await get_province_name(client, lat, lon)

                # PASO 2: provincia en BD
                provincia_db = await self._get_province_from_db(p_name)
                if not provincia_db:
                    logger.error("No hay provincias cargadas en la BD.")
                    return None

                # PASO 3: observaciones AEMET
                observaciones = await fetch_observaciones(client, self.headers)
                if not observaciones:
                    return None

                # PASO 4: estación más cercana
                est_aemet, _ = find_nearest_station(lat, lon, observaciones)
                if not est_aemet:
                    return None

                # PASO 5: guardar estación en BD
                estacion_db = await self._ensure_station_exists(est_aemet, provincia_db.province_id)

                # PASO 6: guardar registro actual
                nuevo_registro = await self._save_record(est_aemet, estacion_db.station_id)
                if not nuevo_registro:
                    return None

                # PASO 7: pronóstico 5 días por municipio
                pronostico_dias = await fetch_pronostico_dias(client, self.headers, lat, lon)

                # PASO 8: histórico 24h para la gráfica del index
                historico = format_history(observaciones, est_aemet["idema"])

                # PASO 9: evaluar si los datos actuales disparan alguna alerta
                # evaluar_alertas recibe el registro y devuelve una lista de alertas activas
                alertas = self.alert_service.evaluar_alertas(nuevo_registro)

                return {
                    "temperatura":     nuevo_registro.temperature,
                    "humedad":         nuevo_registro.humidity,
                    "viento":          nuevo_registro.wind,
                    "precipitacion":   nuevo_registro.rain,
                    "estacion_nombre": estacion_db.name,
                    "ciudad_buscada":  provincia_db.name,
                    "es_noche":        not (7 <= datetime.now().hour <= 21),
                    "pronostico_dias": pronostico_dias,
                    "historico":       historico,
                    "alertas":         alertas,
                }

            except Exception as e:
                logger.exception(f"Fallo inesperado: {e}")
                return None

    # -------------------------------------------------------------------------
    # MÉTODOS PRIVADOS — solo BD, la lógica AEMET está en aemet_client.py
    # -------------------------------------------------------------------------

    async def _get_province_from_db(self, name: str) -> Optional[Province]:
        """
        Busca una provincia en la BD por nombre (búsqueda parcial).
        Si no la encuentra usa 'madrid' como fallback.
        """
        stmt   = select(Province).where(Province.name.ilike(f"%{name}%"))
        result = await self.db.execute(stmt)
        prov   = result.scalar_one_or_none()

        if not prov and name != "madrid":
            logger.warning(f"No se encontró '{name}', usando Madrid.")
            return await self._get_province_from_db("madrid")

        if not prov:
            logger.error("No se encontró la provincia (ni Madrid).")
        return prov

    async def _ensure_station_exists(self, est: dict, prov_id: int) -> Station:
        """
        Comprueba si la estación ya existe en BD por su código idema.
        Si no existe la crea. Patrón 'get or create'.
        """
        idema  = est["idema"]
        stmt   = select(Station).where(Station.idema == idema)
        result = await self.db.execute(stmt)
        estacion_db = result.scalar_one_or_none()

        if not estacion_db:
            estacion_db = Station(
                idema=idema,
                name=est.get("ubi", "Desconocida"),
                latitude=float(est["lat"]),
                longitude=float(est["lon"]),
                province_id=prov_id
            )
            self.db.add(estacion_db)
            await self.db.flush()
        return estacion_db

    async def _save_record(self, est: dict, station_id: int) -> Optional[Record]:
        """
        Guarda el registro meteorológico actual en BD.
        Si falla hace rollback para no dejar la BD en estado inconsistente.
        """
        try:
            nuevo = Record(
                timestamp=datetime.now(),
                temperature=float(est.get("ta")   or 0),
                humidity=   float(est.get("hr")   or 0),
                wind=       float(est.get("vv")   or 0),
                rain=       float(est.get("prec") or 0.0),
                station_id=station_id
            )
            self.db.add(nuevo)
            await self.db.commit()
            return nuevo
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al guardar registro: {e}")
            return None


# Función pública que usan los routers y el main
async def obtener_clima_cercano(lat: float, lon: float, db: AsyncSession) -> Optional[dict]:
    service = WeatherAPIService(db)
    return await service.obtener_clima_por_coordenadas(lat, lon)
