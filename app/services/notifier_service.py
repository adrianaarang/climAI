import os
import httpx
# Importamos tus funciones de log personalizadas
from app.services.logging_service import log_info, log_error, log_critical

class NotifierService:
    def __init__(self):
        # Se cargan desde el .env a través de Docker
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"

    async def send_telegram_message(self, chat_id: str, message: str):
        """
        Envía un mensaje a Telegram y registra el resultado en tus logs.
        """
        if not self.telegram_token:
            log_error("TELEGRAM_TOKEN no configurado. No se pudo enviar la alerta.")
            return

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                # Usamos tu función log_info
                log_info(f"Mensaje enviado a Telegram correctamente al chat {chat_id}")
        except Exception as e:
            # Usamos tu función log_error
            log_error(f"Fallo al contactar con la API de Telegram: {e}")

    async def notify_critical_alert(self, chat_id: str, city: str, temp: float, alert_type: str):
        """
        Estructura el mensaje para alertas ROJAS y registra el evento crítico.
        """
        # Si es una alerta ROJA, lo registramos como CRITICAL en tu log_file
        log_critical(f"PROCESANDO ALERTA MÁXIMA: {alert_type} en {city}")

        emoji = "🔴"
        mensaje = (
            f"{emoji} <b>ALERTA CRÍTICA: {alert_type}</b> {emoji}\n\n"
            f"Ubicación: <b>{city}</b>\n"
            f"Valor registrado: <b>{temp}</b>\n\n"
            f"<i>Acción requerida: Máxima precaución.</i>"
        )
        
        await self.send_telegram_message(chat_id, mensaje)

# Instancia lista para importar
notifier_service = NotifierService()