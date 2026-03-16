"""
Основной модуль приложения FastAPI.
"""
from fastapi import FastAPI
from app.api.endpoints import health_router, messages_router

app = FastAPI(
    title="FinSecure API - Система Б (Центральный реестр)",
    description="REST API для обмена юридически значимыми документами с эмуляцией блокчейн-хранения",
    version="1.0.0",
)

app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(messages_router, prefix="/api/messages", tags=["Messages"])

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в FinSecure API",
        "docs": "/docs",
        "health_check": "/api/health"
    }