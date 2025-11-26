# ======================== task2.py — ИСПРАВЛЕННАЯ ВЕРСИЯ ========================
import pandas as pd
import os
from datetime import datetime

# Глобальные переменные
RESULT_DF = None
OPTIMIZATION_RESULTS = None


def main_task2():
    """Основная функция решения Задачи 2"""
    global RESULT_DF, OPTIMIZATION_RESULTS

    try:
        from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD
    except ImportError:
        print("❌ ОШИБКА: Не установлен модуль pulp")
        print("   Установите: pip install pulp")
        return

    print("=" * 80)
    print("ЗАДАЧА 2: Формирование оптимального портфеля строительных заказов")
    print("=" * 80)
    print()

    # ==================== ИСХОДНЫЕ ДАННЫЕ ====================
    projects = [
        "Строительство скоростной трассы для многофункционального комплекса",
        "Строительство трассы у жилого комплекса из трех высотных зданий",
        "Строительство нетипового выезда из жилого квартала",
        "Строительство частной дороги для гостиницы",
        "Строительство дороги у многофункционального спортивного комплекса"
    ]

    data = {
        "Прибыль": [6000000, 5000000, 4500000, 4000000, 3800000],
        "Бюджет": [3200000, 2100000, 2150000, 1900000, 14500000],
        "Ресурсы_чч": [2800, 1800, 1430, 1200, 1092],
        "Риск": [3, 3, 2, 1, 2],
        "Важность": [0.160411, 0.126499, 0.114086, 0.102577, 0.097539]
    }

    df = pd.DataFrame(data, index=projects)

    print("ИСХОДНЫЕ ДАННЫЕ О ПРОЕКТАХ:")
    print("-" * 80)
    for idx, project in enumerate(projects):
        print(f"\n{idx + 1}. {project}")
        print(f"   Прибыль:     {data['Прибыль'][idx]:>12,} руб")
        print(f"   Бюджет:      {data['Бюджет'][idx]:>12,} руб")
        print(f"   Ресурсы:     {data['Ресурсы_чч'][idx]:>12,} чел.-ч")
        print(f"   Риск:        {data['Риск'][idx]:>12} балл(ов)")
        print(f"   Важность:    {data['Важность'][idx]:>12.6f}")
    print("-" * 80)
    print()

    # ==================== ОГРАНИЧЕНИЯ ====================
    MAX_BUDGET = 7000000
    MIN_PROFIT = 13000000
    MAX_MANHOURS = 5800
    MAX_RISK = 10

    print("ОГРАНИЧЕНИЯ:")
    print(f"   • Максимальный бюджет:           {MAX_BUDGET:>12,} руб")
    print(f"   • Минимальная прибыль:           {MIN_PROFIT:>12,} руб")
    print(f"   • Максимум человеко-часов:       {MAX_MANHOURS:>12,} чел.-ч")
    print(f"   • Максимальный суммарный риск:   {MAX_RISK:>12} баллов")
    print()

    print("ЛОГИЧЕСКИЕ ЗАВИСИМОСТИ:")
    print("   • Проекты №1 и №2 могут быть выбраны только вместе (зависимость)")
    print("   • Проекты №4 и №5 взаимоисключающие (гостиница ИЛИ спорткомплекс)")
    print()

    # ==================== МОДЕЛЬ ОПТИМИЗАЦИИ ====================
    print("Запуск оптимизации...")
    print("-" * 80)

    prob = LpProblem("Портфель_заказов_Дорожно-строительный_холдинг_«Авто-Дор»", LpMaximize)

    # Переменные: x[i] = 1, если берём проект
    x = LpVariable.dicts("Выбрать", projects, cat="Binary")

    # Целевая функция: максимизация суммарной важности
    prob += lpSum(df.loc[p, "Важность"] * x[p] for p in projects), "Целевая_функция"

    # Ограничения
    prob += lpSum(df.loc[p, "Бюджет"] * x[p] for p in projects) <= MAX_BUDGET, "Ограничение_Бюджет"
    prob += lpSum(df.loc[p, "Прибыль"] * x[p] for p in projects) >= MIN_PROFIT, "Ограничение_Прибыль"
    prob += lpSum(df.loc[p, "Ресурсы_чч"] * x[p] for p in projects) <= MAX_MANHOURS, "Ограничение_Ресурсы"
    prob += lpSum(df.loc[p, "Риск"] * x[p] for p in projects) <= MAX_RISK, "Ограничение_Риск"

    # Логические зависимости
    prob += x[projects[0]] == x[projects[1]], "Зависимость_Проекты_1_и_2"
    prob += x[projects[3]] + x[projects[4]] <= 1, "Взаимоисключение_Проекты_4_и_5"

    # Решение
    prob.solve(PULP_CBC_CMD(msg=False))

    # ==================== РЕЗУЛЬТАТЫ ====================
    print()
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ:")
    print("=" * 80)
    print()

    selected = [p for p in projects if x[p].value() == 1]

    if not selected:
        print("❌ Решение не найдено! Проверьте ограничения.")
        return

    print(f"Статус решения: {prob.status} (Optimal = 1)")
    print(f"Количество выбранных проектов: {len(selected)}")
    print()

    # Формируем результат
    result_df = df.loc[selected].copy()
    result_df = result_df.reset_index()
    result_df.insert(0, "№", range(1, len(result_df) + 1))
    result_df.columns = ["№", "Заказ", "Прибыль", "Бюджет", "Ресурсы_чч", "Риск", "Важность"]

    RESULT_DF = result_df

    # Итоговые показатели
    total_profit = sum(df.loc[p, "Прибыль"] * x[p].value() for p in projects)
    total_budget = sum(df.loc[p, "Бюджет"] * x[p].value() for p in projects)
    total_hours = sum(df.loc[p, "Ресурсы_чч"] * x[p].value() for p in projects)
    total_risk = sum(df.loc[p, "Риск"] * x[p].value() for p in projects)
    total_importance = sum(df.loc[p, "Важность"] * x[p].value() for p in projects)

    OPTIMIZATION_RESULTS = {
        'total_profit': total_profit,
        'total_budget': total_budget,
        'total_hours': total_hours,
        'total_risk': total_risk,
        'total_importance': total_importance,
        'selected_count': len(selected)
    }

    print("ВЫБРАННЫЕ ПРОЕКТЫ:")
    print("-" * 80)
    for idx, row in result_df.iterrows():
        print(f"\n{row['№']}. {row['Заказ']}")
        print(f"   Прибыль:     {int(row['Прибыль']):>12,} руб")
        print(f"   Бюджет:      {int(row['Бюджет']):>12,} руб")
        print(f"   Ресурсы:     {int(row['Ресурсы_чч']):>12,} чел.-ч")
        print(f"   Риск:        {int(row['Риск']):>12} балл(ов)")
        print(f"   Важность:    {row['Важность']:>12.6f}")
    print("-" * 80)
    print()

    print("ИТОГОВЫЕ ПОКАЗАТЕЛИ ПОРТФЕЛЯ:")
    print("-" * 80)
    print(f"   Суммарная прибыль:      {int(total_profit):>15,} руб  (мин: {MIN_PROFIT:,})")
    print(f"   Суммарный бюджет:       {int(total_budget):>15,} руб  (макс: {MAX_BUDGET:,})")
    print(f"   Суммарные ресурсы:      {int(total_hours):>15,} чч   (макс: {MAX_MANHOURS:,})")
    print(f"   Суммарный риск:         {int(total_risk):>15} балл (макс: {MAX_RISK})")
    print(f"   Суммарная важность:     {total_importance:>15.6f}")
    print("-" * 80)
    print()

    # Проверка ограничений
    print("ПРОВЕРКА ОГРАНИЧЕНИЙ:")
    budget_ok = total_budget <= MAX_BUDGET
    profit_ok = total_profit >= MIN_PROFIT
    hours_ok = total_hours <= MAX_MANHOURS
    risk_ok = total_risk <= MAX_RISK

    print(f"   {'✅' if budget_ok else '❌'} Бюджет:      {int(total_budget):>12,} <= {MAX_BUDGET:,}")
    print(f"   {'✅' if profit_ok else '❌'} Прибыль:     {int(total_profit):>12,} >= {MIN_PROFIT:,}")
    print(f"   {'✅' if hours_ok else '❌'} Ресурсы:     {int(total_hours):>12,} <= {MAX_MANHOURS:,}")
    print(f"   {'✅' if risk_ok else '❌'} Риск:        {int(total_risk):>12} <= {MAX_RISK}")
    print()

    if all([budget_ok, profit_ok, hours_ok, risk_ok]):
        print("✅ Все ограничения выполнены!")
    else:
        print("⚠️ ВНИМАНИЕ: Некоторые ограничения нарушены!")

    print()
    print("=" * 80)
    print("✅ Оптимизация завершена успешно!")
    print("   Для просмотра результатов нажмите кнопку «Сформировать и открыть документ»")
    print("=" * 80)
    print()


def generate_document():
    """Создание нового Excel-документа с результатами"""
    global RESULT_DF, OPTIMIZATION_RESULTS

    if RESULT_DF is None or OPTIMIZATION_RESULTS is None:
        print("❌ ОШИБКА: Сначала необходимо выполнить расчёт!")
        print("   Запустите скрипт без аргументов: python task2.py")
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
    filename = f"Результат_Задача2_Портфель_заказов_{timestamp}.xlsx"

    try:
        # Создаём новую книгу
        wb = xw.Book()
        sheet = wb.sheets[0]
        sheet.name = "Оптимальный портфель"

        # ==================== ШАПКА ====================
        sheet["B2"].value = 'Дорожно-строительный холдинг «Авто-Дор»'
        sheet["B2"].font.size = 18
        sheet["B2"].font.bold = True

        sheet["B3"].value = "Оптимальный портфель строительных заказов"
        sheet["B3"].font.size = 14

        sheet["B5"].value = f"Дата составления: {datetime.now().strftime('%d.%m.%Y')}"

        # ==================== ЗАГОЛОВКИ ТАБЛИЦЫ ====================
        sheet["B7"].value = "№"
        sheet["C7"].value = "Наименование заказа"
        sheet["D7"].value = "Прибыль, руб."
        sheet["E7"].value = "Бюджет, руб."
        sheet["F7"].value = "Человеческие ресурсы, чел.-ч"
        sheet["G7"].value = "Риск, баллов"
        sheet["H7"].value = "Важность"

        # Форматирование заголовков
        for col in range(2, 9):
            cell = sheet.cells(7, col)
            cell.font.bold = True
            cell.color = (200, 200, 200)

        # ==================== ДАННЫЕ ====================
        for idx, row in RESULT_DF.iterrows():
            excel_row = idx + 8

            sheet.cells(excel_row, 2).value = row["№"]
            sheet.cells(excel_row, 3).value = row["Заказ"]
            sheet.cells(excel_row, 4).value = int(row["Прибыль"])
            sheet.cells(excel_row, 5).value = int(row["Бюджет"])
            sheet.cells(excel_row, 6).value = int(row["Ресурсы_чч"])
            sheet.cells(excel_row, 7).value = int(row["Риск"])
            sheet.cells(excel_row, 8).value = round(row["Важность"], 6)

        # ==================== ИТОГИ ====================
        summary_row = len(RESULT_DF) + 10

        sheet.cells(summary_row, 2).value = "ИТОГО:"
        sheet.cells(summary_row, 2).font.bold = True

        sheet.cells(summary_row, 4).value = int(OPTIMIZATION_RESULTS['total_profit'])
        sheet.cells(summary_row, 5).value = int(OPTIMIZATION_RESULTS['total_budget'])
        sheet.cells(summary_row, 6).value = int(OPTIMIZATION_RESULTS['total_hours'])
        sheet.cells(summary_row, 7).value = int(OPTIMIZATION_RESULTS['total_risk'])
        sheet.cells(summary_row, 8).value = round(OPTIMIZATION_RESULTS['total_importance'], 6)

        # ==================== ПОДВАЛ ====================
        footer_row = summary_row + 1

        sheet.cells(footer_row, 3).value = "Сотрудник отдела по закупкам и снабжению"
        sheet.cells(footer_row, 7).value = "Максимов А.М."

        sheet.cells(footer_row + 1, 4).value = "(подпись)"
        sheet.cells(footer_row + 1, 7).value = "(Ф.И.О.)"

        # ==================== ФОРМАТИРОВАНИЕ ====================
        sheet.autofit(axis="columns")

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
        # Сначала выполняем расчёт, потом обновляем документ
        main_task2()
        generate_document()
    else:
        # Только расчёт
        main_task2()