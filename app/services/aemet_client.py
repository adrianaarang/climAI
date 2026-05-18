import httpx
import json
import asyncio
import logging
from typing import Optional, List, Dict


from app.services.geo_utils import calcular_distancia, parse_coord_aemet

logger = logging.getLogger(__name__)

AEMET_BASE       = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
AEMET_MUNICIPIOS = "https://opendata.aemet.es/opendata/api/maestro/municipios"
AEMET_PREDICCION = "https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{cod}"


async def fetch_observaciones(client: httpx.AsyncClient, headers: dict) -> Optional[List[Dict]]:
    """
    Descarga todas las observaciones de AEMET en tiempo real.
    AEMET responde con una URL intermedia — hay que hacer dos peticiones.
    Reintenta hasta 3 veces con backoff exponencial si hay error.
    """
    for intento in range(3):
        try:
            r_meta = await client.get(AEMET_BASE, headers=headers)
            r_meta.raise_for_status()
            url_datos = r_meta.json().get("datos")

            if url_datos:
                await asyncio.sleep(0.5)
                # FIX: la segunda petición también necesita headers con la api_key
                r_datos = await client.get(url_datos, headers=headers)
                r_datos.raise_for_status()
                return json.loads(r_datos.content.decode("latin-1", errors="replace"))

            logger.warning(f"Reintento AEMET {intento+1}/3: la respuesta no contiene 'datos'")

        except Exception as e:
            # FIX: repr() muestra el tipo y el mensaje aunque str(e) esté vacío
            logger.warning(f"Reintento AEMET {intento+1}/3: {type(e).__name__}: {e!r}")

        # Backoff exponencial: 1s, 2s, 4s
        await asyncio.sleep(2 ** intento)

    return None


def find_nearest_station(lat: float, lon: float, obs: List[Dict]) -> tuple:
    """Devuelve la estación más cercana y su distancia en km."""
    est_min, dist_min = None, float("inf")
    for o in obs:
        try:
            d = calcular_distancia(lat, lon, float(o["lat"]), float(o["lon"]))
            if d < dist_min:
                dist_min, est_min = d, o
        except Exception:
            continue
    return est_min, dist_min


def format_history(observaciones: List[Dict], idema: str) -> Dict:
    """
    Filtra las obs de nuestra estación y devuelve las últimas 24h
    formateadas para la gráfica del index.
    """
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


async def fetch_pronostico_dias(client: httpx.AsyncClient, headers: dict, lat: float, lon: float) -> list:
    """
    Busca el municipio más cercano y devuelve el pronóstico de los próximos 5 días.
    Si falla en cualquier punto devuelve [] sin romper el servicio principal.
    """
    try:
        r = await client.get(AEMET_MUNICIPIOS, headers=headers)
        r.raise_for_status()

        url_municipios = r.json().get("datos")
        if not url_municipios:
            logger.warning("AEMET no devolvió URL de municipios")
            return []

        await asyncio.sleep(0.3)
        r_lista = await client.get(url_municipios, headers=headers)
        r_lista.raise_for_status()
        lista   = json.loads(r_lista.content.decode("latin-1", errors="replace"))
        logger.info(f"Municipios descargados: {len(lista)}")

        cercano = min(lista, key=lambda m: calcular_distancia(
            lat, lon,
            parse_coord_aemet(m.get("latitud",  "0")),
            parse_coord_aemet(m.get("longitud", "0")),
        ))
        logger.info(f"Municipio más cercano: {cercano.get('nombre')} ({cercano.get('id')})")

        cod = cercano["id"].replace("id", "")

        r2 = await client.get(AEMET_PREDICCION.format(cod=cod), headers=headers)
        r2.raise_for_status()

        url_pred = r2.json().get("datos")
        if not url_pred:
            logger.warning(f"AEMET no devolvió URL de predicción para {cod}")
            return []

        await asyncio.sleep(0.5)
        r3   = await client.get(url_pred, headers=headers)
        r3.raise_for_status()
        pred = json.loads(r3.content.decode("latin-1", errors="replace"))

        dias = pred[0]["prediccion"]["dia"]
        logger.info(f"Días de pronóstico recibidos: {len(dias)}")

        return [
            {
                "fecha":       d.get("fecha", "")[:10],
                "temp_max":    d.get("temperatura", {}).get("maxima", "—"),
                "temp_min":    d.get("temperatura", {}).get("minima", "—"),
                "prob_lluvia": d.get("probPrecipitacion", [{}])[0].get("value", 0),
                "estado":      d.get("estadoCielo", [{}])[0].get("descripcion", ""),
            }
            for d in dias[:5]
        ]

    except Exception as e:
        logger.warning(f"Error obteniendo pronóstico municipal: {type(e).__name__}: {e!r}")
        return []