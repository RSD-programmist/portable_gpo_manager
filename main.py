# import tkinter as tk
# from tkinter import ttk, messagebox, simpledialog, filedialog
# import subprocess
# import os
# import winreg
# import ctypes
# import sys
# import json
# from pathlib import Path
# import threading
# import time
# import datetime
# import shutil
#
#
# class PortableGroupPolicyApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Portable Group Policy Manager")
#
#         # На весь экран
#         self.root.state('zoomed')
#
#         # Определяем путь к программе (для работы с флешки)
#         self.app_path = Path(sys.argv[0]).parent
#
#         # ✅ ИСПРАВЛЕНО: убраны лишние пробелы в путях
#         self.config_path = self.app_path / "config"
#         self.profiles_path = self.app_path / "profiles"
#         self.logs_path = self.app_path / "logs"
#
#         # Создаем необходимые папки
#         for path in [self.config_path, self.profiles_path, self.logs_path]:
#             path.mkdir(exist_ok=True)
#
#         # Проверка прав администратора
#         self.check_admin_rights()
#
#         # Основной интерфейс
#         self.create_main_interface()
#
#         # Загружаем сохраненные профили
#         self.load_profiles()
#
#     def check_admin_rights(self):
#         """Проверка прав администратора"""
#         try:
#             if ctypes.windll.shell32.IsUserAnAdmin():
#                 self.admin_status = tk.StringVar(value="(OK) Права администратора")
#                 self.admin_color = "green"
#             else:
#                 self.admin_status = tk.StringVar(value="(?) Ограниченные права (некоторые функции недоступны)")
#                 self.admin_color = "orange"
#         except:
#             self.admin_status = tk.StringVar(value="(X) Не удалось проверить права")
#             self.admin_color = "red"
#
#     def create_main_interface(self):
#         """Создание главного интерфейса"""
#         # Заголовок
#         title_frame = ttk.Frame(self.root)
#         title_frame.pack(fill="x", padx=20, pady=20)
#
#         ttk.Label(title_frame, text="Portable Group Policy Manager",
#                   font=("Arial", 24, "bold")).pack()
#         ttk.Label(title_frame, text=f"Путь: {self.app_path}",
#                   font=("Arial", 10)).pack(pady=5)
#
#         # Статус прав
#         status_label = ttk.Label(title_frame, textvariable=self.admin_status,
#                                  foreground=self.admin_color, font=("Arial", 12))
#         status_label.pack(pady=10)
#
#         # Основные кнопки (центрируем с помощью Frame)
#         center_frame = ttk.Frame(self.root)
#         center_frame.pack(expand=True)
#
#         btn_frame = ttk.Frame(center_frame)
#         btn_frame.pack()
#
#         button_style = {'width': 30, 'padding': 10}
#
#         ttk.Button(btn_frame, text="Групповая политика",
#                    command=self.open_group_policy,
#                    **button_style).pack(pady=10)
#
#         ttk.Button(btn_frame, text="Учетные записи",
#                    command=self.open_accounts_window,
#                    **button_style).pack(pady=10)
#
#         ttk.Button(btn_frame, text="Профили настроек",
#                    command=self.open_profiles_window,
#                    **button_style).pack(pady=10)
#
#         ttk.Button(btn_frame, text="Проверка сети",
#                    command=self.open_network_check,
#                    **button_style).pack(pady=10)
#
#         ttk.Button(btn_frame, text="Журнал изменений",
#                    command=self.open_logs_window,
#                    **button_style).pack(pady=10)
#
#         ttk.Button(btn_frame, text="УСТРАНИТЬ ВСЕ ПРАВИЛА ГРУППОВОЙ ПОЛИТИКИ",
#                    command=self.remove_all_policies,
#                    **button_style).pack(pady=10)
#
#         ttk.Button(btn_frame, text="Выход",
#                    command=self.root.quit,
#                    **button_style).pack(pady=20)
#
#     def load_profiles(self):
#         """Загрузка сохраненных профилей"""
#         self.profiles = {}
#         for profile_file in self.profiles_path.glob("*.json"):
#             try:
#                 with open(profile_file, 'r', encoding='utf-8') as f:
#                     self.profiles[profile_file.stem] = json.load(f)
#             except:
#                 pass
#
#     def log_action(self, action, computer_name=None):
#         """Логирование действий - СОХРАНЕНИЕ НА ФЛЕШКЕ В logs\\"""
#         if computer_name is None:
#             computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
#
#         try:
#             # ✅ Создаём папку logs на флешке если не существует
#             self.logs_path.mkdir(parents=True, exist_ok=True)
#
#             log_file = self.logs_path / f"log_{datetime.date.today()}.txt"
#
#             with open(log_file, 'a', encoding='utf-8') as f:
#                 timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 f.write(f"[{timestamp}] {computer_name}: {action}\n")
#         except PermissionError:
#             # Если нет прав на запись в папку на флешке, пробуем создать с правами
#             try:
#                 # Пробуем создать папку с помощью subprocess от админа
#                 subprocess.run(f'mkdir "{self.logs_path}" 2>nul', shell=True)
#                 log_file = self.logs_path / f"log_{datetime.date.today()}.txt"
#
#                 with open(log_file, 'a', encoding='utf-8') as f:
#                     timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                     f.write(f"[{timestamp}] {computer_name}: {action}\n")
#             except:
#                 # Если совсем не получается, пишем в консоль
#                 print(f"LOG: [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {computer_name}: {action}")
#         except Exception as e:
#             print(f"Ошибка логирования: {e}")
#
#     def get_all_users(self):
#         """Получение списка всех пользователей"""
#         try:
#             result = subprocess.run("net user", shell=True, capture_output=True, text=True)
#             users = []
#             for line in result.stdout.split('\n'):
#                 if line.strip() and not line.startswith('---') and 'команда' not in line.lower():
#                     users.extend(line.strip().split())
#             return users
#         except:
#             return []
#
#     def remove_all_policies(self):
#         """УСТРАНЕНИЕ ВСЕХ ПРАВИЛ ГРУППОВОЙ ПОЛИТИКИ ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ"""
#
#         # Двойное подтверждение для безопасности
#         if not messagebox.askyesno("ПОДТВЕРЖДЕНИЕ",
#                                    "ВНИМАНИЕ! Это действие УДАЛИТ ВСЕ примененные правила групповой политики\n"
#                                    "ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ (включая администраторов) и вернет настройки Windows к состоянию по умолчанию.\n\n"
#                                    "Вы уверены, что хотите продолжить?"):
#             return
#
#         if not messagebox.askyesno("ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ",
#                                    "Это действие НЕЛЬЗЯ отменить!\n\n"
#                                    "Все ограничения будут сняты со всех пользователей.\n\n"
#                                    "Точно продолжить?"):
#             return
#
#         try:
#             computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
#
#             # Показываем индикатор выполнения
#             progress_dialog = tk.Toplevel(self.root)
#             progress_dialog.title("Устранение правил")
#             progress_dialog.geometry("400x150")
#             progress_dialog.transient(self.root)
#             progress_dialog.grab_set()
#
#             ttk.Label(progress_dialog, text="Устранение правил групповой политики...",
#                       font=("Arial", 12)).pack(pady=20)
#
#             progress_bar = ttk.Progressbar(progress_dialog, mode='indeterminate')
#             progress_bar.pack(padx=20, pady=10, fill="x")
#             progress_bar.start(10)
#
#             progress_dialog.update()
#
#             def remove_policies_thread():
#                 try:
#                     all_users = self.get_all_users()
#
#                     user_policy_keys = [
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop",
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\User",
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
#                         r"Software\Policies\Microsoft\Windows\System",
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun",
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\NonEnum",
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\Network",
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\Printers",
#                         r"Software\Microsoft\Windows\CurrentVersion\Policies\WindowsUpdate",
#                         r"Software\Policies\Microsoft\Windows\PowerShell",
#                         r"Software\Policies\Microsoft\Windows\WindowsUpdate",
#                         r"Software\Policies\Microsoft\Windows\Control Panel",
#                         r"Software\Policies\Microsoft\Windows\System"
#                     ]
#
#                     machine_policy_keys = [
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\WindowsStore"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\PowerShell"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Control Panel"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\System"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer"),
#                         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers")
#                     ]
#
#                     users_processed = 0
#                     for username in all_users:
#                         try:
#                             profile_path = f"C:\\Users\\{username}\\NTUSER.DAT"
#                             if os.path.exists(profile_path):
#                                 for key_path in user_policy_keys:
#                                     full_path = f"HKU\\{username}\\{key_path}"
#                                     subprocess.run(f'reg delete "{full_path}" /f',
#                                                    shell=True, capture_output=True, timeout=5)
#                                 users_processed += 1
#                         except Exception as e:
#                             print(f"Ошибка при обработке пользователя {username}: {e}")
#
#                         self.root.after(0, lambda: progress_dialog.update())
#
#                     for hive, key_path in machine_policy_keys:
#                         try:
#                             subprocess.run(f'reg delete "{key_path}" /f', shell=True, capture_output=True, timeout=5)
#                         except:
#                             pass
#
#                     temp_policies = [
#                         r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies",
#                         r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies",
#                         r"HKLM\SOFTWARE\Policies",
#                         r"HKCU\SOFTWARE\Policies"
#                     ]
#
#                     for policy in temp_policies:
#                         subprocess.run(f'reg delete "{policy}" /f', shell=True, capture_output=True, timeout=5)
#
#                     subprocess.run("gpupdate /force", shell=True, capture_output=True, timeout=30)
#
#                     try:
#                         subprocess.run("taskkill /f /im explorer.exe", shell=True, timeout=5)
#                         subprocess.run("start explorer.exe", shell=True, timeout=5)
#                     except:
#                         pass
#
#                     self.root.after(0, progress_dialog.destroy)
#
#                     self.log_action(
#                         f"ПОЛНОЕ УСТРАНЕНИЕ ВСЕХ ПРАВИЛ ГРУППОВОЙ ПОЛИТИКИ для {users_processed} пользователей",
#                         computer_name)
#
#                     self.root.after(0, lambda: messagebox.showinfo("УСПЕХ",
#                                                                    f"Все правила групповой политики успешно устранены!\n\n"
#                                                                    f"Обработано пользователей: {users_processed}\n"
#                                                                    f"Удалены все ограничения для всех пользователей.\n\n"
#                                                                    f"Для полного применения изменений рекомендуется перезагрузка компьютера."))
#
#                 except Exception as e:
#                     self.root.after(0, progress_dialog.destroy)
#                     self.root.after(0,
#                                     lambda: messagebox.showerror("ОШИБКА", f"Не удалось устранить правила: {str(e)}"))
#
#             thread = threading.Thread(target=remove_policies_thread)
#             thread.daemon = True
#             thread.start()
#
#         except Exception as e:
#             messagebox.showerror("ОШИБКА", f"Не удалось устранить правила: {str(e)}")
#
#     def open_group_policy(self):
#         GroupPolicyWindow(self.root, self)
#
#     def open_accounts_window(self):
#         AccountsWindow(self.root, self)
#
#     def open_profiles_window(self):
#         ProfilesWindow(self.root, self)
#
#     def open_network_check(self):
#         NetworkCheckWindow(self.root, self)
#
#     def open_logs_window(self):
#         LogsWindow(self.root, self)
#
#
# class GroupPolicyWindow:
#     def __init__(self, parent, main_app):
#         self.main_app = main_app
#         self.window = tk.Toplevel(parent)
#         self.window.title("Настройка групповой политики")
#         self.window.state('zoomed')
#         self.create_scrollable_frame()
#
#         computer_name = os.environ.get('COMPUTERNAME', 'Неизвестно')
#         ttk.Label(self.main_frame, text=f"Компьютер: {computer_name}",
#                   font=("Arial", 14, "italic")).pack(pady=10)
#
#         info_frame = ttk.LabelFrame(self.main_frame, text="Информация", padding=10)
#         info_frame.pack(padx=20, pady=5, fill="x")
#
#         info_text = "Настройки будут применяться ТОЛЬКО к обычным пользователям (не администраторам).\nАдминистраторы сохранят полный доступ ко всем функциям."
#         ttk.Label(info_frame, text=info_text, foreground="blue", font=("Arial", 10)).pack()
#
#         self.create_policy_controls()
#         self.create_buttons()
#
#     def create_scrollable_frame(self):
#         self.canvas = tk.Canvas(self.window)
#         self.canvas.pack(side="left", fill="both", expand=True)
#
#         scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
#         scrollbar.pack(side="right", fill="y")
#
#         self.canvas.configure(yscrollcommand=scrollbar.set)
#
#         self.main_frame = ttk.Frame(self.canvas)
#         self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
#
#         self.main_frame.bind("<Configure>", self.on_frame_configure)
#         self.canvas.bind("<Configure>", self.on_canvas_configure)
#         self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
#
#     def on_frame_configure(self, event):
#         self.canvas.configure(scrollregion=self.canvas.bbox("all"))
#
#     def on_canvas_configure(self, event):
#         self.canvas.itemconfig(self.canvas_window, width=event.width)
#
#     def on_mousewheel(self, event):
#         self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
#
#     def create_policy_controls(self):
#         notebook = ttk.Notebook(self.main_frame)
#         notebook.pack(padx=20, pady=10, fill="both", expand=True)
#
#         main_frame = ttk.Frame(notebook)
#         notebook.add(main_frame, text="Основные ограничения")
#
#         advanced_frame = ttk.Frame(notebook)
#         notebook.add(advanced_frame, text="Дополнительно")
#
#         self.vars = {
#             'wallpaper': tk.BooleanVar(),
#             'hide_drives': tk.BooleanVar(),
#             'disable_store': tk.BooleanVar(),
#             'block_drives': tk.BooleanVar(),
#             'no_password_change': tk.BooleanVar(),
#             'disable_taskmgr': tk.BooleanVar(),
#             'no_control_panel': tk.BooleanVar(),
#             'block_usb_read': tk.BooleanVar(),
#             'block_usb_write': tk.BooleanVar(),
#             'block_cmd': tk.BooleanVar(),
#             'block_powershell': tk.BooleanVar(),
#             'block_regedit': tk.BooleanVar(),
#             'disable_shutdown': tk.BooleanVar(),
#             'no_run': tk.BooleanVar(),
#             'hide_clock': tk.BooleanVar()
#         }
#
#         main_canvas = tk.Canvas(main_frame)
#         main_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=main_canvas.yview)
#         main_scrollable_frame = ttk.Frame(main_canvas)
#
#         main_canvas.configure(yscrollcommand=main_scrollbar.set)
#         main_canvas.create_window((0, 0), window=main_scrollable_frame, anchor="nw")
#
#         main_canvas.pack(side="left", fill="both", expand=True)
#         main_scrollbar.pack(side="right", fill="y")
#
#         main_scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
#
#         main_checks = [
#             ("Запрет на замену обоев", 'wallpaper'),
#             ("Скрыть диски в Моем компьютере", 'hide_drives'),
#             ("Отключить Магазин Windows", 'disable_store'),
#             ("Запретить доступ к дискам", 'block_drives'),
#             ("Запретить смену пароля", 'no_password_change'),
#             ("Отключить Диспетчер задач", 'disable_taskmgr'),
#             ("Запретить Панель управления", 'no_control_panel'),
#             ("Запретить чтение USB", 'block_usb_read'),
#             ("Запретить запись на USB", 'block_usb_write'),
#             ("Запретить cmd.exe", 'block_cmd'),
#             ("Запретить PowerShell", 'block_powershell')
#         ]
#
#         for text, var_name in main_checks:
#             cb = ttk.Checkbutton(main_scrollable_frame, text=text,
#                                  variable=self.vars[var_name])
#             cb.pack(anchor='w', pady=5, padx=20)
#
#         advanced_canvas = tk.Canvas(advanced_frame)
#         advanced_scrollbar = ttk.Scrollbar(advanced_frame, orient="vertical", command=advanced_canvas.yview)
#         advanced_scrollable_frame = ttk.Frame(advanced_canvas)
#
#         advanced_canvas.configure(yscrollcommand=advanced_scrollbar.set)
#         advanced_canvas.create_window((0, 0), window=advanced_scrollable_frame, anchor="nw")
#
#         advanced_canvas.pack(side="left", fill="both", expand=True)
#         advanced_scrollbar.pack(side="right", fill="y")
#
#         advanced_scrollable_frame.bind("<Configure>",
#                                        lambda e: advanced_canvas.configure(scrollregion=advanced_canvas.bbox("all")))
#
#         advanced_checks = [
#             ("Запретить Редактор реестра", 'block_regedit'),
#             ("Отключить завершение работы", 'disable_shutdown'),
#             ("Убрать пункт 'Выполнить'", 'no_run'),
#             ("Скрыть часы в трее", 'hide_clock')
#         ]
#
#         for text, var_name in advanced_checks:
#             cb = ttk.Checkbutton(advanced_scrollable_frame, text=text,
#                                  variable=self.vars[var_name])
#             cb.pack(anchor='w', pady=5, padx=20)
#
#         ttk.Separator(advanced_scrollable_frame, orient='horizontal').pack(fill='x', pady=15, padx=20)
#         ttk.Label(advanced_scrollable_frame, text="Блокировка приложений:",
#                   font=("Arial", 12, "bold")).pack(anchor='w', padx=20, pady=5)
#
#         self.block_apps_var = tk.BooleanVar()
#         cb = ttk.Checkbutton(advanced_scrollable_frame, text="Запретить запуск приложений",
#                              variable=self.block_apps_var,
#                              command=self.manage_blocked_apps)
#         cb.pack(anchor='w', pady=5, padx=20)
#
#         self.blocked_apps = []
#         self.apps_list_label = ttk.Label(advanced_scrollable_frame, text="", foreground="blue", font=("Arial", 10))
#         self.apps_list_label.pack(anchor='w', padx=40, pady=5)
#
#     def manage_blocked_apps(self):
#         if self.block_apps_var.get():
#             apps = simpledialog.askstring("Запрещенные приложения",
#                                           "Введите названия приложений через запятую\n(например: notepad.exe, calc.exe, chrome.exe)",
#                                           parent=self.window)
#             if apps:
#                 self.blocked_apps = [app.strip() for app in apps.split(',')]
#                 self.apps_list_label.config(text=f"Заблокировано: {', '.join(self.blocked_apps)}")
#             else:
#                 self.block_apps_var.set(False)
#                 self.apps_list_label.config(text="")
#
#     def create_buttons(self):
#         btn_frame = ttk.Frame(self.main_frame)
#         btn_frame.pack(pady=20)
#
#         button_style = {'width': 20, 'padding': 8}
#
#         ttk.Button(btn_frame, text="Сохранить профиль",
#                    command=self.save_profile, **button_style).pack(side='left', padx=5)
#
#         ttk.Button(btn_frame, text="Загрузить профиль",
#                    command=self.load_profile, **button_style).pack(side='left', padx=5)
#
#         ttk.Button(btn_frame, text="Применить",
#                    command=self.apply_policies, **button_style).pack(side='left', padx=5)
#
#         ttk.Button(btn_frame, text="Сбросить (только обычные)",
#                    command=self.reset_policies, **button_style).pack(side='left', padx=5)
#
#         ttk.Button(btn_frame, text="Закрыть",
#                    command=self.window.destroy, **button_style).pack(side='left', padx=5)
#
#     def save_profile(self):
#         name = simpledialog.askstring("Сохранение профиля",
#                                       "Введите название профиля:",
#                                       parent=self.window)
#         if name:
#             profile_data = {
#                 'settings': {key: var.get() for key, var in self.vars.items()},
#                 'blocked_apps': self.blocked_apps,
#                 'block_apps': self.block_apps_var.get()
#             }
#
#             profile_file = self.main_app.profiles_path / f"{name}.json"
#             with open(profile_file, 'w', encoding='utf-8') as f:
#                 json.dump(profile_data, f, ensure_ascii=False, indent=2)
#
#             self.main_app.load_profiles()
#             messagebox.showinfo("Успех", f"Профиль '{name}' сохранен!")
#
#     def load_profile(self):
#         if not self.main_app.profiles:
#             messagebox.showinfo("Информация", "Нет сохраненных профилей")
#             return
#
#         dialog = tk.Toplevel(self.window)
#         dialog.title("Выбор профиля")
#         dialog.geometry("400x500")
#
#         ttk.Label(dialog, text="Выберите профиль:",
#                   font=("Arial", 14)).pack(pady=15)
#
#         listbox = tk.Listbox(dialog, font=("Arial", 12))
#         listbox.pack(padx=20, pady=10, fill="both", expand=True)
#
#         for profile_name in self.main_app.profiles.keys():
#             listbox.insert(tk.END, profile_name)
#
#         def load_selected():
#             selection = listbox.curselection()
#             if selection:
#                 profile_name = listbox.get(selection[0])
#                 profile = self.main_app.profiles[profile_name]
#
#                 for key, value in profile['settings'].items():
#                     if key in self.vars:
#                         self.vars[key].set(value)
#
#                 self.blocked_apps = profile.get('blocked_apps', [])
#                 self.block_apps_var.set(profile.get('block_apps', False))
#
#                 if self.blocked_apps:
#                     self.apps_list_label.config(text=f"Заблокировано: {', '.join(self.blocked_apps)}")
#
#                 dialog.destroy()
#                 messagebox.showinfo("Успех", f"Профиль '{profile_name}' загружен!")
#
#         btn_frame = ttk.Frame(dialog)
#         btn_frame.pack(pady=15)
#
#         ttk.Button(btn_frame, text="Загрузить", command=load_selected, width=15, padding=5).pack(side='left', padx=5)
#         ttk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=15, padding=5).pack(side='left', padx=5)
#
#     def get_standard_users(self):
#         try:
#             standard_users = []
#
#             result = subprocess.run("net user", shell=True, capture_output=True, text=True)
#             all_users = []
#             for line in result.stdout.split('\n'):
#                 if line.strip() and not line.startswith('---') and 'команда' not in line.lower():
#                     all_users.extend(line.strip().split())
#
#             admins = []
#             try:
#                 result = subprocess.run("net localgroup Администраторы", shell=True, capture_output=True, text=True)
#                 for line in result.stdout.split('\n'):
#                     if line.strip() and not line.startswith('---') and 'команда' not in line.lower():
#                         if not any(x in line.lower() for x in ['администратор', 'комментарий', 'члены']):
#                             admins.extend(line.strip().split())
#             except:
#                 pass
#
#             try:
#                 result = subprocess.run("net localgroup Administrators", shell=True, capture_output=True, text=True)
#                 for line in result.stdout.split('\n'):
#                     if line.strip() and not line.startswith('---') and 'команда' not in line.lower():
#                         if not any(x in line.lower() for x in ['administrators', 'comment', 'members']):
#                             admins.extend(line.strip().split())
#             except:
#                 pass
#
#             system_accounts = ['Администратор', 'Гость', 'Administrator', 'Guest', 'DefaultAccount',
#                                'WDAGUtilityAccount']
#
#             for user in all_users:
#                 if user not in admins and user not in system_accounts:
#                     standard_users.append(user)
#
#             return standard_users
#
#         except Exception as e:
#             print(f"Ошибка при получении списка пользователей: {e}")
#             return []
#
#     def copy_wallpaper_to_system(self):
#         """Копирование обоев из папки приложения в системную папку"""
#         try:
#             # Путь к обоям в папке приложения (на флешке)
#             source_wallpaper = self.main_app.app_path / "Wallpaper" / "MainWallPaper_0.jpg"
#
#             # Целевая папка Windows
#             target_folder = Path(r"C:\Windows\Web\Wallpaper")
#             target_wallpaper = target_folder / "MainWallPaper_0.jpg"
#
#             # Создаем папку если не существует
#             target_folder.mkdir(parents=True, exist_ok=True)
#
#             # Проверяем существование исходного файла
#             if not source_wallpaper.exists():
#                 messagebox.showwarning(
#                     "Предупреждение",
#                     f"Файл обоев не найден:\n{source_wallpaper}\n\n"
#                     f"Создайте папку 'Wallpaper' в папке приложения и поместите туда 'MainWallPaper_0.jpg'"
#                 )
#                 return None
#
#             # Копируем файл
#             shutil.copy2(source_wallpaper, target_wallpaper)
#
#             return str(target_wallpaper)
#
#         except Exception as e:
#             messagebox.showerror("Ошибка", f"Не удалось скопировать обои: {str(e)}")
#             return None
#
#     def apply_policies(self):
#         progress_dialog = tk.Toplevel(self.window)
#         progress_dialog.title("Применение политик")
#         progress_dialog.geometry("400x150")
#         progress_dialog.transient(self.window)
#         progress_dialog.grab_set()
#
#         ttk.Label(progress_dialog, text="Применение групповых политик...",
#                   font=("Arial", 12)).pack(pady=20)
#
#         progress_bar = ttk.Progressbar(progress_dialog, mode='indeterminate')
#         progress_bar.pack(padx=20, pady=10, fill="x")
#         progress_bar.start(10)
#
#         progress_dialog.update()
#
#         def apply_policies_thread():
#             try:
#                 computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
#
#                 standard_users = self.get_standard_users()
#
#                 policies_applied = []
#                 machine_policies = []
#
#                 if standard_users:
#                     reg_content = "Windows Registry Editor Version 5.00\n\n"
#
#                     # ✅ ИЗМЕНЁННАЯ СЕКЦИЯ ОБОЕВ - КОПИРОВАНИЕ ИЗ ПАПКИ ПРИЛОЖЕНИЯ
#                     if self.vars['wallpaper'].get():
#                         wallpaper_path = self.copy_wallpaper_to_system()
#
#                         if wallpaper_path and os.path.exists(wallpaper_path):
#                             for username in standard_users:
#                                 reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System]\n"
#                                 reg_content += f'"Wallpaper"= "{wallpaper_path}"\n'
#                                 reg_content += '"WallpaperStyle"= "2"\n\n'
#
#                                 reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\ActiveDesktop]\n"
#                                 reg_content += '"NoChangingWallPaper"=dword:00000001\n\n'
#
#                             policies_applied.append("Запрет смены обоев")
#
#                     if self.vars['hide_drives'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer]\n"
#                             reg_content += '"NoDrives"=dword:3fffffff\n\n'
#                         policies_applied.append("Скрытие дисков")
#
#                     if self.vars['block_drives'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer]\n"
#                             reg_content += '"NoViewOnDrive"=dword:3fffffff\n\n'
#                         policies_applied.append("Запрет доступа к дискам")
#
#                     if self.vars['no_password_change'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\User]\n"
#                             reg_content += '"DisableChangePassword"=dword:00000001\n\n'
#                         policies_applied.append("Запрет смены пароля")
#
#                     if self.vars['disable_taskmgr'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System]\n"
#                             reg_content += '"DisableTaskMgr"=dword:00000001\n\n'
#                         policies_applied.append("Отключение Диспетчера задач")
#
#                     if self.vars['no_control_panel'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer]\n"
#                             reg_content += '"NoControlPanel"=dword:00000001\n\n'
#                         policies_applied.append("Запрет Панели управления")
#
#                     if self.vars['block_cmd'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Policies\\Microsoft\\Windows\\System]\n"
#                             reg_content += '"DisableCMD"=dword:00000002\n\n'
#                         policies_applied.append("Запрет cmd.exe")
#
#                     if self.vars['block_regedit'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System]\n"
#                             reg_content += '"DisableRegistryTools"=dword:00000001\n\n'
#                         policies_applied.append("Запрет Редактора реестра")
#
#                     if self.vars['disable_shutdown'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer]\n"
#                             reg_content += '"NoClose"=dword:00000001\n\n'
#                         policies_applied.append("Отключение завершения работы")
#
#                     if self.vars['no_run'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer]\n"
#                             reg_content += '"NoRun"=dword:00000001\n\n'
#                         policies_applied.append("Убрать пункт Выполнить")
#
#                     if self.vars['hide_clock'].get():
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer]\n"
#                             reg_content += '"HideClock"=dword:00000001\n\n'
#                         policies_applied.append("Скрытие часов")
#
#                     if self.block_apps_var.get() and self.blocked_apps:
#                         for username in standard_users:
#                             reg_content += f"[HKEY_USERS\\{username}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\DisallowRun]\n"
#                             reg_content += '"DisallowRun"=dword:00000001\n'
#                             for i, app in enumerate(self.blocked_apps, 1):
#                                 reg_content += f'"{i}"= "{app}"\n'
#                             reg_content += "\n"
#                         policies_applied.append(f"Блокировка приложений: {', '.join(self.blocked_apps)}")
#
#                     if reg_content:
#                         temp_reg = self.main_app.app_path / "temp_policies.reg"
#                         with open(temp_reg, 'w', encoding='utf-16') as f:
#                             f.write(reg_content)
#
#                         subprocess.run(f'reg import "{temp_reg}"', shell=True, capture_output=True)
#
#                         try:
#                             os.remove(temp_reg)
#                         except:
#                             pass
#
#                 if self.vars['disable_store'].get():
#                     try:
#                         key_path = r"SOFTWARE\Policies\Microsoft\WindowsStore"
#                         subprocess.run(f'reg add "HKLM\\{key_path}" /v "RemoveWindowsStore" /t REG_DWORD /d 1 /f',
#                                        shell=True, capture_output=True)
#                         machine_policies.append("Отключение Магазина")
#                     except:
#                         pass
#
#                 if self.vars['block_usb_read'].get() or self.vars['block_usb_write'].get():
#                     try:
#                         key_path = r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"
#                         subprocess.run(f'reg add "HKLM\\{key_path}" /v "WriteProtect" /t REG_DWORD /d 1 /f',
#                                        shell=True, capture_output=True)
#
#                         if self.vars['block_usb_read'].get():
#                             key_path = r"SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices"
#                             subprocess.run(f'reg add "HKLM\\{key_path}" /v "Deny_Read" /t REG_DWORD /d 1 /f',
#                                            shell=True, capture_output=True)
#                             machine_policies.append("Запрет чтения USB")
#
#                         if self.vars['block_usb_write'].get():
#                             key_path = r"SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices"
#                             subprocess.run(f'reg add "HKLM\\{key_path}" /v "Deny_Write" /t REG_DWORD /d 1 /f',
#                                            shell=True, capture_output=True)
#                             machine_policies.append("Запрет записи на USB")
#                     except:
#                         pass
#
#                 if self.vars['block_powershell'].get():
#                     try:
#                         key_path = r"SOFTWARE\Policies\Microsoft\Windows\PowerShell"
#                         subprocess.run(f'reg add "HKLM\\{key_path}" /v "EnableScripts" /t REG_DWORD /d 0 /f',
#                                        shell=True, capture_output=True)
#                         machine_policies.append("Запрет PowerShell")
#                     except:
#                         pass
#
#                 subprocess.run("gpupdate /force", shell=True, capture_output=True, timeout=30)
#
#                 self.window.after(0, progress_dialog.destroy)
#
#                 result_message = ""
#                 if policies_applied:
#                     result_message += "Применены настройки для обычных пользователей:\n"
#                     result_message += "\n".join(policies_applied)
#                     result_message += f"\n(для {len(standard_users)} пользователей)\n\n"
#
#                 if machine_policies:
#                     result_message += "Применены общесистемные настройки:\n"
#                     result_message += "\n".join(machine_policies)
#
#                 if policies_applied or machine_policies:
#                     self.main_app.log_action(f"Применены настройки: {policies_applied + machine_policies}",
#                                              computer_name)
#                     self.window.after(0, lambda: messagebox.showinfo("Успех",
#                                                                      f"{result_message}\n\nДля полного применения может потребоваться перезагрузка."))
#                 else:
#                     self.window.after(0, lambda: messagebox.showinfo("Информация", "Не выбрано ни одной настройки"))
#
#             except Exception as e:
#                 self.window.after(0, progress_dialog.destroy)
#                 self.window.after(0,
#                                   lambda: messagebox.showerror("Ошибка", f"Не удалось применить настройки: {str(e)}"))
#
#         thread = threading.Thread(target=apply_policies_thread)
#         thread.daemon = True
#         thread.start()
#
#     def reset_policies(self):
#         if messagebox.askyesno("Подтверждение",
#                                "Сбросить все настройки групповой политики для обычных пользователей?\n"
#                                "Это действие удалит все примененные ограничения."):
#             try:
#                 computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
#
#                 standard_users = self.get_standard_users()
#
#                 if not standard_users:
#                     messagebox.showinfo("Информация", "На компьютере нет обычных пользователей.")
#                     return
#
#                 progress_dialog = tk.Toplevel(self.window)
#                 progress_dialog.title("Сброс политик")
#                 progress_dialog.geometry("400x150")
#                 progress_dialog.transient(self.window)
#                 progress_dialog.grab_set()
#
#                 ttk.Label(progress_dialog, text="Сброс групповых политик...",
#                           font=("Arial", 12)).pack(pady=20)
#
#                 progress_bar = ttk.Progressbar(progress_dialog, mode='indeterminate')
#                 progress_bar.pack(padx=20, pady=10, fill="x")
#                 progress_bar.start(10)
#
#                 progress_dialog.update()
#
#                 def reset_thread():
#                     try:
#                         policy_keys = [
#                             r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop",
#                             r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
#                             r"Software\Microsoft\Windows\CurrentVersion\Policies\User",
#                             r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
#                             r"Software\Policies\Microsoft\Windows\System",
#                             r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun"
#                         ]
#
#                         for username in standard_users:
#                             try:
#                                 for key_path in policy_keys:
#                                     full_path = f"HKU\\{username}\\{key_path}"
#                                     subprocess.run(f'reg delete "{full_path}" /f',
#                                                    shell=True, capture_output=True, timeout=5)
#                             except:
#                                 pass
#
#                             self.window.after(0, lambda: progress_dialog.update())
#
#                         machine_keys = [
#                             (r"HKLM\SOFTWARE\Policies\Microsoft\WindowsStore", "RemoveWindowsStore"),
#                             (r"HKLM\SYSTEM\CurrentControlSet\Control\StorageDevicePolicies", "WriteProtect"),
#                             (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices", "Deny_Read"),
#                             (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices", "Deny_Write"),
#                             (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell", "EnableScripts")
#                         ]
#
#                         for key_path, value_name in machine_keys:
#                             try:
#                                 subprocess.run(f'reg delete "{key_path}" /v "{value_name}" /f',
#                                                shell=True, capture_output=True, timeout=5)
#                             except:
#                                 pass
#
#                         subprocess.run("gpupdate /force", shell=True, capture_output=True, timeout=30)
#
#                         self.window.after(0, progress_dialog.destroy)
#
#                         self.main_app.log_action("Сброс настроек групповой политики для обычных пользователей",
#                                                  computer_name)
#                         self.window.after(0, lambda: messagebox.showinfo("Успех",
#                                                                          "Настройки групповой политики для обычных пользователей сброшены!\nДля полного применения может потребоваться перезагрузка."))
#
#                     except Exception as e:
#                         self.window.after(0, progress_dialog.destroy)
#                         self.window.after(0, lambda: messagebox.showerror("Ошибка",
#                                                                           f"Не удалось сбросить настройки: {str(e)}"))
#
#                 thread = threading.Thread(target=reset_thread)
#                 thread.daemon = True
#                 thread.start()
#
#             except Exception as e:
#                 messagebox.showerror("Ошибка", f"Не удалось сбросить настройки: {str(e)}")
#
#
# class AccountsWindow:
#     def __init__(self, parent, main_app=None):
#         self.main_app = main_app
#         self.window = tk.Toplevel(parent)
#         self.window.title("Управление учетными записями")
#         self.window.geometry("400x300")
#         ttk.Label(self.window, text="Управление учетными записями",
#                   font=("Arial", 14)).pack(pady=20)
#
#         btn_frame = ttk.Frame(self.window)
#         btn_frame.pack(pady=10)
#
#         ttk.Button(btn_frame, text="Добавить",
#                    command=self.add_account, width=15).pack(pady=5)
#         ttk.Button(btn_frame, text="Изменить",
#                    command=self.modify_account, width=15).pack(pady=5)
#         ttk.Button(btn_frame, text="Удалить",
#                    command=self.delete_account, width=15).pack(pady=5)
#         ttk.Button(btn_frame, text="Закрыть",
#                    command=self.window.destroy, width=15).pack(pady=5)
#
#     def add_account(self):
#         """Добавление нового пользователя"""
#         dialog = tk.Toplevel(self.window)
#         dialog.title("Добавление учетной записи")
#         dialog.geometry("400x400")
#         dialog.transient(self.window)
#         dialog.grab_set()
#
#         dialog.update_idletasks()
#         x = self.window.winfo_x() + (self.window.winfo_width() - dialog.winfo_width()) // 2
#         y = self.window.winfo_y() + (self.window.winfo_height() - dialog.winfo_height()) // 2
#         dialog.geometry(f"+{x}+{y}")
#
#         main_frame = ttk.Frame(dialog, padding=20)
#         main_frame.pack(fill="both", expand=True)
#
#         ttk.Label(main_frame, text="Логин:", font=("Arial", 11)).pack(anchor='w', pady=(5, 2))
#         login_entry = ttk.Entry(main_frame, width=30, font=("Arial", 11))
#         login_entry.pack(fill="x", pady=5)
#         login_entry.focus()
#
#         ttk.Label(main_frame, text="(буквы, цифры и . - _ @)",
#                   font=("Arial", 8), foreground="gray").pack(anchor='w')
#
#         ttk.Label(main_frame, text="Пароль:", font=("Arial", 11)).pack(anchor='w', pady=(15, 2))
#         password_entry = ttk.Entry(main_frame, show="*", width=30, font=("Arial", 11))
#         password_entry.pack(fill="x", pady=5)
#
#         ttk.Label(main_frame, text="Подтверждение пароля:", font=("Arial", 11)).pack(anchor='w', pady=(10, 2))
#         confirm_entry = ttk.Entry(main_frame, show="*", width=30, font=("Arial", 11))
#         confirm_entry.pack(fill="x", pady=5)
#
#         empty_password_var = tk.BooleanVar()
#         empty_password_frame = ttk.Frame(main_frame)
#         empty_password_frame.pack(fill="x", pady=10)
#
#         def toggle_empty_password():
#             if empty_password_var.get():
#                 password_entry.config(state='disabled')
#                 confirm_entry.config(state='disabled')
#                 password_entry.delete(0, tk.END)
#                 confirm_entry.delete(0, tk.END)
#             else:
#                 password_entry.config(state='normal')
#                 confirm_entry.config(state='normal')
#
#         ttk.Checkbutton(empty_password_frame, text="Пустой пароль (без пароля)",
#                         variable=empty_password_var,
#                         command=toggle_empty_password).pack(anchor='w')
#
#         is_admin = tk.BooleanVar()
#         admin_frame = ttk.Frame(main_frame)
#         admin_frame.pack(fill="x", pady=15)
#
#         ttk.Checkbutton(admin_frame, text="Администратор",
#                         variable=is_admin).pack(anchor='w')
#
#         warning_label = ttk.Label(main_frame,
#                                   text="⚠ Внимание: Пользователи с пустым паролем менее защищены!",
#                                   foreground="orange",
#                                   font=("Arial", 9))
#         warning_label.pack(anchor='w', pady=5)
#         warning_label.pack_forget()
#
#         def show_warning(*args):
#             if empty_password_var.get():
#                 warning_label.pack(anchor='w', pady=5)
#             else:
#                 warning_label.pack_forget()
#
#         empty_password_var.trace('w', show_warning)
#
#         btn_frame = ttk.Frame(main_frame)
#         btn_frame.pack(fill="x", pady=20)
#
#         center_btn_frame = ttk.Frame(btn_frame)
#         center_btn_frame.pack()
#
#         def create_user():
#             login = login_entry.get().strip()
#
#             if not login:
#                 messagebox.showerror("Ошибка", "Введите логин!", parent=dialog)
#                 login_entry.focus()
#                 return
#
#             if empty_password_var.get():
#                 password = ""
#                 confirm = ""
#                 password_info = "с ПУСТЫМ паролем"
#             else:
#                 password = password_entry.get()
#                 confirm = confirm_entry.get()
#                 password_info = f"с паролем: {password}"
#
#                 if not password:
#                     messagebox.showerror("Ошибка", "Введите пароль или выберите 'Пустой пароль'!", parent=dialog)
#                     password_entry.focus()
#                     return
#
#                 if password != confirm:
#                     messagebox.showerror("Ошибка", "Пароли не совпадают!", parent=dialog)
#                     confirm_entry.focus()
#                     return
#
#             try:
#                 result = subprocess.run(f'net user "{login}" "{password}" /add',
#                                         shell=True, capture_output=True, text=True, encoding='cp866')
#
#                 if result.returncode != 0:
#                     error_msg = result.stderr.strip()
#                     messagebox.showerror("Ошибка", f"Не удалось создать пользователя:\n{error_msg}", parent=dialog)
#                     return
#
#                 admin_status = "Администратор" if is_admin.get() else "Обычный пользователь"
#
#                 if is_admin.get():
#                     try:
#                         admin_result = subprocess.run(f'net localgroup Администраторы "{login}" /add',
#                                                       shell=True, capture_output=True, text=True, encoding='cp866')
#                         if admin_result.returncode != 0:
#                             subprocess.run(f'net localgroup Administrators "{login}" /add',
#                                            shell=True, capture_output=True)
#                     except:
#                         pass
#
#                 if self.main_app:
#                     computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
#                     log_message = f"СОЗДАН ПОЛЬЗОВАТЕЛЬ: {login} | Тип: {admin_status} | Пароль: {password_info}"
#                     self.main_app.log_action(log_message, computer_name)
#
#                 messagebox.showinfo("Успех", f"Пользователь {login} создан {password_info}!", parent=dialog)
#                 dialog.destroy()
#
#             except Exception as e:
#                 messagebox.showerror("Ошибка", f"Не удалось создать пользователя:\n{str(e)}", parent=dialog)
#
#         create_btn = ttk.Button(center_btn_frame, text="Создать пользователя",
#                                 command=create_user, width=20, padding=8)
#         create_btn.pack(side='left', padx=10)
#
#         cancel_btn = ttk.Button(center_btn_frame, text="Отмена",
#                                 command=dialog.destroy, width=15, padding=8)
#         cancel_btn.pack(side='left', padx=10)
#
#         dialog.bind('<Return>', lambda e: create_user())
#         dialog.bind('<Escape>', lambda e: dialog.destroy())
#
#     def modify_account(self):
#         """Изменение пароля пользователя"""
#         try:
#             result = subprocess.run("net user", shell=True, capture_output=True, text=True)
#             users = []
#             for line in result.stdout.split('\n'):
#                 if line.strip() and not line.startswith('---') and 'команда' not in line.lower():
#                     users.extend(line.strip().split())
#
#             if not users:
#                 messagebox.showinfo("Информация", "Нет доступных пользователей")
#                 return
#
#             dialog = tk.Toplevel(self.window)
#             dialog.title("Выбор пользователя")
#             dialog.geometry("350x200")
#             dialog.transient(self.window)
#             dialog.grab_set()
#
#             dialog.update_idletasks()
#             x = self.window.winfo_x() + (self.window.winfo_width() - dialog.winfo_width()) // 2
#             y = self.window.winfo_y() + (self.window.winfo_height() - dialog.winfo_height()) // 2
#             dialog.geometry(f"+{x}+{y}")
#
#             main_frame = ttk.Frame(dialog, padding=20)
#             main_frame.pack(fill="both", expand=True)
#
#             ttk.Label(main_frame, text="Выберите пользователя:", font=("Arial", 11)).pack(pady=10)
#
#             user_var = tk.StringVar()
#             user_combo = ttk.Combobox(main_frame, textvariable=user_var, values=users, font=("Arial", 11))
#             user_combo.pack(fill="x", pady=10)
#
#             def change_password():
#                 selected_user = user_var.get()
#                 if not selected_user:
#                     messagebox.showerror("Ошибка", "Выберите пользователя!", parent=dialog)
#                     return
#
#                 password = simpledialog.askstring("Новый пароль",
#                                                   "Введите новый пароль (оставьте пустым для удаления пароля):",
#                                                   show='*',
#                                                   parent=dialog)
#                 if password is None:
#                     return
#
#                 try:
#                     result = subprocess.run(f'net user "{selected_user}" "{password}"',
#                                             shell=True, capture_output=True, text=True, encoding='cp866')
#
#                     if result.returncode != 0:
#                         error_msg = result.stderr.strip()
#                         messagebox.showerror("Ошибка", f"Не удалось изменить пароль:\n{error_msg}", parent=dialog)
#                         return
#
#                     if self.main_app:
#                         computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
#                         if password:
#                             log_message = f"ИЗМЕНЕН ПАРОЛЬ пользователя: {selected_user} | Новый пароль: {password}"
#                         else:
#                             log_message = f"УДАЛЕН ПАРОЛЬ пользователя: {selected_user} | Пароль установлен: ПУСТОЙ"
#                         self.main_app.log_action(log_message, computer_name)
#
#                     password_info = "удален" if not password else f"изменен на: {password}"
#                     messagebox.showinfo("Успех", f"Пароль для {selected_user} {password_info}!", parent=dialog)
#                     dialog.destroy()
#                 except Exception as e:
#                     messagebox.showerror("Ошибка", f"Не удалось изменить пароль:\n{str(e)}", parent=dialog)
#
#             btn_frame = ttk.Frame(main_frame)
#             btn_frame.pack(pady=20)
#
#             ttk.Button(btn_frame, text="Изменить пароль",
#                        command=change_password, width=18, padding=6).pack(side='left', padx=5)
#             ttk.Button(btn_frame, text="Отмена",
#                        command=dialog.destroy, width=12, padding=6).pack(side='left', padx=5)
#
#             dialog.bind('<Return>', lambda e: change_password())
#             dialog.bind('<Escape>', lambda e: dialog.destroy())
#
#         except Exception as e:
#             messagebox.showerror("Ошибка", f"Не удалось получить список пользователей: {str(e)}")
#
#     def delete_account(self):
#         """Удаление пользователя"""
#         try:
#             result = subprocess.run("net user", shell=True, capture_output=True, text=True)
#             users = []
#             for line in result.stdout.split('\n'):
#                 if line.strip() and not line.startswith('---') and 'команда' not in line.lower():
#                     users.extend(line.strip().split())
#
#             protected_users = ['Администратор', 'Гость', 'Administrator', 'Guest']
#             users = [u for u in users if u not in protected_users]
#
#             if not users:
#                 messagebox.showinfo("Информация", "Нет доступных для удаления пользователей")
#                 return
#
#             dialog = tk.Toplevel(self.window)
#             dialog.title("Удаление пользователя")
#             dialog.geometry("350x200")
#             dialog.transient(self.window)
#             dialog.grab_set()
#
#             dialog.update_idletasks()
#             x = self.window.winfo_x() + (self.window.winfo_width() - dialog.winfo_width()) // 2
#             y = self.window.winfo_y() + (self.window.winfo_height() - dialog.winfo_height()) // 2
#             dialog.geometry(f"+{x}+{y}")
#
#             main_frame = ttk.Frame(dialog, padding=20)
#             main_frame.pack(fill="both", expand=True)
#
#             ttk.Label(main_frame, text="Выберите пользователя для удаления:", font=("Arial", 11)).pack(pady=10)
#
#             user_var = tk.StringVar()
#             user_combo = ttk.Combobox(main_frame, textvariable=user_var, values=users, font=("Arial", 11))
#             user_combo.pack(fill="x", pady=10)
#
#             def delete():
#                 selected_user = user_var.get()
#                 if not selected_user:
#                     messagebox.showerror("Ошибка", "Выберите пользователя!", parent=dialog)
#                     return
#
#                 if messagebox.askyesno("Подтверждение",
#                                        f"Удалить пользователя {selected_user}?",
#                                        parent=dialog):
#                     try:
#                         result = subprocess.run(f'net user "{selected_user}" /delete',
#                                                 shell=True, capture_output=True, text=True, encoding='cp866')
#
#                         if result.returncode != 0:
#                             error_msg = result.stderr.strip()
#                             messagebox.showerror("Ошибка", f"Не удалось удалить пользователя:\n{error_msg}",
#                                                  parent=dialog)
#                             return
#
#                         if self.main_app:
#                             computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
#                             log_message = f"УДАЛЕН ПОЛЬЗОВАТЕЛЬ: {selected_user}"
#                             self.main_app.log_action(log_message, computer_name)
#
#                         messagebox.showinfo("Успех", f"Пользователь {selected_user} удален!", parent=dialog)
#                         dialog.destroy()
#                     except Exception as e:
#                         messagebox.showerror("Ошибка", f"Не удалось удалить пользователя:\n{str(e)}", parent=dialog)
#
#             btn_frame = ttk.Frame(main_frame)
#             btn_frame.pack(pady=20)
#
#             ttk.Button(btn_frame, text="Удалить",
#                        command=delete, width=15, padding=6).pack(side='left', padx=5)
#             ttk.Button(btn_frame, text="Отмена",
#                        command=dialog.destroy, width=12, padding=6).pack(side='left', padx=5)
#
#             dialog.bind('<Return>', lambda e: delete())
#             dialog.bind('<Escape>', lambda e: dialog.destroy())
#
#         except Exception as e:
#             messagebox.showerror("Ошибка", f"Не удалось получить список пользователей: {str(e)}")
#
#
# class NetworkCheckWindow:
#     """Окно проверки сети с консолью для диагностики"""
#
#     def __init__(self, parent, main_app):
#         self.main_app = main_app
#         self.window = tk.Toplevel(parent)
#         self.window.title("Проверка сети")
#         self.window.state('zoomed')
#         self.is_running = False
#         self.create_interface()
#         self.run_network_diagnostics()
#
#     def create_interface(self):
#         # Заголовок
#         ttk.Label(self.window, text="Диагностика сети",
#                   font=("Arial", 18, "bold")).pack(pady=15)
#
#         # Верхняя панель с кнопками
#         top_frame = ttk.Frame(self.window)
#         top_frame.pack(fill="x", padx=30, pady=10)
#
#         ttk.Label(top_frame, text="Быстрые команды:", font=("Arial", 12)).pack(side="left", padx=5)
#
#         ttk.Button(top_frame, text="Ping Google",
#                    command=lambda: self.run_command("ping -n 4 google.com"),
#                    width=15, padding=5).pack(side="left", padx=3)
#
#         ttk.Button(top_frame, text="Ping Yandex",
#                    command=lambda: self.run_command("ping -n 4 yandex.ru"),
#                    width=15, padding=5).pack(side="left", padx=3)
#
#         ttk.Button(top_frame, text="Ping 8.8.8.8",
#                    command=lambda: self.run_command("ping -n 4 8.8.8.8"),
#                    width=15, padding=5).pack(side="left", padx=3)
#
#         ttk.Button(top_frame, text="Очистить",
#                    command=self.clear_console,
#                    width=12, padding=5).pack(side="right", padx=3)
#
#         ttk.Button(top_frame, text="Стоп",
#                    command=self.stop_diagnostics,
#                    width=12, padding=5).pack(side="right", padx=3)
#
#         # Поле для ввода пользовательской команды
#         cmd_frame = ttk.Frame(self.window)
#         cmd_frame.pack(fill="x", padx=30, pady=5)
#
#         ttk.Label(cmd_frame, text="Команда:", font=("Arial", 11)).pack(side="left", padx=5)
#         self.cmd_entry = ttk.Entry(cmd_frame, font=("Courier", 11), width=50)
#         self.cmd_entry.pack(side="left", padx=5)
#         self.cmd_entry.bind('<Return>', lambda e: self.execute_custom_command())
#
#         ttk.Button(cmd_frame, text="Выполнить",
#                    command=self.execute_custom_command,
#                    width=12, padding=5).pack(side="left", padx=5)
#
#         # Консоль вывода
#         console_frame = ttk.LabelFrame(self.window, text="Консоль вывода", padding=10)
#         console_frame.pack(padx=30, pady=10, fill="both", expand=True)
#
#         self.console_text = tk.Text(console_frame, wrap="word", font=("Courier", 11),
#                                     bg="black", fg="green", insertbackground="green")
#         self.console_text.pack(side="left", fill="both", expand=True)
#
#         console_scrollbar = ttk.Scrollbar(console_frame, orient="vertical",
#                                           command=self.console_text.yview)
#         self.console_text.configure(yscrollcommand=console_scrollbar.set)
#         console_scrollbar.pack(side="right", fill="y")
#
#         # Статус бар
#         self.status_var = tk.StringVar(value="Готов к работе")
#         status_bar = ttk.Label(self.window, textvariable=self.status_var,
#                                relief="sunken", anchor="w", font=("Arial", 10))
#         status_bar.pack(fill="x", padx=30, pady=5)
#
#         # Кнопка закрытия
#         ttk.Button(self.window, text="Закрыть",
#                    command=self.window.destroy, width=20, padding=8).pack(pady=10)
#
#     def write_to_console(self, text, color=None):
#         """Вывод текста в консоль"""
#         self.console_text.insert(tk.END, text + "\n")
#         self.console_text.see(tk.END)
#         self.window.update()
#
#     def clear_console(self):
#         """Очистка консоли"""
#         self.console_text.delete(1.0, tk.END)
#         self.status_var.set("Консоль очищена")
#
#     def stop_diagnostics(self):
#         """Остановка диагностики"""
#         self.is_running = False
#         self.status_var.set("Диагностика остановлена пользователем")
#         self.write_to_console("\n=== ДИАГНОСТИКА ОСТАНОВЛЕНА ПОЛЬЗОВАТЕЛЕМ ===\n")
#
#     def execute_custom_command(self):
#         """Выполнение пользовательской команды"""
#         command = self.cmd_entry.get().strip()
#         if command:
#             self.run_command(command)
#             self.cmd_entry.delete(0, tk.END)
#
#     def run_command(self, command):
#         """Выполнение отдельной команды"""
#
#         def run_thread():
#             try:
#                 self.status_var.set(f"Выполнение: {command}")
#                 self.write_to_console(f"\n{'=' * 60}")
#                 self.write_to_console(f"КОМАНДА: {command}")
#                 self.write_to_console(f"{'=' * 60}\n")
#
#                 result = subprocess.run(command, shell=True, capture_output=True,
#                                         text=True, encoding='cp866', errors='ignore',
#                                         timeout=30)
#
#                 if result.stdout:
#                     self.write_to_console(result.stdout)
#                 if result.stderr:
#                     self.write_to_console(f"ОШИБКА:\n{result.stderr}", color="red")
#
#                 self.status_var.set("Команда выполнена")
#
#             except subprocess.TimeoutExpired:
#                 self.write_to_console("ОШИБКА: Превышено время ожидания команды (30 сек)")
#                 self.status_var.set("Ошибка: таймаут")
#             except Exception as e:
#                 self.write_to_console(f"ОШИБКА: {str(e)}")
#                 self.status_var.set("Ошибка выполнения")
#
#         thread = threading.Thread(target=run_thread)
#         thread.daemon = True
#         thread.start()
#
#     def run_network_diagnostics(self):
#         """Автоматический запуск сетевой диагностики"""
#
#         def diagnostics_thread():
#             try:
#                 self.is_running = True
#                 computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
#
#                 self.write_to_console("=" * 60)
#                 self.write_to_console("   АВТОМАТИЧЕСКАЯ ДИАГНОСТИКА СЕТИ")
#                 self.write_to_console(f"   Компьютер: {computer_name}")
#                 self.write_to_console(f"   Время: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#                 self.write_to_console("=" * 60)
#                 self.write_to_console(" ")
#
#                 # Список команд для диагностики
#                 commands = [
#                     ("ipconfig /all", "ИНФОРМАЦИЯ О СЕТЕВЫХ АДРЕСАХ"),
#                     ("ping -n 4 127.0.0.1", "ПРОВЕРКА LOCALHOST"),
#                     ("ping -n 4 8.8.8.8", "ПРОВЕРКА DNS GOOGLE (8.8.8.8)"),
#                     ("ping -n 4 yandex.ru", "ПРОВЕРКА YANDEX.RU"),
#                     ("ping -n 4 google.com", "ПРОВЕРКА GOOGLE.COM"),
#                     ("tracert -d -h 10 8.8.8.8", "ТРАССИРОВКА ДО 8.8.8.8 (макс. 10 hops)"),
#                     ("netstat -an | findstr ESTABLISHED", "АКТИВНЫЕ ПОДКЛЮЧЕНИЯ"),
#                     ("nslookup google.com", "ПРОВЕРКА DNS РАЗРЕШЕНИЯ"),
#                     ("route print", "ТАБЛИЦА МАРШРУТИЗАЦИИ"),
#                 ]
#
#                 for cmd, description in commands:
#                     if not self.is_running:
#                         self.write_to_console("\n=== ДИАГНОСТИКА ОСТАНОВЛЕНА ===\n")
#                         break
#
#                     self.status_var.set(f"Выполнение: {description}")
#                     self.write_to_console(f"\n{'=' * 60}")
#                     self.write_to_console(f"  {description}")
#                     self.write_to_console(f"  Команда: {cmd}")
#                     self.write_to_console(f"{'=' * 60}\n")
#
#                     try:
#                         result = subprocess.run(cmd, shell=True, capture_output=True,
#                                                 text=True, encoding='cp866', errors='ignore',
#                                                 timeout=30)
#
#                         if result.stdout:
#                             self.write_to_console(result.stdout)
#                         if result.stderr:
#                             self.write_to_console(f"ОШИБКА:\n{result.stderr}")
#
#                         # Небольшая пауза между командами
#                         time.sleep(0.5)
#
#                     except subprocess.TimeoutExpired:
#                         self.write_to_console("ОШИБКА: Превышено время ожидания (30 сек)")
#                     except Exception as e:
#                         self.write_to_console(f"ОШИБКА: {str(e)}")
#
#                 if self.is_running:
#                     self.write_to_console("\n" + "=" * 60)
#                     self.write_to_console("   ДИАГНОСТИКА ЗАВЕРШЕНА")
#                     self.write_to_console("=" * 60)
#                     self.status_var.set("Диагностика завершена")
#
#                     # Логирование
#                     if self.main_app:
#                         self.main_app.log_action(
#                             "ПРОВЕРКА СЕТИ: Автоматическая диагностика выполнена",
#                             computer_name)
#
#             except Exception as e:
#                 self.write_to_console(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
#                 self.status_var.set("Ошибка диагностики")
#
#         thread = threading.Thread(target=diagnostics_thread)
#         thread.daemon = True
#         thread.start()
#
#
# class ProfilesWindow:
#     def __init__(self, parent, main_app):
#         self.main_app = main_app
#         self.window = tk.Toplevel(parent)
#         self.window.title("Управление профилями")
#         self.window.state('zoomed')
#         self.create_interface()
#         self.refresh_profiles_list()
#
#     def create_interface(self):
#         ttk.Label(self.window, text="Управление профилями настроек",
#                   font=("Arial", 18, "bold")).pack(pady=20)
#
#         frame = ttk.LabelFrame(self.window, text="Сохраненные профили", padding=15)
#         frame.pack(padx=30, pady=10, fill="both", expand=True)
#
#         list_frame = ttk.Frame(frame)
#         list_frame.pack(fill="both", expand=True)
#
#         self.profiles_listbox = tk.Listbox(list_frame, font=("Arial", 12))
#         self.profiles_listbox.pack(side="left", fill="both", expand=True)
#
#         scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.profiles_listbox.yview)
#         self.profiles_listbox.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")
#
#         btn_frame = ttk.Frame(self.window)
#         btn_frame.pack(pady=20)
#
#         button_style = {'width': 15, 'padding': 8}
#
#         ttk.Button(btn_frame, text="Обновить",
#                    command=self.refresh_profiles_list, **button_style).pack(side='left', padx=5)
#
#         ttk.Button(btn_frame, text="Экспорт",
#                    command=self.export_profile, **button_style).pack(side='left', padx=5)
#
#         ttk.Button(btn_frame, text="Импорт",
#                    command=self.import_profile, **button_style).pack(side='left', padx=5)
#
#         ttk.Button(btn_frame, text="Удалить",
#                    command=self.delete_profile, **button_style).pack(side='left', padx=5)
#
#         ttk.Button(btn_frame, text="Закрыть",
#                    command=self.window.destroy, **button_style).pack(side='left', padx=5)
#
#     def refresh_profiles_list(self):
#         self.profiles_listbox.delete(0, tk.END)
#         self.main_app.load_profiles()
#
#         for profile_name in self.main_app.profiles.keys():
#             self.profiles_listbox.insert(tk.END, profile_name)
#
#     def export_profile(self):
#         selection = self.profiles_listbox.curselection()
#         if not selection:
#             messagebox.showwarning("Предупреждение", "Выберите профиль для экспорта!")
#             return
#
#         profile_name = self.profiles_listbox.get(selection[0])
#
#         filename = filedialog.asksaveasfilename(
#             defaultextension=".json",
#             filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
#             initialfile=f"{profile_name}.json"
#         )
#
#         if filename:
#             src = self.main_app.profiles_path / f"{profile_name}.json"
#             shutil.copy2(src, filename)
#             messagebox.showinfo("Успех", f"Профиль экспортирован в {filename}")
#
#     def import_profile(self):
#         filename = filedialog.askopenfilename(
#             filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
#         )
#
#         if filename:
#             dest = self.main_app.profiles_path / Path(filename).name
#             shutil.copy2(filename, dest)
#             self.refresh_profiles_list()
#             messagebox.showinfo("Успех", "Профиль импортирован!")
#
#     def delete_profile(self):
#         selection = self.profiles_listbox.curselection()
#         if not selection:
#             messagebox.showwarning("Предупреждение", "Выберите профиль для удаления!")
#             return
#
#         profile_name = self.profiles_listbox.get(selection[0])
#
#         if messagebox.askyesno("Подтверждение", f"Удалить профиль '{profile_name}'?"):
#             profile_file = self.main_app.profiles_path / f"{profile_name}.json"
#             profile_file.unlink()
#             self.refresh_profiles_list()
#             messagebox.showinfo("Успех", "Профиль удален!")
#
#
# class LogsWindow:
#     def __init__(self, parent, main_app):
#         self.main_app = main_app
#         self.window = tk.Toplevel(parent)
#         self.window.title("Журнал изменений")
#         self.window.state('zoomed')
#         self.create_interface()
#         self.load_logs()
#
#     def create_interface(self):
#         ttk.Label(self.window, text="Журнал изменений",
#                   font=("Arial", 18, "bold")).pack(pady=20)
#
#         top_frame = ttk.Frame(self.window)
#         top_frame.pack(fill="x", padx=30, pady=10)
#
#         ttk.Label(top_frame, text="Дата:", font=("Arial", 12)).pack(side="left", padx=5)
#
#         self.date_var = tk.StringVar()
#         self.date_combo = ttk.Combobox(top_frame, textvariable=self.date_var, width=30, font=("Arial", 11))
#         self.date_combo.pack(side="left", padx=5)
#         self.date_combo.bind('<<ComboboxSelected>>', lambda e: self.load_logs())
#
#         ttk.Button(top_frame, text="Обновить",
#                    command=self.load_logs, width=15, padding=5).pack(side="left", padx=5)
#
#         ttk.Button(top_frame, text="Очистить",
#                    command=self.clear_logs, width=15, padding=5).pack(side="left", padx=5)
#
#         frame = ttk.LabelFrame(self.window, text="Записи", padding=15)
#         frame.pack(padx=30, pady=10, fill="both", expand=True)
#
#         text_frame = ttk.Frame(frame)
#         text_frame.pack(fill="both", expand=True)
#
#         self.logs_text = tk.Text(text_frame, wrap="word", font=("Courier", 11))
#         self.logs_text.pack(side="left", fill="both", expand=True)
#
#         scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.logs_text.yview)
#         self.logs_text.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")
#
#         ttk.Button(self.window, text="Закрыть",
#                    command=self.window.destroy, width=20, padding=8).pack(pady=20)
#
#         self.update_date_list()
#
#     def update_date_list(self):
#         dates = []
#         for log_file in self.main_app.logs_path.glob("log_*.txt"):
#             date_str = log_file.stem.replace("log_", "")
#             dates.append(date_str)
#
#         dates.sort(reverse=True)
#         self.date_combo['values'] = dates
#         if dates:
#             self.date_combo.set(dates[0])
#
#     def load_logs(self):
#         self.logs_text.delete(1.0, tk.END)
#
#         date = self.date_var.get()
#         if not date:
#             return
#
#         log_file = self.main_app.logs_path / f"log_{date}.txt"
#
#         if log_file.exists():
#             with open(log_file, 'r', encoding='utf-8') as f:
#                 self.logs_text.insert(1.0, f.read())
#         else:
#             self.logs_text.insert(1.0, f"Нет записей за {date}")
#
#     def clear_logs(self):
#         if messagebox.askyesno("Подтверждение",
#                                "Очистить все записи в журнале?"):
#             for log_file in self.main_app.logs_path.glob("*.txt"):
#                 log_file.unlink()
#             self.update_date_list()
#             self.logs_text.delete(1.0, tk.END)
#             messagebox.showinfo("Успех", "Журнал очищен!")
#
#
# def main():
#     if not ctypes.windll.shell32.IsUserAnAdmin():
#         response = messagebox.askyesno("Права администратора",
#                                        "Для полной функциональности программе требуются права администратора.\n"
#                                        "Запустить с правами администратора?")
#         if response:
#             ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
#             sys.exit()
#     root = tk.Tk()
#     app = PortableGroupPolicyApp(root)
#     root.mainloop()
#
#
# if __name__ == "__main__":
#     main()


"""
Portable Group Policy Manager
Точка входа приложения
Учебный проект ПМ 02
"""
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox

from core.app import PortableGroupPolicyApp


def check_admin_rights():
    """Проверка прав администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Перезапуск с правами администратора"""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return True
    except:
        return False


def run_tests():
    """Запуск тестового модуля"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(f"Ошибки: {result.stderr}")
    return result.returncode == 0


def main():
    """Основная функция запуска"""
    # Проверка аргументов командной строки
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Запуск тестов...")
        success = run_tests()
        sys.exit(0 if success else 1)

    # Проверка прав администратора
    if not check_admin_rights():
        response = messagebox.askyesno(
            "Права администратора",
            "Для полной функциональности программе требуются права администратора.\n"
            "Запустить с правами администратора?"
        )
        if response:
            if run_as_admin():
                sys.exit()
            else:
                messagebox.showwarning(
                    "Предупреждение",
                    "Не удалось запустить с правами администратора.\n"
                    "Некоторые функции могут быть недоступны."
                )

    # Запуск приложения
    root = tk.Tk()
    root.title("Portable Group Policy Manager")
    app = PortableGroupPolicyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()