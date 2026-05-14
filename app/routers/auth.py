from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.database import User
from app.core.security import hash_password, verify_password

router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="app/templates")


def obtener_usuario_actual(request: Request) -> str | None:
    return request.cookies.get("usuario_login")


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
        result = await db.execute(
            select(User).where(User.email == email.strip().lower())
        )
        user = result.scalar_one_or_none()

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
        result = await db.execute(
            select(User).where(User.email == email_normalizado)
        )
        if result.scalar_one_or_none():
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