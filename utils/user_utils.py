"""
Утилиты для работы с пользователями
"""
import subprocess


class UserUtils:
    """Класс для операций с пользователями"""

    def get_all_users(self):
        """Получение всех пользователей"""
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

    def get_standard_users(self):
        """Получение обычных пользователей (не админы)"""
        all_users = self.get_all_users()

        # Получение администраторов
        admins = []
        try:
            for group in ['Администраторы', 'Administrators']:
                result = subprocess.run(
                    f"net localgroup {group}", shell=True,
                    capture_output=True, text=True, encoding='cp866'
                )
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('---'):
                        admins.extend(line.strip().split())
        except:
            pass

        # Системные учетки
        system_accounts = [
            'Администратор', 'Гость', 'Administrator',
            'Guest', 'DefaultAccount', 'WDAGUtilityAccount'
        ]

        standard_users = []
        for user in all_users:
            if user not in admins and user not in system_accounts:
                standard_users.append(user)

        return standard_users

    def is_admin(self, username):
        """Проверка является ли пользователь администратором"""
        try:
            result = subprocess.run(
                f"net user {username}", shell=True,
                capture_output=True, text=True, encoding='cp866'
            )
            return 'Глобальные группы' in result.stdout or 'Local Group Memberships' in result.stdout
        except:
            return False