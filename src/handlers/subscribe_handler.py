# src/handlers/subscribe_handler.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.json_db import set_user_subscribe_status, set_user_notification_time
# Если нужно, импортируйте и add_user_if_not_exists, чтобы гарантировать наличие пользователя
from utils.json_db import add_user_if_not_exists

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user_if_not_exists(user_id)
    # Устанавливаем время оповещения по умолчанию на 20:00
    set_user_notification_time(user_id, "20:00")
    set_user_subscribe_status(user_id, True)
    await update.message.reply_text("Вы подписаны на ежедневную рассылку расписания на 20:00.\nИзменить время можно в /settings.")

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    set_user_subscribe_status(user_id, False)
    await update.message.reply_text("Вы отписаны от ежедневной рассылки расписания.")

subscribe_handler = CommandHandler("subscribe", subscribe_command)
unsubscribe_handler = CommandHandler("unsubscribe", unsubscribe_command)
