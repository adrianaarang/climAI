# app/api/v1/api_router.py
from fastapi import APIRouter
from app.api.v1.endpoints import climas
from app.api.v1.endpoints import auth_jwt

api_router = APIRouter()

api_router.include_router(climas.router)
api_router.include_router(auth_jwt.router)