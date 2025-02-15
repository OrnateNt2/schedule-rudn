#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import json
from datetime import datetime, timedelta, date

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Загружаем переменные окружения из файла .env (где хранится ваш TELEGRAM_BOT_TOKEN)
load_dotenv()

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------- Глобальные переменные и расписание --------------

SUBSCRIBERS_FILE = "subscribers.json"

# Чтобы хранить пользователей в памяти (словарь вида:
# { "chat_id": {"username": "...", "subscribed": True/False}, ... })
subscribers = {}

# Заранее загрузим подписчиков из JSON (если файл есть)
def load_subscribers():
    global subscribers
    if os.path.isfile(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
            subscribers = json.load(f)
    else:
        subscribers = {}

def save_subscribers():
    global subscribers
    with open(SUBSCRIBERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(subscribers, f, ensure_ascii=False, indent=4)

# Загрузим подписчиков при старте
load_subscribers()


# ------------------- Расписание (пример) ---------------------
schedule = {
    "ПН": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
    ],
    "ВТ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "", "even": ""},
        {"time": "12.00-13.20", "odd": "", "even": ""},
        {"time": "13.30-14.50", "odd": "Древоводство; сем; Роднова А.Д.; АТИ-304", "even": "Древоводство; сем; Роднова А.Д.; АТИ-304"},
        {"time": "15.00-16.20", "odd": "", "even": ""},
        {"time": "16.30-17.50", "odd": "Древоводство; лек; Щепелева А.С.; АТИ-зал№2", "even": ""},
    ],
    "СР": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "Строительство и содержание объектов ЛА; сем; Дубровина Т.А.; АТИ-314", "even": "Строительство и содержание объектов ЛА; сем; Дубровина Т.А.; АТИ-314"},
        {"time": "12.00-13.20", "odd": "Строительство и содержание объектов ЛА; сем; Дубровина Т.А.; АТИ-314", "even": "Строительство и содержание объектов ЛА; сем; Дубровина Т.А.; АТИ-314"},
        {"time": "13.30-14.50", "odd": "Строительство и содержание объектов ЛА; лек; Дмитриева А.Г.; АТИ-зал №2", "even": "Строительство и содержание объектов ЛА; лек; Дмитриева А.Г.; АТИ-зал №2"},
    ],
    "ЧТ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "Немецкий язык ФГОС; сем; Согоян Р.А.; АТИ-335", "even": "Немецкий язык ФГОС; сем; Согоян Р.А.; АТИ-335"},
        {"time": "12.00-13.20", "odd": "Ландшафтное проектирование; лек; Зинченко; АТИ-203", "even": "Ландшафтное проектирование; лек; Зинченко; АТИ-203"},
        {"time": "13.30-14.50", "odd": "Архитектурная графика и основы композиции; лаб; Жукова Т.Е.; АТИ-314", "even": "Архитектурная графика и основы композиции; лаб; Жукова Т.Е.; АТИ-314"},
    ],
    "ПТ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "", "even": ""},
        {"time": "12.00-13.20", "odd": "", "even": ""},
        {"time": "13.30-14.50", "odd": "Ландшафтное проектирование; лаб; Зинченко; АТИ-203", "even": "Ландшафтное проектирование; лаб; Зинченко; АТИ-203"},
        {"time": "15.00-16.20", "odd": "Ландшафтное проектирование; лаб; Зинченко; АТИ-203", "even": ""},
    ],
    "СБ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
    ],
}

day_order = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ"]
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
    """Преобразует '9.00-10.20' в '09:00 до 10:20'."""
    parts = time_range.split('-')
    if len(parts) == 2:
        start = format_time(parts[0])
        end = format_time(parts[1])
        return f"{start} до {end}"
    return time_range

def get_formatted_schedule_text(day_code: str, target_date: date, force_week_type: str = None) -> str:
    """
    Формирует текст расписания для day_code на дату target_date.
    force_week_type = "even" или "odd" для явной установки верхней/нижней недели.
    Если force_week_type не задано, вычисляем по номеру недели (isocalendar).
    """
    if force_week_type is None:
        week_number = target_date.isocalendar()[1]
        is_even = (week_number % 2 == 1)
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
    """Формирует текст расписания на всю неделю (ПН–СБ)."""
    texts = []
    for i, day_code in enumerate(day_order):
        target_date = monday + timedelta(days=i)
        text = get_formatted_schedule_text(day_code, target_date, force_week_type)
        texts.append(text)
    return "\n\n".join(texts)

# ------------------- Обработчики команд -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое приветствие + краткая справка."""
    welcome_text = (
        "Привет!\n"
        "Я бот-расписание. Я могу присылать расписание раз в день (в 21:00) и/или чаще.\n\n"
        "Команды:\n"
        "/subscribe – подписка на рассылку\n"
        "/unsubscribe – отписка\n"
        "/today – расписание на сегодня\n"
        "/tomorrow – расписание на завтра\n"
        "/week – расписание на текущую неделю\n"
        "/weekschedule – выбор варианта недели (чет/нечет и т.д.)\n"
        "/help – все команды\n"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка по командам."""
    help_text = (
        "Доступные команды:\n"
        "/subscribe – подписаться на рассылку\n"
        "/unsubscribe – отписаться от рассылки\n\n"
        "/today – расписание на сегодня\n"
        "/tomorrow – расписание на завтра\n"
        "/week – расписание на текущую неделю (с пролистыванием)\n"
        "/weekschedule – варианты недельного расписания (верхняя/нижняя)\n"
        "/help – справка\n"
    )
    await update.message.reply_text(help_text)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подписка на рассылку: записываем/обновляем в JSON."""
    global subscribers
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "NoName"

    # Обновляем данные
    subscribers[str(chat_id)] = {
        "username": username,
        "subscribed": True
    }
    save_subscribers()
    await update.message.reply_text("Вы успешно подписались на рассылку!")

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отписка от рассылки: ставим subscribed = False (или удаляем)."""
    global subscribers
    chat_id = update.effective_chat.id
    if str(chat_id) in subscribers:
        subscribers[str(chat_id)]["subscribed"] = False
        save_subscribers()
        await update.message.reply_text("Вы отписались от рассылки.")
    else:
        await update.message.reply_text("Вас нет в списке подписчиков. Вы не подписаны.")

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    weekday = today.weekday()  # 0 – понедельник
    if weekday < len(day_order):
        day_code = day_order[weekday]
        text = get_formatted_schedule_text(day_code, today)
    else:
        text = f"Сегодня ({today.strftime('%d.%m.%Y')}) – выходной, расписание отсутствует."
    await update.message.reply_text(text)

async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    Расписание на неделю с пролистыванием дней (ПН–СБ) через inline-кнопки.
    """
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    text = get_formatted_schedule_text(day_order[0], monday)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Следующий ▶️", callback_data="week_1"),
            InlineKeyboardButton("Закрыть", callback_data="close")
        ]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)

async def weekschedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выбор варианта расписания на неделю:
    - Текущая неделя
    - Следующая неделя
    - Верхняя (even)
    - Нижняя (odd)
    """
    text = "Выберите вариант расписания на неделю:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Текущая неделя", callback_data="ws_current")],
        [InlineKeyboardButton("Следующая неделя", callback_data="ws_next")],
        [InlineKeyboardButton("Верхняя неделя (even)", callback_data="ws_even")],
        [InlineKeyboardButton("Нижняя неделя (odd)", callback_data="ws_odd")],
        [InlineKeyboardButton("Закрыть", callback_data="close")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)


# ------------------- Обработчик callback-запросов -------------------

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        else:
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Закрыть", callback_data="close")]
        ])
        await query.edit_message_text(text=week_text, reply_markup=keyboard)

    elif data == "close":
        await query.delete_message()


# ------------------- Функции рассылки -------------------

async def broadcast_daily_schedule(context: ContextTypes.DEFAULT_TYPE):
    """
    Раз в сутки (21:00): отправляем подписчикам расписание на завтра.
    """
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    weekday = tomorrow.weekday()

    if weekday < len(day_order):
        day_code = day_order[weekday]
        text = get_formatted_schedule_text(day_code, tomorrow)
    else:
        text = f"Завтра ({tomorrow.strftime('%d.%m.%Y')}) – выходной, расписание отсутствует."

    # Рассылаем только подписанным
    for chat_id, info in subscribers.items():
        if info.get("subscribed"):
            try:
                await context.bot.send_message(chat_id=int(chat_id), text=text)
            except Exception as e:
                logger.warning(f"Не удалось отправить сообщение {chat_id}: {e}")

async def broadcast_test(context: ContextTypes.DEFAULT_TYPE):
    """
    Пример: рассылаем сообщение каждые 10 секунд (можно отключить, если не нужно).
    """
    text = "Тестовая рассылка каждые 10 секунд (демо)."

    for chat_id, info in subscribers.items():
        if info.get("subscribed"):
            try:
                await context.bot.send_message(chat_id=int(chat_id), text=text)
            except Exception as e:
                logger.warning(f"Не удалось отправить сообщение {chat_id}: {e}")


# ------------------- Основная функция запуска бота -------------------

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("Не задан TELEGRAM_BOT_TOKEN в файле .env")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("tomorrow", tomorrow_command))
    app.add_handler(CommandHandler("week", week_command))
    app.add_handler(CommandHandler("weekschedule", weekschedule_command))

    # Регистрируем обработчик callback (inline-кнопок)
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    # Планируем ежедневную отправку расписания в 21:00
    app.job_queue.run_daily(
        broadcast_daily_schedule, 
        time=datetime.strptime("21:00", "%H:%M").time()
    )

    # Пример: отправлять рассылку каждые 10 секунд (можно закомментировать, если не нужно)
    # app.job_queue.run_repeating(
    #     broadcast_daily_schedule,
    #     interval=10,  # каждые 10 секунд
    #     first=0       # стартуем сразу
    # )

    # Запуск бота
    app.run_polling()

if __name__ == '__main__':
    main()
