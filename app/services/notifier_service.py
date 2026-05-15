# app/services/notifier_service.py
import os
import httpx
from typing import List, Dict, Any

from app.services.logging_service import log_error, log_info


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Emojis y etiquetas por tipo de alerta
ALERT_META = {
    "ROJA_CALOR":     {"emoji": "🔴🌡️", "texto": "Calor extremo"},
    "NARANJA_CALOR":  {"emoji": "🟠🌡️", "texto": "Calor intenso"},
    "ROJA_FRIO":      {"emoji": "🔴❄️",  "texto": "Frío extremo"},
    "NARANJA_FRIO":   {"emoji": "🟠❄️",  "texto": "Frío intenso"},
    "ROJA_VIENTO":    {"emoji": "🔴💨",  "texto": "Viento muy fuerte"},
    "NARANJA_VIENTO": {"emoji": "🟠💨",  "texto": "Viento fuerte"},
    "ROJA_LLUVIA":    {"emoji": "🔴🌧️", "texto": "Lluvia torrencial"},
    "NARANJA_LLUVIA": {"emoji": "🟠🌧️", "texto": "Lluvia intensa"},
    "NARANJA_HUMEDAD":{"emoji": "🟠💧",  "texto": "Humedad muy alta"},
    "VERDE":          {"emoji": "🟢✅",  "texto": "Sin alertas"},
}


class NotifierService:
    """Gestiona el envío de notificaciones vía Telegram."""

    async def enviar_alerta(
        self,
        telegram_id: str,
        estacion: str,
        alertas: List[str],
        datos_meteo: Dict[str, Any] = None,
    ) -> bool:
        """Envía un mensaje de alerta formateado a un usuario de Telegram."""
        if not TELEGRAM_BOT_TOKEN:
            log_error("TELEGRAM_BOT_TOKEN no configurado en .env")
            return False

        mensaje = self._formatear_mensaje(estacion, alertas, datos_meteo)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{TELEGRAM_API_URL}/sendMessage",
                    json={
                        "chat_id": telegram_id,
                        "text": mensaje,
                        "parse_mode": "HTML",
                    },
                )
                if resp.status_code == 200:
                    log_info(f"Notificación Telegram enviada a {telegram_id}")
                    return True
                else:
                    log_error(f"Error Telegram API: {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            log_error(f"Excepción al enviar Telegram: {e}")
            return False

    async def enviar_mensaje_simple(self, telegram_id: str, texto: str) -> bool:
        """Envía un mensaje de texto simple."""
        if not TELEGRAM_BOT_TOKEN:
            return False
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{TELEGRAM_API_URL}/sendMessage",
                    json={"chat_id": telegram_id, "text": texto, "parse_mode": "HTML"},
                )
                return resp.status_code == 200
        except Exception as e:
            log_error(f"Error envío simple Telegram: {e}")
            return False

    def _formatear_mensaje(
        self,
        estacion: str,
        alertas: List[str],
        datos: Dict[str, Any] = None,
    ) -> str:
        """Construye el mensaje HTML para Telegram."""
        lineas = [f"⚠️ <b>ALERTA CLIMÁTICA — ClimAI</b>", f"📍 Estación: <b>{estacion}</b>", ""]

        for alerta in alertas:
            meta = ALERT_META.get(alerta, {"emoji": "⚠️", "texto": alerta})
            lineas.append(f"{meta['emoji']} {meta['texto']}")

        if datos:
            lineas.append("")
            lineas.append("📊 <b>Datos actuales:</b>")
            if datos.get("temperatura") is not None:
                lineas.append(f"  🌡️ Temperatura: <b>{datos['temperatura']}°C</b>")
            if datos.get("viento") is not None:
                lineas.append(f"  💨 Viento: <b>{datos['viento']} km/h</b>")
            if datos.get("lluvia") is not None:
                lineas.append(f"  🌧️ Lluvia: <b>{datos['lluvia']} mm</b>")
            if datos.get("humedad") is not None:
                lineas.append(f"  💧 Humedad: <b>{datos['humedad']}%</b>")

        lineas.append("")
        lineas.append("🤖 <i>Generado automáticamente por ClimAI</i>")
        return "\n".join(lineas)