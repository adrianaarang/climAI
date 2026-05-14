from typing import Dict, Any, List
import asyncio  # <--- NUEVO: Para enviar el mensaje sin bloquear la app

# 1. Importamos el validador de pydatntic que tenemos en schemas
from app.schemas.registro import RecordCreate
from pydantic import ValidationError

# 2. Importamos funciones de logging personalizadas y el nuevo notificador
from app.services.logging_service import log_error, log_warning, log_info
from app.services.notifier_service import notifier_service  # <--- NUEVO

class AlertService:
    """Motor de análisis de riesgos climáticos y generación de alertas."""

    def evaluar_alertas(self, registro_normalizado: Dict[str, Any]) -> List[str]:
        """
        Analiza los datos meteorológicos usando la validación de RecordCreate
        y registra cualquier anomalía en el sistema de logs.
        """
        
        # --- VALIDACIÓN REAL CON PYDANTIC ---
        try:
            # Usamos el esquema oficial para validar rangos (temp -50 a 60, etc.)
            RecordCreate(**registro_normalizado)
        except (ValidationError, TypeError, ValueError) as e:
            # Usamos función de log_error para guardar el fallo en logs
            log_error(f"Validación fallida en AlertService: {e}")
            return []

        alertas = []

        # --- EXTRACCIÓN DE DATOS ---
        try:
            # Extraemos datos usando las claves en inglés del RecordBase
            temp = float(registro_normalizado.get("temperature", 0.0))
            lluvia = float(registro_normalizado.get("rain", 0.0))
            humedad = float(registro_normalizado.get("humidity", 0.0))
            viento = float(registro_normalizado.get("wind", 0.0)) 

        except (TypeError, ValueError) as e:
            log_error(f"Error de formato numérico en AlertService: {e}")
            return []

        # --- LÓGICA DE UMBRALES DE RIESGO ---
        
        # TEMPERATURA
        if temp >= 40.0:
            alertas.append("ROJA_CALOR")
        elif temp >= 35.0:
            alertas.append("NARANJA_CALOR")
        elif temp <= -5.0:
            alertas.append("ROJA_FRIO")
        elif temp <= 0.0:
            alertas.append("NARANJA_FRIO")

        # VIENTO
        if viento > 70.0:
            alertas.append("ROJA_VIENTO")
        elif viento > 40.0:
            alertas.append("NARANJA_VIENTO")

        # LLUVIA
        if lluvia > 30.0:
            alertas.append("ROJA_LLUVIA")
        elif lluvia > 10.0:
            alertas.append("NARANJA_LLUVIA")

        # HUMEDAD
        if humedad >= 90:
            alertas.append("NARANJA_HUMEDAD")

        # --- CONEXIÓN CON TELEGRAM (La parte nueva) ---
        for alerta in alertas:
            if "ROJA" in alerta:
                if chat_id:
                    # Ordenamos al mensajero que envíe la alerta roja
                    asyncio.create_task(
                        notifier_service.notify_critical_alert(
                            chat_id=chat_id,
                            city=ciudad,
                            temp=temp,
                            alert_type=alerta
                        )
                    )
                else:
                    log_warning(f"Alerta {alerta} detectada pero no hay telegram_chat_id.")

        # --- RESULTADO FINAL ---
        if not alertas:
            alertas.append("VERDE")
        else:
            # Opcional: Registrar que se han generado alertas
            log_info(f"Alertas generadas para el registro: {alertas}")

        return alertas
    