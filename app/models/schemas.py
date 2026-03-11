"""
Pydantic схемы для всех структур данных из задания.
Таблицы 1-9 из технического задания.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from app.models.enums import TransactionType, InfoMessageType, BranchCode, ObligationType


# =============================================================================
# Таблица 4.1.1. Структура объекта Taxs
# =============================================================================
class Tax(BaseModel):
    """Налоговое обязательство (Таблица 4.1.1)"""
    Number: str = Field(..., description="Порядковый номер")
    NameTax: str = Field(..., description="Наименование обязательства")
    Amount: float = Field(..., description="Сумма обязательства")
    PennyAmount: float = Field(..., description="Сумма пени (если есть)")


# =============================================================================
# Таблица 4.1. Структура объекта Obligation
# =============================================================================
class Obligation(BaseModel):
    """Обязательство (Таблица 4.1)"""
    Type: ObligationType = Field(..., description="Вид обязательства: 1, 2, 3 или 4")
    StartDate: Optional[datetime] = Field(None, description="Дата периода 'с' (для Type=1)")
    EndDate: Optional[datetime] = Field(None, description="Дата периода 'по' (для Type=1)")
    ActDate: Optional[datetime] = Field(None, description="Дата акта проверки")
    ActNumber: Optional[str] = Field(None, description="Номер акта проверки")
    Taxs: List[Tax] = Field(default_factory=list, description="Массив обязательств по налогам")


# =============================================================================
# Таблица 4. Сообщение о выдаче гарантии (InfoMessageType = 201)
# =============================================================================
class BankGuarantee(BaseModel):
    """Банковская гарантия (Таблица 4)"""
    # Поля из таблицы 4
    InformationType: int = Field(201, description="Тип сообщения, всегда 201")
    InformationTypeString: str = Field("Выдача гарантии", description="Признак информации")
    Number: str = Field(..., description="Номер гарантии")
    IssuedDate: datetime = Field(..., description="Дата выдачи гарантии")
    Guarantor: str = Field(..., description="Наименование организации-гаранта")
    Beneficiary: str = Field(..., description="Наименование получателя")
    Principal: str = Field(..., description="Наименование принципала (должника)")
    Obligations: List[Obligation] = Field(..., description="Массив обязательств")
    StartDate: datetime = Field(..., description="Дата вступления в силу")
    EndDate: datetime = Field(..., description="Дата прекращения действия")
    CurrencyCode: str = Field(..., description="Код валюты (USD, EUR, BYN)")
    CurrencyName: str = Field(..., description="Полное наименование валюты")
    Amount: float = Field(..., description="Общая сумма с точностью до 0.01")
    RevokationInfo: str = Field(..., description="Безотзывная или Отзывная")
    ClaimRightTransfer: str = Field(..., description="Условия перехода права требования")
    PaymentPeriod: str = Field(..., description="Срок осуществления платежа")
    SignerName: str = Field(..., description="ФИО подписанта")
    AuthorizedPosition: str = Field(..., description="Должность подписанта")
    BankGuaranteeHash: str = Field(..., description="ХЭШ гарантии")


# =============================================================================
# Таблица 5. Сообщение о принятии гарантии (InfoMessageType = 202)
# =============================================================================
class GuaranteeAcceptance(BaseModel):
    """Подтверждение принятия гарантии (Таблица 5)"""
    Name: str = Field(..., description="Наименование отправителя")
    BankGuaranteeHash: str = Field(..., description="Хэш гарантии, на которую дается ответ")
    Sign: str = Field(..., description="ЭЦП документа (в Base64)")
    SignerCert: str = Field(..., description="Сертификат подписанта (в Base64)")


# =============================================================================
# Таблица 6. Сообщение об отказе в принятии гарантии (InfoMessageType = 203)
# =============================================================================
class GuaranteeRejection(BaseModel):
    """Отказ в принятии гарантии (Таблица 6)"""
    Name: str = Field(..., description="Наименование отправителя")
    BankGuaranteeHash: str = Field(..., description="Хэш гарантии")
    Sign: str = Field(..., description="ЭЦП документа (в Base64)")
    SignerCert: str = Field(..., description="Сертификат подписанта (в Base64)")
    Reason: str = Field(..., description="Причина отказа")


# =============================================================================
# Таблица 7. Квиток о получении (InfoMessageType = 215)
# =============================================================================
class Receipt(BaseModel):
    """Квиток о получении (Таблица 7)"""
    BankGuaranteeHash: str = Field(..., description="Хэш гарантии, по которой получено сообщение")


# =============================================================================
# Таблица 3. Информационное сообщение (Message)
# =============================================================================
class Message(BaseModel):
    """
    Информационное сообщение (Таблица 3).
    Содержится в поле Data транзакции (для TransactionType = 9).
    """
    Data: str = Field(..., description="Base64 закодированный JSON пакет данных (одна из таблиц 4-9)")
    SenderBranch: BranchCode = Field(..., description="Код отправителя: SYSTEM_A или SYSTEM_B")
    ReceiverBranch: BranchCode = Field(..., description="Код получателя: SYSTEM_A или SYSTEM_B")
    InfoMessageType: InfoMessageType = Field(..., description="Тип информационного сообщения")
    MessageTime: datetime = Field(default_factory=datetime.utcnow, description="Дата создания сообщения в UTC")
    ChainGuid: UUID = Field(default_factory=uuid4, description="Уникальный идентификатор цепочки сообщений")
    PreviousTransactionHash: Optional[str] = Field(None, description="Хэш транзакции с предыдущим сообщением")
    Metadata: Optional[str] = Field(None, description="Метаданные для поиска")

    model_config = ConfigDict(arbitrary_types_allowed=True)


# =============================================================================
# Таблица 2. Транзакция (Transaction)
# =============================================================================
class Transaction(BaseModel):
    """
    Транзакция (Таблица 2).
    Единица хранения в реестре.
    """
    TransactionType: TransactionType = Field(..., description="Тип транзакции: 9 или 18")
    Data: str = Field(..., description="Base64 закодированный JSON пакет данных (Message)")
    Hash: Optional[str] = Field(None, description="Хэш транзакции")
    Sign: Optional[str] = Field(None, description="ЭЦП автора транзакции (в Base64)")
    SignerCert: Optional[str] = Field(None, description="СОК автора транзакции (в Base64)")
    TransactionTime: datetime = Field(default_factory=datetime.utcnow, description="Дата создания транзакции в UTC")
    Metadata: Optional[str] = Field(None, description="Метаданные для быстрого поиска")
    TransactionIn: Optional[str] = Field(None, description="Предыдущая транзакция")
    TransactionOut: Optional[str] = Field(None, description="Следующая транзакция")

    model_config = ConfigDict(arbitrary_types_allowed=True)


# =============================================================================
# Таблица 8. Запрос поиска сообщений (SearchRequest)
# =============================================================================
class SearchRequest(BaseModel):
    """Запрос поиска сообщений (Таблица 8)"""
    StartDate: datetime = Field(..., description="Начало периода поиска (UTC)")
    EndDate: datetime = Field(..., description="Конец периода поиска (UTC)")
    Limit: int = Field(10, ge=1, le=100, description="Максимальное количество сообщений в ответе")
    Offset: int = Field(0, ge=0, description="Смещение для пагинации")


# =============================================================================
# Таблица 9. Ответ со списком транзакций (TransactionsData)
# =============================================================================
class TransactionsData(BaseModel):
    """Ответ со списком транзакций (Таблица 9)"""
    Transactions: List[Transaction] = Field(default_factory=list, description="Массив транзакций")
    Count: int = Field(0, description="Общее количество найденных транзакций")


# =============================================================================
# Таблица 1. Конверт запроса/ответа (SignedApiData)
# =============================================================================
class SignedApiData(BaseModel):
    """
    Конверт запроса/ответа (Таблица 1).
    Этим конвертом оборачиваются все запросы к API и все ответы от API.
    """
    Data: str = Field(..., description="Base64 закодированный JSON пакет данных")
    Sign: str = Field(..., description="ЭЦП отправителя (в Base64)")
    SignerCert: str = Field(..., description="Сертификат открытого ключа отправителя (в Base64)")


# =============================================================================
# Union тип для всех возможных сообщений (для удобства)
# =============================================================================
MessageContent = BankGuarantee | GuaranteeAcceptance | GuaranteeRejection | Receipt