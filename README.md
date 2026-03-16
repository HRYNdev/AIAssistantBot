# 🤖 AI Assistant Bot

Telegram-бот, который отвечает на вопросы клиентов на основе базы знаний компании. Подключаешь свои документы (TXT, PDF, DOCX) — бот знает всё про твой бизнес.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![aiogram](https://img.shields.io/badge/aiogram-3.x-blue) ![LLM](https://img.shields.io/badge/LLM-OpenAI_compatible-orange) ![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-green)

## Как работает

1. Документы из папки `knowledge_base/` разбиваются на фрагменты и индексируются в ChromaDB
2. На вопрос пользователя ищутся релевантные фрагменты через векторный поиск
3. LLM формирует ответ строго на основе найденного контекста
4. Если ответа нет — бот говорит "не знаю" и даёт контакт менеджера

## Возможности

- 📚 **База знаний** — TXT, PDF, DOCX файлы в папке `knowledge_base/`
- 🔍 **Векторный поиск** — ChromaDB + sentence-transformers
- 🤖 **Любой LLM** — OpenAI, DeepSeek, Groq, Ollama, LM Studio (OpenAI-совместимый API)
- 💬 **Контекст диалога** — помнит последние 5 сообщений
- ❓ **Лог пробелов** — сохраняет вопросы без ответа для улучшения базы
- 🔄 **Горячая перезагрузка** — `/reload` обновляет базу без рестарта

## Быстрый старт

```bash
cp .env.example .env
# заполни BOT_TOKEN и LLM_API_KEY

# Добавь свои документы в knowledge_base/
# Поддерживаются: .txt, .pdf, .docx

docker compose up -d
```

Или без Docker:
```bash
pip install -r requirements.txt
python main.py
```

## Конфигурация `.env`

```env
BOT_TOKEN=your_token
ADMIN_IDS=[123456789]

# Любой OpenAI-совместимый провайдер
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1  # или DeepSeek, Groq, Ollama...
LLM_MODEL=gpt-4o-mini

SUPPORT_USERNAME=@manager   # контакт если бот не знает ответа
HISTORY_DEPTH=5             # глубина контекста диалога
MIN_RELEVANCE=0.4           # порог релевантности (0-1)
```

**Примеры провайдеров:**
| Провайдер | BASE_URL | MODEL |
|-----------|----------|-------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Ollama (локально) | `http://localhost:11434/v1` | `llama3.2` |

## Команды

| Команда | Доступ | Описание |
|---------|--------|----------|
| `/start` | все | Начало диалога |
| `/clear` | все | Очистить историю |
| `/reload` | админ | Перезагрузить базу знаний |
| `/gaps` | админ | Вопросы без ответа |

## Структура

```
├── main.py
├── bot/
│   ├── config.py         # настройки
│   ├── db.py             # история диалогов, лог пробелов
│   ├── knowledge.py      # загрузка документов + ChromaDB
│   ├── llm.py            # LLM (OpenAI-compatible)
│   └── handlers/
│       ├── chat.py       # обработка вопросов
│       └── admin.py      # /reload, /gaps
├── knowledge_base/       # сюда кладёшь свои документы
│   ├── about.txt         # пример: о компании
│   ├── prices.txt        # пример: прайс-лист
│   └── faq.txt           # пример: частые вопросы
└── docker-compose.yml
```

## Стек

- **aiogram 3** — Telegram бот
- **OpenAI-compatible API** — любой провайдер (OpenAI, DeepSeek, Groq, Ollama)
- **ChromaDB** — векторная база данных
- **sentence-transformers** — эмбеддинги (all-MiniLM-L6-v2)
- **pypdf / python-docx** — чтение PDF и DOCX
