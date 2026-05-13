# app/routers/views.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.database import User
from app.routers.auth import obtener_usuario_actual

router = APIRouter(tags=["vistas"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def vista_index(request: Request):
    user = obtener_usuario_actual(request)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"usuario": user}
    )


@router.get("/weather-province", response_class=HTMLResponse)
async def vista_provincias(request: Request):
    user = obtener_usuario_actual(request)
    return templates.TemplateResponse(
        request=request, name="weather_province.html", context={"usuario": user}
    )


@router.get("/alertas", response_class=HTMLResponse)
async def vista_alertas(request: Request):
    user = obtener_usuario_actual(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request, name="alertas.html", context={"usuario": user}
    )


@router.get("/prediccion", response_class=HTMLResponse)
async def vista_prediccion(request: Request):
    user = obtener_usuario_actual(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request, name="prediccion_ia.html", context={"usuario": user}
    )


@router.get("/configurar-telegram", response_class=HTMLResponse)
async def vista_telegram(request: Request, db: AsyncSession = Depends(get_db)):
    user_email = obtener_usuario_actual(request)
    if not user_email:
        return RedirectResponse(url="/login")

    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    return templates.TemplateResponse(
        request=request, name="vincular_telegram.html",
        context={
            "usuario":        user.email,
            "telegram_token": user.telegram_id or f"CLIM-{user.user_id}",
            "telegram_linked": bool(user.telegram_id),
        }
    )