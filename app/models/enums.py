"""
Перечисления (enum) для типов данных в API.
"""
from enum import IntEnum, Enum


class TransactionType(IntEnum):
    """Типы транзакций (Таблица 2)"""
    INFO_MESSAGE = 9      # Информационное сообщение
    GUARANTEE = 18        # Гарантия


class InfoMessageType(IntEnum):
    """Типы информационных сообщений (Таблица 3)"""
    GUARANTEE_ISSUED = 201      # Выдача гарантии
    GUARANTEE_ACCEPTED = 202    # Подтверждение принятия
    GUARANTEE_REJECTED = 203    # Отказ в принятии
    RECEIPT = 215               # Квиток о получении


class BranchCode(str, Enum):
    """Коды отделений/систем"""
    SYSTEM_A = "SYSTEM_A"
    SYSTEM_B = "SYSTEM_B"


class ObligationType(IntEnum):
    """Типы обязательств (Таблица 4.1)"""
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4