from fastapi import APIRouter
from app.api.endpoints import user
from app.api.endpoints import finance

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(finance.router, prefix="/users", tags=["finance"])
