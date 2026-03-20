"""
Главный класс приложения
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from pathlib import Path
import ctypes

from windows.group_policy import GroupPolicyWindow
from windows.accounts import AccountsWindow
from windows.network import NetworkCheckWindow
from windows.profiles import ProfilesWindow
from windows.logs import LogsWindow
from utils.logging_helper import LoggingHelper


class PortableGroupPolicyApp:
    """Основной класс приложения"""

    def __init__(self, root):
        self.root = root
        self.root.title("Portable Group Policy Manager")
        self.root.state('zoomed')

        # Пути к папкам
        self.app_path = Path(sys.argv[0]).parent
        self.config_path = self.app_path / "config"
        self.profiles_path = self.app_path / "profiles"
        self.logs_path = self.app_path / "logs"

        # Создаем необходимые папки
        for path in [self.config_path, self.profiles_path, self.logs_path]:
            path.mkdir(exist_ok=True)

        # Проверка прав администратора
        self.check_admin_rights()

        # Инициализация логгера
        self.logger = LoggingHelper(self.logs_path)

        # Загрузка профилей
        self.profiles = {}
        self.load_profiles()

        # Создание интерфейса
        self.create_main_interface()

    def check_admin_rights(self):
        """Проверка прав администратора"""
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                self.admin_status = tk.StringVar(value="(OK) Права администратора")
                self.admin_color = "green"
            else:
                self.admin_status = tk.StringVar(value="(?) Ограниченные права")
                self.admin_color = "orange"
        except:
            self.admin_status = tk.StringVar(value="(X) Не удалось проверить")
            self.admin_color = "red"

    def create_main_interface(self):
        """Создание главного интерфейса"""
        # Заголовок
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill="x", padx=20, pady=20)

        ttk.Label(
            title_frame,
            text="Portable Group Policy Manager",
            font=("Arial", 24, "bold")
        ).pack()

        ttk.Label(
            title_frame,
            text=f"Путь: {self.app_path}",
            font=("Arial", 10)
        ).pack(pady=5)

        # Статус прав
        ttk.Label(
            title_frame,
            textvariable=self.admin_status,
            foreground=self.admin_color,
            font=("Arial", 12)
        ).pack(pady=10)

        # Основные кнопки
        center_frame = ttk.Frame(self.root)
        center_frame.pack(expand=True)

        btn_frame = ttk.Frame(center_frame)
        btn_frame.pack()

        button_style = {'width': 30, 'padding': 10}

        ttk.Button(
            btn_frame, text="Групповая политика",
            command=self.open_group_policy, **button_style
        ).pack(pady=10)

        ttk.Button(
            btn_frame, text="Учетные записи",
            command=self.open_accounts_window, **button_style
        ).pack(pady=10)

        ttk.Button(
            btn_frame, text="Профили настроек",
            command=self.open_profiles_window, **button_style
        ).pack(pady=10)

        ttk.Button(
            btn_frame, text="Проверка сети",
            command=self.open_network_check, **button_style
        ).pack(pady=10)

        ttk.Button(
            btn_frame, text="Журнал изменений",
            command=self.open_logs_window, **button_style
        ).pack(pady=10)

        ttk.Button(
            btn_frame, text="УСТРАНИТЬ ВСЕ ПРАВИЛА",
            command=self.remove_all_policies, **button_style
        ).pack(pady=10)

        ttk.Button(
            btn_frame, text="Выход",
            command=self.root.quit, **button_style
        ).pack(pady=20)

    def load_profiles(self):
        """Загрузка сохраненных профилей"""
        self.profiles = {}
        for profile_file in self.profiles_path.glob("*.json"):
            try:
                import json
                with open(profile_file, 'r', encoding='utf-8') as f:
                    self.profiles[profile_file.stem] = json.load(f)
            except:
                pass

    def log_action(self, action, computer_name=None):
        """Логирование действий"""
        self.logger.log(action, computer_name)

    def open_group_policy(self):
        """Открытие окна групповой политики"""
        GroupPolicyWindow(self.root, self)

    def open_accounts_window(self):
        """Открытие окна учетных записей"""
        AccountsWindow(self.root, self)

    def open_profiles_window(self):
        """Открытие окна профилей"""
        ProfilesWindow(self.root, self)

    def open_network_check(self):
        """Открытие окна проверки сети"""
        NetworkCheckWindow(self.root, self)

    def open_logs_window(self):
        """Открытие окна журнала"""
        LogsWindow(self.root, self)

    def remove_all_policies(self):
        """Удаление всех политик"""
        from core.registry_utils import RegistryUtils

        if not messagebox.askyesno(
                "ПОДТВЕРЖДЕНИЕ",
                "ВНИМАНИЕ! Это действие УДАЛИТ ВСЕ примененные правила\n"
                "групповой политики для всех пользователей.\n\nПродолжить?"
        ):
            return

        if not messagebox.askyesno(
                "ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ",
                "Это действие НЕЛЬЗЯ отменить!\nТочно продолжить?"
        ):
            return

        try:
            registry = RegistryUtils()
            users_removed = registry.remove_all_policies()

            self.log_action(
                f"ПОЛНОЕ УСТРАНЕНИЕ ВСЕХ ПРАВИЛ - {users_removed} пользователей",
                os.environ.get('COMPUTERNAME', 'UNKNOWN')
            )

            messagebox.showinfo(
                "УСПЕХ",
                f"Все правила устранены!\nОбработано пользователей: {users_removed}\n"
                "Рекомендуется перезагрузка."
            )
        except Exception as e:
            messagebox.showerror("ОШИБКА", f"Не удалось устранить правила: {str(e)}")