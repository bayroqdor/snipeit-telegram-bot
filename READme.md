# 🤖 Snipe-IT Telegram Bot

Этот бот предназначен для управления активами и пользователями в системе Snipe-IT через Telegram.

## 📌 Основные функции

### 📁 Управление активами (Assets)
- 📋 Просмотр всех активов с пагинацией
- 🔍 Поиск активов по имени, тегу или серийному номеру
- ➕ Добавление нового актива с выбором модели и статуса
- 👤 Назначение актива пользователю
- 📄 Просмотр деталей актива и текущего состояния

### 👤 Управление пользователями (Users)
- 📋 Просмотр всех пользователей с пагинацией
- 🔍 Поиск пользователей по имени или username
- ➕ Добавление нового пользователя (имя, username, пароль)
- 📄 Просмотр профиля пользователя и списка назначенных активов

## 🚀 Как запустить

### 🔧 Требования

- Python 3.10+
- Аккаунт и токен API от вашей инсталляции [Snipe-IT](https://snipeitapp.com/)
- Telegram Bot Token

### 📁 Структура проекта

snipeit_bot/
├── handlers/ # Основная логика бота
│ ├── assets.py
│ ├── users.py
│ └── common.py
├── keyboards/ # Клавиатуры (inline и reply)
├── utils/ # Вспомогательные функции
├── snipe_api.py # Обращения к API Snipe-IT
├── config.py # Конфигурация: токены и URL
└── main.py # Главный файл запуска бота

### ⚙️ Установка и запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/bayroqdor/snipeit-telegram-bot.git
cd snipeit-telegram-bot
```

2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate     # Для Windows
```
3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл config.py в корне проекта и добавьте:

```bash
TELEGRAM_BOT_TOKEN = 'ваш_telegram_bot_token'
SNIPEIT_URL = 'https://ваш-домен.snipe-it.com'
SNIPEIT_API_KEY = 'ваш_snipeit_api_key'
```
5. python main.py

```bash
python main.py
```

После запуска бот будет работать в Telegram и обрабатывать команды.

### 🛠 Зависимости
- python-telegram-bot==22.2
- aiohttp
- apscheduler

### 📄 Лицензия
GNU 