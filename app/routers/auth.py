import os
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.database import User

# Configuramos el router y los templates
router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="app/templates")

# Helper para leer la cookie
def obtener_usuario_actual(request: Request):
    return request.cookies.get("usuario_login")

# --- RUTAS DE LOGIN ---

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "usuario": None})

@router.post("/login")
async def login_process(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user and user.password == password:
            response = RedirectResponse(url="/", status_code=303)
            response.set_cookie(key="usuario_login", value=user.email)
            return response

        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email o contraseña incorrectos",
            "usuario": None,
        })
    except Exception as e:
        print(f"Error en Login: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Error interno del servidor",
            "usuario": None,
        })

# --- RUTAS DE REGISTRO ---

@router.get("/registro_usuario", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("registro_usuario.html", {"request": request, "usuario": None})

@router.post("/registro_usuario")
async def register_process(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    if password != confirm_password:
        return templates.TemplateResponse("registro_usuario.html", {
            "request": request,
            "error": "Las contraseñas no coinciden"
        })

    try:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            return templates.TemplateResponse("registro_usuario.html", {
                "request": request,
                "error": "El email ya está registrado"
            })

        nuevo_usuario = User(email=email, password=password)
        db.add(nuevo_usuario)
        await db.commit()
        return RedirectResponse(url="/login", status_code=303)

    except Exception as e:
        await db.rollback()
        print(f"Error DB: {e}")
        return templates.TemplateResponse("registro_usuario.html", {
            "request": request,
            "error": "Error interno al procesar el registro"
        })

# --- LOGOUT ---

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("usuario_login")
    return response