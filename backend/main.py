from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

@app.get("/")
def home():
    return {
        "message": f"Welcome to {settings.APP_NAME} API"
    }

app.include_router(health_router)