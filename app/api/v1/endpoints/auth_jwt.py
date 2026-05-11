# app/api/v1/endpoints/auth_jwt.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.database import User
from app.schemas.token import Token
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación JWT"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# ══════════════════════════════════════════════════════════════
# POST /api/v1/auth/token
# Endpoint JWT — distinto al /login
# ══════════════════════════════════════════════════════════════
@router.post(
    "/token",
    response_model=Token,
    summary="Obtener token JWT",
)
async def login_jwt(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


# ══════════════════════════════════════════════════════════════
# Dependencia reutilizable por todo el equipo
# ══════════════════════════════════════════════════════════════
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Protege cualquier endpoint del equipo:

    from app.api.v1.endpoints.auth_jwt import get_current_user

    @router.get("/protegido")
    async def ruta(user = Depends(get_current_user)):
        return {"user": user.email}
    """
    from app.core.security import decode_access_token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user