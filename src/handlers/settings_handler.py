# src/handlers/settings_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils.json_db import set_user_group, set_user_notification_time, set_user_program, set_user_language, get_user_group
from services.cache import get_all_groups, get_available_languages

PROGRAM_OPTIONS = ["ФГОС", "МП"]
NOTIFICATION_TIMES = ["07:00", "08:00", "09:00", "10:00"]

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = get_all_groups()
    if not groups:
        await update.message.reply_text("Не удалось загрузить группы из расписания.")
        return

    keyboard = [
        [InlineKeyboardButton(text=g, callback_data=f"set_group:{g}") for g in groups],
        [InlineKeyboardButton(text=p, callback_data=f"set_program:{p}") for p in PROGRAM_OPTIONS],
        [InlineKeyboardButton(text=t, callback_data=f"set_time:{t}") for t in NOTIFICATION_TIMES],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите группу, программу (ФГОС/МП) и время уведомлений.\nПосле выбора программы будет предложен выбор языка.",
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
        response = f"Группа установлена: {value}"
    elif action == "set_time":
        set_user_notification_time(query.from_user.id, value)
        response = f"Время уведомлений установлено: {value}"
    elif action == "set_program":
        set_user_program(query.from_user.id, value)
        response = f"Программа установлена: {value}"
        group = get_user_group(query.from_user.id)
        if group:
            langs = get_available_languages(group, program=value)
            if langs:
                lang_buttons = [InlineKeyboardButton(text=lang, callback_data=f"set_language:{lang}") for lang in langs]
                keyboard = [[btn] for btn in lang_buttons]
                reply_markup = InlineKeyboardMarkup(keyboard)
                response += "\nВыберите язык:"
                await query.edit_message_text(response, reply_markup=reply_markup)
                return
            else:
                response += "\nДоступных языков не найдено."
    elif action == "set_language":
        set_user_language(query.from_user.id, value)
        response = f"Язык установлен: {value}"

    await query.edit_message_text(response)

settings_handler = CommandHandler("settings", settings_command)
settings_callback_handler = CallbackQueryHandler(settings_callback, pattern="^(set_group|set_time|set_program|set_language):")
