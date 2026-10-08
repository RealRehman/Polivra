from fastapi import FastAPI

from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for the Polivra AI HR Policy Assistant.",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}