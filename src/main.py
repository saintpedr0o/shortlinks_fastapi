from fastapi import FastAPI
from src.api.router import api_router
from src.api.redirect import router as redirect_router
from src.config import get_settings
import uvicorn


settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(api_router, prefix="/api")
app.include_router(redirect_router, prefix="/r")
