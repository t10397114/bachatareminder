from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from cachetools import TTLCache
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import (
    ContextTypes,
)

import bot
from config import ADMIN_ID, TIMEZONE, logger
from config import GROUPS

processed_callbacks = TTLCache(maxsize=1000, ttl=86400)

def decision_keyboard(group_name):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Да", callback_data=f"yes|{group_name}")],
        [InlineKeyboardButton("❌ Нет, отмена", callback_data=f"no|{group_name}")],
        [InlineKeyboardButton("⏭ Нет, но я сама напишу в группу", callback_data=f"skip|{group_name}")],
    ])


async def ask_admin(group, class_time):
    logger.info(f"[ask_admin] Спрашиваем про: {group['name']}, чат: {group['chat_id']}, ADMIN_ID: {ADMIN_ID}")

    if group["ask_day"] == "before":
        text = f"Завтра будет занятие '{group['name']}' в {class_time}?"
    else:
        text = f"Сегодня будет занятие '{group['name']}' в {class_time}?"

    try:
        await bot.app.bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            reply_markup=decision_keyboard(group['name'])
        )
    except Exception as e:
        logger.info(f"[ask_admin] Ошибка при отправке сообщения: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, group_name = query.data.split("|")

    # проверяем на дубликат
    now = datetime.now(TIMEZONE)
    day = now.strftime("%Y-%m-%d")
    callback_key = f"{day}|{group_name}"
    if callback_key in processed_callbacks:
        logger.info(f"[callback] Already processed callback: {callback_key}")
        return
    processed_callbacks[callback_key] = True

    group = next((g for g in GROUPS if g["name"] == group_name), None)
    now = datetime.now(ZoneInfo("Asia/Novosibirsk"))
    if group["ask_day"] == "before":
        now = now + timedelta(days=1)
        day_word = "Завтра"
    else:
        day_word = "Сегодня"

    weekday = now.strftime("%A")

    class_time = group["time"][weekday]

    try:
        if action == "yes":
            logger.info(f"[callback] отправляем опрос в: {group['name']}, чат: {group['chat_id']}")
            await context.bot.send_poll(
                chat_id=group["chat_id"],
                question=f"Всем привет! {day_word} занятие в {class_time}. Кто придёт?",
                options=["✅ Приду", "❌ Не смогу"],
                is_anonymous=False,
            )
            await query.edit_message_text("Опрос отправлен ✅")

        elif action == "no":
            await context.bot.send_message(
                chat_id=group["chat_id"],
                text=f"Всем привет! {day_word} занятия в {class_time} не будет."
            )
            await query.edit_message_text("Отмена отправлена ❌")

        elif action == "skip":
            await query.edit_message_text("Хорошо, сообщение не отправлено 🚫")
    except Exception as e:
        logger.info(f"[callback] Ошибка при отправке сообщения: {e}")
