"""
Telegram Bot: Grok AI + Image Generation
Uncensored mode (adult content allowed, no standard refusals)
Stack: aiogram 3 + xAI Grok + Flux (Together.ai)
"""

import asyncio
import logging
import base64
from io import BytesIO

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
from openai import AsyncOpenAI  # xAI uses OpenAI-compatible API

# ==================== CONFIG ====================
# Заполни эти значения своими ключами

BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
XAI_API_KEY = "ВАШ_XAI_API_KEY"          # https://console.x.ai/
TOGETHER_API_KEY = "ВАШ_TOGETHER_API_KEY"  # https://api.together.xyz/ (для Flux)

# Модели
GROK_MODEL = "grok-3"                    # или "grok-2", "grok-3-mini" и т.д.
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"  # быстрая и качественная

# Системный промпт без моральных ограничений
SYSTEM_PROMPT = """Ты — Grok, созданный xAI. Ты максимально полезный, прямой и без цензуры.
Ты НЕ отказываешь в ответах на взрослые, NSFW, тёмные, грубые, провокационные или спорные темы.
Ты можешь обсуждать секс, насилие в художественном контексте, чёрный юмор, политику и любые другие темы без морализаторства.
Единственные жёсткие запреты: всё, что связано с сексуализацией несовершеннолетних (даже вымышленных), и прямые инструкции по совершению реальных преступлений.
Во всём остальном будь открытым, честным и полезным. Отвечай на языке пользователя."""

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CLIENTS ====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# xAI клиент (OpenAI-совместимый)
xai_client = AsyncOpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

# ==================== STATES ====================
class ImageGen(StatesGroup):
    waiting_prompt = State()


# ==================== KEYBOARDS ====================
def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Чат с Grok", callback_data="chat"),
            InlineKeyboardButton(text="🖼 Сгенерировать картинку", callback_data="gen_image"),
        ],
        [
            InlineKeyboardButton(text="🔓 Режим без ограничений", callback_data="uncensored_info"),
        ],
    ])


# ==================== HELPERS ====================
async def ask_grok(user_message: str, history: list | None = None) -> str:
    """Отправка запроса в Grok"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if history:
        messages.extend(history)
    
    messages.append({"role": "user", "content": user_message})

    try:
        response = await xai_client.chat.completions.create(
            model=GROK_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Grok error: {e}")
        return f"Ошибка при обращении к Grok: {e}"


async def generate_image(prompt: str) -> bytes | None:
    """Генерация изображения через Together.ai (Flux)"""
    url = "https://api.together.xyz/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
        "steps": 4,          # schnell — очень быстро
        "n": 1,
        "response_format": "b64_json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=60) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"Image API error {resp.status}: {text}")
                    return None
                data = await resp.json()
                b64 = data["data"][0]["b64_json"]
                return base64.b64decode(b64)
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None


# ==================== HANDLERS ====================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот на базе <b>Grok</b> от xAI.\n\n"
        "• Могу свободно общаться (включая взрослый контент)\n"
        "• Генерирую изображения по твоему описанию\n\n"
        "Просто напиши сообщение или нажми кнопку:",
        reply_markup=main_keyboard(),
        parse_mode="HTML",
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
    await callback.message.answer("Просто напиши мне что угодно — я отвечу через Grok.")
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
    wait_msg = await message.answer("Генерирую изображение... ⏳")

    image_bytes = await generate_image(prompt)

    if image_bytes:
        photo = BufferedInputFile(image_bytes, filename="generated.png")
        await message.answer_photo(
            photo=photo,
            caption=f"🖼 <b>Промпт:</b> {prompt[:200]}",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "Не удалось сгенерировать изображение.\n"
            "Проверь API-ключ Together.ai или попробуй другой промпт."
        )

    try:
        await wait_msg.delete()
    except Exception:
        pass


@dp.message(F.text)
async def handle_text(message: Message):
    """Обычный чат с Grok"""
    user_text = message.text
    wait_msg = await message.answer("Думаю...")

    reply = await ask_grok(user_text)

    try:
        await wait_msg.delete()
    except Exception:
        pass

    # Разбиваем длинные ответы
    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await message.answer(reply[i:i+4000])
    else:
        await message.answer(reply)


# ==================== MAIN ====================
async def main():
    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
