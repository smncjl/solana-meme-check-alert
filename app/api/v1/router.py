from fastapi import APIRouter

from app.api.v1.alerts import router as alerts_router
from app.api.v1.health import router as health_router
from app.api.v1.stats import router as stats_router
from app.api.v1.tokens import router as tokens_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(tokens_router)
api_router.include_router(alerts_router)
api_router.include_router(stats_router)
