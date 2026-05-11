import os
import math
import httpx
import json
import asyncio
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import Province, Station, Record

AEMET_BASE    = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class WeatherAPIService:
    def __init__(self, db: AsyncSession):
        self.api_key = os.getenv("AEMET_API_KEY")
        self.headers = {"api_key": self.api_key, "cache-control": "no-cache"}
        self.db = db

    async def obtener_clima_por_coordenadas(self, lat: float, lon: float) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:

            # --- PASO 1: Geocodificación inversa con Nominatim ---
            p_name_search = "madrid"
            try:
                res_geo = await client.get(
                    NOMINATIM_URL,
                    params={"lat": lat, "lon": lon, "format": "json", "zoom": 6},
                    headers={"User-Agent": "climAI/1.0"},
                )
                if res_geo.status_code == 200:
                    addr = res_geo.json().get("address", {})
                    p_name_search = (addr.get("province") or addr.get("state") or "madrid").lower()
                    print(f"[weather_service] Provincia detectada: {p_name_search}")
            except Exception as e:
                print(f"[weather_service] Nominatim falló, usando Madrid: {e}")

            # --- PASO 2: Buscar provincia en BD ---
            try:
                stmt_prov = select(Province).where(Province.name.ilike(f"%{p_name_search}%"))
                provincia_db = (await self.db.execute(stmt_prov)).scalar_one_or_none()

                if not provincia_db:
                    print(f"[weather_service] '{p_name_search}' no en BD, usando Madrid")
                    stmt_prov = select(Province).where(Province.name.ilike("%madrid%"))
                    provincia_db = (await self.db.execute(stmt_prov)).scalar_one_or_none()

                if not provincia_db:
                    print("[weather_service] ERROR: tabla provinces vacía")
                    return None
            except Exception as e:
                print(f"[weather_service] Error BD provincias: {e}")
                return None

            # --- PASO 3: Obtener observaciones de AEMET ---
            print(f"[weather_service] API KEY presente: {bool(self.api_key)}")
            observaciones = None
            for intento in range(3):
                try:
                    r_meta = await client.get(AEMET_BASE, headers=self.headers)
                    print(f"[weather_service] AEMET meta status: {r_meta.status_code}")
                    meta_json = r_meta.json()
                    print(f"[weather_service] AEMET meta: {meta_json}")

                    url_datos = meta_json.get("datos")
                    if not url_datos:
                        print(f"[weather_service] Sin URL de datos (intento {intento+1})")
                        await asyncio.sleep(1)
                        continue

                    await asyncio.sleep(0.2)
                    r_datos = await client.get(url_datos)
                    print(f"[weather_service] AEMET datos status: {r_datos.status_code}, bytes: {len(r_datos.content)}")

                    if r_datos.content:
                        observaciones = json.loads(r_datos.content.decode("latin-1", errors="replace"))
                        print(f"[weather_service] Observaciones recibidas: {len(observaciones)}")
                        break
                except Exception as e:
                    print(f"[weather_service] Error AEMET intento {intento+1}: {e}")
                    await asyncio.sleep(1)

            if not observaciones:
                print("[weather_service] ERROR: No se obtuvieron observaciones de AEMET")
                return None

            # --- PASO 4: Estación más cercana ---
            est_aemet, dist_min = None, float("inf")
            for obs in observaciones:
                try:
                    d = calcular_distancia(lat, lon, float(obs["lat"]), float(obs["lon"]))
                    if d < dist_min:
                        dist_min, est_aemet = d, obs
                except Exception:
                    continue

            if not est_aemet:
                print("[weather_service] ERROR: No se encontró estación cercana")
                return None

            idema_actual = est_aemet["idema"]
            print(f"[weather_service] Estación: {idema_actual} — {est_aemet.get('ubi')} ({dist_min:.1f} km)")

            # --- PASO 5: Registrar estación en BD si es nueva ---
            try:
                stmt_st = select(Station).where(Station.idema == idema_actual)
                estacion_db = (await self.db.execute(stmt_st)).scalar_one_or_none()

                if not estacion_db:
                    estacion_db = Station(
                        idema=idema_actual,
                        name=est_aemet.get("ubi", "Desconocida"),
                        latitude=float(est_aemet["lat"]),
                        longitude=float(est_aemet["lon"]),
                        province_id=provincia_db.province_id,
                    )
                    self.db.add(estacion_db)
                    await self.db.flush()
                    print(f"[weather_service] Nueva estación guardada: {idema_actual}")
            except Exception as e:
                print(f"[weather_service] Error guardando estación: {e}")
                await self.db.rollback()
                return None

            # --- PASO 6: Guardar registro actual ---
            try:
                nuevo_registro = Record(
                    timestamp=datetime.now(),
                    temperature=float(est_aemet.get("ta") or 0),
                    humidity=float(est_aemet.get("hr") or 0),
                    wind=float(est_aemet.get("vv") or 0),
                    rain=float(est_aemet.get("prec") or 0.0),
                    station_id=estacion_db.station_id,
                )
                self.db.add(nuevo_registro)
                await self.db.commit()
                print(f"[weather_service] Registro guardado — {nuevo_registro.temperature}°C")
            except Exception as e:
                print(f"[weather_service] Error guardando registro: {e}")
                await self.db.rollback()
                return None

            # --- PASO 7: Histórico para las gráficas ---
            # Claves en inglés para que coincidan con index.js
            regs_estacion = [o for o in observaciones if o.get("idema") == idema_actual]
            regs_estacion.sort(key=lambda x: x.get("fint", ""))

            hist_data = {"horas": [], "temperature": [], "humidity": [], "precipitation": []}
            for r in regs_estacion[-24:]:
                fint = r.get("fint", "")
                hora_label = fint.split("T")[-1][:5] if "T" in fint else "--"
                hist_data["horas"].append(hora_label)
                hist_data["temperature"].append(float(r.get("ta") or r.get("temp") or 0))
                hist_data["humidity"].append(float(r.get("hr") or 0))
                hist_data["precipitation"].append(float(r.get("prec") or 0.0))

            # --- PASO 8: Respuesta final ---
            return {
                "temperatura":     nuevo_registro.temperature,
                "humedad":         nuevo_registro.humidity,
                "viento":          nuevo_registro.wind,
                "precipitacion":   nuevo_registro.rain,
                "estacion_nombre": estacion_db.name,
                "ciudad_buscada":  provincia_db.name,
                "es_noche":        datetime.now().hour < 7 or datetime.now().hour > 21,
                "historico":       hist_data,
            }


async def obtener_clima_cercano(lat: float, lon: float, db: AsyncSession) -> Optional[dict]:
    service = WeatherAPIService(db)
    return await service.obtener_clima_por_coordenadas(lat, lon)