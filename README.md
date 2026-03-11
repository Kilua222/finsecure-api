# FinSecure API - Система Б (Центральный реестр)

REST API для обмена юридически значимыми документами с эмуляцией блокчейн-хранения.

## 🚀 Быстрый старт

### Требования
- Python 3.9+
- Git

### Установка

```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd finsecure-api

# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate
# Или (Mac/Linux)
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --reload