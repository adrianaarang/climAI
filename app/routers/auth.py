from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid  # Para generar el token de vinculación

from app.db.session import get_db
from app.models.database import User
from app.core.security import hash_password, verify_password

router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="app/templates")

# --- FUNCIONES DE APOYO ---
def obtener_usuario_actual(request: Request) -> str | None:
    return request.cookies.get("usuario_login")

async def buscar_usuario_por_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

# --- RUTAS DE TELEGRAM (Lo que faltaba) ---

@router.get("/vincular_telegram", response_class=HTMLResponse)
async def vincular_telegram_page(request: Request, db: AsyncSession = Depends(get_db)):
    email = obtener_usuario_actual(request)
    if not email:
        return RedirectResponse(url="/login")
    
    user = await buscar_usuario_por_email(db, email)
    
    # Si el usuario no tiene un token de sincronización, le creamos uno temporal
    # Esto es lo que aparecerá en tu HTML como {{ telegram_token }}
    sync_token = str(uuid.uuid4())[:8].upper() 
    
    return templates.TemplateResponse(
        request=request, 
        name="vincular_telegram.html", 
        context={
            "usuario": email,
            "telegram_token": sync_token,
            "telegram_linked": user.telegram_id is not None
        }
    )

# --- RUTAS DE LOGIN Y REGISTRO (Tus rutas originales corregidas) ---

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html", context={"usuario": None}
    )

@router.post("/login")
async def login_process(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await buscar_usuario_por_email(db, email.strip().lower())

        if user and verify_password(password, user.password):
            response = RedirectResponse(url="/", status_code=303)
            response.set_cookie(key="usuario_login", value=user.email, httponly=True, samesite="lax")
            return response

        return templates.TemplateResponse(
            request=request, name="login.html",
            context={"error": "Email o contraseña incorrectos", "usuario": None}
        )
    except Exception as e:
        print(f"Error en Login: {e}")
        return templates.TemplateResponse(
            request=request, name="login.html",
            context={"error": "Error interno del servidor", "usuario": None}
        )

@router.get("/registro_usuario", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="registro_usuario.html", context={"usuario": None}
    )

@router.post("/registro_usuario")
async def register_process(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    telegram_id: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    email_normalizado = email.strip().lower()

    if password != confirm_password:
        return templates.TemplateResponse(
            request=request, name="registro_usuario.html",
            context={"error": "Las contraseñas no coinciden", "usuario": None}
        )

    try:
        if await buscar_usuario_por_email(db, email_normalizado):
            return templates.TemplateResponse(
                request=request, name="registro_usuario.html",
                context={"error": "El email ya está registrado", "usuario": None}
            )

        nuevo_usuario = User(
            email=email_normalizado,
            password=hash_password(password),
            telegram_id=telegram_id or None,
        )
        db.add(nuevo_usuario)
        await db.commit()
        return RedirectResponse(url="/login", status_code=303)

    except Exception as e:
        await db.rollback()
        print(f"Error DB: {e}")
        return templates.TemplateResponse(
            request=request, name="registro_usuario.html",
            context={"error": "Error interno al procesar el registro", "usuario": None}
        )

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("usuario_login")
    return response


