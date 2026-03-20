"""
Окно управления профилями
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
from pathlib import Path


class ProfilesWindow:
    """Класс окна управления профилями"""

    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Управление профилями")
        self.window.state('zoomed')

        self.create_interface()
        self.refresh_profiles_list()

    def create_interface(self):
        """Создание интерфейса"""
        ttk.Label(
            self.window,
            text="Управление профилями настроек",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        frame = ttk.LabelFrame(self.window, text="Сохраненные профили", padding=15)
        frame.pack(padx=30, pady=10, fill="both", expand=True)

        self.profiles_listbox = tk.Listbox(frame, font=("Arial", 12))
        self.profiles_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.profiles_listbox.yview)
        self.profiles_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=20)

        button_style = {'width': 15, 'padding': 8}

        ttk.Button(btn_frame, text="Обновить", command=self.refresh_profiles_list, **button_style).pack(side='left',
                                                                                                        padx=5)
        ttk.Button(btn_frame, text="Экспорт", command=self.export_profile, **button_style).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Импорт", command=self.import_profile, **button_style).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_profile, **button_style).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Закрыть", command=self.window.destroy, **button_style).pack(side='left', padx=5)

    def refresh_profiles_list(self):
        """Обновление списка профилей"""
        self.profiles_listbox.delete(0, tk.END)
        self.main_app.load_profiles()
        for profile_name in self.main_app.profiles.keys():
            self.profiles_listbox.insert(tk.END, profile_name)

    def export_profile(self):
        """Экспорт профиля"""
        selection = self.profiles_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите профиль!")
            return

        profile_name = self.profiles_listbox.get(selection[0])
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{profile_name}.json"
        )

        if filename:
            src = self.main_app.profiles_path / f"{profile_name}.json"
            shutil.copy2(src, filename)
            messagebox.showinfo("Успех", f"Профиль экспортирован в {filename}")

    def import_profile(self):
        """Импорт профиля"""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            dest = self.main_app.profiles_path / Path(filename).name
            shutil.copy2(filename, dest)
            self.refresh_profiles_list()
            messagebox.showinfo("Успех", "Профиль импортирован!")

    def delete_profile(self):
        """Удаление профиля"""
        selection = self.profiles_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите профиль!")
            return

        profile_name = self.profiles_listbox.get(selection[0])

        if messagebox.askyesno("Подтверждение", f"Удалить профиль '{profile_name}'?"):
            profile_file = self.main_app.profiles_path / f"{profile_name}.json"
            profile_file.unlink()
            self.refresh_profiles_list()
            messagebox.showinfo("Успех", "Профиль удален!")