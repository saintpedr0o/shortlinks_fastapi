from fastapi import APIRouter
from src.api import auth, users, links, clicks

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(users.admin_router)
api_router.include_router(links.router)
api_router.include_router(clicks.router)
