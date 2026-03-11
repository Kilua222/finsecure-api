"""
Основной модуль приложения FastAPI.
"""
from fastapi import FastAPI
from app.api.endpoints import health_router, messages_router

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="FinSecure API - Система Б (Центральный реестр)",
    description="REST API для обмена юридически значимыми документами с эмуляцией блокчейн-хранения",
    version="1.0.0",
)

# Подключаем роутеры
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(messages_router, prefix="/api/messages", tags=["Messages"])

@app.get("/")
async def root():
    """Корневой эндпоинт для приветствия."""
    return {
        "message": "Добро пожаловать в FinSecure API",
        "docs": "/docs",
        "health_check": "/api/health",
        "endpoints": {
            "GET /api/health": "Проверка работоспособности",
            "POST /api/messages/outgoing": "Получить входящие сообщения",
            "POST /api/messages/incoming": "Отправить сообщения в реестр"
        }
    }