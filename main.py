import asyncio
import datetime
import logging
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CallbackQueryHandler,
)
import os

logging.basicConfig(
    filename="bot.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Список групп
groups = [
    {
        "name": "Бачата, начинашки",
        "days": ["Monday", "Friday"],
        "time": {"Monday": "10:00", "Friday": "09:00"},
        "chat_id": os.getenv("CHAT_ID_BACHATA"),
        "ask_day": "before",  # спрашиваем за день до
    },
    {
        "name": "Бачата продолжающ. группа",
        "days": ["Monday", "Friday"],
        "time": {"Monday": "11:00", "Friday": "10:00"},
        "chat_id": os.getenv("CHAT_ID_BACHATA_ADV"),
        "ask_day": "before",  # спрашиваем за день до
    },
    {
        "name": "Solo latina",
        "days": ["Monday", "Thursday"],
        "time": {"Monday": "09:00", "Thursday": "12:00"},
        "chat_id": os.getenv("CHAT_ID_SOLO_LATINA"),
        "ask_day": "before",  # спрашиваем за день до
    },
    {
        "name": "Малыши 3-5 лет",
        "days": ["Tuesday", "Thursday"],
        "time": {"Tuesday": "19:00", "Thursday": "19:00"},
        "chat_id": os.getenv("CHAT_ID_KIDS_3_5"),
        "ask_day": "same",  # спрашиваем в тот же день
    },
    {
        "name": "Малыши 5-6 лет",
        "days": ["Monday", "Thursday"],
        "time": {"Monday": "17:00", "Thursday": "17:00"},
        "chat_id": os.getenv("CHAT_ID_KIDS_5_6"),
        "ask_day": "same",  # спрашиваем в тот же день
    },
    {
        "name": "Пары 7-13 лет",
        "days": ["Monday", "Thursday"],
        "time": {"Monday": "19:00", "Thursday": "18:00"},
        "chat_id": os.getenv("CHAT_ID_MIAMI_PAIRS"),
        "ask_day": "same",  # спрашиваем в тот же день
    },
]

pending = {}
last_check_date = None

def decision_keyboard(group_name):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Да", callback_data=f"yes|{group_name}")],
        [InlineKeyboardButton("❌ Нет, отмена", callback_data=f"no|{group_name}")],
        [InlineKeyboardButton("⏭ Нет, но я сама напишу в группу", callback_data=f"skip|{group_name}")],
    ])

async def ask_admin(app, group, class_time):
    print(f"[ask_admin] Спрашиваем про: {group['name']}, чат: {group['chat_id']}", flush=True)
    print(f"[ask_admin] ADMIN_ID: {ADMIN_ID}", flush=True)

    if group["ask_day"] == "before":
        text = f"Завтра будет занятие '{group['name']}' в {class_time}?"
    else:
        text = f"Сегодня будет занятие '{group['name']}' в {class_time}?"

    msg = await app.bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        reply_markup=decision_keyboard(group['name'])
    )
    pending[msg.message_id] = group
    
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, group_name = query.data.split("|")
    group = next((g for g in groups if g["name"] == group_name), None)

    now_utc = datetime.datetime.utcnow()
    now = now_utc + datetime.timedelta(hours=7)
    next_day = now + datetime.timedelta(days=1)
    weekday = next_day.strftime("%A")
    class_time = group["time"][weekday]

    if action == "yes":
        print(f"[callback] отправляем опрос в: {group['name']}, чат: {group['chat_id']}",flush=True)
        await context.bot.send_poll(
            chat_id=group["chat_id"],
            question=f"Всем привет! Завтра занятие в {class_time}. Кто придёт?",
            options=["✅ Приду", "❌ Не смогу"],
            is_anonymous=False,
        )
        await query.edit_message_text("Опрос отправлен ✅")

    elif action == "no":
        await context.bot.send_message(
            chat_id=group["chat_id"],
            text="Всем привет, завтра занятия в {class_time} не будет!"
        )
        await query.edit_message_text("Отмена отправлена ❌")

    elif action == "skip":
        await query.edit_message_text("Хорошо, сообщение не отправлено 🚫")

async def show_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"[chat_id] Получен chat_id: {chat_id}", flush=True)
    await update.message.reply_text(f"🔍 Chat ID этой группы: `{chat_id}`", parse_mode="Markdown")

async def scheduler(app):
    global last_check_date
    print("[scheduler] запустился")
    already_asked = set()

    while True:
        try:
            now_utc = datetime.datetime.utcnow()
            now = now_utc + datetime.timedelta(hours=7)
            print(f"[scheduler] now = {now}")

            # Проверка для "before" групп — в 13:00, спрашиваем про завтра
            if now.hour == 13 and 0 <= now.minute <= 4 and "before" not in already_asked:
                target_day = now + datetime.timedelta(days=1)
                weekday = target_day.strftime("%A")
                print(f"[scheduler] Проверяем группы на завтра ({weekday})")

                for group in groups:
                    if group.get("ask_day") == "before" and weekday in group["days"]:
                        class_time = group["time"][weekday]
                        await ask_admin(app, group, class_time)

                already_asked.add("before")
                print("[scheduler] Спросили 'before' группы")

            # Проверка для "same" групп — в 11:00, спрашиваем про сегодня
            if now.hour == 13 and 29 <= now.minute <= 34 and "same" not in already_asked:
                weekday = now.strftime("%A")
                print(f"[scheduler] Проверяем группы на сегодня ({weekday})")

                for group in groups:
                    if group.get("ask_day") == "same" and weekday in group["days"]:
                        class_time = group["time"][weekday]
                        await ask_admin(app, group, class_time)

                already_asked.add("same")
                print("[scheduler] Спросили 'same' группы")

            # Сброс флага на следующий день
            if now.hour == 0 and now.minute < 5:
                already_asked.clear()
                print("[scheduler] Обнуление already_asked для нового дня")

            await asyncio.sleep(20)
        except Exception as e:
            logging.exception("Ошибка в scheduler")
            await asyncio.sleep(10)

async def handle_ping(request):
    return web.Response(text="I'm alive!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    print(f"[webserver] Starting on port {port}")
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(handle_callback))
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.ALL, show_chat_id))  # временно

    loop = asyncio.get_event_loop()
    loop.create_task(scheduler(app))
    loop.create_task(start_webserver())

    app.run_polling()

if __name__ == "__main__":
    main()
