# test.py
import os
import openpyxl
import openpyxl.cell.cell

DEFAULT_EXCEL_PATH = os.path.join("data", "schedule.xlsx")

def read_excel_range(range_str: str, file_path: str = DEFAULT_EXCEL_PATH):
    """
    Читает указанный range (например, 'A1' или 'B5:D10') из Excel
    и возвращает двумерный список значений (list of lists).
    """
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active  # Или wb["Имя_листа"], если нужно явно

    # При чтении диапазона openpyxl возвращает tuple кортежей строк
    # Но если это одна ячейка (например, 'K4'), вернётся один объект Cell
    cells = sheet[range_str]

    # Проверяем, не вернулся ли одиночный Cell
    if isinstance(cells, openpyxl.cell.cell.Cell):
        # Оборачиваем в кортеж, чтобы обрабатывать как диапазон
        cells = ((cells,),)

    data = []
    for row in cells:
        row_values = []
        for cell in row:
            row_values.append(cell.value)
        data.append(row_values)

    return data

def main():
    print(f"Используется файл Excel: {DEFAULT_EXCEL_PATH}\n")
    print("Введите ячейку (например, K4) или диапазон (например, B5:D10).")
    print("Чтобы выйти, введите 'exit' и нажмите Enter.\n")

    while True:
        range_str = input("Введите ячейку/диапазон: ").strip()
        if range_str.lower() == 'exit':
            print("Выход из программы.")
            break

        try:
            data = read_excel_range(range_str, DEFAULT_EXCEL_PATH)
            print(f"\nСодержимое диапазона '{range_str}':")
            for i, row_values in enumerate(data, start=1):
                print(f"  Строка {i}: {row_values}")
            print()
        except Exception as e:
            print(f"Ошибка при чтении диапазона '{range_str}': {e}\n")

if __name__ == "__main__":
    main()
