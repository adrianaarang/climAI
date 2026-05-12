import os
import math
import httpx
import json
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import Province, Station, Record
from app.services.weather_ai_service import WeatherAIService

# Configuración de logs para producción
logger = logging.getLogger(__name__)

AEMET_BASE = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

class WeatherAPIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = os.getenv("AEMET_API_KEY")
        self.headers = {"api_key": self.api_key, "cache-control": "no-cache"}
        # Inicializamos el servicio de IA
        self.ai = WeatherAIService()

    async def obtener_clima_por_coordenadas(self, lat: float, lon: float) -> Optional[dict]:
        """
        Orquestador principal: Geolocaliza, consulta AEMET, 
        persiste en BD y genera predicción IA.
        """
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            try:
                # 1. Localización
                p_name = await self._get_province_name(client, lat, lon)
                provincia_db = await self._get_province_from_db(p_name)
                
                if not provincia_db:
                    logger.error("Error crítico: No hay provincias cargadas en la BD.")
                    return None

                # 2. Datos de AEMET
                observaciones = await self._fetch_aemet_data(client)
                if not observaciones:
                    return None

                # 3. Estación más cercana
                est_aemet, dist = self._find_nearest_station(lat, lon, observaciones)
                if not est_aemet:
                    return None

                # 4. Persistencia (Estación y Registro)
                estacion_db = await self._ensure_station_exists(est_aemet, provincia_db.province_id)
                nuevo_registro = await self._save_record(est_aemet, estacion_db.station_id)
                
                if not nuevo_registro:
                    return None

                # 5. Predicción IA
                pronostico = self.ai.obtener_prediccion(
                    temp=nuevo_registro.temperature,
                    humedad=nuevo_registro.humidity
                )

                # 6. Preparar Histórico y Respuesta
                hist_data = self._format_history(observaciones, est_aemet["idema"])

                return {
                    "temperatura": nuevo_registro.temperature,
                    "humedad": nuevo_registro.humidity,
                    "viento": nuevo_registro.wind,
                    "precipitacion": nuevo_registro.rain,
                    "estacion_nombre": estacion_db.name,
                    "ciudad_buscada": provincia_db.name,
                    "es_noche": not (7 <= datetime.now().hour <= 21),
                    "pronostico_ia": pronostico,
                    "historico": hist_data,
                }

            except Exception as e:
                logger.exception(f"Fallo inesperado en WeatherAPIService: {e}")
                return None

    # --- MÉTODOS PRIVADOS DE APOYO ---

    async def _get_province_name(self, client: httpx.AsyncClient, lat: float, lon: float) -> str:
        try:
            res = await client.get(
                NOMINATIM_URL,
                params={"lat": lat, "lon": lon, "format": "json", "zoom": 6},
                headers={"User-Agent": "climAI/1.0"}
            )
            if res.status_code == 200:
                addr = res.json().get("address", {})
                return (addr.get("province") or addr.get("state") or "madrid").lower()
        except Exception as e:
            logger.warning(f"Nominatim falló, usando fallback: {e}")
        return "madrid"

    async def _get_province_from_db(self, name: str) -> Optional[Province]:
        stmt = select(Province).where(Province.name.ilike(f"%{name}%"))
        result = await self.db.execute(stmt)
        prov = result.scalar_one_or_none()
        if not prov and name != "madrid":
            return await self._get_province_from_db("madrid")
        return prov

    async def _fetch_aemet_data(self, client: httpx.AsyncClient) -> Optional[List[Dict]]:
        for intento in range(3):
            try:
                r_meta = await client.get(AEMET_BASE, headers=self.headers)
                r_meta.raise_for_status()
                url_datos = r_meta.json().get("datos")

                if url_datos:
                    await asyncio.sleep(0.5) # Respetar rate limit
                    r_datos = await client.get(url_datos)
                    return json.loads(r_datos.content.decode("latin-1", errors="replace"))
            except Exception as e:
                logger.warning(f"Reintento AEMET {intento+1}/3 debido a: {e}")
                await asyncio.sleep(1)
        return None

    def _find_nearest_station(self, lat: float, lon: float, obs: List[Dict]) -> tuple:
        est_min, dist_min = None, float("inf")
        for o in obs:
            try:
                d = self._calcular_distancia(lat, lon, float(o["lat"]), float(o["lon"]))
                if d < dist_min:
                    dist_min, est_min = d, o
            except: continue
        return est_min, dist_min

    def _calcular_distancia(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    async def _ensure_station_exists(self, est: Dict, prov_id: int) -> Station:
        idema = est["idema"]
        stmt = select(Station).where(Station.idema == idema)
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

    async def _save_record(self, est: Dict, station_id: int) -> Optional[Record]:
        try:
            nuevo = Record(
                timestamp=datetime.now(),
                temperature=float(est.get("ta") or 0),
                humidity=float(est.get("hr") or 0),
                wind=float(est.get("vv") or 0),
                rain=float(est.get("prec") or 0.0),
                station_id=station_id
            )
            self.db.add(nuevo)
            await self.db.commit()
            return nuevo
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al guardar registro: {e}")
            return None

    def _format_history(self, observaciones: List[Dict], idema: str) -> Dict:
        regs = [o for o in observaciones if o.get("idema") == idema]
        regs.sort(key=lambda x: x.get("fint", ""))
        
        hist = {"horas": [], "temperature": [], "humidity": [], "precipitation": []}
        for r in regs[-24:]:
            fint = r.get("fint", "")
            hist["horas"].append(fint.split("T")[-1][:5] if "T" in fint else "--")
            hist["temperature"].append(float(r.get("ta") or r.get("temp") or 0))
            hist["humidity"].append(float(r.get("hr") or 0))
            hist["precipitation"].append(float(r.get("prec") or 0.0))
        return hist

# Función de entrada
async def obtener_clima_cercano(lat: float, lon: float, db: AsyncSession) -> Optional[dict]:
    service = WeatherAPIService(db)
    return await service.obtener_clima_por_coordenadas(lat, lon)