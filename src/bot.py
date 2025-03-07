# src/bot.py
import logging
from telegram.ext import ApplicationBuilder, JobQueue
from config import BOT_TOKEN
from handlers.start_handler import start_handler, course_callback_handler
from handlers.schedule_handler import today_handler, tomorrow_handler, week_handler, week_callback_handler, nextweek_callback_handler, nextweek_handler
from handlers.settings_handler import settings_handler, settings_callback_handler
from handlers.subscribe_handler import subscribe_handler, unsubscribe_handler
from services.notification import schedule_jobs
from services.cache import init_cache


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Инициализируем кэш (например, парсинг Excel)
    init_cache()

    # Создаем приложение
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Явно создаем JobQueue и запускаем её
    job_queue = JobQueue()
    job_queue.set_application(application)
    job_queue.start()
    
    # Регистрируем обработчики команд
    application.add_handler(start_handler)
    # Добавляем обработчик обратного вызова для выбора курса
    application.add_handler(course_callback_handler)
    
    application.add_handler(today_handler)
    application.add_handler(tomorrow_handler)
    application.add_handler(week_handler)
    application.add_handler(nextweek_handler)
    application.add_handler(week_callback_handler)
    application.add_handler(nextweek_callback_handler)
    application.add_handler(settings_handler)
    application.add_handler(settings_callback_handler)
    application.add_handler(subscribe_handler)
    application.add_handler(unsubscribe_handler)

    # Передаем созданный job_queue напрямую в schedule_jobs
    schedule_jobs(job_queue)

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
