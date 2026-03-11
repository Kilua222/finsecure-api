"""
Утилиты для работы с Base64 кодированием/декодированием.
"""
import base64
import json
from typing import Any, Type, TypeVar, Union
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


def encode_to_base64(data: Any) -> str:
    """
    Кодирует любой объект в Base64 строку.

    1. Если data - строка, используем её как есть
    2. Если data - Pydantic модель, конвертируем в JSON
    3. Если data - словарь, конвертируем в JSON

    Args:
        data: Данные для кодирования

    Returns:
        Base64 строка
    """
    if isinstance(data, str):
        json_str = data
    elif isinstance(data, BaseModel):
        # Используем model_dump_json вместо model_dump_json (для Pydantic v2)
        json_str = data.model_dump_json(exclude_none=True, by_alias=True)
    elif isinstance(data, dict):
        json_str = json.dumps(data, ensure_ascii=False, default=str)
    else:
        # Для других типов пытаемся преобразовать в dict
        json_str = json.dumps(data, ensure_ascii=False, default=str)

    # Кодируем в UTF-8 байты
    utf8_bytes = json_str.encode('utf-8')

    # Кодируем в Base64
    base64_bytes = base64.b64encode(utf8_bytes)

    # Декодируем в строку
    return base64_bytes.decode('utf-8')


def decode_from_base64(base64_str: str, model_class: Type[T] = None) -> Any:
    """
    Декодирует Base64 строку обратно в объект.

    Args:
        base64_str: Base64 строка для декодирования
        model_class: Опционально, Pydantic модель для парсинга

    Returns:
        Декодированные данные (словарь или Pydantic модель)
    """
    # Декодируем из Base64 в байты
    base64_bytes = base64_str.encode('utf-8')
    utf8_bytes = base64.b64decode(base64_bytes)

    # Декодируем из UTF-8 в строку
    json_str = utf8_bytes.decode('utf-8')

    if model_class:
        # Если указана модель, парсим JSON в модель
        return model_class.model_validate_json(json_str)
    else:
        # Иначе возвращаем как словарь
        return json.loads(json_str)


def decode_message_from_transaction(transaction_data: str, message_model=None):
    """
    Декодирует сообщение из транзакции.

    Транзакция.Data -> Base64 -> JSON (Message) -> Data -> Base64 -> JSON (контент)

    Args:
        transaction_data: Base64 строка из поля Data транзакции
        message_model: Опционально, модель для парсинга Message

    Returns:
        Декодированное сообщение
    """
    # Первый уровень: Transaction.Data -> Message
    message_dict = decode_from_base64(transaction_data)

    if isinstance(message_dict, dict) and 'Data' in message_dict:
        # Второй уровень: Message.Data -> контент
        try:
            content = decode_from_base64(message_dict['Data'])
            message_dict['_content'] = content
        except:
            # Если не получается декодировать, оставляем как есть
            pass

    if message_model and isinstance(message_dict, dict):
        return message_model.model_validate(message_dict)

    return message_dict


def encode_message_with_content(message_data: Any, content_data: Any) -> str:
    """
    Кодирует сообщение с контентом в Base64.

    1. Контент -> Base64
    2. Message с заполненным полем Data -> JSON -> Base64

    Args:
        message_data: Данные сообщения (словарь или модель)
        content_data: Данные контента

    Returns:
        Base64 строка для поля Data транзакции
    """
    # Кодируем контент в Base64
    content_base64 = encode_to_base64(content_data)

    # Создаем или обновляем сообщение
    if isinstance(message_data, dict):
        message_dict = message_data.copy()
        message_dict['Data'] = content_base64
    elif isinstance(message_data, BaseModel):
        # Для Pydantic модели создаем словарь и обновляем
        message_dict = message_data.model_dump(exclude_none=True, by_alias=True)
        message_dict['Data'] = content_base64
    else:
        message_dict = {'Data': content_base64}

    # Кодируем сообщение в Base64
    return encode_to_base64(message_dict)