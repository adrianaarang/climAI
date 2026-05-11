# app/api/v1/api_router.py
from fastapi import APIRouter
from app.api.v1.endpoints import climas

api_router = APIRouter()

api_router.include_router(climas.router)