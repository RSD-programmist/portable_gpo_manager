"""
Утилиты для работы с реестром Windows
Тестовый модуль для ПМ 02
"""
import subprocess
import winreg
from pathlib import Path


def validate_registry_path(path):
    """
    Валидация пути реестра
    Возвращает True если путь безопасен
    """
    if not path:
        return False

    # Запрещенные паттерны
    dangerous_patterns = ['..', '\x00', '|', '<', '>', '?', '*']
    for pattern in dangerous_patterns:
        if pattern in path:
            return False

    # Разрешенные корневые ключи
    allowed_roots = [
        'HKEY_CURRENT_USER', 'HKCU',
        'HKEY_LOCAL_MACHINE', 'HKLM',
        'HKEY_USERS', 'HKU',
        'Software\\', 'SOFTWARE\\',
        'Policies\\', 'POLICIES\\'
    ]

    path_upper = path.upper()
    if not any(path_upper.startswith(root.upper()) for root in allowed_roots):
        return False

    return True


def sanitize_reg_value(value):
    """
    Санитизация значения для реестра
    Экранирование специальных символов
    """
    if not isinstance(value, str):
        return str(value)

    # Экранирование обратных слешей и кавычек
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')

    return value


class RegistryUtils:
    """Класс для операций с реестром"""

    def __init__(self):
        self.user_policy_keys = [
            r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop",
            r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
            r"Software\Microsoft\Windows\CurrentVersion\Policies\User",
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            r"Software\Policies\Microsoft\Windows\System",
        ]

        self.machine_policy_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\WindowsStore"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\PowerShell"),
        ]

    def get_all_users(self):
        """Получение списка всех пользователей"""
        try:
            result = subprocess.run(
                "net user", shell=True,
                capture_output=True, text=True, encoding='cp866'
            )
            users = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('---'):
                    if 'команда' not in line.lower():
                        users.extend(line.strip().split())
            return users
        except:
            return []

    def remove_all_policies(self):
        """Удаление всех политик для всех пользователей"""
        all_users = self.get_all_users()
        users_processed = 0

        for username in all_users:
            try:
                for key_path in self.user_policy_keys:
                    full_path = f"HKU\\{username}\\{key_path}"
                    subprocess.run(
                        f'reg delete "{full_path}" /f',
                        shell=True, capture_output=True, timeout=5
                    )
                users_processed += 1
            except:
                pass

        for hive, key_path in self.machine_policy_keys:
            try:
                subprocess.run(
                    f'reg delete "{key_path}" /f',
                    shell=True, capture_output=True, timeout=5
                )
            except:
                pass

        subprocess.run("gpupdate /force", shell=True, capture_output=True, timeout=30)

        return users_processed

    def apply_policy(self, username, key_path, value_name, value_data, value_type=winreg.REG_DWORD):
        """Применение политики для пользователя"""
        try:
            key = winreg.CreateKey(winreg.HKEY_USERS, f"{username}\\{key_path}")
            winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            winreg.CloseKey(key)
            return True
        except:
            return False

    def delete_policy(self, username, key_path, value_name=None):
        """Удаление политики"""
        try:
            if value_name:
                key = winreg.OpenKey(winreg.HKEY_USERS, f"{username}\\{key_path}", 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, value_name)
                winreg.CloseKey(key)
            else:
                subprocess.run(
                    f'reg delete "HKU\\{username}\\{key_path}" /f',
                    shell=True, capture_output=True
                )
            return True
        except:
            return False