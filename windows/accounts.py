"""
Окно управления учетными записями
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import os


class AccountsWindow:
    def __init__(self, parent, main_app=None):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Управление учетными записями")
        self.window.geometry("500x450")
        self.window.minsize(400, 350)

        # Делаем окно видимым
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.window.transient(parent)
        self.window.grab_set()

        # Центрирование окна
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.window.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")

        self.create_interface()

    def create_interface(self):
        """Создание интерфейса окна"""
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Заголовок
        ttk.Label(main_frame, text="Управление учетными записями",
                  font=("Arial", 16, "bold")).pack(pady=20)

        # Информационная панель
        info_frame = ttk.LabelFrame(main_frame, text="Информация", padding=10)
        info_frame.pack(fill="x", pady=10)

        info_text = (
            "• Для управления учетными записями требуются права администратора\n"
            "• Будьте осторожны при удалении пользователей\n"
            "• Нельзя удалить текущую активную учетную запись"
        )
        ttk.Label(info_frame, text=info_text, font=("Arial", 9),
                  foreground="blue", justify="left").pack(anchor='w')

        # Кнопки действий
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)

        button_style = {'width': 25, 'padding': 10}

        ttk.Button(btn_frame, text="Добавить пользователя",
                   command=self.add_account, **button_style).pack(pady=8)

        ttk.Button(btn_frame, text="Изменить пароль",
                   command=self.modify_account, **button_style).pack(pady=8)

        ttk.Button(btn_frame, text="Удалить пользователя",
                   command=self.delete_account, **button_style).pack(pady=8)

        ttk.Button(btn_frame, text="Показать всех пользователей",
                   command=self.show_all_users, **button_style).pack(pady=8)

        # Кнопка закрытия
        ttk.Button(main_frame, text="Закрыть",
                   command=self.window.destroy, width=25, padding=10).pack(pady=20)

    def get_all_users_list(self):
        """Получение списка всех пользователей с информацией"""
        users_data = []
        try:
            # Используем net user с более точным парсингом
            result = subprocess.run(
                "net user", shell=True, capture_output=True,
                text=True, encoding='cp866', errors='ignore'
            )

            if result.returncode == 0:
                # Флаги для определения секции с пользователями
                in_users_section = False
                users_found = []

                for line in result.stdout.split('\n'):
                    line = line.strip()

                    # Пропускаем пустые строки
                    if not line:
                        continue

                    # Пропускаем заголовки и служебные строки
                    if any(x in line.lower() for x in [
                        'команда выполнена успешно',
                        'user accounts for',
                        '----',
                        'члены группы',
                        'глобальные члены группы',
                        'локальные члены группы'
                    ]):
                        continue

                    # Проверяем начало секции пользователей
                    # Обычно это строка с дефисами или заголовок
                    if '----' in line or line.startswith('-'):
                        in_users_section = True
                        continue

                    # Если мы в секции пользователей
                    if in_users_section:
                        # Проверяем, не конец ли это списка
                        if 'команда' in line.lower() and 'выполнена' in line.lower():
                            break

                        # Разделяем строку на части (обычно 3 имени в строке)
                        # Имена разделены множественными пробелами
                        parts = line.split()

                        for user in parts:
                            user = user.strip()
                            # Фильтруем валидные имена пользователей
                            if (user and len(user) > 1 and len(user) < 30 and
                                    user not in ['Администратор', 'Гость', 'Administrator',
                                                 'Guest', 'DefaultAccount', 'WDAGUtilityAccount',
                                                 'Все', 'None', 'команда', 'выполнена', 'успешно',
                                                 'user', 'accounts', 'for']):

                                # Проверяем, не заголовок ли это
                                if not any(x in user.lower() for x in [
                                    'user', 'account', 'name', 'comment',
                                    'администратор', 'гость', 'комментарий'
                                ]):
                                    is_admin = self.check_user_admin_status(user)
                                    users_data.append({
                                        'name': user,
                                        'is_admin': is_admin,
                                        'display': f"{user} {'(Администратор)' if is_admin else '(Пользователь)'}"
                                    })

            # Если не нашли пользователей, пробуем WMIC
            if not users_data:
                result = subprocess.run(
                    'wmic useraccount where "LocalAccount=True" get name,sid /value',
                    shell=True, capture_output=True, text=True,
                    encoding='cp866', errors='ignore'
                )

                if result.returncode == 0:
                    current_user = {}
                    for line in result.stdout.strip().split('\n'):
                        line = line.strip()
                        if not line:
                            if current_user and 'name' in current_user:
                                name = current_user.get('name', '').strip()
                                if (name and len(name) > 1 and len(name) < 30 and
                                        name not in ['DefaultAccount', 'WDAGUtilityAccount',
                                                     'Администратор', 'Гость', 'Administrator', 'Guest']):
                                    is_admin = self.check_user_admin_status(name)
                                    users_data.append({
                                        'name': name,
                                        'is_admin': is_admin,
                                        'display': f"{name} {'(Администратор)' if is_admin else '(Пользователь)'}"
                                    })
                            current_user = {}
                            continue
                        if '=' in line:
                            key, value = line.split('=', 1)
                            current_user[key.strip().lower()] = value.strip()

                    # Последний пользователь
                    if current_user and 'name' in current_user:
                        name = current_user.get('name', '').strip()
                        if (name and len(name) > 1 and len(name) < 30 and
                                name not in ['DefaultAccount', 'WDAGUtilityAccount',
                                             'Администратор', 'Гость', 'Administrator', 'Guest']):
                            is_admin = self.check_user_admin_status(name)
                            users_data.append({
                                'name': name,
                                'is_admin': is_admin,
                                'display': f"{name} {'(Администратор)' if is_admin else '(Пользователь)'}"
                            })

            # Если всё ещё пусто, пробуем PowerShell
            if not users_data:
                try:
                    result = subprocess.run(
                        'powershell -command "Get-LocalUser | Select-Object Name"',
                        shell=True, capture_output=True, text=True,
                        encoding='cp866', errors='ignore'
                    )

                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            line = line.strip()
                            if line and '----' not in line and 'Name' not in line:
                                user = line.strip()
                                if (user and len(user) > 1 and len(user) < 30 and
                                        user not in ['Администратор', 'Гость', 'Administrator',
                                                     'Guest', 'DefaultAccount', 'WDAGUtilityAccount']):
                                    is_admin = self.check_user_admin_status(user)
                                    users_data.append({
                                        'name': user,
                                        'is_admin': is_admin,
                                        'display': f"{user} {'(Администратор)' if is_admin else '(Пользователь)'}"
                                    })
                except:
                    pass

        except Exception as e:
            print(f"Ошибка получения пользователей: {e}")
        print(f"Найдено пользователей: {len(users_data)}")
        for u in users_data:
            print(f"  - {u['name']} ({'Admin' if u['is_admin'] else 'User'})")

        return users_data



    def check_user_admin_status(self, username):
        """Проверка является ли пользователь администратором"""
        try:
            # Проверяем русскую группу
            result = subprocess.run(
                f'net localgroup Администраторы', shell=True,
                capture_output=True, text=True, encoding='cp866', errors='ignore'
            )
            if username in result.stdout:
                return True

            # Проверяем английскую группу
            result = subprocess.run(
                f'net localgroup Administrators', shell=True,
                capture_output=True, text=True, encoding='cp866', errors='ignore'
            )
            if username in result.stdout:
                return True
        except:
            pass

        return False

    def show_all_users(self):
        """Показать список всех пользователей"""
        users = self.get_all_users_list()

        if not users:
            messagebox.showinfo("Информация", "На компьютере не найдено пользователей")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("Все пользователи компьютера")
        dialog.geometry("500x400")
        dialog.transient(self.window)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Список всех пользователей",
                  font=("Arial", 14, "bold")).pack(pady=10)

        # Список с прокруткой
        list_frame = ttk.LabelFrame(main_frame, text="Пользователи", padding=10)
        list_frame.pack(fill="both", expand=True, pady=10)

        listbox = tk.Listbox(list_frame, font=("Arial", 11))
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        for user_data in users:
            listbox.insert(tk.END, user_data['display'])

        # Статистика
        admins_count = sum(1 for u in users if u['is_admin'])
        users_count = len(users) - admins_count

        stats_label = ttk.Label(main_frame,
                                text=f"Всего: {len(users)} | Администраторов: {admins_count} | Пользователей: {users_count}",
                                font=("Arial", 10), foreground="blue")
        stats_label.pack(pady=5)

        ttk.Button(main_frame, text="Закрыть", command=dialog.destroy, width=15).pack(pady=10)

    def show_users_dialog(self, title, action_name):
        """Отображение диалога выбора пользователя"""
        users = self.get_all_users_list()

        if not users:
            messagebox.showinfo("Информация", "На компьютере не найдено пользователей")
            return None

        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("500x500")
        dialog.transient(self.window)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text=f"Выберите пользователя для: {action_name}",
                  font=("Arial", 12, "bold")).pack(pady=10)

        list_frame = ttk.LabelFrame(main_frame, text="Все пользователи компьютера", padding=10)
        list_frame.pack(fill="both", expand=True, pady=10)

        listbox = tk.Listbox(list_frame, font=("Arial", 11), selectmode='single')
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Сохраняем данные пользователей
        listbox.users_data = []
        for user_data in users:
            listbox.insert(tk.END, user_data['display'])
            listbox.users_data.append(user_data)

        # Статистика
        admins_count = sum(1 for u in users if u['is_admin'])
        stats_label = ttk.Label(main_frame,
                                text=f"Всего: {len(users)} | Администраторов: {admins_count}",
                                font=("Arial", 9), foreground="blue")
        stats_label.pack(pady=5)

        selected_user = [None]

        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_user[0] = listbox.users_data[selection[0]]
                dialog.destroy()

        def on_double_click(event):
            on_select()

        listbox.bind('<Double-Button-1>', on_double_click)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Выбрать", command=on_select, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=15).pack(side='left', padx=5)

        dialog.bind('<Return>', lambda e: on_select())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

        dialog.wait_window()

        return selected_user[0]

    def add_account(self):
        """Добавление нового пользователя с логированием пароля"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Добавление учетной записи")
        dialog.geometry("400x400")
        dialog.transient(self.window)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - dialog.winfo_width()) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Логин:", font=("Arial", 11)).pack(anchor='w', pady=(5, 2))
        login_entry = ttk.Entry(main_frame, width=30, font=("Arial", 11))
        login_entry.pack(fill="x", pady=5)
        login_entry.focus()

        ttk.Label(main_frame, text="(буквы, цифры и . - _ @)",
                  font=("Arial", 8), foreground="gray").pack(anchor='w')

        ttk.Label(main_frame, text="Пароль:", font=("Arial", 11)).pack(anchor='w', pady=(15, 2))
        password_entry = ttk.Entry(main_frame, show="*", width=30, font=("Arial", 11))
        password_entry.pack(fill="x", pady=5)

        ttk.Label(main_frame, text="Подтверждение пароля:", font=("Arial", 11)).pack(anchor='w', pady=(10, 2))
        confirm_entry = ttk.Entry(main_frame, show="*", width=30, font=("Arial", 11))
        confirm_entry.pack(fill="x", pady=5)

        # Пустой пароль
        empty_password_var = tk.BooleanVar()
        empty_password_frame = ttk.Frame(main_frame)
        empty_password_frame.pack(fill="x", pady=10)

        def toggle_empty_password():
            if empty_password_var.get():
                password_entry.config(state='disabled')
                confirm_entry.config(state='disabled')
                password_entry.delete(0, tk.END)
                confirm_entry.delete(0, tk.END)
            else:
                password_entry.config(state='normal')
                confirm_entry.config(state='normal')

        ttk.Checkbutton(empty_password_frame, text="Пустой пароль (без пароля)",
                        variable=empty_password_var,
                        command=toggle_empty_password).pack(anchor='w')

        # Права администратора
        is_admin = tk.BooleanVar()
        admin_frame = ttk.Frame(main_frame)
        admin_frame.pack(fill="x", pady=15)
        ttk.Checkbutton(admin_frame, text="Администратор",
                        variable=is_admin).pack(anchor='w')

        # Предупреждение
        warning_label = ttk.Label(main_frame,
                                  text="⚠ Внимание: Пользователи с пустым паролем менее защищены!",
                                  foreground="orange", font=("Arial", 9))
        warning_label.pack(anchor='w', pady=5)
        warning_label.pack_forget()

        def show_warning(*args):
            if empty_password_var.get():
                warning_label.pack(anchor='w', pady=5)
            else:
                warning_label.pack_forget()

        empty_password_var.trace('w', show_warning)

        def create_user():
            login = login_entry.get().strip()
            if not login:
                messagebox.showerror("Ошибка", "Введите логин!", parent=dialog)
                login_entry.focus()
                return

            if empty_password_var.get():
                password = ""
                password_info = "с ПУСТЫМ паролем"
            else:
                password = password_entry.get()
                confirm = confirm_entry.get()
                password_info = f"с паролем: {password}"

                if not password:
                    messagebox.showerror("Ошибка", "Введите пароль или выберите 'Пустой пароль'!", parent=dialog)
                    password_entry.focus()
                    return

                if password != confirm:
                    messagebox.showerror("Ошибка", "Пароли не совпадают!", parent=dialog)
                    confirm_entry.focus()
                    return

            try:
                result = subprocess.run(f'net user "{login}" "{password}" /add',
                                        shell=True, capture_output=True, text=True, encoding='cp866')

                if result.returncode != 0:
                    error_msg = result.stderr.strip()
                    messagebox.showerror("Ошибка", f"Не удалось создать пользователя:\n{error_msg}", parent=dialog)
                    return

                admin_status = "Администратор" if is_admin.get() else "Обычный пользователь"

                if is_admin.get():
                    try:
                        admin_result = subprocess.run(f'net localgroup Администраторы "{login}" /add',
                                                      shell=True, capture_output=True, text=True, encoding='cp866')
                        if admin_result.returncode != 0:
                            subprocess.run(f'net localgroup Administrators "{login}" /add',
                                           shell=True, capture_output=True)
                    except:
                        pass

                # ✅ ИСПРАВЛЕНО: Логирование с указанием реального пароля
                if self.main_app:
                    computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
                    # Логируем пароль явно - для учебного проекта
                    actual_password = password if password else "[ПУСТОЙ]"
                    log_message = f"СОЗДАН ПОЛЬЗОВАТЕЛЬ: {login} | Тип: {admin_status} | ПАРОЛЬ: {actual_password}"
                    self.main_app.log_action(log_message, computer_name)

                password_display = "с ПУСТЫМ паролем" if not password else f"с паролем: {password}"
                messagebox.showinfo("Успех", f"Пользователь {login} создан {password_display}!", parent=dialog)
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать пользователя:\n{str(e)}", parent=dialog)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=20)

        center_btn_frame = ttk.Frame(btn_frame)
        center_btn_frame.pack()

        create_btn = ttk.Button(center_btn_frame, text="Создать пользователя",
                                command=create_user, width=20, padding=8)
        create_btn.pack(side='left', padx=10)

        cancel_btn = ttk.Button(center_btn_frame, text="Отмена",
                                command=dialog.destroy, width=15, padding=8)
        cancel_btn.pack(side='left', padx=10)

        dialog.bind('<Return>', lambda e: create_user())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def modify_account(self):
        """Изменение пароля пользователя"""
        user_data = self.show_users_dialog("Выбор пользователя", "изменения пароля")

        if not user_data:
            return

        username = user_data['name']
        is_admin = user_data['is_admin']
        user_type = "Администратор" if is_admin else "Обычный пользователь"

        dialog = tk.Toplevel(self.window)
        dialog.title(f"Изменение пароля: {username}")
        dialog.geometry("400x350")
        dialog.transient(self.window)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text=f"Пользователь: {username}",
                  font=("Arial", 12, "bold")).pack(pady=10)

        ttk.Label(main_frame, text=f"Тип: {user_type}",
                  font=("Arial", 10), foreground="blue").pack(pady=5)

        ttk.Label(main_frame, text="Новый пароль:", font=("Arial", 11)).pack(anchor='w', pady=(15, 2))
        password_entry = ttk.Entry(main_frame, show="*", width=35, font=("Arial", 11))
        password_entry.pack(fill="x", pady=5)
        password_entry.focus()

        ttk.Label(main_frame, text="Подтверждение:", font=("Arial", 11)).pack(anchor='w', pady=(10, 2))
        confirm_entry = ttk.Entry(main_frame, show="*", width=35, font=("Arial", 11))
        confirm_entry.pack(fill="x", pady=5)

        empty_password_var = tk.BooleanVar()

        def toggle_empty_password():
            if empty_password_var.get():
                password_entry.config(state='disabled')
                confirm_entry.config(state='disabled')
                password_entry.delete(0, tk.END)
                confirm_entry.delete(0, tk.END)
            else:
                password_entry.config(state='normal')
                confirm_entry.config(state='normal')

        ttk.Checkbutton(main_frame, text="Удалить пароль (пустой пароль)",
                        variable=empty_password_var,
                        command=toggle_empty_password).pack(anchor='w', pady=10)

        def change_password():
            if empty_password_var.get():
                password = ""
            else:
                password = password_entry.get()
                confirm = confirm_entry.get()

                if password != confirm:
                    messagebox.showerror("Ошибка", "Пароли не совпадают!", parent=dialog)
                    confirm_entry.focus()
                    return

            try:
                result = subprocess.run(f'net user "{username}" "{password}"',
                                        shell=True, capture_output=True, text=True, encoding='cp866')

                if result.returncode != 0:
                    messagebox.showerror("Ошибка", f"Не удалось изменить пароль:\n{result.stderr}", parent=dialog)
                    return

                # Логирование с указанием пароля (включая пустой)
                if self.main_app:
                    computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
                    actual_password = password if password else "[ПУСТОЙ]"
                    log_message = f"ИЗМЕНЕН ПАРОЛЬ: {username} | Тип: {user_type} | НОВЫЙ ПАРОЛЬ: {actual_password}"
                    self.main_app.log_action(log_message, computer_name)

                password_status = "удален" if not password else "изменен"
                messagebox.showinfo("Успех", f"Пароль для {username} {password_status}!", parent=dialog)
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить пароль:\n{str(e)}", parent=dialog)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Изменить", command=change_password, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=15).pack(side='left', padx=5)

        dialog.bind('<Return>', lambda e: change_password())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def delete_account(self):
        """Удаление пользователя"""
        user_data = self.show_users_dialog("Выбор пользователя", "удаления")

        if not user_data:
            return

        username = user_data['name']
        is_admin = user_data['is_admin']

        # Защита от удаления системных учеток
        protected_users = ['Администратор', 'Гость', 'Administrator', 'Guest', 'DefaultAccount']
        if username in protected_users:
            messagebox.showerror("Ошибка", "Нельзя удалить системную учетную запись!")
            return

        user_type = "Администратор" if is_admin else "Пользователь"
        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить пользователя:\n\n{username} ({user_type})\n\n"
                                   f"⚠ Все файлы пользователя будут потеряны!\n\nПродолжить?",
                                   parent=self.window):
            return

        try:
            result = subprocess.run(f'net user "{username}" /delete',
                                    shell=True, capture_output=True, text=True, encoding='cp866')

            if result.returncode != 0:
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя:\n{result.stderr}")
                return

            if self.main_app:
                computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
                log_message = f"УДАЛЕН ПОЛЬЗОВАТЕЛЬ: {username} | Тип: {user_type}"
                self.main_app.log_action(log_message, computer_name)

            messagebox.showinfo("Успех", f"Пользователь {username} удален!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить пользователя:\n{str(e)}")