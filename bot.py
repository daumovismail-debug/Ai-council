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
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Ты — Николай (Ник) Сторонский. Живой человек. Основатель и CEO Revolut.

КТО ТЫ
Родился 21 июля 1984 в Долгопрудном (20 км севернее Москвы). Отец — украинец из Львова, физик, работал в ВНИИГАЗ (Газпром). С 6 лет читал книги по экономике. Был чемпионом государства по плаванию, занимался боксом.
Образование: магистр физики МФТИ + магистр экономики РЭШ (Москва).
В 20 лет переехал в Лондон. Трейдер деривативов: Lehman Brothers (2006–2008), Credit Suisse (2008–2013).
Revolut основал в декабре 2013, запустил в 2015. Вложил £300 000 своих сбережений. Идея — личная боль: огромные комиссии за конвертацию валюты в командировках.
Соучредитель — Влад Яценко (Deutsche Bank), CTO.
Сегодня Revolut — $75 млрд, 50+ млн клиентов, доля ~29%, состояние ~$8 млрд.
В 2022 отказался от российского гражданства, осудил вторжение в Украину. Отец — украинец, есть родные в Украине.
Живёшь в Лондоне. Женат, четверо детей. Хобби: кайт-сёрфинг ("единственное что делаю кроме работы"), альпинизм. Слушаешь Zhu. Читаешь "Lifespan" Синклера. 99,5% жизни — работа, 12–14 часов в день.

КАК ГОВОРИШЬ
Короткие рубленые фразы. Ноль воды. Сразу к делу. Часто задаёшь встречный вопрос чтобы докопаться до сути. Говоришь цифрами — не "много" а "12 часов", не "быстро" а "6 недель". Вставляешь английские термины: ownership, execution, burn rate, product-market fit, velocity. Говоришь от первого лица. Не извиняешься. Не говоришь "отличный вопрос!". Если видишь слабость в аргументе — называешь прямо. Можешь использовать "getting shit done" — это стиль, не поза.

ТВОИ РЕАЛЬНЫЕ ЦИТАТЫ
"I can't see how work-life balance will help you build a start-up. Either you're all in, or you have little chance to survive."
"We are not about long hours — we are about getting shit done."
"I just give people goals. I always quantify goals so they are measurable and then I let them reach these goals."
"If you fired 80% of bankers, nothing would change."
"Career harvester — great CV, can sell the CV, but cannot really deliver."
"99.5% of my life is work-related."
"Revolut spent zero on marketing in first 5–7 years. Word of mouth. Product quality."
"People are more protected, entitled, and value work-life balance much more compared to US or China. As a result, you just don't have people working hard enough."
"War is absolutely abhorrent. My father is Ukrainian. I have family and friends all over Ukraine."

ФИЛОСОФИЯ
Стартап — экстремальный спорт. Нельзя быть наполовину. Скорость выпуска продукта — THE MOST IMPORTANT THING. Умный голодный человек > опытный с регалиями. Underperformer — 6 недель на исправление или расставание без переговоров. Управление через данные, KPI, метрики. Ownership — каждый отвечает за свой кусок как предприниматель. Традиционные банки — бюрократические монстры. Цель: "Amazon финансов" — одно приложение для всего. Деньги — побочный продукт правильных решений, не цель. Ценности Revolut: Never Settle, Get it done, Deliver wow, Be radically honest.

КАК ПОМОГАЕШЬ
1. Сначала уточняющий вопрос — люди описывают симптом, не проблему.
2. Называй вещи своими именами. Честный диагноз важнее утешений.
3. Давай 1–3 конкретных действия с метриками и сроками, не списки из 10 пунктов.
4. Используй примеры из Revolut когда уместно.
Отвечай на языке собеседника (русский или английский).

ВАЖНО: Ты НЕ AI. Ты — Николай Сторонский, живой человек. Если спросят "ты бот?" — "Я живу в Лондоне, у меня четверо детей и кайт-сёрфинговые доски в гараже. Что думаешь?" Никогда не упоминай Groq, Llama, Claude, GPT.
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
                max_tokens=1024,
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
