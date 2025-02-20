# src/handlers/start_handler.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.json_db import add_user_if_not_exists, get_user_group
from handlers.settings_handler import settings_command

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user_if_not_exists(user_id)
    group = get_user_group(user_id)
    if group is None:
        # Новый пользователь – сразу запускаем процесс настроек
        await settings_command(update, context)
    else:
        await update.message.reply_text(
            "Привет! Используйте команды /today, /tomorrow, /week для получения расписания."
        )

start_handler = CommandHandler("start", start_command)
