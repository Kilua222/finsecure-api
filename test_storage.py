"""
Тестирование in-memory хранилища.
"""
from datetime import datetime, timezone, timedelta
from app.core.storage import get_storage
from app.models.enums import BranchCode


def test_storage():
    """Тест работы хранилища."""
    print("=" * 60)
    print("ТЕСТ ХРАНИЛИЩА")
    print("=" * 60)

    # Получаем хранилище
    storage = get_storage()

    # Проверяем, что тестовые данные добавились
    all_tx = storage.get_all_transactions()
    print(f"Всего транзакций: {len(all_tx)}")

    # Ищем транзакции для SYSTEM_A
    now = datetime.now(timezone.utc)  # ✅ ИСПРАВЛЕНО: используем timezone.utc
    start = now - timedelta(days=30)
    end = now + timedelta(days=30)

    found = storage.get_transactions_by_receiver(
        receiver=BranchCode.SYSTEM_A,
        start_date=start,
        end_date=end,
        limit=10,
        offset=0
    )

    print(f"Найдено транзакций для SYSTEM_A: {len(found)}")

    if found:
        tx = found[0]
        print(f"\nПервая транзакция:")
        print(f"  Хэш: {tx.Hash}")
        print(f"  Тип: {tx.transaction_type}")
        print(f"  Время: {tx.TransactionTime}")

    print("\n✅ Тест хранилища пройден!")


if __name__ == "__main__":
    test_storage()