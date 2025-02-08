#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, timedelta, date

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Загружаем переменные окружения из файла .env
load_dotenv()

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------- Расписание ---------------------
# В расписании для каждой пары задано время и варианты для нечетной ("odd") и четной ("even") недели.
# Если в расписании пары нет символа "/" (разделитель), то текст один и тот же для обеих недель.
# Если есть разделитель, то до "/" – вариант для нечетной (нижней) недели, после "/" – для четной (верхней).
# Здесь строки должны иметь формат:
# "<Предмет> ; <тип> ; <Преподаватель> ; <аудитория>"
# Например: "Правоведение; лек; Бертовский Лев Владимирович; 1201 м"
schedule = {
    "ПН": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "", "even": ""},
        {"time": "12.00-13.20", "odd": "", "even": ""},
        # Остальные пары можно заполнить по аналогии (или оставить пустыми – будет выводиться "Нет пары")
        {"time": "13.30-14.50", "odd": "", "even": ""},
        {"time": "15.00-16.20", "odd": "", "even": ""},
        {"time": "16.30-17.50", "odd": "", "even": ""},
        {"time": "18.00-19.20", "odd": "", "even": ""},
        {"time": "19.30-20.50", "odd": "", "even": ""},
        {"time": "21:00-22:20", "odd": "", "even": ""},
    ],
    "ВТ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "", "even": ""},
        {"time": "12.00-13.20", "odd": "", "even": ""},
        {"time": "13.30-14.50", "odd": "Древоводство; сем; Роднова А.Д.; АТИ-304", "even": "Древоводство; сем; Роднова А.Д.; АТИ-304"},
        {"time": "15.00-16.20", "odd": "", "even": ""},
        {"time": "16.30-17.50", "odd": "", "even": "Древоводство; лек; Щепелева А.С.; АТИ-зал№2"},
        {"time": "18.00-19.20", "odd": "", "even": ""},
        {"time": "19.30-20.50", "odd": "", "even": ""},
        {"time": "21:00-22:20", "odd": "", "even": ""},
    ],
    "СР": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "Строительство и содержание объектов ЛА; сем; Дубровина Т.А.; АТИ-314", "even": "Строительство и содержание объектов ЛА; сем; Дубровина Т.А.; АТИ-314"},
        {"time": "12.00-13.20", "odd": "Строительство и содержание объектов ЛА; сем; Дубровина Т.А.; АТИ-314", "even": "Строительство и содержание объектов ЛА; сем; Дубровина Т.А.; АТИ-314"},
        {"time": "13.30-14.50", "odd": "Строительство и содержание объектов ЛА; лек; Дмитриева А.Г.; АТИ-зал №2", "even": "Строительство и содержание объектов ЛА; лек; Дмитриева А.Г.; АТИ-зал №2"},
        {"time": "15.00-16.20", "odd": "", "even": ""},
        {"time": "16.30-17.50", "odd": "", "even": ""},
        {"time": "18.00-19.20", "odd": "", "even": ""},
        {"time": "19.30-20.50", "odd": "", "even": ""},
        {"time": "21:00-22:20", "odd": "", "even": ""},
    ],
    "ЧТ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "Немецкий язык ФГОС; сем; Согоян Р.А.; АТИ-335", "even": "Немецкий язык ФГОС; сем; Согоян Р.А.; АТИ-335"},
        {"time": "12.00-13.20", "odd": "Ландшафтное проектирование; лек; Зинченко; АТИ-203", "even": "Ландшафтное проектирование; лек; Зинченко; АТИ-203"},
        {"time": "13.30-14.50", "odd": "Архитектурная графика и основы композиции; лаб; Жукова Т.Е.; АТИ-314", "even": "Архитектурная графика и основы композиции; лаб; Жукова Т.Е.; АТИ-314"},
        {"time": "15.00-16.20", "odd": "", "even": ""},
        {"time": "16.30-17.50", "odd": "", "even": ""},
        {"time": "18.00-19.20", "odd": "", "even": ""},
        {"time": "19.30-20.50", "odd": "", "even": ""},
        {"time": "21:00-22:20", "odd": "", "even": ""},
    ],
    "ПТ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "", "even": ""},
        {"time": "12.00-13.20", "odd": "", "even": ""},
        {"time": "13.30-14.50", "odd": "Ландшафтное проектирование; лаб; Зинченко; АТИ-203", "even": "Ландшафтное проектирование; лаб; Зинченко; АТИ-203"},
        {"time": "15.00-16.20", "odd": "", "even": "Ландшафтное проектирование; лаб; Зинченко; АТИ-203"},
        {"time": "16.30-17.50", "odd": "", "even": ""},
        {"time": "18.00-19.20", "odd": "", "even": ""},
        {"time": "19.30-20.50", "odd": "", "even": ""},
        {"time": "21:00-22:20", "odd": "", "even": ""},
    ],
    "СБ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "", "even": ""},
        {"time": "12.00-13.20", "odd": "", "even": ""},
        {"time": "13.30-14.50", "odd": "", "even": ""},
        {"time": "15.00-16.20", "odd": "", "even": ""},
        {"time": "16.30-17.50", "odd": "", "even": ""},
        {"time": "18.00-19.20", "odd": "", "even": ""},
        {"time": "19.30-20.50", "odd": "", "even": ""},
        {"time": "21:00-22:20", "odd": "", "even": ""},
    ],
}

# Порядок дней недели (используется для навигации и определения даты)
day_order = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ"]

# Для вывода полного названия дня
day_full = {
    "ПН": "Понедельник",
    "ВТ": "Вторник",
    "СР": "Среда",
    "ЧТ": "Четверг",
    "ПТ": "Пятница",
    "СБ": "Суббота",
}

# ------------------ Вспомогательные функции ------------------

def format_time(time_str: str) -> str:
    """Преобразует время вида '9.00' в '09:00'."""
    time_str = time_str.strip().replace('.', ':')
    parts = time_str.split(':')
    if len(parts) == 2:
        hours = parts[0].zfill(2)
        minutes = parts[1].zfill(2)
        return f"{hours}:{minutes}"
    return time_str

def format_time_range(time_range: str) -> str:
    """Преобразует строку '9.00-10.20' в '09:00 до 10:20'."""
    parts = time_range.split('-')
    if len(parts) == 2:
        start = format_time(parts[0])
        end = format_time(parts[1])
        return f"{start} до {end}"
    return time_range

def get_formatted_schedule_text(day_code: str, target_date: date, force_week_type: str = None) -> str:
    """
    Формирует отформатированный текст расписания для дня day_code на дату target_date.
    Если force_week_type задан (значения "even" или "odd"), то используется принудительный выбор.
    В противном случае определяется по номеру недели.
    """
    if force_week_type is None:
        week_number = target_date.isocalendar()[1]
        is_even = (week_number % 2 == 0)
        used_week_type = "even" if is_even else "odd"
        week_label = "верхняя" if is_even else "нижняя"
    else:
        used_week_type = force_week_type
        week_label = "верхняя" if force_week_type == "even" else "нижняя"

    header = f"{day_full.get(day_code, day_code)} ({target_date.strftime('%d.%m.%Y')}, {week_label} неделя):"
    lessons = schedule.get(day_code, [])
    lines = [header]
    for i, lesson in enumerate(lessons, start=1):
        formatted_time = format_time_range(lesson["time"])
        lesson_detail = lesson[used_week_type]
        if not lesson_detail:
            lesson_text = f"{i} пара с {formatted_time}\nНет пары"
        else:
            parts = [p.strip() for p in lesson_detail.split(';')]
            if len(parts) >= 4:
                subject = parts[0]
                lesson_type = parts[1].capitalize()
                teacher = parts[2]
                room = parts[3]
                lesson_text = f"{i} пара с {formatted_time}\n{subject} [{lesson_type}]\n{teacher}\n{room}"
            else:
                lesson_text = f"{i} пара с {formatted_time}\n{lesson_detail}"
        lines.append(lesson_text)
        lines.append("-----")
    return "\n".join(lines)

def get_formatted_week_schedule(monday: date, force_week_type: str = None) -> str:
    """
    Формирует текст расписания на всю неделю (с понедельника по субботу).
    Если force_week_type задан, то для всех дней используется данный вариант.
    """
    texts = []
    for i, day_code in enumerate(day_order):
        target_date = monday + timedelta(days=i)
        text = get_formatted_schedule_text(day_code, target_date, force_week_type)
        texts.append(text)
    return "\n\n".join(texts)

# ------------------- Обработчики команд -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /start – подписывает пользователя и выводит справку."""
    chat_id = update.effective_chat.id
    welcome_text = (
        "Привет!\n"
        "Я бот-расписание. Я ежедневно в 21:00 буду отправлять расписание на завтрашний день.\n"
        "Также доступны следующие команды:\n"
        "/today – расписание на сегодня\n"
        "/tomorrow – расписание на завтра\n"
        "/week – расписание на текущую неделю (с пролистыванием дней)\n"
        "/weekschedule – выбрать вариант недельного расписания\n"
        "Нажмите нужную команду или кнопку ниже."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Расписание на неделю", callback_data="week_0")]
    ])
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выводит расписание на сегодня."""
    today = datetime.now().date()
    weekday = today.weekday()  # 0 – понедельник
    if weekday < len(day_order):
        day_code = day_order[weekday]
        text = get_formatted_schedule_text(day_code, today)
    else:
        text = f"Сегодня ({today.strftime('%d.%m.%Y')}) – выходной, расписание отсутствует."
    await update.message.reply_text(text)

async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выводит расписание на завтра."""
    tomorrow = datetime.now().date() + timedelta(days=1)
    weekday = tomorrow.weekday()
    if weekday < len(day_order):
        day_code = day_order[weekday]
        text = get_formatted_schedule_text(day_code, tomorrow)
    else:
        text = f"Завтра ({tomorrow.strftime('%d.%m.%Y')}) – выходной, расписание отсутствует."
    await update.message.reply_text(text)

async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выводит расписание на текущую неделю с возможностью пролистывать дни (от Понедельника до Субботы)
    с помощью inline-кнопок.
    """
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    text = get_formatted_schedule_text(day_order[0], monday)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Следующий ▶️", callback_data="week_1"),
         InlineKeyboardButton("Закрыть", callback_data="close")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)

async def weekschedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выводит сообщение с кнопками для выбора варианта недельного расписания:
    - Текущая неделя
    - Следующая неделя
    - Верхняя неделя (принудительно четная)
    - Нижняя неделя (принудительно нечетная)
    """
    text = "Выберите вариант расписания на неделю:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Текущая неделя", callback_data="ws_current")],
        [InlineKeyboardButton("Следующая неделя", callback_data="ws_next")],
        [InlineKeyboardButton("Верхняя неделя", callback_data="ws_even")],
        [InlineKeyboardButton("Нижняя неделя", callback_data="ws_odd")],
        [InlineKeyboardButton("Закрыть", callback_data="close")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывод справки по командам."""
    help_text = (
        "Доступные команды:\n"
        "/today – расписание на сегодня\n"
        "/tomorrow – расписание на завтра\n"
        "/week – расписание на текущую неделю (с пролистыванием дней)\n"
        "/weekschedule – выбор варианта недельного расписания\n"
        "/start – старт и справка"
    )
    await update.message.reply_text(help_text)

# ------------------- Обработчик callback-запросов -------------------

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает inline-кнопки:
    - "week_{day_index}" для навигации по дням недели (/week)
    - "ws_*" для выбора варианта недельного расписания (/weekschedule)
    - "close" для закрытия сообщения
    - "ws_back" для возврата к выбору вариантов недельного расписания
    """
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("week_"):
        try:
            day_index = int(data.split("_")[1])
        except (IndexError, ValueError):
            day_index = 0
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        target_date = monday + timedelta(days=day_index)
        text = get_formatted_schedule_text(day_order[day_index], target_date)
        buttons = []
        if day_index > 0:
            buttons.append(InlineKeyboardButton("◀️ Предыдущий", callback_data=f"week_{day_index - 1}"))
        if day_index < len(day_order) - 1:
            buttons.append(InlineKeyboardButton("Следующий ▶️", callback_data=f"week_{day_index + 1}"))
        buttons.append(InlineKeyboardButton("Закрыть", callback_data="close"))
        keyboard = InlineKeyboardMarkup([buttons])
        await query.edit_message_text(text=text, reply_markup=keyboard)

    elif data.startswith("ws_"):
        if data == "ws_current":
            today = datetime.now().date()
            monday = today - timedelta(days=today.weekday())
            week_text = get_formatted_week_schedule(monday)
        elif data == "ws_next":
            today = datetime.now().date()
            monday = today - timedelta(days=today.weekday()) + timedelta(days=7)
            week_text = get_formatted_week_schedule(monday)
        elif data == "ws_even":
            today = datetime.now().date()
            monday = today - timedelta(days=today.weekday())
            week_text = get_formatted_week_schedule(monday, force_week_type="even")
        elif data == "ws_odd":
            today = datetime.now().date()
            monday = today - timedelta(days=today.weekday())
            week_text = get_formatted_week_schedule(monday, force_week_type="odd")
        elif data == "ws_back":
            week_selection_text = "Выберите вариант расписания на неделю:"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Текущая неделя", callback_data="ws_current")],
                [InlineKeyboardButton("Следующая неделя", callback_data="ws_next")],
                [InlineKeyboardButton("Верхняя неделя", callback_data="ws_even")],
                [InlineKeyboardButton("Нижняя неделя", callback_data="ws_odd")],
                [InlineKeyboardButton("Закрыть", callback_data="close")]
            ])
            await query.edit_message_text(text=week_selection_text, reply_markup=keyboard)
            return
        else:
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад", callback_data="ws_back"),
             InlineKeyboardButton("Закрыть", callback_data="close")]
        ])
        await query.edit_message_text(text=week_text, reply_markup=keyboard)

    elif data == "close":
        await query.delete_message()

# ------------------- Ежедневная рассылка -------------------

async def daily_schedule_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Ежедневная задача (в 21:00), которая отправляет подписанным пользователям расписание на завтрашний день.
    Если завтрашний день не попадает в расписание (например, воскресенье), отправляется сообщение о выходном.
    """
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    weekday = tomorrow.weekday()
    if weekday < len(day_order):
        day_code = day_order[weekday]
        text = get_formatted_schedule_text(day_code, tomorrow)
    else:
        text = f"Завтра ({tomorrow.strftime('%d.%m.%Y')}) – выходной, расписание отсутствует."
    # В данном примере рассылка отправляется всем пользователям, подписка может храниться, например, в БД.
    # Здесь для простоты рассылка не реализована (список подписчиков отсутствует).
    # При необходимости можно добавить хранение chat_id и отправлять сообщения через context.bot.send_message(...)
    logger.info("Ежедневная рассылка: " + text)

# ------------------- Основная функция -------------------

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("Не задан TELEGRAM_BOT_TOKEN в файле .env")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("tomorrow", tomorrow_command))
    app.add_handler(CommandHandler("week", week_command))
    app.add_handler(CommandHandler("weekschedule", weekschedule_command))
    app.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчик callback-запросов (inline‑кнопок)
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    # Планируем ежедневную отправку расписания в 21:00 (при необходимости можно доработать отправку подписчикам)
    app.job_queue.run_daily(daily_schedule_job, time=datetime.strptime("21:00", "%H:%M").time())

    app.run_polling()

if __name__ == '__main__':
    main()
