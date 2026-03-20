"""
Модуль логирования действий
"""
import datetime
import os
from pathlib import Path


class LoggingHelper:
    """Класс для логирования действий"""

    def __init__(self, logs_path):
        self.logs_path = Path(logs_path)
        self.logs_path.mkdir(parents=True, exist_ok=True)

    def log(self, action, computer_name=None):
        """Запись действия в лог"""
        if computer_name is None:
            computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')

        try:
            log_file = self.logs_path / f"log_{datetime.date.today()}.txt"
            with open(log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {computer_name}: {action}\n")
        except Exception as e:
            print(f"Ошибка логирования: {e}")

    def get_logs_for_date(self, date_str):
        """Получение логов за дату"""
        log_file = self.logs_path / f"log_{date_str}.txt"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def clear_all_logs(self):
        """Очистка всех логов"""
        for log_file in self.logs_path.glob("*.txt"):
            log_file.unlink()