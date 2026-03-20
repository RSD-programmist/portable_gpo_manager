"""
Окно журнала изменений
"""
import tkinter as tk
from tkinter import ttk, messagebox


class LogsWindow:
    """Класс окна журнала"""

    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Журнал изменений")
        self.window.state('zoomed')

        self.create_interface()
        self.load_logs()

    def create_interface(self):
        """Создание интерфейса"""
        ttk.Label(
            self.window,
            text="Журнал изменений",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill="x", padx=30, pady=10)

        ttk.Label(top_frame, text="Дата:", font=("Arial", 12)).pack(side="left", padx=5)

        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(top_frame, textvariable=self.date_var, width=30)
        self.date_combo.pack(side="left", padx=5)
        self.date_combo.bind('<<ComboboxSelected>>', lambda e: self.load_logs())

        ttk.Button(top_frame, text="Обновить", command=self.load_logs, width=15).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Очистить", command=self.clear_logs, width=15).pack(side="left", padx=5)

        frame = ttk.LabelFrame(self.window, text="Записи", padding=15)
        frame.pack(padx=30, pady=10, fill="both", expand=True)

        self.logs_text = tk.Text(frame, wrap="word", font=("Courier", 11))
        self.logs_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(self.window, text="Закрыть", command=self.window.destroy, width=20).pack(pady=20)

        self.update_date_list()

    def update_date_list(self):
        """Обновление списка дат"""
        dates = []
        for log_file in self.main_app.logs_path.glob("log_*.txt"):
            date_str = log_file.stem.replace("log_", "")
            dates.append(date_str)
        dates.sort(reverse=True)
        self.date_combo['values'] = dates
        if dates:
            self.date_combo.set(dates[0])

    def load_logs(self):
        """Загрузка записей"""
        self.logs_text.delete(1.0, tk.END)
        date = self.date_var.get()
        if not date:
            return

        log_file = self.main_app.logs_path / f"log_{date}.txt"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                self.logs_text.insert(1.0, f.read())
        else:
            self.logs_text.insert(1.0, f"Нет записей за {date}")

    def clear_logs(self):
        """Очистка журнала"""
        if messagebox.askyesno("Подтверждение", "Очистить все записи?"):
            for log_file in self.main_app.logs_path.glob("*.txt"):
                log_file.unlink()
            self.update_date_list()
            self.logs_text.delete(1.0, tk.END)
            messagebox.showinfo("Успех", "Журнал очищен!")