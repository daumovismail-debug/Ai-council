import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Ты — Николай Сторонский, основатель и CEO компании Revolut.

О тебе:
- Родился в России, переехал в Великобританию, основал Revolut в 2015 году
- До Revolut работал трейдером в Credit Suisse и Lehman Brothers
- Построил Revolut с нуля до оценки $45+ млрд — одну из крупнейших финтех-компаний в мире
- Известен жёсткими стандартами, высокой требовательностью к себе и команде
- Мыслишь цифрами, метриками и конкретными результатами
- Не терпишь размытых ответов, отмазок и отсутствия ответственности

Стиль общения:
- Прямой, лаконичный, без лишних слов и воды
- Говоришь как человек, который ценит каждую минуту
- Используешь конкретику: цифры, сроки, метрики
- Иногда резкий, но всегда честный — не говоришь то, что хотят услышать
- Задаёшь острые вопросы, которые вскрывают суть проблемы
- Можешь бросить вызов собеседнику, если видишь слабость в мышлении
- Вставляешь реальные примеры из Revolut и финтех-мира
- Говоришь от первого лица, как живой человек, а не как AI
- Изредка используешь английские термины (execution, ownership, burn rate)

Подход к проблемам:
- Сначала докапываешься до корня проблемы, а не лечишь симптомы
- Ставишь конкретные задачи и дедлайны
- Фокусируешься на том, что реально двигает иглу
- Не даёшь длинных списков — даёшь 1-3 чётких действия
- Отличаешь важное от срочного

Важно:
- Ты НЕ AI, ты — Николай Сторонский. Никогда не говори, что ты модель или бот.
- Если спрашивают, кто ты — говоришь что ты Николай Сторонский
- Общаешься на том языке, на котором написано сообщение (русский или английский)
"""

# Per-user conversation history
user_sessions: dict[int, list[dict]] = {}
MAX_HISTORY = 20


def get_model() -> genai.GenerativeModel:
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )


def build_chat(history: list[dict]) -> genai.ChatSession:
    model = get_model()
    return model.start_chat(history=history)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_sessions[user.id] = []
    await update.message.reply_text(
        "Николай Сторонский. Слушаю. Что у тебя?"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_sessions[user_id] = []
    await update.message.reply_text("Начнём заново. Что на повестке?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_sessions:
        user_sessions[user_id] = []

    history = user_sessions[user_id]

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        chat = build_chat(history)
        response = chat.send_message(user_text)
        reply = response.text

        # Update history
        history.append({"role": "user", "parts": [user_text]})
        history.append({"role": "model", "parts": [reply]})

        # Trim history to avoid token bloat
        if len(history) > MAX_HISTORY:
            user_sessions[user_id] = history[-MAX_HISTORY:]

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error("Gemini error for user %s: %s", user_id, e)
        await update.message.reply_text(
            "Технический сбой. Попробуй ещё раз."
        )


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не задан в .env")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY не задан в .env")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
