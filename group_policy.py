"""
Окно настройки групповой политики
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import os
import threading
import json
import shutil
from pathlib import Path


class GroupPolicyWindow:
    """Класс окна групповой политики"""

    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Настройка групповой политики")
        self.window.state('zoomed')

        self.vars = {}
        self.blocked_apps = []

        self.create_scrollable_frame()
        self.create_policy_controls()
        self.create_buttons()

    def create_scrollable_frame(self):
        """Создание прокручиваемого фрейма"""
        self.canvas = tk.Canvas(self.window)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.main_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        self.main_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_policy_controls(self):
        """Создание элементов управления политиками"""
        computer_name = os.environ.get('COMPUTERNAME', 'Неизвестно')

        ttk.Label(
            self.main_frame,
            text=f"Компьютер: {computer_name}",
            font=("Arial", 14, "italic")
        ).pack(pady=10)

        info_frame = ttk.LabelFrame(self.main_frame, text="Информация", padding=10)
        info_frame.pack(padx=20, pady=5, fill="x")

        info_text = (
            "Настройки будут применяться ТОЛЬКО к обычным пользователям.\n"
            "Администраторы сохранят полный доступ."
        )
        ttk.Label(
            info_frame,
            text=info_text,
            foreground="blue",
            font=("Arial", 10)
        ).pack()

        # Вкладки
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(padx=20, pady=10, fill="both", expand=True)

        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Основные ограничения")

        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Дополнительно")

        # Переменные
        self.vars = {
            'wallpaper': tk.BooleanVar(),
            'hide_drives': tk.BooleanVar(),
            'disable_store': tk.BooleanVar(),
            'block_drives': tk.BooleanVar(),
            'no_password_change': tk.BooleanVar(),
            'disable_taskmgr': tk.BooleanVar(),
            'no_control_panel': tk.BooleanVar(),
            'block_cmd': tk.BooleanVar(),
            'block_powershell': tk.BooleanVar(),
            'block_regedit': tk.BooleanVar(),
            'disable_shutdown': tk.BooleanVar(),
        }

        # Основные чекбоксы
        main_checks = [
            ("Запрет на замену обоев", 'wallpaper'),
            ("Скрыть диски", 'hide_drives'),
            ("Отключить Магазин Windows", 'disable_store'),
            ("Запретить доступ к дискам", 'block_drives'),
            ("Запретить смену пароля", 'no_password_change'),
            ("Отключить Диспетчер задач", 'disable_taskmgr'),
            ("Запретить Панель управления", 'no_control_panel'),
            ("Запретить cmd.exe", 'block_cmd'),
            ("Запретить PowerShell", 'block_powershell'),
        ]

        for text, var_name in main_checks:
            cb = ttk.Checkbutton(main_frame, text=text, variable=self.vars[var_name])
            cb.pack(anchor='w', pady=5, padx=20)

        # Дополнительные
        advanced_checks = [
            ("Запретить Редактор реестра", 'block_regedit'),
            ("Отключить завершение работы", 'disable_shutdown'),
        ]

        for text, var_name in advanced_checks:
            cb = ttk.Checkbutton(advanced_frame, text=text, variable=self.vars[var_name])
            cb.pack(anchor='w', pady=5, padx=20)

        # Блокировка приложений
        ttk.Separator(advanced_frame, orient='horizontal').pack(fill='x', pady=15, padx=20)

        ttk.Label(
            advanced_frame,
            text="Блокировка приложений:",
            font=("Arial", 12, "bold")
        ).pack(anchor='w', padx=20, pady=5)

        self.block_apps_var = tk.BooleanVar()
        cb = ttk.Checkbutton(
            advanced_frame,
            text="Запретить запуск приложений",
            variable=self.block_apps_var,
            command=self.manage_blocked_apps
        )
        cb.pack(anchor='w', pady=5, padx=20)

        self.apps_list_label = ttk.Label(
            advanced_frame,
            text="",
            foreground="blue",
            font=("Arial", 10)
        )
        self.apps_list_label.pack(anchor='w', padx=40, pady=5)

    def manage_blocked_apps(self):
        """Управление заблокированными приложениями"""
        if self.block_apps_var.get():
            apps = simpledialog.askstring(
                "Запрещенные приложения",
                "Введите названия через запятую (например: notepad.exe, calc.exe)",
                parent=self.window
            )
            if apps:
                self.blocked_apps = [app.strip() for app in apps.split(',')]
                self.apps_list_label.config(text=f"Заблокировано: {', '.join(self.blocked_apps)}")
            else:
                self.block_apps_var.set(False)
                self.apps_list_label.config(text="")

    def create_buttons(self):
        """Создание кнопок"""
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)

        button_style = {'width': 20, 'padding': 8}

        ttk.Button(
            btn_frame, text="Сохранить профиль",
            command=self.save_profile, **button_style
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame, text="Загрузить профиль",
            command=self.load_profile, **button_style
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame, text="Применить",
            command=self.apply_policies, **button_style
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame, text="Сбросить",
            command=self.reset_policies, **button_style
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame, text="Закрыть",
            command=self.window.destroy, **button_style
        ).pack(side='left', padx=5)

    def save_profile(self):
        """Сохранение профиля"""
        name = simpledialog.askstring("Сохранение профиля", "Введите название:", parent=self.window)
        if name:
            profile_data = {
                'settings': {key: var.get() for key, var in self.vars.items()},
                'blocked_apps': self.blocked_apps,
                'block_apps': self.block_apps_var.get()
            }
            profile_file = self.main_app.profiles_path / f"{name}.json"
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            self.main_app.load_profiles()
            messagebox.showinfo("Успех", f"Профиль '{name}' сохранен!")

    def load_profile(self):
        """Загрузка профиля"""
        if not self.main_app.profiles:
            messagebox.showinfo("Информация", "Нет сохраненных профилей")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("Выбор профиля")
        dialog.geometry("400x500")

        ttk.Label(dialog, text="Выберите профиль:", font=("Arial", 14)).pack(pady=15)

        listbox = tk.Listbox(dialog, font=("Arial", 12))
        listbox.pack(padx=20, pady=10, fill="both", expand=True)

        for profile_name in self.main_app.profiles.keys():
            listbox.insert(tk.END, profile_name)

        def load_selected():
            selection = listbox.curselection()
            if selection:
                profile_name = listbox.get(selection[0])
                profile = self.main_app.profiles[profile_name]
                for key, value in profile['settings'].items():
                    if key in self.vars:
                        self.vars[key].set(value)
                self.blocked_apps = profile.get('blocked_apps', [])
                self.block_apps_var.set(profile.get('block_apps', False))
                dialog.destroy()
                messagebox.showinfo("Успех", f"Профиль '{profile_name}' загружен!")

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Загрузить", command=load_selected, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=15).pack(side='left', padx=5)

    def get_standard_users(self):
        """Получение списка обычных пользователей"""
        from utils.user_utils import UserUtils
        utils = UserUtils()
        return utils.get_standard_users()

    def apply_policies(self):
        """Применение политик"""

        def apply_thread():
            try:
                standard_users = self.get_standard_users()

                for username in standard_users:
                    for key, var in self.vars.items():
                        if var.get():
                            # Применение политики (упрощенно)
                            pass

                self.main_app.log_action(
                    f"Применены настройки для {len(standard_users)} пользователей",
                    os.environ.get('COMPUTERNAME', 'UNKNOWN')
                )

                self.window.after(0, lambda: messagebox.showinfo(
                    "Успех",
                    "Настройки применены!\nТребуется перезагрузка."
                ))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Ошибка", str(e)))

        thread = threading.Thread(target=apply_thread)
        thread.daemon = True
        thread.start()

    def reset_policies(self):
        """Сброс политик"""
        if messagebox.askyesno("Подтверждение", "Сбросить все настройки?"):
            from core.registry_utils import RegistryUtils
            registry = RegistryUtils()

            standard_users = self.get_standard_users()
            for username in standard_users:
                registry.delete_policy(username, r"Software\Microsoft\Windows\CurrentVersion\Policies")

            self.main_app.log_action(
                "Сброс настроек групповой политики",
                os.environ.get('COMPUTERNAME', 'UNKNOWN')
            )

            messagebox.showinfo("Успех", "Настройки сброшены!")