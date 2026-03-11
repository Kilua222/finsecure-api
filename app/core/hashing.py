"""
Функции для вычисления хэша и эмуляции ЭЦП.
В соответствии с Примечанием 1 и Примечанием 2 из задания.
"""
import hashlib
import json
from typing import Any, Dict
import base64


def calculate_hash(obj: Dict[str, Any]) -> str:
    """
    Вычисляет хэш объекта в соответствии с Примечанием 1.

    Порядок вычисления:
    1. Удалить поля, участвующие в подписи (Hash и Sign установить в None/пустую строку)
    2. Сериализовать объект в JSON-строку (порядок полей сохраняется)
    3. Получить байты строки в UTF-8
    4. Вычислить SHA-256 хэш
    5. Представить результат в виде HEX-строки (верхний регистр)

    Args:
        obj: Словарь с данными объекта (Transaction или другой)

    Returns:
        HEX-строка хэша в верхнем регистре
    """
    # Создаем копию объекта, чтобы не изменять оригинал
    obj_copy = obj.copy()

    # Удаляем поля, участвующие в подписи (устанавливаем в None)
    obj_copy.pop('Hash', None)
    obj_copy.pop('Sign', None)

    # Для поля SignerCert тоже нужно убрать из хэширования?
    # В задании сказано только про Hash и Sign, оставляем SignerCert

    # Сериализуем в JSON с сортировкой ключей для стабильности
    # Важно: сохраняем порядок полей как в оригинале, но для надежности используем sort_keys=False
    json_str = json.dumps(obj_copy, ensure_ascii=False, sort_keys=False, default=str)

    # Получаем байты в UTF-8
    bytes_data = json_str.encode('utf-8')

    # Вычисляем SHA-256
    sha256_hash = hashlib.sha256(bytes_data).hexdigest().upper()

    return sha256_hash


def emulate_sign(hash_hex: str) -> str:
    """
    Эмулирует ЭЦП в соответствии с Примечанием 2.

    Порядок вычисления:
    1. Взять значение Hash (HEX-строка)
    2. Преобразовать в байты
    3. Закодировать в Base64
    4. Полученную строку использовать как значение поля Sign

    Args:
        hash_hex: HEX-строка хэша

    Returns:
        Base64 строка - эмулированная подпись
    """
    # Преобразуем HEX строку в байты
    # Сначала в обычные байты из hex
    hash_bytes = bytes.fromhex(hash_hex)

    # Кодируем в Base64
    sign_base64 = base64.b64encode(hash_bytes).decode('utf-8')

    return sign_base64


def verify_sign(data: Dict[str, Any], expected_hash: str, sign: str) -> bool:
    """
    Проверяет эмулированную подпись.

    Args:
        data: Данные для проверки
        expected_hash: Ожидаемый хэш из поля Hash
        sign: Подпись для проверки

    Returns:
        True если подпись валидна, иначе False
    """
    # Перевычисляем хэш
    calculated_hash = calculate_hash(data)

    # Проверяем совпадение хэша
    if calculated_hash != expected_hash:
        return False

    # Эмулируем подпись заново и сравниваем
    expected_sign = emulate_sign(calculated_hash)

    return expected_sign == sign


def prepare_transaction_for_hashing(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Подготавливает транзакцию для вычисления хэша.
    Устанавливает Hash и Sign в None.

    Args:
        transaction: Словарь с данными транзакции

    Returns:
        Копия транзакции с очищенными полями Hash и Sign
    """
    tx_copy = transaction.copy()
    tx_copy['Hash'] = None
    tx_copy['Sign'] = None
    return tx_copy