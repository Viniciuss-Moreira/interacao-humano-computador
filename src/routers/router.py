from fastapi import APIRouter

from .consulta_router import router as consulta_router

api_router = APIRouter()
api_router.include_router(consulta_router)