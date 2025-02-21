# src/services/cache.py
import os
from services.parser import parse_schedule

# Глобальный кэш расписаний: ключ – номер курса (строкой), значение – данные расписания (словарь)
schedule_cache = {}

def init_cache_for_course(course):
    """
    Парсит файл schedule{course}.xlsx из папки data и сохраняет результат в кэше.
    """
    course_str = str(course)
    file_path = os.path.join("data", f"schedule{course_str}.xlsx")
    schedule_cache[course_str] = parse_schedule(file_path)

def init_cache():
    """
    Инициализирует кэш для курса "1" по умолчанию.
    """
    init_cache_for_course("1")

def get_all_groups(course=None):
    """
    Возвращает список групп, найденных в расписании.
    Если course не указан, по умолчанию используется курс "1".
    """
    if course is None:
        course = "1"
    else:
        course = str(course)
    if course not in schedule_cache:
        init_cache_for_course(course)
    schedule_data = schedule_cache.get(course)
    return list(schedule_data.keys()) if schedule_data else []

def get_schedule_for_day(group: str, day: int, course, program: str = None, language: str = None) -> str:
    """
    Возвращает расписание на заданный день для указанной группы и курса.
    Если заданы фильтры по программе или языку, они учитываются.
    """
    course = str(course)
    if course not in schedule_cache:
        init_cache_for_course(course)
    schedule_data = schedule_cache.get(course)
    if group not in schedule_data:
        return f"Группа '{group}' не найдена в расписании для курса {course}."
    lessons = schedule_data[group].get(day, [])
    if not lessons:
        return "На этот день нет занятий."
    output_lines = []
    for lesson in lessons:
        filtered_entries = []
        for entry in lesson.get("entries", []):
            if program and entry.get("program") and entry["program"] != program:
                continue
            if entry.get("cell_color") == "green" and entry.get("is_language"):
                if language:
                    if language.lower() not in entry["text"].lower():
                        continue
                else:
                    continue
            processed_text = entry["text"]
            filtered_entries.append(processed_text)
        if filtered_entries:
            time_text = lesson["time"].replace('.', ':')
            output_lines.append(f"{lesson.get('number')}. {time_text}: " + "; ".join(filtered_entries))
    return "\n".join(output_lines) if output_lines else "На этот день нет занятий."

def get_schedule_for_week(group: str, course, program: str = None, language: str = None) -> dict:
    """
    Возвращает расписание на всю неделю (0-5) для указанной группы и курса.
    """
    course = str(course)
    if course not in schedule_cache:
        init_cache_for_course(course)
    schedule_data = schedule_cache.get(course)
    result = {}
    if group not in schedule_data:
        return result
    for day in range(6):
        lessons = schedule_data[group].get(day, [])
        output_lines = []
        for lesson in lessons:
            filtered_entries = []
            for entry in lesson.get("entries", []):
                if program and entry.get("program") and entry["program"] != program:
                    continue
                if entry.get("cell_color") == "green" and entry.get("is_language"):
                    if language:
                        if language.lower() not in entry["text"].lower():
                            continue
                    else:
                        continue
                processed_text = entry["text"]
                filtered_entries.append(processed_text)
            if filtered_entries:
                time_text = lesson["time"].replace('.', ':')
                output_lines.append(f"{lesson.get('number')}. {time_text}: " + "; ".join(filtered_entries))
        result[day] = "\n".join(output_lines) if output_lines else "На этот день нет занятий."
    return result

def get_available_languages(group: str, course, program: str = None) -> list:
    """
    Сканирует расписание для указанной группы и курса и возвращает список языков,
    найденных в зелёных ячейках с текстом, содержащим слово "язык".
    Если задан фильтр по программе, учитывается он.
    """
    course = str(course)
    if course not in schedule_cache:
        init_cache_for_course(course)
    schedule_data = schedule_cache.get(course)
    if group not in schedule_data:
        return []
    languages = set()
    for day, lessons in schedule_data[group].items():
        for lesson in lessons:
            for entry in lesson.get("entries", []):
                if entry.get("cell_color") == "green" and entry.get("is_language"):
                    if program and entry.get("program") and entry["program"] != program:
                        continue
                    import re
                    match = re.search(r"(.+?)\s*язык", entry["text"], re.IGNORECASE)
                    if match:
                        lang = match.group(1).strip()
                        languages.add(lang)
    return list(languages)
