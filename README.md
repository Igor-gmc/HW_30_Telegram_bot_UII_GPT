# Task Management Telegram Bot

A comprehensive Telegram bot that helps managers and marketers organize tasks, deals, and get AI-powered advice. Built with aiogram 3.x and SQLAlchemy.

## Features

### Task Management
- Add tasks with titles and deadlines
- View all tasks with status tracking
- Mark tasks as completed/incomplete
- Delete tasks

### Deal Management
- Create deals with title, amount and status
- View and sort deals by status
- Update deal status (Open/In Progress/Closed)
- Delete deals
- Track deal statistics

### AI-Powered Assistant
- Get marketing advice using ChatGPT
- Receive motivational phrases for sales
- Smart conversation handling

### Reporting
- View completed tasks count
- Track closed deals and total amounts
- Get session statistics

## Technical Stack

### Core Components
- Python 3.10
- aiogram 3.x (Telegram Bot Framework)
- SQLAlchemy 2.x (ORM)
- PostgreSQL (via asyncpg)
- OpenAI API (GPT-4)

### Database Structure
- Users table (id, telegram_id, username)
- Tasks table (id, user_id, title, time, status)
- Deals table (id, user_id, title, amount, status)

### Project Structure
```
├── bot.py              # Main bot file
├── config.py           # Configuration and environment
├── database/          
│   ├── db.py          # Database connection
│   └── models.py      # SQLAlchemy models
├── handlers/           # Message handlers
├── keyboards/          # Keyboard layouts
├── services/          # External services
└── states/            # FSM states
```

# Архитектура проекта

Ниже сохранена gjlhj,yfzя структура проекта и краткое описание файлов и каталогов (на русском).
```
project_root/
│
├── bot.py                          # Главная точка входа (инициализация, запуск бота)
├── config.py                       # Настройки: токены, API ключи, параметры подключения
├── .env                            # Переменные окружения (Bot token, DB, API keys)
│
├── database/
│   ├── db.py                       # Подключение и работа с PostgreSQL (async SQLAlchemy)
│   ├── models.py                   # ORM-модели таблиц (users, tasks, deals, session_stats)
│   └── faiss_db.py                 # Инициализация и управление FAISS базой знаний
│
├── handlers/
│   ├── __init__.py
│   ├── start.py                    # /start и главное меню
│   ├── tasks.py                    # Добавление / просмотр задач
│   ├── deals.py                    # Добавление / просмотр сделок
│   ├── marketing.py                # Советы по маркетингу через ChatGPT
│   ├── motivation.py               # Мотивация через ChatGPT
│   ├── report.py                   # /report — отчёт по сделкам
│   ├── knowledge.py                # Вопросы к базе знаний (через FAISS)
│
├── keyboards/
│   ├── reply.py                    # Reply-клавиатуры (основное меню)
│   ├── inline.py                   # Inline-кнопки (действия с задачами и сделками)
│
├── states/
│   ├── task_states.py              # FSM состояния для задач
│   ├── deal_states.py              # FSM состояния для сделок
│   ├── marketing_states.py         # FSM состояния для советов / мотивации
│   ├── knowledge_states.py         # FSM состояния для вопросов к базе знаний
│
├── services/
│   ├── chatgpt.py                  # Интеграция с ChatGPT API
│   ├── faiss_utils.py              # Эмбеддинги, семилар-серч, работа с FAISS
│   ├── utils.py                    # Утилиты (форматирование, вспомогательные функции)
│
├── logs/
│   ├── bot.log                     # Логи работы бота
│   ├── db.log                      # Логи работы с PostgreSQL
│   └── faiss.log                   # Логи FAISS запросов - не реализована
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Environment Requirements

Required environment variables (.env):
```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=assistant_bot
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

## Setup Instructions

1. Create virtual environment:
```bash
conda env create -f environment.yml
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup PostgreSQL database

4. Create .env file with required variables

5. Run the bot:
```bash
python bot.py
```

## Bot Commands

- `/start` - Show main menu
- `/add_task` - Add new task
- `/view_tasks` - View all tasks
- `/add_deal` - Add new deal
- `/view_deals` - View all deals
- `/marketing` - Get marketing advice
- `/motivation` - Get motivation phrase
- `/report` - View statistics
- `/cancel` - Cancel current operation

## Architecture Notes

- Asynchronous architecture using asyncio
- FSM (Finite State Machine) for complex dialogs
- Clean architecture with separated concerns
- Logging system with rotation
- Error handling and validation