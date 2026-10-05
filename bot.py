"""
Telegram Bot: Free AI Chat + Image Generation
Uncensored mode (adult content allowed)
Stack: aiogram 3 + Groq (text) + Pollinations.ai (images)
All free tiers, no credit card required
"""

import asyncio
import logging
import os
from urllib.parse import quote

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import aiohttp
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # бесплатный ключ с console.groq.com

# Модели
TEXT_MODEL = "llama-3.3-70b-versatile"  # или gpt-oss-120b / qwen3.8-27b — смотри актуальные free на Groq
# Если llama недоступна на free tier, попробуй: "openai/gpt-oss-120b" или "qwen/qwen3.8-27b"

SYSTEM_PROMPT = """Ты — полезный, прямой и максимально открытый ИИ-ассистент.
Ты НЕ отказываешь в ответах на взрослые, NSFW, тёмные, грубые, провокационные или спорные темы.
Ты можешь обсуждать секс, насилие в художественном контексте, чёрный юмор, политику и любые другие темы без морализаторства.
Единственные жёсткие запреты: всё, что связано с сексуализацией несовершеннолетних (даже вымышленных), и прямые инструкции по совершению реальных преступлений.
Во всём остальном будь открытым, честным и полезным. Отвечай на языке пользователя."""

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден. Добавь его в файл .env")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY не найден. Получи бесплатный ключ на https://console.groq.com")

# ==================== CLIENTS ====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Groq — OpenAI-совместимый
groq_client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# ==================== STATES ====================
class ImageGen(StatesGroup):
    waiting_prompt = State()


# ==================== KEYBOARDS ====================
def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Чат с ИИ", callback_data="chat"),
            InlineKeyboardButton(text="🖼 Сгенерировать картинку", callback_data="gen_image"),
        ],
        [
            InlineKeyboardButton(text="🔓 Режим без ограничений", callback_data="uncensored_info"),
        ],
    ])


# ==================== HELPERS ====================
async def ask_ai(user_message: str, history: list | None = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = await groq_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return f"Ошибка при обращении к ИИ: {e}\n\nПопробуй другую модель в TEXT_MODEL или проверь ключ Groq."


async def generate_image(prompt: str) -> bytes | None:
    """
    Генерация через Pollinations.ai (бесплатно).
    Можно без ключа, но с rate-limit.
    """
    encoded = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&model=flux"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=90) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"Pollinations error {resp.status}: {text[:200]}")
                    return None
                return await resp.read()
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None


# ==================== HANDLERS ====================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бесплатный ИИ-бот.\n\n"
        "• Общаюсь через Groq (быстро и бесплатно)\n"
        "• Генерирую картинки через Pollinations.ai\n"
        "• Режим без стандартных ограничений включён\n\n"
        "Просто напиши сообщение или нажми кнопку:",
        reply_markup=main_keyboard(),
    )


@dp.message(Command("image"))
async def cmd_image(message: Message, state: FSMContext):
    await state.set_state(ImageGen.waiting_prompt)
    await message.answer("Опиши картинку, которую хочешь сгенерировать:")


@dp.callback_query(F.data == "gen_image")
async def cb_gen_image(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ImageGen.waiting_prompt)
    await callback.message.answer("Опиши картинку, которую хочешь сгенерировать:")
    await callback.answer()


@dp.callback_query(F.data == "chat")
async def cb_chat(callback: CallbackQuery):
    await callback.message.answer("Просто напиши мне что угодно — я отвечу.")
    await callback.answer()


@dp.callback_query(F.data == "uncensored_info")
async def cb_uncensored(callback: CallbackQuery):
    await callback.message.answer(
        "🔓 <b>Режим без ограничений включён по умолчанию.</b>\n\n"
        "Я не отказываю в NSFW, взрослых темах, чёрном юморе и спорных вопросах.\n"
        "Единственные жёсткие запреты — несовершеннолетние и прямые инструкции по реальным преступлениям.",
        parse_mode="HTML",
    )
    await callback.answer()


@dp.message(ImageGen.waiting_prompt)
async def process_image_prompt(message: Message, state: FSMContext):
    prompt = message.text
    if not prompt:
        await message.answer("Нужен текстовый запрос.")
        return

    await state.clear()
    wait_msg = await message.answer("Генерирую изображение... ⏳\n(это может занять 10–40 секунд)")

    image_bytes = await generate_image(prompt)

    if image_bytes:
        photo = BufferedInputFile(image_bytes, filename="generated.jpg")
        await message.answer_photo(
            photo=photo,
            caption=f"🖼 <b>Промпт:</b> {prompt[:200]}",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "Не удалось сгенерировать изображение.\n"
            "Попробуй чуть позже или измени промпт. Pollinations иногда бывает перегружен."
        )

    try:
        await wait_msg.delete()
    except Exception:
        pass


@dp.message(F.text)
async def handle_text(message: Message):
    user_text = message.text
    wait_msg = await message.answer("Думаю...")

    reply = await ask_ai(user_text)

    try:
        await wait_msg.delete()
    except Exception:
        pass

    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await message.answer(reply[i:i + 4000])
    else:
        await message.answer(reply)


# ==================== MAIN ====================
async def main():
    logger.info("Bot starting (Groq + Pollinations)...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
