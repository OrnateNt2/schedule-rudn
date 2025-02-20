# src/services/cache.py
import os
from services.parser import parse_schedule
import re
from config import CURRENT_WEEK  # Импортируем текущую неделю из конфигурации

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

def process_entry_by_week(entry_text: str, current_week: str) -> str:
    """
    Если в тексте есть разделитель '/', то левая часть – для верхней недели, правая – для нижней.
    Если выбранная сторона пустая, возвращается пустая строка (запись не выводится).
    Если разделителя нет, возвращается исходный текст.
    """
    if "/" in entry_text:
        parts = entry_text.split("/", 1)
        if current_week == "upper":
            chosen = parts[0].strip()
        else:
            chosen = parts[1].strip()
        return chosen  # Если chosen пустая, запись потом отфильтруется
    return entry_text

def get_schedule_for_day(group: str, day: int, program: str = None, language: str = None) -> str:
    """
    Возвращает отфильтрованное расписание для группы и дня с нумерацией пар.
    Перед выводом время пары преобразуется: точки заменяются на двоеточия.
    Если ячейка содержит разделитель '/', выбирается нужная часть по текущей неделе (CURRENT_WEEK).
    """
    if _schedule_cache is None:
        init_cache()

    if group not in _schedule_cache:
        return f"Группа '{group}' не найдена в расписании."

    lessons = _schedule_cache[group].get(day, [])
    if not lessons:
        return "На этот день нет занятий."

    output_lines = []
    lesson_number = 1
    for lesson in lessons:
        filtered_entries = []
        for entry in lesson.get("entries", []):
            # Фильтрация по программе: если указана метка программы и она не совпадает с выбранной, пропускаем
            if program and entry.get("program") and entry["program"] != program:
                continue
            # Если выбран фильтр по языку для зелёных ячеек, проверяем наличие выбранного языка
            if entry.get("cell_color") == "green" and entry.get("is_language"):
                if language:
                    if language.lower() not in entry["text"].lower():
                        continue
                else:
                    continue
            # Обработка разделителя "/" для верхней/нижней недели
            processed_text = process_entry_by_week(entry["text"], CURRENT_WEEK)
            if processed_text:  # если после обработки строка не пустая
                filtered_entries.append(processed_text)
        if filtered_entries:
            # Преобразуем время: заменяем точки на двоеточия
            time_text = lesson['time'].replace('.', ':')
            output_lines.append(f"{lesson_number}. {time_text}: " + "; ".join(filtered_entries))
            lesson_number += 1
    return "\n".join(output_lines) if output_lines else "На этот день нет занятий."

def get_schedule_for_week(group: str, program: str = None, language: str = None) -> dict:
    """
    Возвращает расписание на всю неделю (0-5) с нумерацией пар для каждого дня.
    """
    if _schedule_cache is None:
        init_cache()

    result = {}
    if group not in _schedule_cache:
        return result

    for day in range(6):
        lessons = _schedule_cache[group].get(day, [])
        output_lines = []
        lesson_number = 1
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
                processed_text = process_entry_by_week(entry["text"], CURRENT_WEEK)
                if processed_text:
                    filtered_entries.append(processed_text)
            if filtered_entries:
                time_text = lesson['time'].replace('.', ':')
                output_lines.append(f"{lesson_number}. {time_text}: " + "; ".join(filtered_entries))
                lesson_number += 1
        result[day] = "\n".join(output_lines) if output_lines else "На этот день нет занятий."
    return result

def get_available_languages(group: str, program: str = None) -> list:
    """
    Сканирует расписание для группы и возвращает список языков,
    найденных в зелёных ячейках с текстом, содержащим слово "язык".
    Если задан program, фильтрует по нему.
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
                    if program and entry.get("program") and entry["program"] != program:
                        continue
                    match = re.search(r"(.+?)\s*язык", entry["text"], re.IGNORECASE)
                    if match:
                        lang = match.group(1).strip()
                        languages.add(lang)
    return list(languages)
