import os
from services.parser import parse_schedule
import datetime
from config import CURRENT_WEEK_PARITY  # например, "even" или "odd"

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

def get_current_week_type():
    """
    Вычисляет текущую неделю.
    Если CURRENT_WEEK_PARITY == "even": чётные недели – верхние, нечётные – нижние.
    Если "odd": наоборот.
    """
    week_num = datetime.date.today().isocalendar()[1]
    if CURRENT_WEEK_PARITY.lower() == "even":
        return "upper" if week_num % 2 == 0 else "lower"
    else:
        return "upper" if week_num % 2 == 1 else "lower"

def get_next_week_type():
    """
    Возвращает тип следующей недели, инвертируя текущий.
    """
    current = get_current_week_type()
    return "lower" if current == "upper" else "upper"

def process_entry_by_week(entry_text: str, week_type: str) -> str:
    """
    Если в тексте присутствует разделитель '/', возвращает левую часть для верхней недели и правую для нижней.
    """
    if "/" in entry_text:
        parts = entry_text.split("/", 1)
        return parts[0].strip() if week_type == "upper" else parts[1].strip()
    return entry_text

def get_all_groups(course=None):
    """
    Возвращает список групп, найденных в расписании для указанного курса.
    Если курс не указан, по умолчанию используется "1".
    """
    if course is None:
        course = "1"
    else:
        course = str(course)
    if course not in schedule_cache:
        init_cache_for_course(course)
    schedule_data = schedule_cache.get(course)
    return list(schedule_data.keys()) if schedule_data else []

def get_schedule_for_day(group: str, day: int, course, program: str = None, language: str = None, week_type: str = None) -> str:
    """
    Возвращает расписание на заданный день для указанной группы и курса.
    Если week_type не указан, используется текущая неделя.
    Фильтрует по программе и языку.
    """
    if week_type is None:
        week_type = get_current_week_type()
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
            processed_text = process_entry_by_week(entry["text"], week_type)
            filtered_entries.append(processed_text)
        if filtered_entries:
            time_text = lesson["time"].replace('.', ':')
            output_lines.append(f"{lesson.get('number')}. {time_text}: " + "; ".join(filtered_entries))
    return "\n".join(output_lines) if output_lines else "На этот день нет занятий."

def get_schedule_for_week(group: str, course, program: str = None, language: str = None, week_type: str = None) -> dict:
    """
    Возвращает расписание на всю неделю (0–5) для указанной группы и курса.
    Если week_type не указан, используется текущая неделя.
    """
    if week_type is None:
        week_type = get_current_week_type()
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
                processed_text = process_entry_by_week(entry["text"], week_type)
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
