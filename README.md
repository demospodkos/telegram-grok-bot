# Telegram Free AI Bot (Groq + Pollinations)

Бесплатный Telegram-бот с ИИ-чатом и генерацией изображений.

- **Текст** — через Groq (очень быстро, бесплатный тариф)
- **Картинки** — через Pollinations.ai (бесплатно)
- Режим без стандартных моральных ограничений

## Где взять ключи (всё бесплатно)

### 1. Telegram Bot Token
- Открой [@BotFather](https://t.me/BotFather)
- `/newbot` или возьми существующий токен

### 2. Groq API Key (текст)
1. Зайди на [console.groq.com](https://console.groq.com)
2. Зарегистрируйся (можно через Google/GitHub)
3. Перейди в **API Keys** → Create API Key
4. Скопируй ключ  
**Карта не нужна.**

### 3. Картинки
Ключ **не нужен**. Используется бесплатный Pollinations.ai.

## Установка

```bash
git clone https://github.com/demospodkos/telegram-grok-bot.git
cd telegram-grok-bot
pip install -r requirements.txt
```

## Настройка

1. Создай файл `.env`:
```bash
cp .env.example .env
```

2. Вставь ключи в `.env`:
```env
BOT_TOKEN=твой_токен_от_BotFather
GROQ_API_KEY=твой_ключ_Groq
```

3. Запусти:
```bash
python bot.py
```

## Если модель на Groq не работает

В файле `bot.py` поменяй строку:

```python
TEXT_MODEL = "llama-3.3-70b-versatile"
```

На одну из актуальных бесплатных (смотри в console.groq.com):
- `"openai/gpt-oss-120b"`
- `"openai/gpt-oss-20b"`
- `"qwen/qwen3.8-27b"`

## Важно

- Файл `.env` не коммить в Git
- Rate-лимиты на free-тарифах есть (обычно хватает для личного использования)
- Pollinations иногда тормозит при большой нагрузке — просто подожди и попробуй снова
