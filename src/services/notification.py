import datetime
import pytz
from utils.json_db import load_users
from services.cache import get_schedule_for_day

# Используем московский часовой пояс
TIMEZONE = pytz.timezone("Europe/Moscow")

async def send_daily_schedule(context):
    users = load_users()
    now = datetime.datetime.now(TIMEZONE)
    weekday = now.weekday()  # 0 - понедельник, 6 - воскресенье

    for user_id, user_data in users.items():
        if user_data.get("subscribed"):
            group = user_data.get("group")
            if group:
                schedule_text = get_schedule_for_day(group, weekday)
                if not schedule_text:
                    schedule_text = "На сегодня нет занятий."
                await context.bot.send_message(chat_id=user_id, text=f"Ваше расписание на сегодня:\n\n{schedule_text}")

def schedule_jobs(job_queue):
    # Планируем ежедневное оповещение в 07:00 по Москве
    job_queue.run_daily(
        callback=send_daily_schedule,
        time=datetime.time(hour=7, minute=0, tzinfo=TIMEZONE),
        name="daily_schedule"
    )
