from fastapi import APIRouter
from app.api.v1.endpoints import videos, qa

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(qa.router, prefix="/qa", tags=["qa"]) 