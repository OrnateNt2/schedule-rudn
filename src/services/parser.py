# src/services/parser.py
import openpyxl

# Диапазоны строк для дней недели (0: Пн, 1: Вт, …, 5: Сб)
DAY_RANGES = {
    0: range(5, 14),   # Понедельник: строки 5–13
    1: range(14, 23),  # Вторник: строки 14–22
    2: range(23, 32),  # Среда: строки 23–31
    3: range(32, 41),  # Четверг: строки 32–40
    4: range(41, 50),  # Пятница: строки 41–49
    5: range(50, 59),  # Суббота: строки 50–58
}

def process_lesson_cell(cell):
    """
    Обрабатывает ячейку урока и возвращает список записей.
    Каждая запись – словарь с:
      - text: текст урока
      - program: "ФГОС" или "МП", если найдено, иначе None
      - is_language: True, если в тексте есть слово "язык"
      - cell_color: "blue" или "green" или "default"
    """
    text = cell.value
    if text is None:
        return []
    text = str(text).strip()

    # Определяем цвет ячейки по значению RGB
    color_rgb = cell.fill.fgColor.rgb
    cell_color = "default"
    if color_rgb:
        if color_rgb.startswith("FF"):
            color_hex = color_rgb[2:]
        else:
            color_hex = color_rgb
        if color_hex.upper() == "7DB4F0":  # синий
            cell_color = "blue"
        elif color_hex.upper() == "70AD47":  # зелёный
            cell_color = "green"
        else:
            cell_color = "default"

    # Если в ячейке несколько вариантов, разделённых "|", разбиваем
    parts = text.split("|")
    entries = []
    for part in parts:
        part = part.strip()
        program_marker = None
        if "ФГОС" in part:
            program_marker = "ФГОС"
        elif "МП" in part:
            program_marker = "МП"
        is_language = "язык" in part.lower()
        entries.append({
            "text": part,
            "program": program_marker,
            "is_language": is_language,
            "cell_color": cell_color
        })
    return entries

def parse_schedule(excel_path: str):
    print(f"[parser.py] Открываем файл: {excel_path}")
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active

    # Считываем названия групп из 4-й строки (E4..S4)
    group_names = {}
    for col_idx in range(5, 20):  # E=5, ..., S=19
        cell_value = sheet.cell(row=4, column=col_idx).value
        print(f"DEBUG: col={col_idx} -> group_name='{cell_value}'")
        if cell_value:
            group_names[col_idx] = str(cell_value).strip()

    # Инициализируем структуру: schedule_data[group][day] = список уроков
    schedule_data = {}
    for col_idx, group_name in group_names.items():
        schedule_data[group_name] = {day: [] for day in DAY_RANGES}

    for day, rows in DAY_RANGES.items():
        for row in rows:
            time_cell = sheet.cell(row=row, column=4)  # время занятий в столбце D
            time_cell_value = time_cell.value
            if not time_cell_value:
                continue
            time_text = str(time_cell_value).strip()

            for col_idx, group_name in group_names.items():
                cell = sheet.cell(row=row, column=col_idx)
                entries = process_lesson_cell(cell)
                if entries:
                    schedule_data[group_name][day].append({
                        "time": time_text,
                        "entries": entries
                    })

    print("\n[parser.py] Итоговое расписание (schedule_data):")
    for grp, days in schedule_data.items():
        print(f"Группа '{grp}':")
        for d, lessons in days.items():
            print(f"  День {d} => {lessons}")
    print("[parser.py] Конец вывода расписания.\n")
    return schedule_data
