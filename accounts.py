"""
Окно управления учетными записями
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import os


class AccountsWindow:
    """Класс окна управления учетными записями"""

    def __init__(self, parent, main_app=None):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Управление учетными записями")
        self.window.geometry("400x300")

        ttk.Label(
            self.window,
            text="Управление учетными записями",
            font=("Arial", 14)
        ).pack(pady=20)

        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Добавить", command=self.add_account, width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Изменить", command=self.modify_account, width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_account, width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Закрыть", command=self.window.destroy, width=15).pack(pady=5)

    def add_account(self):
        """Добавление пользователя"""
        login = simpledialog.askstring("Логин", "Введите имя пользователя:", parent=self.window)
        if not login:
            return

        password = simpledialog.askstring("Пароль", "Введите пароль:", show='*', parent=self.window)

        try:
            result = subprocess.run(
                f'net user "{login}" "{password}" /add',
                shell=True, capture_output=True, text=True, encoding='cp866'
            )

            if result.returncode == 0:
                if self.main_app:
                    self.main_app.log_action(f"СОЗДАН ПОЛЬЗОВАТЕЛЬ: {login}")
                messagebox.showinfo("Успех", f"Пользователь {login} создан!")
            else:
                messagebox.showerror("Ошибка", result.stderr)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def modify_account(self):
        """Изменение пароля"""
        try:
            result = subprocess.run("net user", shell=True, capture_output=True, text=True)
            users = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('---'):
                    users.extend(line.strip().split())

            if not users:
                messagebox.showinfo("Информация", "Нет пользователей")
                return

            user = simpledialog.askstring("Пользователь", "Введите имя:", parent=self.window)
            if not user:
                return

            password = simpledialog.askstring("Пароль", "Новый пароль:", show='*', parent=self.window)

            result = subprocess.run(
                f'net user "{user}" "{password}"',
                shell=True, capture_output=True, text=True, encoding='cp866'
            )

            if result.returncode == 0:
                if self.main_app:
                    self.main_app.log_action(f"ИЗМЕНЕН ПАРОЛЬ: {user}")
                messagebox.showinfo("Успех", "Пароль изменен!")
            else:
                messagebox.showerror("Ошибка", result.stderr)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_account(self):
        """Удаление пользователя"""
        user = simpledialog.askstring("Удаление", "Введите имя пользователя:", parent=self.window)
        if not user:
            return

        if messagebox.askyesno("Подтверждение", f"Удалить {user}?"):
            try:
                result = subprocess.run(
                    f'net user "{user}" /delete',
                    shell=True, capture_output=True, text=True, encoding='cp866'
                )

                if result.returncode == 0:
                    if self.main_app:
                        self.main_app.log_action(f"УДАЛЕН ПОЛЬЗОВАТЕЛЬ: {user}")
                    messagebox.showinfo("Успех", f"Пользователь {user} удален!")
                else:
                    messagebox.showerror("Ошибка", result.stderr)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))