"""
Сервис для обработки транзакций и сообщений.
"""
import hashlib
import json
from typing import List, Tuple, Optional, Any
from datetime import datetime, timezone
from uuid import uuid4

from app.core.storage import get_storage, TransactionStorage
from app.core.hashing import calculate_hash, emulate_sign, verify_sign
from app.core.base64_utils import encode_to_base64, decode_from_base64
from app.models.schemas import (
    SignedApiData, Transaction, TransactionsData,
    Message, SearchRequest, BankGuarantee, Receipt,
    GuaranteeAcceptance, GuaranteeRejection
)
from app.models.enums import TransactionType, InfoMessageType, BranchCode


class TransactionService:
    """
    Сервис для работы с транзакциями.
    Содержит бизнес-логику обработки запросов.
    """

    def __init__(self, storage: TransactionStorage = None):
        """Инициализация сервиса с хранилищем."""
        self.storage = storage or get_storage()

    def process_incoming_transactions(self, signed_data: SignedApiData) -> Tuple[
        Optional[TransactionsData], Optional[str]]:
        """
        Обрабатывает входящие транзакции от SYSTEM_A.

        1. Проверяет подпись конверта
        2. Декодирует TransactionsData
        3. Для каждой транзакции проверяет хэш и подпись
        4. Сохраняет транзакции
        5. Генерирует квитки для полученных сообщений

        Args:
            signed_data: Подписанные данные запроса

        Returns:
            Tuple[Optional[TransactionsData], Optional[str]]:
                - Данные с квитками или None
                - Сообщение об ошибке (если есть)
        """
        # Проверяем подпись конверта (эмуляция)
        if not self._verify_signed_data(signed_data):
            return None, "Неверная подпись конверта"

        # Декодируем TransactionsData
        try:
            transactions_data = decode_from_base64(signed_data.Data, TransactionsData)
        except Exception as e:
            return None, f"Ошибка декодирования TransactionsData: {str(e)}"

        receipts = []

        # Обрабатываем каждую транзакцию
        for transaction in transactions_data.Transactions:
            # Проверяем транзакцию
            is_valid, error_msg = self._validate_transaction(transaction)
            if not is_valid:
                return None, f"Невалидная транзакция: {error_msg}"

            # Сохраняем транзакцию
            self.storage.add_transaction(transaction)

            # Генерируем квиток (для всех сообщений кроме квитков)
            receipt = self._generate_receipt_if_needed(transaction)
            if receipt:
                receipts.append(receipt)

        # Создаем ответ с квитками
        receipts_data = TransactionsData(
            Transactions=receipts,
            Count=len(receipts)
        )

        return receipts_data, None

    def get_outgoing_messages(self, signed_data: SignedApiData) -> Tuple[Optional[TransactionsData], Optional[str]]:
        """
        Получает исходящие сообщения для SYSTEM_A.

        Args:
            signed_data: Подписанные данные запроса (SearchRequest)

        Returns:
            Tuple[Optional[TransactionsData], Optional[str]]:
                - Найденные транзакции или None
                - Сообщение об ошибке (если есть)
        """
        # Проверяем подпись конверта
        if not self._verify_signed_data(signed_data):
            return None, "Неверная подпись конверта"

        # Декодируем SearchRequest
        try:
            search_request = decode_from_base64(signed_data.Data, SearchRequest)
        except Exception as e:
            return None, f"Ошибка декодирования SearchRequest: {str(e)}"

        # Ищем транзакции для SYSTEM_A
        transactions = self.storage.get_transactions_by_receiver(
            receiver=BranchCode.SYSTEM_A,
            start_date=search_request.StartDate,
            end_date=search_request.EndDate,
            limit=search_request.Limit,
            offset=search_request.Offset
        )

        # Получаем общее количество
        total_count = self.storage.count_transactions_by_receiver(
            receiver=BranchCode.SYSTEM_A,
            start_date=search_request.StartDate,
            end_date=search_request.EndDate
        )

        # Создаем ответ
        result = TransactionsData(
            Transactions=transactions,
            Count=total_count
        )

        return result, None

    def _validate_transaction(self, transaction: Transaction) -> Tuple[bool, str]:
        """
        Проверяет валидность транзакции.

        1. Проверяет, что Sign не пустой
        2. Проверяет, что хэш совпадает с вычисленным

        Args:
            transaction: Транзакция для проверки

        Returns:
            Tuple[bool, str]: (валидна ли, сообщение об ошибке)
        """
        # Проверяем, что подпись не пустая
        if not transaction.Sign:
            return False, "Поле Sign не может быть пустым"

        # Проверяем, что хэш не пустой
        if not transaction.Hash:
            return False, "Поле Hash не может быть пустым"

        # Вычисляем хэш заново
        tx_dict = transaction.model_dump(exclude_none=True, by_alias=True)
        calculated_hash = calculate_hash(tx_dict)

        # Сравниваем с переданным хэшем
        if calculated_hash != transaction.Hash:
            return False, f"Хэш не совпадает. Ожидался: {calculated_hash}, получен: {transaction.Hash}"

        # Проверяем подпись
        if not verify_sign(tx_dict, transaction.Hash, transaction.Sign):
            return False, "Неверная подпись транзакции"

        return True, ""

    def _generate_receipt_if_needed(self, transaction: Transaction) -> Optional[Transaction]:
        """
        Генерирует квиток для транзакции, если это необходимо.

        Args:
            transaction: Полученная транзакция

        Returns:
            Optional[Transaction]: Транзакция-квиток или None
        """
        # Проверяем, что это информационное сообщение
        if transaction.transaction_type != TransactionType.INFO_MESSAGE:
            return None

        # Декодируем Message из транзакции
        try:
            message_dict = decode_from_base64(transaction.Data)
            message = Message.model_validate(message_dict)
        except Exception as e:
            print(f"Ошибка декодирования Message: {e}")
            return None

        # Не генерируем квиток на квиток
        if message.message_type == InfoMessageType.RECEIPT:
            return None

        # Извлекаем BankGuaranteeHash из контента
        bank_guarantee_hash = self._extract_bank_guarantee_hash(message)
        if not bank_guarantee_hash:
            # Если нет хэша, используем хэш транзакции
            bank_guarantee_hash = transaction.Hash

        # Создаем квиток
        receipt_content = Receipt(
            BankGuaranteeHash=bank_guarantee_hash
        )

        # Создаем Message для квитка
        receipt_message = Message(
            Data=encode_to_base64(receipt_content.model_dump(by_alias=True)),
            SenderBranch=BranchCode.SYSTEM_B,
            ReceiverBranch=BranchCode.SYSTEM_A,
            message_type=InfoMessageType.RECEIPT,
            MessageTime=datetime.now(timezone.utc),
            ChainGuid=message.ChainGuid,
            PreviousTransactionHash=transaction.Hash,
            Metadata=None
        )

        # Создаем транзакцию для квитка
        receipt_transaction = Transaction(
            transaction_type=TransactionType.INFO_MESSAGE,
            Data=encode_to_base64(receipt_message.model_dump(by_alias=True)),
            Hash=None,
            Sign=None,
            SignerCert="SYSTEM_B_CERT",
            TransactionTime=datetime.now(timezone.utc),
            Metadata=None,
            TransactionIn=transaction.Hash,
            TransactionOut=None
        )

        # Вычисляем хэш и подпись
        tx_dict = receipt_transaction.model_dump(exclude_none=True, by_alias=True)
        tx_dict['Hash'] = None
        tx_dict['Sign'] = None

        hash_value = calculate_hash(tx_dict)
        sign_value = emulate_sign(hash_value)

        receipt_transaction.Hash = hash_value
        receipt_transaction.Sign = sign_value

        return receipt_transaction

    def _extract_bank_guarantee_hash(self, message: Message) -> Optional[str]:
        """
        Извлекает BankGuaranteeHash из сообщения.

        Args:
            message: Сообщение для анализа

        Returns:
            Optional[str]: Хэш гарантии или None
        """
        try:
            content = decode_from_base64(message.Data)

            if isinstance(content, dict):
                return content.get('BankGuaranteeHash')
            elif hasattr(content, 'BankGuaranteeHash'):
                return content.BankGuaranteeHash

            return None
        except Exception as e:
            print(f"Ошибка извлечения хэша: {e}")
            return None

    def _verify_signed_data(self, signed_data: SignedApiData) -> bool:
        """
        Проверяет подпись конверта SignedApiData.

        Args:
            signed_data: Подписанные данные

        Returns:
            bool: True если подпись валидна
        """
        # Для тестового задания просто проверяем, что подпись не пустая
        # В реальном проекте здесь была бы проверка ЭЦП
        return bool(signed_data.Sign and signed_data.Data)


# Создаем глобальный экземпляр сервиса
_service_instance = None


def get_transaction_service() -> TransactionService:
    """Возвращает глобальный экземпляр сервиса."""
    global _service_instance
    if _service_instance is None:
        _service_instance = TransactionService()
    return _service_instance