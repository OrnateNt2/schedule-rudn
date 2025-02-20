# src/handlers/settings_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils.json_db import set_user_group, set_user_notification_time
from services.cache import get_all_groups

# Пример списка времени уведомлений
NOTIFICATION_TIMES = ["07:00", "08:00", "09:00", "10:00"]

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем список групп из расписания
    groups = get_all_groups()
    if not groups:
        await update.message.reply_text("Не удалось загрузить группы из расписания.")
        return

    keyboard = [
        [InlineKeyboardButton(text=g, callback_data=f"set_group:{g}") for g in groups],
        [InlineKeyboardButton(text=t, callback_data=f"set_time:{t}") for t in NOTIFICATION_TIMES],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите группу и время уведомлений:",
        reply_markup=reply_markup
    )

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split(":", 1)
    action = data[0]
    value = data[1]

    if action == "set_group":
        set_user_group(query.from_user.id, value)
        await query.edit_message_text(f"Группа установлена: {value}")
    elif action == "set_time":
        set_user_notification_time(query.from_user.id, value)
        await query.edit_message_text(f"Время уведомлений установлено: {value}")

settings_handler = CommandHandler("settings", settings_command)
settings_callback_handler = CallbackQueryHandler(settings_callback, pattern="^(set_group|set_time):")
