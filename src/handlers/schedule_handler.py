# src/handlers/schedule_handler.py
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils.json_db import get_user_group, get_user_course, get_user_program, get_user_language
from services.cache import get_schedule_for_day, get_schedule_for_week, get_next_week_type

DAY_NAMES = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group = get_user_group(user_id)
    course = get_user_course(user_id)
    program = get_user_program(user_id)
    language = get_user_language(user_id)
    if not course:
        await update.message.reply_text("Сначала выберите ваш курс, используя /start.")
        return
    if not group:
        await update.message.reply_text("Сначала выберите группу и настройки в /settings.")
        return
    weekday = datetime.datetime.now().weekday()
    if weekday > 5:
        await update.message.reply_text("Сегодня выходной.")
        return
    schedule_text = get_schedule_for_day(group, weekday, course, program=program, language=language)
    await update.message.reply_text(schedule_text)

async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group = get_user_group(user_id)
    course = get_user_course(user_id)
    program = get_user_program(user_id)
    language = get_user_language(user_id)
    if not course:
        await update.message.reply_text("Сначала выберите ваш курс, используя /start.")
        return
    if not group:
        await update.message.reply_text("Сначала выберите группу и настройки в /settings.")
        return
    weekday = datetime.datetime.now().weekday() + 1
    if weekday > 5:
        await update.message.reply_text("Завтра выходной.")
        return
    schedule_text = get_schedule_for_day(group, weekday, course, program=program, language=language)
    await update.message.reply_text(schedule_text)

async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group = get_user_group(user_id)
    course = get_user_course(user_id)
    program = get_user_program(user_id)
    language = get_user_language(user_id)
    if not course:
        await update.message.reply_text("Сначала выберите курс, используя /start.")
        return
    if not group:
        await update.message.reply_text("Сначала выберите группу и настройки в /settings.")
        return
    schedule_week = get_schedule_for_week(group, course, program=program, language=language)
    context.user_data["week_day_index"] = 0
    day_index = context.user_data["week_day_index"]
    day_name = DAY_NAMES[day_index]
    text = f"Расписание для группы {group} (курс {course}) на текущую неделю:\n\n{day_name}:\n{schedule_week.get(day_index, 'На этот день нет занятий.')}"
    keyboard = [
        [
            InlineKeyboardButton("← Пред.", callback_data="week_prev"),
            InlineKeyboardButton("След. →", callback_data="week_next")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=markup)

async def nextweek_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /nextweek показывает расписание, но для следующей недели (с противоположной четностью).
    """
    user_id = update.effective_user.id
    group = get_user_group(user_id)
    course = get_user_course(user_id)
    program = get_user_program(user_id)
    language = get_user_language(user_id)
    if not course:
        await update.message.reply_text("Сначала выберите курс, используя /start.")
        return
    if not group:
        await update.message.reply_text("Сначала выберите группу и настройки в /settings.")
        return
    next_week_type = get_next_week_type()
    schedule_week = get_schedule_for_week(group, course, program=program, language=language, week_type=next_week_type)
    context.user_data["week_day_index"] = 0
    day_index = context.user_data["week_day_index"]
    day_name = DAY_NAMES[day_index]
    week_label = "Верхняя" if next_week_type == "upper" else "Нижняя"
    text = f"Расписание для группы {group} (курс {course}) на следующую неделю ({week_label}):\n\n{day_name}:\n{schedule_week.get(day_index, 'На этот день нет занятий.')}"
    keyboard = [
        [
            InlineKeyboardButton("← Пред.", callback_data="nweek_prev"),
            InlineKeyboardButton("След. →", callback_data="nweek_next")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=markup)

async def week_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    group = get_user_group(user_id)
    course = get_user_course(user_id)
    program = get_user_program(user_id)
    language = get_user_language(user_id)
    if not course or not group:
        await query.edit_message_text("Сначала выберите курс и группу в /settings.")
        return
    schedule_week = get_schedule_for_week(group, course, program=program, language=language)
    day_index = context.user_data.get("week_day_index", 0)
    if query.data == "week_prev":
        day_index = max(0, day_index - 1)
    elif query.data == "week_next":
        day_index = min(5, day_index + 1)
    context.user_data["week_day_index"] = day_index
    day_name = DAY_NAMES[day_index]
    text = f"Расписание для группы {group} (курс {course}) на текущую неделю:\n\n{day_name}:\n{schedule_week.get(day_index, 'На этот день нет занятий.')}"
    keyboard = [
        [
            InlineKeyboardButton("← Пред.", callback_data="week_prev"),
            InlineKeyboardButton("След. →", callback_data="week_next")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=markup)

async def nextweek_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    group = get_user_group(user_id)
    course = get_user_course(user_id)
    program = get_user_program(user_id)
    language = get_user_language(user_id)
    if not course or not group:
        await query.edit_message_text("Сначала выберите курс и группу в /settings.")
        return
    next_week_type = get_next_week_type()
    schedule_week = get_schedule_for_week(group, course, program=program, language=language, week_type=next_week_type)
    day_index = context.user_data.get("week_day_index", 0)
    if query.data == "nweek_prev":
        day_index = max(0, day_index - 1)
    elif query.data == "nweek_next":
        day_index = min(5, day_index + 1)
    context.user_data["week_day_index"] = day_index
    day_name = DAY_NAMES[day_index]
    week_label = "Верхняя" if next_week_type == "upper" else "Нижняя"
    text = f"Расписание для группы {group} (курс {course}) на следующую неделю ({week_label}):\n\n{day_name}:\n{schedule_week.get(day_index, 'На этот день нет занятий.')}"
    keyboard = [
        [
            InlineKeyboardButton("← Пред.", callback_data="nweek_prev"),
            InlineKeyboardButton("След. →", callback_data="nweek_next")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=markup)

today_handler = CommandHandler("today", today_command)
tomorrow_handler = CommandHandler("tomorrow", tomorrow_command)
week_handler = CommandHandler("week", week_command)
nextweek_handler = CommandHandler("nextweek", nextweek_command)
week_callback_handler = CallbackQueryHandler(week_callback, pattern="^week_(prev|next)$")
nextweek_callback_handler = CallbackQueryHandler(nextweek_callback, pattern="^nweek_(prev|next)$")
