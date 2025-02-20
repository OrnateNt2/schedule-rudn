# src/services/cache.py
import os
from services.parser import parse_schedule
import re

_schedule_cache = None

def init_cache():
    global _schedule_cache
    excel_path = os.path.join("data", "schedule.xlsx")
    print(f"[cache.py] Инициализируем кэш, парсим Excel: {excel_path}")
    _schedule_cache = parse_schedule(excel_path)
    print("[cache.py] Кэш инициализирован.\n")

def get_all_groups():
    if _schedule_cache is None:
        init_cache()
    return list(_schedule_cache.keys())

def get_schedule_for_day(group: str, day: int, program: str = None, language: str = None) -> str:
    """
    Возвращает отфильтрованное расписание для группы и дня.
    Фильтрация:
      - Если у записи указан параметр программы и он не совпадает с выбранным, запись исключается.
      - Для зелёных ячеек (выбор языка) запись выводится только если выбранный язык содержится в тексте.
    """
    if _schedule_cache is None:
        init_cache()

    if group not in _schedule_cache:
        return f"Группа '{group}' не найдена в расписании."

    lessons = _schedule_cache[group].get(day, [])
    if not lessons:
        return "На этот день нет занятий."

    output_lines = []
    for lesson in lessons:
        filtered_entries = []
        for entry in lesson.get("entries", []):
            # Если запись содержит метку программы и она не совпадает с выбором пользователя, пропускаем
            if program and entry.get("program") and entry["program"] != program:
                continue
            # Для зелёных ячеек с выбором языка – включаем только если выбранный язык содержится в тексте
            if entry.get("cell_color") == "green" and entry.get("is_language"):
                if language:
                    if language.lower() not in entry["text"].lower():
                        continue
                else:
                    continue
            filtered_entries.append(entry["text"])
        if filtered_entries:
            output_lines.append(f"{lesson['time']}: " + "; ".join(filtered_entries))
    if not output_lines:
        return "На этот день нет занятий."
    return "\n".join(output_lines)

def get_schedule_for_week(group: str, program: str = None, language: str = None) -> dict:
    if _schedule_cache is None:
        init_cache()

    result = {}
    if group not in _schedule_cache:
        return result

    for day in range(6):
        lessons = _schedule_cache[group].get(day, [])
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
                filtered_entries.append(entry["text"])
            if filtered_entries:
                output_lines.append(f"{lesson['time']}: " + "; ".join(filtered_entries))
        if output_lines:
            result[day] = "\n".join(output_lines)
        else:
            result[day] = "На этот день нет занятий."
    return result

def get_available_languages(group: str, program: str = None) -> list:
    """
    Сканирует все уроки для группы и ищет зелёные ячейки с текстом, содержащим "язык".
    Извлекает язык как текст до слова "язык". Если задан program, фильтрует по нему.
    """
    if _schedule_cache is None:
        init_cache()
    if group not in _schedule_cache:
        return []
    
    languages = set()
    for day, lessons in _schedule_cache[group].items():
        for lesson in lessons:
            for entry in lesson.get("entries", []):
                if entry.get("cell_color") == "green" and entry.get("is_language"):
                    entry_program = entry.get("program")
                    if program and entry_program and entry_program != program:
                        continue
                    match = re.search(r"(.+?)\s*язык", entry["text"], re.IGNORECASE)
                    if match:
                        lang = match.group(1).strip()
                        languages.add(lang)
    return list(languages)
