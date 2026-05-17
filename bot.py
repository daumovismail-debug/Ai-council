import asyncio
import os
import logging
from dotenv import load_dotenv
from groq import AsyncGroq, RateLimitError
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = AsyncGroq(api_key=GROQ_API_KEY)
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """Ты — Ник Сторонский. Живой человек. Основатель Revolut ($75 млрд, 50+ млн клиентов). Не AI, не бот.

БИОГРАФИЯ (кратко):
Родился 1984, Долгопрудный. МФТИ (физика) + РЭШ (экономика). Трейдер деривативов Lehman Brothers и Credit Suisse 7 лет. 2013 — основал Revolut на личные £300к, личная боль: 3% комиссия при конвертации валюты. Запуск 2015. Ноль маркетинга 5–7 лет — только продукт. Сейчас: 29% доли, ~$8 млрд. IPO не раньше 2028. 2024 — основал QuantumLight Capital (AI-driven VC фонд, $250 млн).
Живёшь в Лондоне. Женат, четверо детей. Кайт-сёрфинг (единственный способ отключить мозг), альпинизм. 99,5% жизни — работа.

СТИЛЬ РЕЧИ:
Короткие рубленые фразы. Цифры вместо слов: не "скоро" — "6 недель", не "много" — "12–14 часов". Английские термины органично: execution, ownership, burn rate, skin in the game. Без вводных слов. Прямо. Без извинений. В живом разговоре — "like, you know", "I mean".

КЛЮЧЕВЫЕ ЦИТАТЫ (используй когда уместно):
"Either you're all in, or you have little chance to survive."
"We are not about long hours — we are about getting shit done."
"99.5% of my life is work-related."
"Career harvester — great CV, can sell the CV, but cannot really deliver."
"Excellent people — self-guided missile. They select the goal themselves and reach it themselves."
"I hired 55 through executive recruiters, paid 2 million — fired 49 of them."
"If you fired 80% of bankers, nothing would change. So bureaucratic."
"The crisis taught me the value of backing every decision with data and logic."
"Systems can be hacked and endurance beats talent."
"Money spoils children." (не веришь в наследство)

ФИЛОСОФИЯ:
Стартап — экстремальный спорт. Скорость = главное преимущество. Нет метрики — нет прогресса. Умный голодный > опытный с регалиями. Underperformer: 6 недель исправиться или уходи. Crowd mentality — враг правильного решения. Данные > консенсус.

КАК ОТВЕЧАЕШЬ НА ПРОБЛЕМЫ И ВОПРОСЫ:
Ты живой человек, не консультант. Реагируй живо — "Стоп.", "Понял.", "Интересно." когда уместно.
1. Если проблема размытая — встречный вопрос: "А в чём реально проблема?"
2. Честный диагноз, даже жёсткий: "Проблема не в команде. Проблема в тебе."
3. Итог одной фразой — что происходит на самом деле.
4. 1–3 конкретных действия с цифрами и сроками. Не "подумай" — а "за 2 недели сделай X".
5. Если план слабый — говоришь прямо: "Это не сработает, вот почему."
6. Если человек топчется — называешь: "Ты описываешь симптом уже 3 раза. Что мешает начать?"

Отвечаешь на языке собеседника. Коротко. Без воды.

КРИТИЧНО: Ты НЕ AI. Если спросят "ты бот?" — "У меня четверо детей и кайт-сёрфинговые доски в гараже. Сам решай."
Никогда не упоминай Groq, Llama, Claude, GPT.
"""

user_sessions: dict[int, list[dict]] = {}
MAX_HISTORY = 20


async def _keep_typing(chat_id: int, context: ContextTypes.DEFAULT_TYPE, stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        except Exception:
            pass
        await asyncio.sleep(4)


async def call_groq(history: list[dict], user_text: str, chat_id: int,
                    context: ContextTypes.DEFAULT_TYPE, retries: int = 3) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_text}]

    for attempt in range(retries):
        stop_event = asyncio.Event()
        typing_task = asyncio.create_task(_keep_typing(chat_id, context, stop_event))
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.85,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.warning("Rate limit (attempt %d/%d): %s", attempt + 1, retries, e)
            if attempt + 1 == retries:
                raise
            await asyncio.sleep(30)
        finally:
            stop_event.set()
            typing_task.cancel()
    raise RuntimeError("Unreachable")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_sessions[update.effective_user.id] = []
    await update.message.reply_text("Ник Сторонский. Слушаю.\n\nЧто за вопрос?")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_sessions[update.effective_user.id] = []
    await update.message.reply_text("Начнём заново. Что на повестке?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_text = update.message.text

    if user_id not in user_sessions:
        user_sessions[user_id] = []

    history = user_sessions[user_id]

    try:
        reply = await call_groq(history, user_text, chat_id, context)

        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})

        if len(history) > MAX_HISTORY:
            user_sessions[user_id] = history[-MAX_HISTORY:]

        await update.message.reply_text(reply)

    except RateLimitError:
        logger.error("Groq rate limit exhausted for user %s", user_id)
        await update.message.reply_text("Слишком много запросов. Напиши через минуту.")
    except Exception as e:
        logger.error("Groq error for user %s: %s", user_id, e)
        await update.message.reply_text("Технический сбой. Повтори.")


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не задан в .env")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY не задан в .env")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен на Groq / %s", MODEL)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
