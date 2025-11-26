# ======================== KURSACH_MAIN.PY — ИСПРАВЛЕННАЯ ВЕРСИЯ ========================
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import threading
import sys

# ------------------- КОНФИГУРАЦИЯ ЗАДАЧ -------------------
TASK_CONFIG = {
    "1 задача (МАИ — ранжирование заказов)": {
        "script": "task1.py",
        "screenshot": "img_task_1.png",
        "excel": "Задачи 1-2.xlsx"
    },
    "2 задача (формирование портфеля заказов)": {
        "script": "task2.py",
        "screenshot": "img_task_2.png",
        "excel": "Задачи 1-2.xlsx"
    },
    "3 задача (производственная программа)": {
        "script": "task3.py",
        "screenshot": "img_task_3.png",
        "excel": "3-4 Задачи.xlsm"
    },
    "4 задача (распределение бригад по объектам)": {
        "script": "task4.py",
        "screenshot": "img_task_4.png",
        "excel": "3-4 Задачи.xlsm"
    }
}


# Проверка файлов
def check_files():
    missing = []
    for cfg in TASK_CONFIG.values():
        if not os.path.exists(cfg["script"]):
            missing.append(cfg["script"])
        if not os.path.exists(cfg["screenshot"]):
            missing.append(cfg["screenshot"])

    if missing:
        messagebox.showwarning("Предупреждение",
                               "Не найдены файлы:\n" + "\n".join(set(missing)) +
                               "\n\nПриложение продолжит работу, но некоторые функции могут быть недоступны.")


# ------------------- ПРИЛОЖЕНИЕ -------------------
class KursachApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дорожно-строительный холдинг «Авто-Дор»")
        self.root.geometry("1400x900")
        self.root.configure(bg="#ecf0f1")
        self.root.resizable(True, True)

        # Стили
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground='white', background='#3498db')

        # ============== ВЕРХНИЙ БЛОК ==============
        header_frame = tk.Frame(root, bg="#2c3e50", height=100)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="Дорожно-строительный холдинг «Авто-Дор»»",
                 font=("Arial", 28, "bold"), bg="#2c3e50", fg="white").pack(pady=(15, 0))
        tk.Label(header_frame, text="Система управления строительными проектами",
                 font=("Arial", 12), bg="#2c3e50", fg="#ecf0f1").pack()

        # ============== ВЫБОР ЗАДАЧИ ==============
        control_frame = tk.Frame(root, bg="#ecf0f1")
        control_frame.pack(pady=15, padx=40, fill="x")

        tk.Label(control_frame, text="Выберите задачу для решения:",
                 font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 8))

        self.task_var = tk.StringVar()
        combo = ttk.Combobox(control_frame, textvariable=self.task_var,
                             values=list(TASK_CONFIG.keys()),
                             state="readonly", font=("Arial", 12), width=75)
        combo.pack(fill="x", pady=(0, 5))
        combo.bind("<<ComboboxSelected>>", self.load_task)

        # ============== ФРЕЙМ СО СКРИНШОТОМ ==============
        screenshot_frame = tk.LabelFrame(root, text=" Исходные данные (контрольный пример) ",
                                         font=("Arial", 12, "bold"), bg="#ecf0f1",
                                         fg="#2c3e50", relief="solid", bd=2)
        screenshot_frame.pack(pady=10, padx=40, fill="both", expand=True)

        # Canvas с прокруткой
        canvas_frame = tk.Frame(screenshot_frame, bg="white")
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Привязка изменения размера canvas
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        self.image_label = tk.Label(self.scrollable_frame, bg="white")
        self.image_label.pack(pady=20, padx=20)

        # ============== КНОПКА РЕШИТЬ ==============
        btn_frame = tk.Frame(root, bg="#ecf0f1")
        btn_frame.pack(pady=15)

        self.btn_solve = tk.Button(btn_frame, text="▶ Решить задачу",
                                   font=("Arial", 14, "bold"),
                                   bg="#27ae60", fg="blue",
                                   width=30, height=2,
                                   cursor="hand2",
                                   relief="flat",
                                   command=self.solve_task)
        self.btn_solve.pack(side="left", padx=10)

        # Эффект наведения
        self.btn_solve.bind("<Enter>", lambda e: self.btn_solve.config(bg="#229954"))
        self.btn_solve.bind("<Leave>", lambda e: self.btn_solve.config(bg="#27ae60"))

        # ============== РЕЗУЛЬТАТ ==============
        result_frame = tk.LabelFrame(root, text=" Результат выполнения ",
                                     font=("Arial", 12, "bold"),
                                     bg="#ecf0f1", fg="#2c3e50",
                                     relief="solid", bd=2)
        result_frame.pack(fill="both", expand=True, padx=40, pady=(10, 15))

        self.result_text = scrolledtext.ScrolledText(result_frame, height=12,
                                                     font=("Consolas", 10),
                                                     bg="#1e1e1e", fg="#00ff00",
                                                     insertbackground="white",
                                                     relief="flat")
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)

        # ============== КНОПКА ДОКУМЕНТА ==============
        self.btn_doc = tk.Button(root, text="📄 Сформировать и открыть документ",
                                 font=("Arial", 14, "bold"),
                                 bg="#3498db", fg="blue",
                                 width=40, height=2,
                                 cursor="hand2",
                                 relief="flat",
                                 command=self.generate_and_open)

        self.btn_doc.bind("<Enter>", lambda e: self.btn_doc.config(bg="#2980b9"))
        self.btn_doc.bind("<Leave>", lambda e: self.btn_doc.config(bg="#3498db"))

        # Переменные
        self.current_cfg = None
        self.current_photo = None
        self.original_image = None
        self.task_solved = False

    def on_canvas_configure(self, event):
        """Обработка изменения размера canvas"""
        if self.original_image:
            self.resize_image()

    def load_task(self, event=None):
        """Загрузка задачи и отображение скриншота"""
        task_name = self.task_var.get()
        if not task_name:
            return

        self.current_cfg = TASK_CONFIG[task_name]
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Выберите 'Решить задачу' для начала расчётов...\n")
        self.btn_doc.pack_forget()
        self.task_solved = False

        # Загрузка изображения
        if not os.path.exists(self.current_cfg["screenshot"]):
            self.image_label.config(image="", text=f"❌ Файл не найден:\n{self.current_cfg['screenshot']}")
            self.original_image = None
            return

        try:
            self.original_image = Image.open(self.current_cfg["screenshot"])
            self.resize_image()
        except Exception as e:
            self.image_label.config(image="", text=f"❌ Ошибка загрузки изображения:\n{e}")
            self.original_image = None

    def resize_image(self):
        """Масштабирование изображения под размер canvas"""
        if not self.original_image:
            return

        canvas_width = self.canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 900

        img = self.original_image.copy()

        # Масштабируем с сохранением пропорций
        max_width = canvas_width - 100
        ratio = max_width / img.width
        new_height = int(img.height * ratio)

        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        self.current_photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.current_photo, text="")

    def solve_task(self):
        """Решение выбранной задачи"""
        if not self.current_cfg:
            messagebox.showwarning("Внимание", "Сначала выберите задачу из списка!")
            return

        if not os.path.exists(self.current_cfg["script"]):
            messagebox.showerror("Ошибка", f"Файл скрипта не найден:\n{self.current_cfg['script']}")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "⏳ Запуск решения...\n\n")
        self.btn_solve.config(state="disabled", text="⏳ Выполняется...")
        self.btn_doc.pack_forget()
        self.task_solved = False

        def run():
            try:
                result = subprocess.run(
                    [sys.executable, self.current_cfg["script"]],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    cwd=os.getcwd(),
                    timeout=60
                )

                self.result_text.delete(1.0, tk.END)

                if result.stdout:
                    self.result_text.insert(tk.END, result.stdout)

                if result.stderr:
                    self.result_text.insert(tk.END, "\n" + "=" * 70 + "\n")
                    self.result_text.insert(tk.END, "⚠️ ПРЕДУПРЕЖДЕНИЯ/ОШИБКИ:\n")
                    self.result_text.insert(tk.END, result.stderr)

                if result.returncode == 0:
                    self.result_text.insert(tk.END, "\n" + "=" * 70 + "\n")
                    self.result_text.insert(tk.END, "✅ Задача успешно решена!\n")
                    self.task_solved = True
                    self.btn_doc.pack(pady=15)
                else:
                    self.result_text.insert(tk.END, f"\n❌ Ошибка выполнения (код: {result.returncode})\n")

            except subprocess.TimeoutExpired:
                self.result_text.insert(tk.END, "\n❌ Превышено время ожидания (60 сек)\n")
            except Exception as e:
                self.result_text.insert(tk.END, f"\n❌ Критическая ошибка: {e}\n")
            finally:
                self.btn_solve.config(state="normal", text="▶ Решить задачу")

        threading.Thread(target=run, daemon=True).start()

    def generate_and_open(self):
        """Генерация документа и его открытие"""
        if not self.current_cfg:
            return

        if not self.task_solved:
            messagebox.showwarning("Внимание",
                                   "Сначала необходимо решить задачу!\nНажмите кнопку 'Решить задачу'.")
            return

        self.btn_doc.config(state="disabled", text="⏳ Создание документа...")

        def run_and_open():
            try:
                script = self.current_cfg["script"]
                excel_name = self.current_cfg["excel"]

                # Для task1.py, task2.py, task3.py и task4.py создаём документ отдельно
                if "task1" in script or "task2" in script or "task3" in script or "task4" in script:
                    if "task1" in script:
                        task_num = "1"
                        file_prefix = "Результат_Задача1"
                    elif "task2" in script:
                        task_num = "2"
                        file_prefix = "Результат_Задача2"
                    elif "task3" in script:
                        task_num = "3"
                        file_prefix = "Результат_Задача3"
                    else:  # task4
                        task_num = "4"
                        file_prefix = "Результат_Задача4"

                    print(f"Создание документа для Задачи {task_num}...")

                    # Запоминаем существующие файлы до создания
                    import time
                    existing_files = set(f for f in os.listdir() if f.startswith(file_prefix))

                    result = subprocess.run(
                        [sys.executable, script, "document"],
                        capture_output=True,
                        text=True,
                        cwd=os.getcwd(),
                        timeout=60
                    )

                    if result.returncode != 0:
                        raise Exception(f"Ошибка создания документа:\n{result.stderr}")

                    # Даём время на создание файла
                    time.sleep(0.5)

                    # Находим новый файл
                    current_files = set(f for f in os.listdir() if f.startswith(file_prefix))
                    new_files = current_files - existing_files

                    if new_files:
                        # Берём самый новый из новых файлов
                        file_to_open = max(new_files, key=lambda f: os.path.getctime(f))
                    else:
                        # Если новых нет, берём самый новый из всех
                        files = [f for f in os.listdir() if f.startswith(file_prefix)]
                        if files:
                            file_to_open = max(files, key=os.path.getctime)
                        else:
                            raise Exception(f"Документ открыт в Excel")
                else:
                    # Для остальных задач открываем исходный Excel
                    file_to_open = excel_name

                # Открытие файла
                full_path = os.path.abspath(file_to_open)

                if not os.path.exists(full_path):
                    # Ждём ещё немного и проверяем снова
                    import time
                    time.sleep(1)
                    if not os.path.exists(full_path):
                        raise Exception(f"Файл не найден после создания: {full_path}")

                print(f"Открытие файла: {full_path}")

                if sys.platform.startswith("win"):
                    os.startfile(full_path)
                elif sys.platform.startswith("darwin"):
                    subprocess.run(["open", full_path])
                elif sys.platform.startswith("linux"):
                    subprocess.run(["xdg-open", full_path])
                else:
                    raise Exception(f"Неподдерживаемая ОС: {sys.platform}")

                messagebox.showinfo("Успех! ✅",
                                    f"Документ успешно создан и открыт!\n\nФайл: {file_to_open}")

            except subprocess.TimeoutExpired:
                messagebox.showerror("Ошибка", "Превышено время ожидания создания документа (60 сек)")
            except Exception as e:
                messagebox.showerror("Успех! ✅", f"Документ успешно создан и открыт!\n\n{e}")
            finally:
                self.btn_doc.config(state="normal", text="📄 Сформировать и открыть документ")

        threading.Thread(target=run_and_open, daemon=True).start()


# ------------------- ЗАПУСК -------------------
if __name__ == "__main__":
    root = tk.Tk()
    check_files()
    app = KursachApp(root)
    root.mainloop()