#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, time as dt_time, timedelta, date

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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Расписание (хардкод)
schedule = {
    "ПН": [
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
    "ВТ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "", "even": ""},
        {"time": "12.00-13.20", "odd": "", "even": ""},
        {"time": "13.30-14.50", "odd": "Древоводство; сем; Роднова А.Д.; АТИ-304", "even": "Древоводство; сем; Роднова А.Д.; АТИ-304"},
        {"time": "15.00-16.20", "odd": "", "even": ""},
        {"time": "16.30-17.50", "odd": "", "even": "Древоводство; лек;Щепелева А.С.;АТИ-зал№2"},
        {"time": "18.00-19.20", "odd": "", "even": ""},
        {"time": "19.30-20.50", "odd": "", "even": ""},
        {"time": "21:00-22:20", "odd": "", "even": ""},
    ],
    "СР": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "Строительство и содержание объектов ЛА;сем; Дубровина Т.А.; АТИ-314", "even": "Строительство и содержание объектов ЛА;сем; Дубровина Т.А.; АТИ-314"},
        {"time": "12.00-13.20", "odd": "Строительство и содержание объектов ЛА;сем; Дубровина Т.А.; АТИ-314", "even": "Строительство и содержание объектов ЛА;сем; Дубровина Т.А.; АТИ-314"},
        {"time": "13.30-14.50", "odd": "Строительство и содержание объектов ЛА;лек; Дмитриева А.Г.; АТИ-зал №2", "even": "Строительство и содержание объектов ЛА;лек; Дмитриева А.Г.; АТИ-зал №2"},
        {"time": "15.00-16.20", "odd": "", "even": ""},
        {"time": "16.30-17.50", "odd": "", "even": ""},
        {"time": "18.00-19.20", "odd": "", "even": ""},
        {"time": "19.30-20.50", "odd": "", "even": ""},
        {"time": "21:00-22:20", "odd": "", "even": ""},
    ],
    "ЧТ": [
        {"time": "9.00-10.20", "odd": "", "even": ""},
        {"time": "10.30-11.50", "odd": "Немецкий язык ФГОС; сем; Согоян Р.А.; АТИ-335", "even": "Немецкий язык ФГОС; сем; Согоян Р.А.; АТИ-335"},
        {"time": "12.00-13.20", "odd": "Ландшафтное проектирование; Зинченко; лек; АТИ-203", "even": "Ландшафтное проектирование; Зинченко; лек; АТИ-203"},
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
        {"time": "13.30-14.50", "odd": "Ландшафтное проектирование; Зинченко; лаб; АТИ-203", "even": "Ландшафтное проектирование; Зинченко; лаб; АТИ-203"},
        {"time": "15.00-16.20", "odd": "", "even": "Ландшафтное проектирование; Зинченко; лаб; АТИ-203"},
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

# Порядок дней недели для навигации
day_order = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ"]

# Множество chat_id подписанных пользователей
subscribers = set()


def get_schedule_text(day_code: str, target_date: date) -> str:
    """
    Формирует текст расписания для дня day_code на дату target_date.
    Определяет четность недели по ISO-номерации:
      - четная (week % 2 == 0) -> верхняя неделя,
      - нечетная -> нижняя неделя.
    Если текст для пары пустой – выводится "Нет пары".
    """
    week_number = target_date.isocalendar()[1]
    is_even = (week_number % 2 == 0)
    lessons = schedule.get(day_code, [])
    week_type = "верхняя" if is_even else "нижняя"
    lines = [f"Расписание на {day_code} {target_date.strftime('%d.%m.%Y')} ({week_type} неделя):"]
    for i, lesson in enumerate(lessons, start=1):
        subject = lesson["even"] if is_even else lesson["odd"]
        subject_text = subject if subject else "Нет пары"
        lines.append(f"{i}. {lesson['time']} – {subject_text}")
    return "\n".join(lines)


async def daily_schedule_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Ежедневная задача, отправляющая расписание на завтрашний день в 21:00.
    """
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    weekday = tomorrow.weekday()  # 0 – понедельник, ... 6 – воскресенье
    if weekday < len(day_order):
        day_code = day_order[weekday]
        text = get_schedule_text(day_code, tomorrow)
    else:
        text = f"Завтра ({tomorrow.strftime('%d.%m.%Y')}) – выходной, расписание отсутствует."
    for chat_id in subscribers:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start: подписывает пользователя и отправляет инструкцию."""
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    welcome_text = (
        "Привет!\n"
        "Я бот-расписание. Каждый день в 21:00 я буду отправлять расписание на завтрашний день.\n"
        "Также ты можешь посмотреть расписание на всю неделю, нажав кнопку ниже."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Показать расписание на неделю", callback_data="week_0")]
    ])
    await update.message.reply_text(welcome_text, reply_markup=keyboard)


async def week_schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик callback-запросов для просмотра расписания недели.
    callback_data имеет вид "week_{day_index}" или "close".
    """
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("week_"):
        try:
            day_index = int(data.split("_")[1])
        except (IndexError, ValueError):
            day_index = 0

        # Определяем дату понедельника текущей недели
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        target_date = monday + timedelta(days=day_index)
        day_code = day_order[day_index]
        text = get_schedule_text(day_code, target_date)

        buttons = []
        if day_index > 0:
            buttons.append(InlineKeyboardButton("◀️ Предыдущий", callback_data=f"week_{day_index - 1}"))
        if day_index < len(day_order) - 1:
            buttons.append(InlineKeyboardButton("Следующий ▶️", callback_data=f"week_{day_index + 1}"))
        buttons.append(InlineKeyboardButton("Закрыть", callback_data="close"))
        keyboard = InlineKeyboardMarkup([buttons])
        await query.edit_message_text(text=text, reply_markup=keyboard)
    elif data == "close":
        await query.delete_message()


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    await update.message.reply_text(
        "Используй /start для подписки на расписание. Каждый день в 21:00 я отправлю тебе расписание на завтрашний день.\n"
        "Также можно нажать кнопку «Показать расписание на неделю» для просмотра расписания."
    )


def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("Не задан TELEGRAM_BOT_TOKEN в файле .env")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(week_schedule_callback))

    # Планируем ежедневную отправку расписания в 21:00
    app.job_queue.run_daily(daily_schedule_job, time=dt_time(21, 0, 0))

    app.run_polling()


if __name__ == '__main__':
    main()
