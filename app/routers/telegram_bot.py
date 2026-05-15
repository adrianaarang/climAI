# app/routers/telegram_bot.py
import os
import httpx
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.database import User
from app.routers.auth import obtener_usuario_actual

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


@router.post("/webhook")
async def telegram_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        message = data.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        texto   = message.get("text", "").strip()

        if not chat_id or not texto:
            return {"ok": True}

        if texto.startswith("CLIM-"):
            try:
                user_id = int(texto.replace("CLIM-", ""))
            except ValueError:
                await _responder(chat_id, "❌ Código inválido. Cópialo exactamente desde ClimAI.")
                return {"ok": True}

            result = await db.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                await _responder(chat_id, "❌ No encontré ningún usuario con ese código.")
                return {"ok": True}

            user.telegram_id = chat_id
            await db.commit()
            await _responder(chat_id, f"✅ ¡Cuenta vinculada!\n📧 {user.email}")

        elif texto in ("/start", "start"):
            await _responder(chat_id, "👋 ¡Bienvenido a ClimAI!\nEnvíame tu código CLIM-123 para vincular tu cuenta.")
        else:
            await _responder(chat_id, "Envíame tu código de vinculación (formato CLIM-123).")

    except Exception as e:
        print(f"[telegram webhook] Error: {e}")

    return {"ok": True}


@router.post("/vincular-manual")
async def vincular_manual(datos: dict, request: Request, db: AsyncSession = Depends(get_db)):
    user_email = obtener_usuario_actual(request)
    if not user_email:
        return {"status": "error", "message": "No autenticado"}

    chat_id = str(datos.get("chat_id", "")).strip()
    if not chat_id:
        return {"status": "error", "message": "chat_id requerido"}

    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    if not user:
        return {"status": "error", "message": "Usuario no encontrado"}

    user.telegram_id = chat_id
    await db.commit()

    await _responder(chat_id, f"✅ Cuenta ClimAI vinculada correctamente.\n📧 {user_email}")
    return {"status": "ok", "message": "Telegram vinculado"}


@router.post("/desvincular")
async def desvincular(request: Request, db: AsyncSession = Depends(get_db)):
    user_email = obtener_usuario_actual(request)
    if not user_email:
        return {"status": "error", "message": "No autenticado"}

    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    if not user:
        return {"status": "error", "message": "Usuario no encontrado"}

    user.telegram_id = None
    await db.commit()
    return {"status": "ok", "message": "Telegram desvinculado"}


@router.get("/estado")
async def estado_vinculacion(request: Request, db: AsyncSession = Depends(get_db)):
    user_email = obtener_usuario_actual(request)
    if not user_email:
        return {"vinculado": False}

    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    return {
        "vinculado": bool(user and user.telegram_id),
        "telegram_id": user.telegram_id if user else None,
    }


async def _responder(chat_id: str, texto: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"},
            )
    except Exception as e:
        print(f"[telegram] Error: {e}")