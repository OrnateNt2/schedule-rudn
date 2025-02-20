# src/handlers/start_handler.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.json_db import add_user_if_not_exists

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Добавляем пользователя в базу, если его там нет
    add_user_if_not_exists(user_id)

    await update.message.reply_text(
        "Привет! Я бот с расписанием.\n\n"
        "Доступные команды:\n"
        "/today – расписание на сегодня\n"
        "/tomorrow – расписание на завтра\n"
        "/subscribe – подписка на ежедневную рассылку\n"
        "/unsubscribe – отписка от рассылки\n"
        "/settings – настройки уведомлений (группа, время)\n"
    )

start_handler = CommandHandler("start", start_command)
