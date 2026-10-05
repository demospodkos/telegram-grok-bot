# Telegram Grok Bot + Image Generation

Telegram-бот на базе **Grok (xAI)** с генерацией изображений через Flux.

## Возможности

- Свободное общение через Grok (режим без стандартных моральных ограничений)
- Генерация изображений по текстовому описанию (Flux.1-schnell)
- Удобное меню с кнопками
- Команды `/start` и `/image`

## Где взять ключи

### 1. Telegram Bot Token
1. Открой [@BotFather](https://t.me/BotFather)
2. Создай бота командой `/newbot` или возьми токен существующего
3. Скопируй токен

### 2. xAI API Key (Grok)
1. Зайди на [console.x.ai](https://console.x.ai)
2. Зарегистрируйся / войди
3. Перейди в раздел **API Keys**
4. Создай новый ключ и сразу скопируй его (показывается только один раз)
5. Обычно нужно добавить платёжный метод и кредиты

### 3. Together.ai API Key (картинки)
1. Зайди на [api.together.ai](https://api.together.ai) или [together.ai](https://together.ai)
2. Зарегистрируйся
3. Перейди в Settings → API Keys
4. Создай ключ и скопируй
5. Обычно нужно пополнить баланс (минимум ~$5)

## Установка

```bash
git clone https://github.com/demospodkos/telegram-grok-bot.git
cd telegram-grok-bot
pip install -r requirements.txt
```

## Настройка

1. Скопируй пример файла окружения:
```bash
cp .env.example .env
```

2. Открой файл `.env` и вставь свои ключи:
```env
BOT_TOKEN=твой_токен_от_BotFather
XAI_API_KEY=твой_ключ_xAI
TOGETHER_API_KEY=твой_ключ_Together.ai
```

3. Запусти бота:
```bash
python bot.py
```

## Важно

- Файл `.env` **не** должен попадать в GitHub
- Никогда не публикуй свои ключи
- Режим без цензуры включён по умолчанию
