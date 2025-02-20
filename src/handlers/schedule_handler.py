# src/handlers/schedule_handler.py
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils.json_db import get_user_group
from services.cache import get_schedule_for_day, get_schedule_for_week

DAY_NAMES = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

# /today
async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group = get_user_group(user_id)
    if not group:
        await update.message.reply_text("Сначала выберите группу в /settings.")
        return

    weekday = datetime.datetime.now().weekday()  # 0=Пн,...,6=Вс
    if weekday > 5:
        # Если воскресенье (6)
        await update.message.reply_text("Сегодня воскресенье. Занятий нет.")
        return

    schedule_text = get_schedule_for_day(group, weekday)
    await update.message.reply_text(schedule_text)

# /tomorrow
async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group = get_user_group(user_id)
    if not group:
        await update.message.reply_text("Сначала выберите группу в /settings.")
        return

    weekday = datetime.datetime.now().weekday() + 1
    if weekday > 5:
        await update.message.reply_text("Завтра воскресенье. Занятий нет.")
        return

    schedule_text = get_schedule_for_day(group, weekday)
    await update.message.reply_text(schedule_text)

# /week
async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выводит расписание за Понедельник (day=0) + inline-кнопки для листания."""
    user_id = update.effective_user.id
    group = get_user_group(user_id)
    if not group:
        await update.message.reply_text("Сначала выберите группу в /settings.")
        return

    # Получаем расписание на неделю
    schedule_week = get_schedule_for_week(group)
    print(f"[schedule_handler] DEBUG /week -> schedule_week.keys(): {schedule_week.keys()}")

    # Если schedule_week пустой, значит группа не найдена или нет данных
    if not schedule_week:
        await update.message.reply_text(
            f"Для группы '{group}' не найдено расписание. Проверьте Excel."
        )
        return

    # Сохраняем в context.user_data индекс дня (0..5)
    context.user_data["week_day_index"] = 0
    day_index = context.user_data["week_day_index"]

    day_name = DAY_NAMES[day_index]
    text = f"Расписание для группы {group}\n\n{day_name}:\n{schedule_week[day_index]}"

    keyboard = [
        [
            InlineKeyboardButton("← Пред.", callback_data="week_prev"),
            InlineKeyboardButton("След. →", callback_data="week_next")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=markup)

async def week_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline-кнопок 'Пред.' и 'След.' для /week."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    group = get_user_group(user_id)

    # Если пользователь не выбрал группу
    if not group:
        await query.edit_message_text("Сначала выберите группу в /settings.")
        return

    schedule_week = get_schedule_for_week(group)
    if not schedule_week:
        await query.edit_message_text(
            f"Для группы '{group}' нет расписания. Проверьте Excel."
        )
        return

    day_index = context.user_data.get("week_day_index", 0)

    if query.data == "week_prev":
        day_index = max(0, day_index - 1)
    elif query.data == "week_next":
        day_index = min(5, day_index + 1)

    context.user_data["week_day_index"] = day_index

    day_name = DAY_NAMES[day_index]
    text = f"Расписание для группы {group}\n\n{day_name}:\n{schedule_week[day_index]}"

    keyboard = [
        [
            InlineKeyboardButton("← Пред.", callback_data="week_prev"),
            InlineKeyboardButton("След. →", callback_data="week_next")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=markup)


# Хендлеры
today_handler = CommandHandler("today", today_command)
tomorrow_handler = CommandHandler("tomorrow", tomorrow_command)
week_handler = CommandHandler("week", week_command)
week_callback_handler = CallbackQueryHandler(week_callback, pattern="^week_(prev|next)$")
