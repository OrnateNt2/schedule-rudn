# src/handlers/start_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils.json_db import add_user_if_not_exists, get_user_course, get_user_group, set_user_course
from handlers.settings_handler import settings_command

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user_if_not_exists(user_id)
    course = get_user_course(user_id)
    if course is None:
        # Если курс не выбран, предлагаем выбрать курс (1-6)
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data="set_course:1"),
                InlineKeyboardButton("2", callback_data="set_course:2"),
                InlineKeyboardButton("3", callback_data="set_course:3")
            ],
            [
                InlineKeyboardButton("4", callback_data="set_course:4"),
                InlineKeyboardButton("5", callback_data="set_course:5"),
                InlineKeyboardButton("6", callback_data="set_course:6")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Пожалуйста, выберите ваш курс (1–6):", reply_markup=reply_markup)
    else:
        # Если курс выбран, но группа ещё не установлена, предлагаем настройки
        group = get_user_group(user_id)
        if group is None:
            await settings_command(update, context)
        else:
            await update.message.reply_text("Привет! Используйте команды /today, /tomorrow, /week для получения расписания.")

async def course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")
    if data[0] == "set_course":
        course = data[1]
        set_user_course(query.from_user.id, course)
        await query.edit_message_text(f"Курс установлен: {course}\nТеперь перейдите в /settings для выбора группы и остальных настроек.")

start_handler = CommandHandler("start", start_command)
course_callback_handler = CallbackQueryHandler(course_callback, pattern="^set_course:")

# Экспортируйте оба хендлера для регистрации в bot.py
