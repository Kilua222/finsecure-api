"""
Эндпоинты для работы с сообщениями.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from app.models.schemas import SignedApiData, TransactionsData
from app.services.transaction_service import get_transaction_service, TransactionService
from app.core.base64_utils import encode_to_base64, decode_from_base64

router = APIRouter()


@router.post(
    "/outgoing",
    response_model=SignedApiData,
    status_code=status.HTTP_200_OK,
    summary="Получение входящих сообщений",
    description="Возвращает список транзакций с сообщениями, адресованными Системе А, за указанный период."
)
async def get_outgoing_messages(
        request: SignedApiData,
        service: TransactionService = Depends(get_transaction_service)
):
    """
    Эндпоинт для получения сообщений, адресованных SYSTEM_A.

    Ожидает SignedApiData с SearchRequest в поле Data.
    Возвращает SignedApiData с TransactionsData в поле Data.
    """
    try:
        # Обрабатываем запрос через сервис
        transactions_data, error = service.get_outgoing_messages(request)

        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        # Создаем ответ
        response_data = SignedApiData(
            Data=encode_to_base64(transactions_data),
            Sign="EMULATED_SIGN_" + transactions_data.Count.__str__(),  # Эмулируем подпись
            SignerCert="SYSTEM_B_CERT"
        )

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post(
    "/incoming",
    response_model=SignedApiData,
    status_code=status.HTTP_200_OK,
    summary="Отправка сообщений в реестр",
    description="Принимает новые сообщения от Системы А и возвращает квитки."
)
async def post_incoming_messages(
        request: SignedApiData,
        service: TransactionService = Depends(get_transaction_service)
):
    """
    Эндпоинт для приема сообщений от SYSTEM_A.

    Ожидает SignedApiData с TransactionsData в поле Data.
    Возвращает SignedApiData с TransactionsData (квитки) в поле Data.
    """
    try:
        # Обрабатываем запрос через сервис
        receipts_data, error = service.process_incoming_transactions(request)

        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        # Создаем ответ
        response_data = SignedApiData(
            Data=encode_to_base64(receipts_data),
            Sign="EMULATED_SIGN_" + receipts_data.Count.__str__(),
            SignerCert="SYSTEM_B_CERT"
        )

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


# Дополнительный эндпоинт для отладки
@router.get(
    "/debug",
    status_code=status.HTTP_200_OK,
    summary="Отладка - показать все транзакции",
    include_in_schema=False  # Не показывать в документации
)
async def debug_get_all(
        service: TransactionService = Depends(get_transaction_service)
):
    """Возвращает все транзакции в хранилище (только для отладки)."""
    transactions = service.storage.get_all_transactions()
    return {
        "count": len(transactions),
        "transactions": [
            {
                "hash": tx.Hash,
                "type": tx.transaction_type,
                "time": tx.TransactionTime.isoformat()
            }
            for tx in transactions
        ]
    }