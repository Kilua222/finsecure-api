"""
In-memory хранилище для транзакций.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4
import threading
import json
from app.models.schemas import Transaction, Message
from app.models.enums import BranchCode, TransactionType as TxTypeEnum


class TransactionStorage:
    """
    Хранилище транзакций в памяти (thread-safe).
    """

    def __init__(self):
        """Инициализация пустого хранилища."""
        self._transactions: Dict[str, Transaction] = {}  # hash -> Transaction
        self._lock = threading.Lock()

    def add_transaction(self, transaction: Transaction) -> str:
        """
        Добавляет транзакцию в хранилище.

        Args:
            transaction: Транзакция для добавления

        Returns:
            Хэш транзакции
        """
        with self._lock:
            # Генерируем хэш, если его нет
            if not transaction.Hash:
                # В реальном коде здесь нужно вычислить хэш
                # Пока используем UUID для теста
                transaction.Hash = str(uuid4()).replace('-', '').upper()

            self._transactions[transaction.Hash] = transaction
            return transaction.Hash

    def get_transaction(self, hash_value: str) -> Optional[Transaction]:
        """
        Получает транзакцию по хэшу.

        Args:
            hash_value: Хэш транзакции

        Returns:
            Транзакция или None, если не найдена
        """
        with self._lock:
            return self._transactions.get(hash_value)

    def get_transactions_by_receiver(
        self,
        receiver: BranchCode,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
        offset: int = 0
    ) -> List[Transaction]:
        """
        Получает транзакции по получателю и диапазону дат.

        Args:
            receiver: Код получателя (SYSTEM_A или SYSTEM_B)
            start_date: Начало периода
            end_date: Конец периода
            limit: Максимальное количество
            offset: Смещение для пагинации

        Returns:
            Список транзакций
        """
        with self._lock:
            # Фильтруем транзакции
            filtered = []
            for tx in self._transactions.values():
                # Проверяем, что транзакция содержит Message
                if tx.transaction_type != TxTypeEnum.INFO_MESSAGE:  # ✅ ИСПРАВЛЕНО
                    continue

                # Декодируем Message из tx.Data
                try:
                    from app.core.base64_utils import decode_from_base64
                    message_dict = decode_from_base64(tx.Data)

                    # Проверяем получателя
                    if message_dict.get('ReceiverBranch') != receiver.value:
                        continue

                except Exception as e:
                    # Если не можем декодировать, пропускаем
                    print(f"Ошибка декодирования Message: {e}")
                    continue

                # Проверяем дату (убираем timezone для сравнения)
                tx_time = tx.TransactionTime
                if tx_time.tzinfo:
                    tx_time = tx_time.replace(tzinfo=None)

                start = start_date
                if start.tzinfo:
                    start = start.replace(tzinfo=None)

                end = end_date
                if end.tzinfo:
                    end = end.replace(tzinfo=None)

                if start <= tx_time <= end:
                    filtered.append(tx)

            # Сортируем по времени (новые сначала)
            filtered.sort(key=lambda x: x.TransactionTime, reverse=True)

            # Применяем пагинацию
            return filtered[offset:offset + limit]

    def count_transactions_by_receiver(
        self,
        receiver: BranchCode,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """
        Подсчитывает количество транзакций по получателю и диапазону дат.

        Args:
            receiver: Код получателя
            start_date: Начало периода
            end_date: Конец периода

        Returns:
            Количество транзакций
        """
        with self._lock:
            count = 0
            for tx in self._transactions.values():
                if tx.transaction_type != TxTypeEnum.INFO_MESSAGE:  # ✅ ИСПРАВЛЕНО
                    continue

                # Декодируем Message для проверки получателя
                try:
                    from app.core.base64_utils import decode_from_base64
                    message_dict = decode_from_base64(tx.Data)
                    if message_dict.get('ReceiverBranch') != receiver.value:
                        continue
                except:
                    continue

                # Проверяем дату
                tx_time = tx.TransactionTime
                if tx_time.tzinfo:
                    tx_time = tx_time.replace(tzinfo=None)

                start = start_date
                if start.tzinfo:
                    start = start.replace(tzinfo=None)

                end = end_date
                if end.tzinfo:
                    end = end.replace(tzinfo=None)

                if start <= tx_time <= end:
                    count += 1

            return count

    def get_all_transactions(self) -> List[Transaction]:
        """Возвращает все транзакции (для отладки)."""
        with self._lock:
            return list(self._transactions.values())

    def clear(self):
        """Очищает хранилище (для тестов)."""
        with self._lock:
            self._transactions.clear()

    def add_test_data(self):
        """Добавляет тестовые данные при первом запуске."""
        from app.core.base64_utils import encode_to_base64, decode_from_base64
        from app.models.schemas import BankGuarantee, Message
        from app.models.enums import InfoMessageType
        from datetime import datetime, timezone

        # Создаем тестовую гарантию из Примера 1
        test_guarantee = BankGuarantee(
            InformationType=201,
            InformationTypeString="Выдача гарантии",
            Number="BG-2024-001",
            IssuedDate=datetime(2024, 5, 20, 10, 0, 0, tzinfo=timezone.utc),
            Guarantor="ООО 'Финансовая гарантия'",
            Beneficiary="Государственное учреждение 'Получатель'",
            Principal="ООО 'Должник'",
            Obligations=[],  # Для простоты оставим пустым
            StartDate=datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
            EndDate=datetime(2024, 12, 15, 0, 0, 0, tzinfo=timezone.utc),
            CurrencyCode="USD",
            CurrencyName="Доллар США",
            Amount=65000.00,
            RevokationInfo="Безотзывная",
            ClaimRightTransfer="Не допускается",
            PaymentPeriod="5 рабочих дней с момента получения требования",
            SignerName="Иванов Иван Иванович",
            AuthorizedPosition="Генеральный директор",
            BankGuaranteeHash="5D6F8E2A1C3B9F4D7E8A2C5B1D3F6E8A9C2D4F6A8B1C3E5F7A9D2B4C6E8F0A1"
        )

        # Создаем Message
        message = Message(
            Data=encode_to_base64(test_guarantee.model_dump(by_alias=True)),
            SenderBranch=BranchCode.SYSTEM_B,
            ReceiverBranch=BranchCode.SYSTEM_A,
            message_type=InfoMessageType.GUARANTEE_ISSUED,
            MessageTime=datetime.now(timezone.utc),
            ChainGuid=uuid4(),
            PreviousTransactionHash=None,
            Metadata=None
        )

        # Создаем транзакцию
        transaction = Transaction(
            transaction_type=TxTypeEnum.INFO_MESSAGE,
            Data=encode_to_base64(message.model_dump(by_alias=True)),
            Hash=None,
            Sign=None,
            SignerCert=None,
            TransactionTime=datetime.now(timezone.utc),
            Metadata=None,
            TransactionIn=None,
            TransactionOut=None
        )

        # Добавляем в хранилище
        self.add_transaction(transaction)
        print("✅ Тестовые данные добавлены в хранилище")


# Создаем глобальный экземпляр хранилища (синглтон)
_storage_instance = None


def get_storage() -> TransactionStorage:
    """Возвращает глобальный экземпляр хранилища."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = TransactionStorage()
        # Добавляем тестовые данные при первом создании
        _storage_instance.add_test_data()
    return _storage_instance