"""
Основной модуль приложения FastAPI.
"""
from fastapi import FastAPI

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="FinSecure API - Система Б (Центральный реестр)",
    description="REST API для обмена юридически значимыми документами с эмуляцией блокчейн-хранения",
    version="1.0.0",
)

@app.get("/")
async def root():
    """Корневой эндпоинт для приветствия."""
    return {
        "message": "Добро пожаловать в FinSecure API",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Проверка работоспособности."""
    return "OK"