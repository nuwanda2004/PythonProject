# ======================== task3.py — ИСПРАВЛЕННАЯ ВЕРСИЯ ========================
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Глобальные переменные
RESULT_DATA = None
OPTIMIZATION_RESULTS = None


def main_task3():
    """Основная функция решения Задачи 3"""
    global RESULT_DATA, OPTIMIZATION_RESULTS

    try:
        from scipy.optimize import linprog
    except ImportError:
        print("❌ ОШИБКА: Не установлен модуль scipy")
        print("   Установите: pip install scipy")
        return

    print("=" * 80)
    print("ЗАДАЧА 3: Формирование производственной программы")
    print("Заказ: Строительство скоростной трассы для многофункционального комплекса")
    print("=" * 80)
    print()

    # ==================== ИСХОДНЫЕ ДАННЫЕ ====================
    works = [
        "Подготовительные работы и расчистка полосы отвода",
        "Земляные работы (планировка и уплотнение земляного полотна)",
        "Устройство основания",
        "Укладка нижнего слоя асфальтобетона",
        "Укладка верхнего слоя асфальтобетона",
        "Устройство дренажной системы",
        "Установка дорожных ограждений и знаков",
        "Нанесение дорожной разметки"
    ]

    units = [
        "куб. м.",
        "куб. м.",
        "куб. м.",
        "кв. м.",
        "куб. м.",
        "кв. м.",
        "кв. м.",
        "кв. м."
    ]

    # Нормы расхода рабочих (чел-ч на единицу)
    norm_workers = [4, 7, 7, 5, 4, 3, 3, 4]

    # Нормы расхода сырья (м³ на единицу)
    norm_materials = [3, 1, 5, 8, 3, 5, 3, 4]

    # Планируемый (максимальный) объем работ
    max_volumes = [600, 700, 450, 800, 520, 800, 600, 600]

    # Доход на единицу работы (тыс. руб.)
    income_per_unit = [39, 36, 36, 37, 38, 32, 32, 33]

    # Доступные ресурсы
    total_workers = 19000  # чел-ч
    total_materials = 19000  # м³

    print("ИСХОДНЫЕ ДАННЫЕ:")
    print("-" * 100)
    print(f"{'№':<3} {'Виды работ':<60} {'Ед.изм.':<10} {'Раб,чч':<8} {'Сырье,м³':<10} {'План':<8} {'Доход'}")
    print("-" * 100)

    for i, work in enumerate(works):
        print(
            f"{i + 1:<3} {work:<60} {units[i]:<10} {norm_workers[i]:<8} {norm_materials[i]:<10} {max_volumes[i]:<8} {income_per_unit[i]:.0f}")

    print("-" * 100)
    print(f"Объем выделяемых ресурсов:")
    print(f"   • Рабочие (чел-ч):  {total_workers:>10,}")
    print(f"   • Сырье (м³):       {total_materials:>10,}")
    print()

    # ==================== МОДЕЛЬ ОПТИМИЗАЦИИ ====================
    print("Запуск оптимизации методом линейного программирования...")
    print("-" * 100)

    # Целевая функция (максимизация дохода, поэтому минус)
    C = [-income for income in income_per_unit]

    # Матрица ограничений
    # Первые 8 строк - ограничения на максимальные объемы работ
    A_ub = []
    for i in range(8):
        row = [0] * 8
        row[i] = 1
        A_ub.append(row)

    # Добавляем ограничения по ресурсам
    A_ub.append(norm_workers)  # ограничение по рабочим
    A_ub.append(norm_materials)  # ограничение по сырью

    # Вектор ограничений
    B_ub = max_volumes + [total_workers, total_materials]

    # Решение задачи
    try:
        res_linprog = linprog(C, A_ub=A_ub, b_ub=B_ub, bounds=(0, None), method='highs')

        if not res_linprog.success:
            print(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: Оптимизация завершена с кодом: {res_linprog.message}")
            print(f"   Статус: {res_linprog.status}")

        result = res_linprog.x
        total_income = abs(res_linprog.fun)

        # Проверка результата
        if result is None or len(result) == 0:
            print("❌ ОШИБКА: Не удалось получить решение")
            return

        # Округляем очень маленькие значения до нуля
        result = np.where(result < 0.01, 0, result)

    except Exception as e:
        print(f"❌ ОШИБКА при решении задачи оптимизации: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==================== РЕЗУЛЬТАТЫ ====================
    print()
    print("=" * 100)
    print("РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ:")
    print("=" * 100)
    print()

    # Формируем таблицу результатов
    results_table = []
    for i, work in enumerate(works):
        volume = result[i]
        income = income_per_unit[i] * volume
        results_table.append({
            '№': i + 1,
            'Наименование': work,
            'Ед.изм.': units[i],
            'Объем работ': volume,
            'Доход, тыс.руб.': income
        })

    RESULT_DATA = pd.DataFrame(results_table)

    # Расчет использования ресурсов
    used_workers = sum(norm_workers[i] * result[i] for i in range(8))
    used_materials = sum(norm_materials[i] * result[i] for i in range(8))

    OPTIMIZATION_RESULTS = {
        'total_income': total_income,
        'used_workers': used_workers,
        'used_materials': used_materials,
        'total_workers': total_workers,
        'total_materials': total_materials,
        'income_per_unit': income_per_unit
    }

    print("ОПТИМАЛЬНАЯ ПРОИЗВОДСТВЕННАЯ ПРОГРАММА:")
    print("-" * 100)
    print(f"{'№':<3} {'Виды работ':<60} {'Ед.изм.':<10} {'Объем':<12} {'Доход, тыс.руб.'}")
    print("-" * 100)

    for _, row in RESULT_DATA.iterrows():
        work_name = row['Наименование']
        if len(work_name) > 58:
            work_name = work_name[:55] + "..."
        volume = row['Объем работ']
        income = row['Доход, тыс.руб.']

        # Пропускаем работы с нулевым объемом в выводе
        if volume > 0.01:
            print(f"{int(row['№']):<3} {work_name:<60} {row['Ед.изм.']:<10} {volume:>10.2f}  {income:>12.2f}")

    print("-" * 100)
    print(f"{'ИТОГО:':<75} {total_income:>25.2f}")
    print("-" * 100)
    print()

    # Подсчет выполненных работ
    performed_works = sum(1 for _, row in RESULT_DATA.iterrows() if row['Объем работ'] > 0.01)
    print(f"Количество выполняемых работ: {performed_works} из {len(RESULT_DATA)}")
    print()

    print("ИСПОЛЬЗОВАНИЕ РЕСУРСОВ:")
    print("-" * 100)
    workers_percent = (used_workers / total_workers) * 100
    materials_percent = (used_materials / total_materials) * 100

    print(f"   • Рабочие (чел-ч):  {used_workers:>10,.2f} / {total_workers:>10,} ({workers_percent:>5.1f}%)")
    print(f"   • Сырье (м³):       {used_materials:>10,.2f} / {total_materials:>10,} ({materials_percent:>5.1f}%)")
    print("-" * 100)
    print()

    # Проверка ограничений
    workers_ok = used_workers <= total_workers
    materials_ok = used_materials <= total_materials

    print("ПРОВЕРКА ОГРАНИЧЕНИЙ:")
    print(f"   {'✅' if workers_ok else '❌'} Рабочие:  {used_workers:>10,.2f} <= {total_workers:>10,}")
    print(f"   {'✅' if materials_ok else '❌'} Сырье:    {used_materials:>10,.2f} <= {total_materials:>10,}")
    print()

    if all([workers_ok, materials_ok]):
        print("✅ Все ограничения выполнены!")
    else:
        print("⚠️ ВНИМАНИЕ: Некоторые ограничения нарушены!")

    print()
    print("=" * 100)
    print("✅ Оптимизация завершена успешно!")
    print(f"   Общий доход: {total_income:,.2f} тыс. руб.")
    print("   Для создания отчёта нажмите кнопку «Сформировать и открыть документ»")
    print("=" * 100)
    print()


def generate_document():
    """Создание нового Excel-документа с результатами"""
    global RESULT_DATA, OPTIMIZATION_RESULTS

    if RESULT_DATA is None or OPTIMIZATION_RESULTS is None:
        print("❌ ОШИБКА: Сначала необходимо выполнить расчёт!")
        print("   Запустите скрипт без аргументов: python task3.py")
        return

    try:
        import xlwings as xw
    except ImportError:
        print("❌ ОШИБКА: Не установлен модуль xlwings")
        print("   Установите: pip install xlwings")
        return

    print("=" * 80)
    print("СОЗДАНИЕ ДОКУМЕНТА...")
    print("=" * 80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Результат_Задача3_Производственная_программа_{timestamp}.xlsx"

    try:
        # Создаём новую книгу
        wb = xw.Book()
        sheet = wb.sheets[0]
        sheet.name = "Производственная программа"

        # ==================== ШАПКА ====================
        sheet["B2"].value = 'Дорожно-строительный холдинг «Авто-Дор»'
        sheet["B2"].font.size = 16
        sheet["B2"].font.bold = True
        sheet["B2"].api.HorizontalAlignment = -4108  # xlCenter

        sheet["B3"].value = 'Производственная программа заказа "Строительство многофункционального комплекса"'
        sheet["B3"].font.size = 11
        sheet["B3"].api.HorizontalAlignment = -4108

        # ==================== ЗАГОЛОВКИ ТАБЛИЦЫ ====================
        sheet["B6"].value = "№"
        sheet["C6"].value = "Наименование"
        sheet["E6"].value = "Объем работ"
        sheet["F6"].value = "Доход, тыс.руб."

        # Форматирование заголовков
        header_cells = [sheet["B6"], sheet["C6"], sheet["E6"], sheet["F6"]]
        for cell in header_cells:
            cell.font.bold = True
            cell.color = (220, 220, 220)
            cell.api.HorizontalAlignment = -4108  # xlCenter
            cell.api.VerticalAlignment = -4108

        # Дополнительная строка с номерами колонок (как на образце)
        sheet["B7"].value = "1"
        sheet["C7"].value = "2"
        sheet["E7"].value = "3"
        sheet["F7"].value = "4"

        for cell in [sheet["B7"], sheet["C7"], sheet["E7"], sheet["F7"]]:
            cell.font.bold = True
            cell.api.HorizontalAlignment = -4108

        # ==================== ДАННЫЕ ====================
        row_num = 8
        for idx, row in RESULT_DATA.iterrows():
            sheet.cells(row_num, 2).value = int(row["№"])

            # Наименование с единицей измерения
            name_with_unit = f"{row['Наименование']}"
            sheet.cells(row_num, 3).value = name_with_unit

            volume = round(row["Объем работ"], 2)
            income = round(row["Доход, тыс.руб."], 2)

            # Выравнивание по центру для номера
            sheet.cells(row_num, 2).api.HorizontalAlignment = -4108

            # Записываем данные
            sheet.cells(row_num, 5).value = volume if volume > 0 else 0
            sheet.cells(row_num, 6).value = income if income > 0 else 0

            # Числа по центру
            sheet.cells(row_num, 5).api.HorizontalAlignment = -4108
            sheet.cells(row_num, 6).api.HorizontalAlignment = -4108

            row_num += 1

        # ==================== ИТОГО ====================
        total_row = row_num

        sheet.cells(total_row, 5).value = "ИТОГО"
        sheet.cells(total_row, 5).font.bold = True
        sheet.cells(total_row, 5).api.HorizontalAlignment = -4108

        sheet.cells(total_row, 6).value = round(OPTIMIZATION_RESULTS['total_income'], 2)
        sheet.cells(total_row, 6).font.bold = True
        sheet.cells(total_row, 6).api.HorizontalAlignment = -4108

        # ==================== ПОДВАЛ ====================
        footer_row = total_row + 3

        sheet.cells(footer_row, 3).value = "Сотрудник отдела по закупкам и снабжению"
        sheet.cells(footer_row + 1, 3).value = "(подпись)"
        sheet.cells(footer_row + 1, 3).api.HorizontalAlignment = -4108

        sheet.cells(footer_row, 6).value = "Максимов А.М."
        sheet.cells(footer_row + 1, 6).value = "(Фамилия, инициалы)"
        sheet.cells(footer_row + 1, 6).api.HorizontalAlignment = -4108

        # ==================== ФОРМАТИРОВАНИЕ ====================
        # Установка ширины колонок
        sheet.range("B:B").column_width = 3  # Номер
        sheet.range("C:D").column_width = 35  # Наименование (объединенные)
        sheet.range("E:E").column_width = 15  # Объем работ
        sheet.range("F:F").column_width = 18  # Доход

        # Границы таблицы
        table_range = sheet.range(f"B6:F{total_row}")
        for border_id in range(7, 13):  # Все границы
            table_range.api.Borders(border_id).LineStyle = 1
            table_range.api.Borders(border_id).Weight = 2

        # Сохранение
        wb.save(filename)
        wb.close()

        print(f"✅ ДОКУМЕНТ УСПЕШНО СОЗДАН:")
        print(f"   📄 {filename}")
        print(f"   📁 {os.path.abspath(filename)}")
        print("=" * 80)

    except Exception as e:
        print(f"❌ ОШИБКА при создании документа: {e}")
        import traceback
        traceback.print_exc()


# ==================== ТОЧКА ВХОДА ====================
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "document":
        # Сначала выполняем расчёт, потом создаём документ
        main_task3()
        generate_document()
    else:
        # Только расчёт
        main_task3()