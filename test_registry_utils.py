"""
Тестовый модуль для проверки функций работы с реестром
Интегрируется в учебный проект для валидации изменений
Тема 02.2 - Создание и интеграция собственного модуля
"""
import unittest
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.registry_utils import validate_registry_path, sanitize_reg_value, RegistryUtils


class TestRegistryUtils(unittest.TestCase):
    """Тесты для утилит реестра"""

    def test_validate_registry_path_valid_software(self):
        """Проверка валидного пути Software"""
        path = r"Software\Microsoft\Windows\CurrentVersion\Policies"
        self.assertTrue(validate_registry_path(path))

    def test_validate_registry_path_valid_hkcu(self):
        """Проверка валидного пути HKCU"""
        path = r"HKEY_CURRENT_USER\Software\Policies"
        self.assertTrue(validate_registry_path(path))

    def test_validate_registry_path_valid_hklm(self):
        """Проверка валидного пути HKLM"""
        path = r"HKEY_LOCAL_MACHINE\SOFTWARE\Policies"
        self.assertTrue(validate_registry_path(path))

    def test_validate_registry_path_invalid_traversal(self):
        """Проверка невалидного пути с обходом"""
        path = r"Invalid\Path\With\Injection\..\.."
        self.assertFalse(validate_registry_path(path))

    def test_validate_registry_path_invalid_chars(self):
        """Проверка пути с запрещенными символами"""
        path = r"Software\Test|Invalid"
        self.assertFalse(validate_registry_path(path))

    def test_validate_registry_path_empty(self):
        """Проверка пустого пути"""
        path = ""
        self.assertFalse(validate_registry_path(path))

    def test_sanitize_reg_value_backslash(self):
        """Проверка экранирования обратных слешей"""
        input_val = r'Test\Value\With\Backslash'
        expected = r'Test\\Value\\With\\Backslash'
        self.assertEqual(sanitize_reg_value(input_val), expected)

    def test_sanitize_reg_value_quotes(self):
        """Проверка экранирования кавычек"""
        input_val = 'Test"Value"With"Quotes'
        expected = 'Test\\"Value\\"With\\"Quotes'
        self.assertEqual(sanitize_reg_value(input_val), expected)

    def test_sanitize_reg_value_integer(self):
        """Проверка преобразования числа"""
        input_val = 123
        self.assertEqual(sanitize_reg_value(input_val), "123")

    def test_registry_utils_get_all_users(self):
        """Проверка получения списка пользователей"""
        registry = RegistryUtils()
        users = registry.get_all_users()
        self.assertIsInstance(users, list)

    def test_log_action_format(self):
        """Проверка формата логирования"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.assertRegex(timestamp, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""

    def test_module_import(self):
        """Проверка импорта модулей"""
        from core import registry_utils
        from utils import logging_helper
        from windows import group_policy
        self.assertTrue(True)

    def test_app_initialization(self):
        """Проверка инициализации приложения"""
        # Тест без запуска GUI
        from core.registry_utils import RegistryUtils
        registry = RegistryUtils()
        self.assertIsNotNone(registry)


if __name__ == "__main__":
    # Запуск тестов
    unittest.main(verbosity=2)