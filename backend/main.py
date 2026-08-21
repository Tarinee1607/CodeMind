from fastapi import FastAPI
from app.database.database import init_db
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.api.routes.auth import router as auth_router
from app.database.database import Base, engine
from app.models.revoked_token import RevokedToken
from app.api.routes.repositories import router as repositories_router
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)
@app.on_event("startup")
def startup_event():
    init_db()



@app.get("/")
def home():
    return {
        "message": f"Welcome to {settings.APP_NAME} API"
    }

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(repositories_router)