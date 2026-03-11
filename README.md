# 🔐 FinSecure API — Система Б (Центральный реестр)

## 📋 Описание проекта

**FinSecure API** — сервис центрального реестра для обмена юридически значимыми документами между информационными системами.

### Архитектура взаимодействия

- **Система А (внешняя)** — инициирует запросы и отправляет документы  
- **Система Б (центральный реестр)** — принимает, проверяет и хранит документы  

### Основные возможности

- 📥 Прием и валидация транзакций  
- 🗄 Хранение документов в защищенном реестре  
- ✍️ Эмуляция ЭЦП (SHA-256 + Base64)  
- 📄 Генерация квитков подтверждения  
- 🔍 Поиск сообщений по дате и получателю  
- 🧠 In-memory хранилище с тестовыми данными  

---

# 🚀 Установка и запуск

## 1. Клонировать репозиторий

```bash
git clone https://github.com/Kilua222/finsecure-api.git
cd finsecure-api
```

## 2. Создать виртуальное окружение

```bash
python -m venv venv
```

### Активация

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

## 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## 4. Запустить сервер

```bash
uvicorn app.main:app --reload
```

После запуска API будет доступно по адресу:

```
http://localhost:8000
```

Swagger документация:

```
http://localhost:8000/docs
```

---

# 🧪 Примеры запросов

## Проверка API

### GET /api/health

```bash
curl -X GET "http://localhost:8000/api/health"
```

---

## Отправка исходящего сообщения

### POST /api/messages/outgoing

```bash
curl -X POST "http://localhost:8000/api/messages/outgoing" \
-H "Content-Type: application/json" \
-d '{
  "Data": "eyJTdGFydERhdGUiOiAiMjAyNC0wMS0wMVQwMDowMDowMFoiLCAiRW5kRGF0ZSI6ICIyMDI0LTEyLTMxVDIzOjU5OjU5WiIsICJMaW1pdCI6IDEwLCAiT2Zmc2V0IjogMH0=",
  "Sign": "test_sign",
  "SignerCert": "test_cert"
}'
```

---

## Получение входящего сообщения

### POST /api/messages/incoming

```bash
curl -X POST "http://localhost:8000/api/messages/incoming" \
-H "Content-Type: application/json" \
-d '{
  "Data": "eyJUcmFuc2FjdGlvbnMiOiBbXSwgIkNvdW50IjogMH0=",
  "Sign": "test_sign",
  "SignerCert": "test_cert"
}'
```

---

## Debug endpoint

### GET /api/messages/debug

```bash
curl -X GET "http://localhost:8000/api/messages/debug"
```

---

# 📂 Структура проекта

```
finsecure-api/

app/
 ├── api/endpoints/
 │   ├── health.py
 │   └── messages.py
 │
 ├── core/
 │   ├── hashing.py
 │   ├── base64_utils.py
 │   └── storage.py
 │
 ├── models/
 │   ├── enums.py
 │   └── schemas.py
 │
 ├── services/
 │   └── transaction_service.py
 │
 └── main.py

tests/
 ├── test_hashing.py
 └── test_storage.py

requirements.txt
README.md
```

---

# 🧪 Тестирование

Запуск тестов:

```bash
pytest
```

---
