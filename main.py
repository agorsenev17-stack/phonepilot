
import os
import json
import traceback
from pathlib import Path
from aiohttp import web, ClientSession

TOKEN = os.environ["TELEGRAM_TOKEN"]
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

CATALOG_PATH = Path(__file__).parent / "phones.json"

users = {}


async def telegram(method, data):
    async with ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/{method}",
            json=data
        ) as response:
            result = await response.json()

            if not result.get("ok"):
                print("Telegram API error:", result)

            return result


async def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        data["reply_markup"] = {
            "inline_keyboard": keyboard
        }

    await telegram("sendMessage", data)


def main_keyboard():
    return [
        [
            {"text": "📱 Подобрать телефон", "callback_data": "start"}
        ],
        [
            {"text": "⚖️ Сравнить модели", "callback_data": "compare"}
        ],
        [
            {"text": "💰 Стоит ли покупать?", "callback_data": "worth"}
        ]
    ]


def budget_keyboard():
    return [
        [
            {"text": "До 15 000 ₽", "callback_data": "budget:15000"},
            {"text": "15–30 тыс. ₽", "callback_data": "budget:30000"}
        ],
        [
            {"text": "30–50 тыс. ₽", "callback_data": "budget:50000"},
            {"text": "50–80 тыс. ₽", "callback_data": "budget:80000"}
        ],
        [
            {"text": "80–120 тыс. ₽", "callback_data": "budget:120000"},
            {"text": "Бюджет не важен", "callback_data": "budget:999999"}
        ]
    ]


def usage_keyboard():
    return [
        [
            {"text": "📸 Камера", "callback_data": "usage:camera"},
            {"text": "🎮 Игры", "callback_data": "usage:games"}
        ],
        [
            {"text": "🔋 Батарея", "callback_data": "usage:battery"},
            {"text": "⚡ Производительность", "callback_data": "usage:power"}
        ],
        [
            {"text": "🌟 Универсальный", "callback_data": "usage:all"}
        ]
    ]


def load_phones():
    print("Загрузка каталога:", CATALOG_PATH)

    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Файл phones.json не найден: {CATALOG_PATH}"
        )

    with open(CATALOG_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Корень phones.json должен быть объектом")

    phones = data.get("phones")

    if not isinstance(phones, list):
        raise ValueError(
            "В phones.json отсутствует список phones"
        )

    if not phones:
        raise ValueError("Каталог смартфонов пуст")

    for index, phone in enumerate(phones):
        if not isinstance(phone, dict):
            raise ValueError(
                f"Некорректная запись смартфона №{index + 1}"
            )

    print("Каталог успешно загружен. Смартфонов:", len(phones))

    return phones


def recommend(budget, usage):
    phones = load_phones()

    keywords = {
        "camera": ["фотографии", "камера", "портреты", "видео"],
        "games": ["игры", "производительность"],
        "battery": ["автономность"],
        "power": ["производительность", "скорость"],
        "all": []
    }

    selected = keywords.get(usage, [])

    if selected:
        matched = []

        for phone in phones:
            strengths = phone.get("strengths", [])

            if not isinstance(strengths, list):
                strengths = []

            strengths_text = " ".join(
                str(item) for item in strengths
            ).lower()

            if any(word in strengths_text for word in selected):
                matched.append(phone)
    else:
        matched = phones

    if not matched:
        matched = phones

    result = []

    for phone in matched[:4]:
        result.append(
            f"{phone.get('brand', 'Неизвестный бренд')} "
            f"{phone.get('model', 'Неизвестная модель')}\n"
            f"Процессор: {phone.get('processor', 'Не указан')}\n"
            f"Экран: {phone.get('display', 'Не указан')}\n"
            f"Камера: {phone.get('main_camera', 'Не указана')}\n"
            f"Батарея: {phone.get('battery', 'Не указана')}\n"
            f"Память: {phone.get('memory', 'Не указана')}"
        )

    return result


async def handle_callback(update):
    query = update["callback_query"]
    chat_id = query["message"]["chat"]["id"]
    user_id = query["from"]["id"]
    action = query["data"]

    await telegram("answerCallbackQuery", {
        "callback_query_id": query["id"]
    })

    if action == "start":
        users[user_id] = {}

        await send_message(
            chat_id,
            "💰 Какой у тебя бюджет на смартфон?",
            budget_keyboard()
        )

    elif action.startswith("budget:"):
        budget = int(action.split(":")[1])

        users.setdefault(user_id, {})["budget"] = budget

        await send_message(
            chat_id,
            "Отлично! А что для тебя важнее всего?",
            usage_keyboard()
        )

    elif action.startswith("usage:"):
        usage = action.split(":")[1]

        user = users.get(user_id, {})
        budget = user.get("budget", 999999)

        try:
            models = recommend(budget, usage)

            if not models:
                result = "Пока не нашёл подходящих смартфонов."

            else:
                result = "🎯 ТВОЯ ПОДБОРКА СМАРТФОНОВ\n\n"

                for number, model in enumerate(models, 1):
                    result += f"{number}. {model}\n\n"

                result += (
                    "Подборка составлена по назначению смартфона.\n"
                    "Цены и соответствие бюджету пока уточняются.\n\n"
                    "Попробуем подобрать ещё раз?"
                )

        except Exception:
            print("ОШИБКА ПРИ ПОДБОРЕ СМАРТФОНОВ:")
            traceback.print_exc()

            result = (
                "Не удалось загрузить каталог смартфонов. "
                "Попробуй немного позже."
            )

        await send_message(
            chat_id,
            result,
            main_keyboard()
        )

    elif action == "compare":
        await send_message(
            chat_id,
            "⚖️ Функция сравнения готовится!\n\n"
            "Скоро можно будет сравнивать смартфоны "
            "по камере, процессору, батарее и другим параметрам.",
            main_keyboard()
        )

    elif action == "worth":
        await send_message(
            chat_id,
            "💰 Скоро можно будет отправить модель "
            "и цену, а PhonePilot оценит, "
            "стоит ли покупать этот смартфон.",
            main_keyboard()
        )


async def handle_update(request):
    if request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    ) != WEBHOOK_SECRET:
        raise web.HTTPForbidden()

    try:
        update = await request.json()

        if "callback_query" in update:
            await handle_callback(update)

        elif "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            if text.startswith("/start"):
                await send_message(
                    chat_id,
                    "👋 Привет! Я PhonePilot.\n\n"
                    "Помогу выбрать смартфон "
                    "под твои задачи и бюджет.\n\n"
                    "Начнём?",
                    main_keyboard()
                )

            else:
                await send_message(
                    chat_id,
                    "Выбери нужную функцию в меню 👇",
                    main_keyboard()
                )

    except Exception:
        print("ОШИБКА ОБРАБОТКИ TELEGRAM UPDATE:")
        traceback.print_exc()

    return web.Response(text="OK")


async def on_startup(app):
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if render_url:
        result = await telegram("setWebhook", {
            "url": f"{render_url}/webhook",
            "secret_token": WEBHOOK_SECRET,
            "allowed_updates": ["message", "callback_query"]
        })

        print("Webhook:", result)


app = web.Application()

app.router.add_post("/webhook", handle_update)

app.router.add_get(
    "/",
    lambda request: web.Response(
        text="PhonePilot is running!"
    )
)

app.on_startup.append(on_startup)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)
