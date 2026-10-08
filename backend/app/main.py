from fastapi import FastAPI

from app.routes.users import router as users_router

from app.core.config import get_settings
from app.routes.auth import router as auth_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for the Polivra AI HR Policy Assistant.",
)

app.include_router(auth_router)

app.include_router(users_router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}