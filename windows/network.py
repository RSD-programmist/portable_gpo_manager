"""
Окно проверки сети
"""
import tkinter as tk
from tkinter import ttk
import subprocess
import os
import threading
import datetime


class NetworkCheckWindow:
    """Класс окна проверки сети"""

    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Проверка сети")
        self.window.state('zoomed')
        self.is_running = False

        self.create_interface()
        self.run_network_diagnostics()

    def create_interface(self):
        """Создание интерфейса"""
        ttk.Label(
            self.window,
            text="Диагностика сети",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        # Консоль
        console_frame = ttk.LabelFrame(self.window, text="Консоль", padding=10)
        console_frame.pack(padx=30, pady=10, fill="both", expand=True)

        self.console_text = tk.Text(
            console_frame, wrap="word",
            font=("Courier", 11), bg="black", fg="green"
        )
        self.console_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(console_frame, orient="vertical", command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Ping Google", command=lambda: self.run_command("ping -n 4 google.com")).pack(
            side='left', padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_console).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Закрыть", command=self.window.destroy).pack(side='left', padx=5)

    def write_to_console(self, text):
        """Вывод в консоль"""
        self.console_text.insert(tk.END, text + "\n")
        self.console_text.see(tk.END)
        self.window.update()

    def clear_console(self):
        """Очистка консоли"""
        self.console_text.delete(1.0, tk.END)

    def run_command(self, command):
        """Выполнение команды"""

        def run_thread():
            try:
                self.write_to_console(f"\n{'=' * 60}")
                self.write_to_console(f"КОМАНДА: {command}")
                self.write_to_console(f"{'=' * 60}\n")

                result = subprocess.run(
                    command, shell=True,
                    capture_output=True, text=True,
                    encoding='cp866', timeout=30
                )

                if result.stdout:
                    self.write_to_console(result.stdout)
                if result.stderr:
                    self.write_to_console(f"ОШИБКА: {result.stderr}")
            except Exception as e:
                self.write_to_console(f"ОШИБКА: {str(e)}")

        thread = threading.Thread(target=run_thread)
        thread.daemon = True
        thread.start()

    def run_network_diagnostics(self):
        """Автоматическая диагностика"""

        def diagnostics_thread():
            commands = [
                ("ipconfig /all", "ИНФОРМАЦИЯ О СЕТИ"),
                ("ping -n 4 127.0.0.1", "ПРОВЕРКА LOCALHOST"),
                ("ping -n 4 8.8.8.8", "ПРОВЕРКА DNS"),
            ]

            for cmd, desc in commands:
                self.write_to_console(f"\n{'=' * 60}")
                self.write_to_console(f"  {desc}")
                self.write_to_console(f"{'=' * 60}\n")

                try:
                    result = subprocess.run(
                        cmd, shell=True,
                        capture_output=True, text=True,
                        encoding='cp866', timeout=30
                    )
                    if result.stdout:
                        self.write_to_console(result.stdout)
                except:
                    pass

        thread = threading.Thread(target=diagnostics_thread)
        thread.daemon = True
        thread.start()