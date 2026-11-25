import os
import traceback
from aiohttp import web, ClientSession


TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

PORT = int(os.environ.get("PORT", 10000))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

user_budgets = {}


# КАТАЛОГ СМАРТФОНОВ

PHONES = [
    {
        "brand": "Apple",
        "model": "iPhone 16",
        "processor": "Apple A18",
        "display": "6.1 OLED",
        "battery": "3561 мА·ч",
        "main_camera": "48 МП",
        "memory": "128/256/512 ГБ",
        "strengths": ["Видео", "Производительность", "Экосистема"]
    },
    {
        "brand": "Samsung",
        "model": "Galaxy S25",
        "processor": "Snapdragon 8 Elite",
        "display": "6.2 AMOLED 120 Гц",
        "battery": "4000 мА·ч",
        "main_camera": "50 МП",
        "memory": "128/256/512 ГБ",
        "strengths": ["Камера", "Компактность", "Универсальность"]
    },
    {
        "brand": "Xiaomi",
        "model": "Xiaomi 15",
        "processor": "Snapdragon 8 Elite",
        "display": "6.36 AMOLED 120 Гц",
        "battery": "5240 мА·ч",
        "main_camera": "50 МП",
        "memory": "256/512 ГБ",
        "strengths": ["Камера", "Производительность", "Экран"]
    },
    {
        "brand": "POCO",
        "model": "POCO X7 Pro",
        "processor": "Dimensity 8400 Ultra",
        "display": "6.67 AMOLED 120 Гц",
        "battery": "6000 мА·ч",
        "main_camera": "50 МП",
        "memory": "256/512 ГБ",
        "strengths": ["Игры", "Автономность", "Производительность"]
    },
    {
        "brand": "OnePlus",
        "model": "OnePlus 13",
        "processor": "Snapdragon 8 Elite",
        "display": "6.82 AMOLED 120 Гц",
        "battery": "6000 мА·ч",
        "main_camera": "50 МП",
        "memory": "256/512 ГБ/1 ТБ",
        "strengths": ["Скорость", "Экран", "Автономность"]
    },
    {
        "brand": "Google",
        "model": "Pixel 9",
        "processor": "Google Tensor G4",
        "display": "6.3 OLED 120 Гц",
        "battery": "4700 мА·ч",
        "main_camera": "50 МП",
        "memory": "128/256 ГБ",
        "strengths": ["Фотографии", "Чистый Android", "ИИ-функции"]
    },
    {
        "brand": "realme",
        "model": "GT 7 Pro",
        "processor": "Snapdragon 8 Elite",
        "display": "6.78 AMOLED 120 Гц",
        "battery": "6500 мА·ч",
        "main_camera": "50 МП",
        "memory": "256/512 ГБ",
        "strengths": ["Игры", "Автономность", "Производительность"]
    },
    {
        "brand": "HONOR",
        "model": "200 Pro",
        "processor": "Snapdragon 8s Gen 3",
        "display": "6.78 OLED 120 Гц",
        "battery": "5200 мА·ч",
        "main_camera": "50 МП",
        "memory": "512 ГБ",
        "strengths": ["Портреты", "Камера", "Дизайн"]
    }
]


# ОТПРАВКА ЗАПРОСОВ TELEGRAM

async def telegram(method, data):
    async with ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/{method}",
            json=data
        ) as response:
            result = await response.json()

            if not result.get("ok"):
                print("Ошибка Telegram API:", result)

            return result


# ГЛАВНОЕ МЕНЮ

async def show_start(chat_id):
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "📱 Подобрать телефон",
                    "callback_data": "start"
                }
            ]
        ]
    }

    await telegram("sendMessage", {
        "chat_id": chat_id,
        "text": (
            "👋 Добро пожаловать в PhonePilot!\n\n"
            "Я помогу подобрать смартфон под твои задачи "
            "и бюджет.\n\n"
            "Нажми кнопку ниже, чтобы начать."
        ),
        "reply_markup": keyboard
    })


# ВЫБОР БЮДЖЕТА

async def show_budgets(chat_id):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "До 15 000 ₽", "callback_data": "budget:15000"},
                {"text": "До 30 000 ₽", "callback_data": "budget:30000"}
            ],
            [
                {"text": "До 50 000 ₽", "callback_data": "budget:50000"},
                {"text": "До 80 000 ₽", "callback_data": "budget:80000"}
            ],
            [
                {"text": "До 120 000 ₽", "callback_data": "budget:120000"},
                {"text": "Бюджет не ограничен", "callback_data": "budget:999999"}
            ]
        ]
    }

    await telegram("sendMessage", {
        "chat_id": chat_id,
        "text": "💰 Какой у тебя бюджет на смартфон?",
        "reply_markup": keyboard
    })


# ВЫБОР НАЗНАЧЕНИЯ

async def show_usage(chat_id):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📸 Камера и фотографии", "callback_data": "usage:camera"}
            ],
            [
                {"text": "🎮 Игры", "callback_data": "usage:games"}
            ],
            [
                {"text": "🔋 Автономность", "callback_data": "usage:battery"}
            ],
            [
                {"text": "⚡ Производительность", "callback_data": "usage:power"}
            ],
            [
                {"text": "🌟 Для всего", "callback_data": "usage:all"}
            ]
        ]
    }

    await telegram("sendMessage", {
        "chat_id": chat_id,
        "text": "🎯 Для чего тебе нужен смартфон?",
        "reply_markup": keyboard
    })


# ПОДБОР СМАРТФОНОВ

def recommend(budget, usage):

    keywords = {
        "camera": [
            "фотографии", "камера", "портреты", "видео"
        ],
        "games": [
            "игры", "производительность"
        ],
        "battery": [
            "автономность"
        ],
        "power": [
            "производительность", "скорость"
        ],
        "all": []
    }

    suitable = []

    for phone in PHONES:

        strengths = phone["strengths"]

        if usage == "all":
            suitable.append(phone)
            continue

        score = 0

        for strength in strengths:
            for keyword in keywords[usage]:
                if keyword.lower() in strength.lower():
                    score += 1

        if score > 0:
            suitable.append(phone)

    if not suitable:
        suitable = PHONES

    result = (
        "🤖 **Результаты PhonePilot**\n\n"
        f"💰 Твой бюджет: до {budget:,} ₽\n\n"
    )

    result = result.replace(",", " ")

    result += "Вот смартфоны, которые стоит рассмотреть:\n\n"

    for phone in suitable[:4]:

        result += (
            f"📱 **{phone['brand']} {phone['model']}**\n"
            f"⚙️ Процессор: {phone['processor']}\n"
            f"🖥 Экран: {phone['display']}\n"
            f"🔋 Аккумулятор: {phone['battery']}\n"
            f"📷 Камера: {phone['main_camera']}\n"
            f"💾 Память: {phone['memory']}\n"
            f"⭐ Сильные стороны: {', '.join(phone['strengths'])}\n\n"
        )

    result += (
        "ℹ️ Пока каталог не содержит актуальных цен, "
        "поэтому бюджет используется как ориентир, "
        "а не как точный фильтр по стоимости.\n\n"
        "Выбирай смартфон с учётом своих задач."
    )

    return result


# ОБРАБОТКА КНОПОК

async def handle_callback(callback):

    callback_id = callback["id"]
    data = callback.get("data", "")
    chat_id = callback["message"]["chat"]["id"]
    user_id = callback["from"]["id"]

    await telegram("answerCallbackQuery", {
        "callback_query_id": callback_id
    })

    try:

        if data == "start":
            await show_budgets(chat_id)

        elif data.startswith("budget:"):

            budget = int(data.split(":")[1])
            user_budgets[user_id] = budget

            await show_usage(chat_id)

        elif data.startswith("usage:"):

            usage = data.split(":")[1]
            budget = user_budgets.get(user_id, 30000)

            result = recommend(budget, usage)

            await telegram("sendMessage", {
                "chat_id": chat_id,
                "text": result,
                "parse_mode": "Markdown"
            })

            await telegram("sendMessage", {
                "chat_id": chat_id,
                "text": "Хочешь подобрать другой смартфон?",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "🔄 Подобрать ещё раз",
                                "callback_data": "start"
                            }
                        ]
                    ]
                }
            })

    except Exception as error:

        print("ОШИБКА ПОДБОРА:")
        traceback.print_exc()

        await telegram("sendMessage", {
            "chat_id": chat_id,
            "text": (
                "❌ Произошла ошибка:\n"
                f"{type(error).__name__}: {error}"
            )
        })


# ОБРАБОТКА СООБЩЕНИЙ

async def handle_message(message):

    text = message.get("text", "")
    chat_id = message["chat"]["id"]

    if text == "/start":
        await show_start(chat_id)


# WEBHOOK

async def webhook(request):

    secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if secret != WEBHOOK_SECRET:
        return web.Response(status=403)

    try:
        update = await request.json()

        if "message" in update:
            await handle_message(update["message"])

        elif "callback_query" in update:
            await handle_callback(update["callback_query"])

    except Exception:
        traceback.print_exc()

    return web.Response(text="OK")


# ПРОВЕРКА РАБОТЫ СЕРВЕРА

async def health(request):
    return web.Response(text="PhonePilot is running!")


# УСТАНОВКА WEBHOOK

async def on_startup(app):

    if not RENDER_URL:
        print("RENDER_EXTERNAL_URL не найден")
        return

    webhook_url = f"{RENDER_URL}/webhook"

    result = await telegram("setWebhook", {
        "url": webhook_url,
        "secret_token": WEBHOOK_SECRET
    })

    print("Установка webhook:", result)


# ЗАПУСК СЕРВЕРА

app = web.Application()

app.router.add_get("/", health)
app.router.add_post("/webhook", webhook)

app.on_startup.append(on_startup)


if __name__ == "__main__":
    web.run_app(
        app,
        host="0.0.0.0",
        port=PORT
    )
