"""
Эндпоинт для проверки работоспособности сервиса.
"""
from fastapi import APIRouter, status
from fastapi.responses import PlainTextResponse

# 👈 ВАЖНО: должен быть создан router
router = APIRouter()

@router.get(
    "/health",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Проверка доступности сервиса",
    description="Возвращает 'OK' если сервис работает."
)
async def health_check():
    """
    Простой эндпоинт для проверки, что API запущен и работает.
    """
    return "OK"