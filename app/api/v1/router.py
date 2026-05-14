from fastapi import APIRouter
from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.history import router as history_router

api_router = APIRouter()
api_router.include_router(analysis_router)
api_router.include_router(health_router)
api_router.include_router(history_router)