# src/handlers/subscribe_handler.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.json_db import set_user_subscribe_status

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    set_user_subscribe_status(user_id, True)
    await update.message.reply_text("Вы подписались на ежедневную рассылку расписания.")

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    set_user_subscribe_status(user_id, False)
    await update.message.reply_text("Вы отписались от ежедневной рассылки расписания.")

subscribe_handler = CommandHandler("subscribe", subscribe_command)
unsubscribe_handler = CommandHandler("unsubscribe", unsubscribe_command)
