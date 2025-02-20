# src/services/cache.py
import os
from services.parser import parse_schedule

_schedule_cache = None

def init_cache():
    global _schedule_cache
    excel_path = os.path.join("data", "schedule.xlsx")
    print(f"[cache.py] Инициализируем кэш, парсим Excel: {excel_path}")
    _schedule_cache = parse_schedule(excel_path)
    print("[cache.py] Кэш инициализирован.\n")

def get_all_groups():
    """
    Возвращает список групп, найденных в расписании.
    """
    if _schedule_cache is None:
        init_cache()
    return list(_schedule_cache.keys())

def get_schedule_for_day(group: str, day: int) -> str:
    if _schedule_cache is None:
        init_cache()

    if group not in _schedule_cache:
        return f"Группа '{group}' не найдена в расписании."

    if day not in _schedule_cache[group]:
        return f"Не найден день {day} для группы '{group}'."

    lessons = _schedule_cache[group][day]
    if not lessons:
        return "На этот день нет занятий."

    lines = [f"{t}: {subj}" for (t, subj) in lessons]
    return "\n".join(lines)

def get_schedule_for_week(group: str) -> dict:
    if _schedule_cache is None:
        init_cache()

    result = {}
    if group not in _schedule_cache:
        return result

    for day in range(6):  # 0..5 (Пн..Сб)
        lessons = _schedule_cache[group][day]
        if not lessons:
            result[day] = "На этот день нет занятий."
        else:
            lines = [f"{t}: {subj}" for (t, subj) in lessons]
            result[day] = "\n".join(lines)

    return result
