# ======================== task4.py — ИСПРАВЛЕННАЯ ВЕРСИЯ ========================
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Глобальные переменные
RESULT_DATA = None
OPTIMIZATION_RESULTS = None


def main_task4():
    """Основная функция решения Задачи 4 - Динамическое программирование"""
    global RESULT_DATA, OPTIMIZATION_RESULTS

    print("=" * 90)
    print("ЗАДАЧА 4: Оптимальное распределение бригад по объектам")
    print("Метод: Динамическое программирование")
    print("=" * 90)
    print()

    # ==================== ИСХОДНЫЕ ДАННЫЕ ====================
    objects = [
        "Строительство трассы у жилого комплекса из трех высотных зданий",
        "Возведение магистрали у бизнес-центра",
        "Строительство частной дороги для гостиницы",
        "Строительство скоростной трассы многофункционального комплекса"
    ]

    # Таблица объемов СМР в зависимости от количества бригад
    # Строки - количество бригад (0-4), Столбцы - объекты (1-4)
    smr_table = [
        [0, 0, 0, 0],  # 0 бригад
        [100, 110, 90, 140],  # 1 бригада
        [230, 230, 190, 220],  # 2 бригады
        [350, 290, 280, 310],  # 3 бригады
        [370, 360, 350, 320]  # 4 бригады
    ]

    total_brigades = 4  # Всего бригад для распределения
    n_objects = 4  # Количество объектов

    print("ИСХОДНЫЕ ДАННЫЕ:")
    print("-" * 90)
    print(f"Всего бригад для распределения: {total_brigades}")
    print(f"Количество объектов: {n_objects}")
    print()

    print("ТАБЛИЦА ОБЪЕМОВ СМР (тыс. руб.) в зависимости от количества бригад:")
    print("-" * 90)
    print(f"{'Кол-во бригад':<15} {'Объект 1':<12} {'Объект 2':<12} {'Объект 3':<12} {'Объект 4':<12}")
    print("-" * 90)
    for brigades in range(5):
        print(
            f"{brigades:<15} {smr_table[brigades][0]:<12} {smr_table[brigades][1]:<12} {smr_table[brigades][2]:<12} {smr_table[brigades][3]:<12}")
    print("-" * 90)
    print()

    # ==================== ДИНАМИЧЕСКОЕ ПРОГРАММИРОВАНИЕ ====================
    print("Запуск алгоритма динамического программирования...")
    print("-" * 90)

    # F[i][k] - максимальный объем СМР для первых i объектов при k бригадах
    F = [[0 for _ in range(total_brigades + 1)] for _ in range(n_objects + 1)]

    # X[i][k] - оптимальное количество бригад для i-го объекта при общем количестве k
    X = [[0 for _ in range(total_brigades + 1)] for _ in range(n_objects + 1)]

    # Прямой ход - заполнение таблицы
    for i in range(1, n_objects + 1):
        for k in range(total_brigades + 1):
            max_smr = -1
            best_x = 0

            # Перебираем возможное количество бригад для текущего объекта
            for x in range(min(k, 4) + 1):  # не более 4 бригад на объект
                current_smr = F[i - 1][k - x] + smr_table[x][i - 1]
                if current_smr > max_smr:
                    max_smr = current_smr
                    best_x = x

            F[i][k] = max_smr
            X[i][k] = best_x

    # Обратный ход - восстановление оптимального решения
    brigades_distribution = [0] * n_objects
    remaining_brigades = total_brigades

    for i in range(n_objects, 0, -1):
        brigades_distribution[i - 1] = X[i][remaining_brigades]
        remaining_brigades -= X[i][remaining_brigades]

    # Расчет объемов СМР для каждого объекта
    smr_per_object = []
    for i in range(n_objects):
        smr = smr_table[brigades_distribution[i]][i]
        smr_per_object.append(smr)

    total_smr = F[n_objects][total_brigades]

    # ==================== РЕЗУЛЬТАТЫ ====================
    print()
    print("=" * 90)
    print("РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ:")
    print("=" * 90)
    print()

    # Формируем таблицу результатов
    results_table = []
    for i in range(n_objects):
        results_table.append({
            '№': i + 1,
            'Объект': objects[i],
            'Кол-во бригад': brigades_distribution[i],
            'Объем СМР, тыс.руб.': smr_per_object[i]
        })

    RESULT_DATA = pd.DataFrame(results_table)

    OPTIMIZATION_RESULTS = {
        'total_smr': total_smr,
        'brigades_distribution': brigades_distribution,
        'smr_per_object': smr_per_object,
        'F_table': F,
        'X_table': X
    }

    print("ОПТИМАЛЬНОЕ РАСПРЕДЕЛЕНИЕ БРИГАД:")
    print("-" * 90)
    print(f"{'№':<3} {'Объект':<60} {'Бригад':<10} {'СМР, тыс.руб.'}")
    print("-" * 90)

    for _, row in RESULT_DATA.iterrows():
        obj_name = row['Объект']
        if len(obj_name) > 58:
            obj_name = obj_name[:55] + "..."
        print(f"{int(row['№']):<3} {obj_name:<60} {row['Кол-во бригад']:>8}  {row['Объем СМР, тыс.руб.']:>15.0f}")

    print("-" * 90)
    print(f"{'ИТОГО:':<65} {sum(brigades_distribution):>8}  {total_smr:>15.0f}")
    print("-" * 90)
    print()

    # Проверка распределения
    print("ПРОВЕРКА РЕШЕНИЯ:")
    print("-" * 90)
    total_allocated = sum(brigades_distribution)
    print(f"   Распределено бригад: {total_allocated} из {total_brigades}")
    print(f"   Общий объем СМР: {total_smr:,.0f} тыс. руб.")

    if total_allocated == total_brigades:
        print("   ✅ Все бригады распределены оптимально!")
    else:
        print(f"   ⚠️ ВНИМАНИЕ: Распределено {total_allocated}, требуется {total_brigades}")

    print("-" * 90)
    print()

    # Анализ эффективности
    print("АНАЛИЗ ЭФФЕКТИВНОСТИ РАСПРЕДЕЛЕНИЯ:")
    print("-" * 90)
    for i in range(n_objects):
        brigades = brigades_distribution[i]
        if brigades > 0:
            efficiency = smr_per_object[i] / brigades
            print(
                f"   Объект {i + 1}: {brigades} бриг. → {smr_per_object[i]:>6.0f} тыс.руб. (эффект: {efficiency:.1f} тыс.руб/бриг.)")
        else:
            print(f"   Объект {i + 1}: 0 бригад → не задействован")
    print("-" * 90)
    print()

    print("=" * 90)
    print("✅ Оптимизация завершена успешно!")
    print(f"   Максимальный объем СМР: {total_smr:,.0f} тыс. руб.")
    print("   Для создания отчёта нажмите кнопку «Сформировать и открыть документ»")
    print("=" * 90)
    print()


def generate_document():
    """Создание нового Excel-документа с результатами"""
    global RESULT_DATA, OPTIMIZATION_RESULTS

    if RESULT_DATA is None or OPTIMIZATION_RESULTS is None:
        print("❌ ОШИБКА: Сначала необходимо выполнить расчёт!")
        print("   Запустите скрипт без аргументов: python task4.py")
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
    filename = f"Результат_Задача4_Распределение_бригад_{timestamp}.xlsx"

    try:
        # Создаём новую книгу
        wb = xw.Book()
        sheet = wb.sheets[0]
        sheet.name = "Распределение бригад"

        # ==================== ШАПКА ====================
        sheet["B1"].value = 'Дорожно-строительный холдинг «Авто-Дор»'
        sheet["B1"].font.size = 16
        sheet["B1"].font.bold = True
        sheet["B1"].api.HorizontalAlignment = -4108

        sheet["B2"].value = 'Распределение бригад по объектам'
        sheet["B2"].font.size = 12
        sheet["B2"].api.HorizontalAlignment = -4108

        sheet["B3"].value = "Список объектов"
        sheet["B3"].font.size = 11
        sheet["B3"].font.bold = True

        # ==================== ЗАГОЛОВКИ ТАБЛИЦЫ ====================
        sheet["B4"].value = "№"
        sheet["C4"].value = "Наименование"
        sheet["F4"].value = "Кол-во бригад, шт."
        sheet["H4"].value = "Объем СМР, тыс.руб."

        # Форматирование заголовков
        header_cells = [sheet["B4"], sheet["C4"], sheet["F4"], sheet["H4"]]
        for cell in header_cells:
            cell.font.bold = True
            cell.color = (220, 220, 220)
            cell.api.HorizontalAlignment = -4108
            cell.api.VerticalAlignment = -4108

        # Дополнительная строка с номерами колонок
        sheet["B5"].value = "1"
        sheet["C5"].value = "2"
        sheet["F5"].value = "3"
        sheet["H5"].value = "4"

        for cell in [sheet["B5"], sheet["C5"], sheet["F5"], sheet["H5"]]:
            cell.font.bold = True
            cell.api.HorizontalAlignment = -4108

        # ==================== ДАННЫЕ ====================
        row_num = 6
        for idx, row in RESULT_DATA.iterrows():
            sheet.cells(row_num, 2).value = int(row["№"])
            sheet.cells(row_num, 3).value = row["Объект"]

            brigades = int(row["Кол-во бригад"])
            smr = int(row["Объем СМР, тыс.руб."])

            # Выравнивание по центру для номера
            sheet.cells(row_num, 2).api.HorizontalAlignment = -4108

            sheet.cells(row_num, 6).value = brigades
            sheet.cells(row_num, 8).value = smr

            # Числа по центру
            sheet.cells(row_num, 6).api.HorizontalAlignment = -4108
            sheet.cells(row_num, 8).api.HorizontalAlignment = -4108

            row_num += 1

        # ==================== ИТОГО ====================
        total_row = row_num

        sheet.cells(total_row, 6).value = "Итог"
        sheet.cells(total_row, 6).font.bold = True
        sheet.cells(total_row, 6).api.HorizontalAlignment = -4108

        sheet.cells(total_row, 8).value = int(OPTIMIZATION_RESULTS['total_smr'])
        sheet.cells(total_row, 8).font.bold = True
        sheet.cells(total_row, 8).api.HorizontalAlignment = -4108

        # ==================== ПОДВАЛ ====================
        footer_row = total_row + 2

        sheet.cells(footer_row, 3).value = "Сотрудник: отдела по закупкам и снабжению"
        sheet.cells(footer_row + 1, 3).value = "(подпись)"
        sheet.cells(footer_row + 1, 3).api.HorizontalAlignment = -4108

        sheet.cells(footer_row, 7).value = "Максимов А.М."
        sheet.cells(footer_row + 1, 7).value = "(фамилия, инициалы)"
        sheet.cells(footer_row + 1, 7).api.HorizontalAlignment = -4108

        # ==================== ФОРМАТИРОВАНИЕ ====================
        # Установка ширины колонок
        sheet.range("B:B").column_width = 5
        sheet.range("C:E").column_width = 35
        sheet.range("F:G").column_width = 15
        sheet.range("H:H").column_width = 20

        # Границы таблицы
        table_range = sheet.range(f"B4:H{total_row}")
        for border_id in range(7, 13):
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
        main_task4()
        generate_document()
    else:
        # Только расчёт
        main_task4()