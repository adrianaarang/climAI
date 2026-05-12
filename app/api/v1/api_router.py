from fastapi import APIRouter
from app.api.v1.endpoints import climas, auth

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(climas.router, prefix="/clima", tags=["clima"])

