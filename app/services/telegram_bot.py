import os
import asyncio
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.database import User
from app.services.logging_service import log_info, log_error

async def procesar_mensajes_telegram():
    """
    Revisa si alguien ha enviado un código de vinculación al bot.
    """
    token = os.getenv("TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            data = response.json()
            
            if not data.get("ok"):
                return

            for result in data.get("result", []):
                chat_id = result["message"]["chat"]["id"]
                texto = result["message"]["text"].strip().upper()
                
                # Buscamos en la DB si algún usuario tiene este token
                async for db in get_db():
                    query = select(User).where(User.telegram_sync_token == texto)
                    result_db = await db.execute(query)
                    user = result_db.scalar_one_or_none()
                    
                    if user:
                        user.telegram_id = str(chat_id)
                        user.telegram_sync_token = None # Borramos el token una vez usado
                        await db.commit()
                        log_info(f"Usuario {user.email} vinculado a Telegram con éxito.")
                        
        except Exception as e:
            log_error(f"Error al procesar mensajes de Telegram: {e}")