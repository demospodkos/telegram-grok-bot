# Telegram Grok Bot + Image Generation

Telegram-бот на базе **Grok (xAI)** с генерацией изображений через Flux.

## Возможности

- Свободное общение через Grok (режим без стандартных моральных ограничений)
- Генерация изображений по текстовому описанию (Flux.1-schnell)
- Удобное меню с кнопками
- Команды `/start` и `/image`

## Быстрый старт

### 1. Получи ключи

- **Telegram Bot Token** — у [@BotFather](https://t.me/BotFather)
- **xAI API Key** — [console.x.ai](https://console.x.ai/)
- **Together.ai API Key** — [api.together.xyz](https://api.together.xyz/) (для генерации картинок)

### 2. Установка

```bash
git clone https://github.com/demospodkos/telegram-grok-bot.git
cd telegram-grok-bot
pip install -r requirements.txt
```

### 3. Настройка

Открой `bot.py` и замени:

```python
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
XAI_API_KEY = "ВАШ_XAI_API_KEY"
TOGETHER_API_KEY = "ВАШ_TOGETHER_API_KEY"
```

### 4. Запуск

```bash
python bot.py
```

Бот готов к работе.

## Структура

- `bot.py` — основной код
- `requirements.txt` — зависимости

## Примечания

- Режим без цензуры включён по умолчанию в системном промпте.
- Жёсткие запреты остаются только на контент с несовершеннолетними и прямые инструкции по реальным преступлениям.
- Для продакшена лучше вынести ключи в `.env` и использовать `python-dotenv`.
