# src/services/parser.py
import openpyxl

# Пример маппинга день -> диапазон строк (включительно).
# Подгоните под свою таблицу!
DAY_RANGES = {
    0: range(5, 14),   # Понедельник: строки 5–13
    1: range(14, 23),  # Вторник: строки 14–22
    2: range(23, 32),  # Среда: строки 23–31
    3: range(32, 41),  # Четверг: строки 32–40
    4: range(41, 50),  # Пятница: строки 41–49
    5: range(50, 59),  # Суббота: строки 50–58
    # 6: воскресенье, если нужно
}

def parse_schedule(excel_path: str):
    print(f"[parser.py] Открываем файл: {excel_path}")
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active  # Предполагаем, что нужный лист – активный

    # Предположим, что группы находятся в 4-й строке (row=4) с колонки E(5) по S(19).
    group_names = {}
    for col_idx in range(5, 20):  # E=5, F=6, ..., S=19
        cell_value = sheet.cell(row=4, column=col_idx).value
        print(f"DEBUG: col={col_idx} -> group_name='{cell_value}'")
        if cell_value:
            group_name = str(cell_value).strip()
            group_names[col_idx] = group_name
        else:
            # Если пусто, пропускаем
            pass

    # Инициализируем структуру данных:
    # schedule_data[group][day] = список (time, subject)
    schedule_data = {}
    for col_idx, group_name in group_names.items():
        schedule_data[group_name] = {day: [] for day in DAY_RANGES}

    # Проходим по дням и строкам
    for day, rows in DAY_RANGES.items():
        for row in rows:
            # Читаем время пары из столбца D (column=4)
            time_cell_value = sheet.cell(row=row, column=4).value
            if not time_cell_value:
                continue  # Пустая ячейка, пропускаем

            time_text = str(time_cell_value).strip()

            # Для каждой группы (колонки E..S) берём предмет
            for col_idx, group_name in group_names.items():
                subject_cell_value = sheet.cell(row=row, column=col_idx).value
                if subject_cell_value:
                    subject_text = str(subject_cell_value).strip()
                    schedule_data[group_name][day].append((time_text, subject_text))

    # Выводим итоговую структуру для отладки
    print("\n[parser.py] Итоговое расписание (schedule_data):")
    for grp, days in schedule_data.items():
        print(f"Группа '{grp}':")
        for d, lessons in days.items():
            print(f"  День {d} => {lessons}")
    print("[parser.py] Конец вывода расписания.\n")

    return schedule_data
