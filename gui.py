"""gui.py - Все графические окна программы"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List

from models import CarPass, FileManager, valid_date, valid_plate_number, DATE_FORMAT, DATE_EXAMPLE, VALID_PLATE_LETTERS, DEFAULT_FILENAME

# ========== ГЛАВНОЕ МЕНЮ ==========
class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Главное меню")
        self.geometry("300x250")
        self.resizable(False, False)
        self.work_window = None
        
        title = tk.Label(self, text="Фиксация проезда\nавтомобилей", font=('Arial', 14, 'bold'), pady=20)
        title.pack()
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(expand=True)
        
        buttons = [
            ("Работать", self._open_work, '#4CAF50'),
            ("Справка", self._open_help, '#2196F3'),
            ("Выход", self.quit_app, '#f44336')
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd, bg=color,
                           fg='white', font=('Arial', 11, 'bold'), width=15)
            btn.pack(pady=5)
        
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
    
    def _open_work(self):
        self.withdraw()
        self.work_window = WorkWindow(self)
    
    def _open_help(self):
        HelpWindow(self)
    
    def show_menu(self):
        self.deiconify()
        self.work_window = None
    
    def quit_app(self):
        self.quit()
        self.destroy()

# ========== ОКНО СПРАВКИ ==========
class HelpWindow(tk.Toplevel):
    def __init__(self, parent_menu):
        super().__init__(parent_menu)
        self.parent_menu = parent_menu
        self.title("Справка")
        self.geometry("600x500")
        self.transient(parent_menu)
        self.grab_set()
        
        self._add_image()
        self._add_info_text()
        
        btn = ttk.Button(self, text="← Назад", command=self._go_back, width=20)
        btn.pack(side=tk.BOTTOM, pady=10)
        
        self.protocol("WM_DELETE_WINDOW", self._go_back)
    
    def _add_image(self):
        frame = ttk.Frame(self)
        frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        image_path = os.path.join(os.path.dirname(__file__), "foto.jpg")
        
        if os.path.exists(image_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(image_path)
                img.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(img)
                label = ttk.Label(frame, image=photo)
                label.image = photo
                label.pack()
                ttk.Label(frame, text="foto.jpg", font=('Arial', 9, 'italic')).pack(pady=5)
            except ImportError:
                ttk.Label(frame, text="PIL не установлен", foreground='red').pack()
            except Exception as e:
                ttk.Label(frame, text=f"Ошибка: {e}").pack()
        else:
            ttk.Label(frame, text="Файл foto.jpg не найден", foreground='red').pack()
    
    def _add_info_text(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(frame, text="Программа фиксации проезда автомобилей", font=('Arial', 14, 'bold')).pack(pady=10)
        
        text = f"""
Формат данных: {DATE_FORMAT},НомерАвтомобиля

Примеры:
2025.05.11,А123ВС77
2025.05.12,В456ОК777

Формат номера:
• Буква + 3 цифры + 2 буквы + 2-3 цифры
• Допустимые буквы: {VALID_PLATE_LETTERS}

Функции:
• Загрузка/сохранение в файл
• Добавление/удаление записей
"""
        ta = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10, font=('Courier', 10))
        ta.pack(fill=tk.BOTH, expand=True)
        ta.insert(tk.END, text)
        ta.config(state=tk.DISABLED)
    
    def _go_back(self):
        self.destroy()
        self.parent_menu.focus_set()

# ========== ДИАЛОГ ДОБАВЛЕНИЯ ==========
class AddDialog:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Добавить запись")
        self.window.geometry("450x250")
        self.window.transient(parent)
        self.window.grab_set()
        
        main = ttk.Frame(self.window, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main, text=f"Дата ({DATE_FORMAT}):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(main, width=25)
        self.date_entry.grid(row=0, column=1, pady=5, padx=10)
        ttk.Label(main, text=f"Пример: {DATE_EXAMPLE}", font=('Arial', 8), foreground='gray').grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(main, text="Номер автомобиля:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.plate_entry = ttk.Entry(main, width=25)
        self.plate_entry.grid(row=2, column=1, pady=5, padx=10)
        ttk.Label(main, text="Формат: А123ВС77 или А123ВС777", font=('Arial', 8), foreground='gray').grid(row=3, column=1, sticky=tk.W)
        
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="OK", command=self._ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)
        
        self.window.bind('<Return>', lambda e: self._ok())
        self._center_window()
        self.date_entry.focus()
    
    def _center_window(self):
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.window.winfo_height()) // 2
        self.window.geometry(f'+{x}+{y}')
    
    def _ok(self):
        date_str = self.date_entry.get().strip()
        plate_str = self.plate_entry.get().strip()
        
        if not date_str or not plate_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return
        if not valid_date(date_str):
            messagebox.showerror("Ошибка", f"Неверный формат даты. Используйте {DATE_FORMAT}")
            return
        if not valid_plate_number(plate_str):
            messagebox.showerror("Ошибка", f"Неверный формат номера.\nФормат: буква + 3 цифры + 2 буквы + 2-3 цифры\nДопустимые буквы: {VALID_PLATE_LETTERS}")
            return
        
        self.parent.add_record(date_str, plate_str.upper())
        self.window.destroy()

# ========== РАБОЧЕЕ ОКНО ==========
class WorkWindow(tk.Toplevel):
    COLUMNS = ["Дата", "Номер автомобиля"]
    
    def __init__(self, parent_menu):
        super().__init__()
        self.parent_menu = parent_menu
        self.title("Фиксация проезда автомобилей")
        self.geometry("700x400")
        
        self.data: List[CarPass] = []
        self.current_file = DEFAULT_FILENAME
        
        self._create_menu()
        self._create_toolbar()
        self._create_table()
        self._create_status_bar()
        
        self._load_default_file()
        self.protocol("WM_DELETE_WINDOW", self._go_back)
    
    def _create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть файл", command=self._open_file)
        file_menu.add_command(label="Сохранить", command=self._save)
        file_menu.add_command(label="Сохранить как...", command=self._save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Закрыть окно", command=self._go_back)
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.config(menu=menubar)
    
    def _create_toolbar(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Добавить", command=self._show_add_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить", command=self._delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="← Назад", command=self._go_back).pack(side=tk.LEFT, padx=20)
    
    def _create_table(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(frame, show="headings", columns=self.COLUMNS)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for i, col in enumerate(self.COLUMNS):
            self.tree.heading(col, text=col)
            width = 120 if i == 0 else 250
            anchor = 'center' if i == 0 else 'w'
            self.tree.column(col, width=width, anchor=anchor)
        
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)
    
    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Готов")
        status = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _load_default_file(self):
        if os.path.exists(self.current_file):
            self.data = FileManager.load(self.current_file)
            self._refresh_table()
            self.status_var.set(f"Загружено из {self.current_file}")
    
    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.data:
            self.tree.insert("", tk.END, values=(item.date, item.plate_number))
        self.status_var.set(f"Всего записей: {len(self.data)}")
    
    def _go_back(self):
        self.parent_menu.show_menu()
        self.destroy()
    
    def _open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if filename:
            self.data = FileManager.load(filename)
            self.current_file = filename
            self._refresh_table()
            self.status_var.set(f"Загружено: {os.path.basename(filename)}")
    
    def _save(self):
        if FileManager.save(self.current_file, self.data):
            messagebox.showinfo("Успех", "Данные сохранены")
            self.status_var.set("Сохранено")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные")
    
    def _save_as(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt")])
        if filename:
            self.current_file = filename
            self._save()
    
    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Ничего не выбрано")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить {len(selected)} запись(и)?"):
            for item in reversed(selected):
                index = self.tree.index(item)
                del self.data[index]
            self._refresh_table()
            self.status_var.set(f"Удалено записей: {len(selected)}")
    
    def _show_add_dialog(self):
        AddDialog(self)
    
    def add_record(self, date_str: str, plate_number: str):
        self.data.append(CarPass(date_str, plate_number.upper()))
        self._refresh_table()
        self.status_var.set(f"Добавлена запись: {date_str}")
