"""
view.py - Представление для программы фиксации проезда автомобителей

Содержит все графические окна:
- MainMenu (главное меню)
- HelpWindow (окно справки)
- AddDialog (диалог добавления)
- WorkWindow (рабочее окно с таблицей)
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List, Optional, Callable

from model import CarPass, Validation, DATE_FORMAT, DATE_EXAMPLE, VALID_PLATE_LETTERS


# ============================================================
# Вспомогательная функция
# ============================================================

def show_error(parent, title: str, message: str):
    """Показать сообщение об ошибке"""
    messagebox.showerror(title, message, parent=parent)


# ============================================================
# Главное меню
# ============================================================

class MainMenu(tk.Tk):
    """Главное окно с меню программы"""
    
    def __init__(self, on_work_click: Callable, on_help_click: Callable, on_exit_click: Callable):
        """
        Инициализация главного меню
        
        Args:
            on_work_click: callback для кнопки "Работать"
            on_help_click: callback для кнопки "Справка"
            on_exit_click: callback для кнопки "Выход"
        """
        super().__init__()
        self.on_work_click = on_work_click
        self.on_help_click = on_help_click
        self.on_exit_click = on_exit_click
        
        self.title("Главное меню")
        self.geometry("300x250")
        self.resizable(False, False)
        
        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_exit_click)
    
    def _create_widgets(self):
        """Создание виджетов главного меню"""
        # Заголовок
        title_label = tk.Label(
            self,
            text="Фиксация проезда\nавтомобилей",
            font=('Arial', 14, 'bold'),
            pady=20
        )
        title_label.pack()
        
        # Кнопки
        btn_frame = tk.Frame(self)
        btn_frame.pack(expand=True)
        
        buttons = [
            ("Работать", self.on_work_click, '#4CAF50'),
            ("Справка", self.on_help_click, '#2196F3'),
            ("Выход", self.on_exit_click, '#f44336')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                btn_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 11, 'bold'),
                width=15,
                height=1,
                relief=tk.RAISED,
                bd=2
            )
            btn.pack(pady=5)
    
    def show(self):
        """Показать окно"""
        self.deiconify()
        self.focus_force()
    
    def hide(self):
        """Скрыть окно"""
        self.withdraw()


# ============================================================
# Окно справки
# ============================================================

class HelpWindow(tk.Toplevel):
    """Окно с информацией о программе и изображением"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Справка")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        self._add_image()
        self._add_info_text()
        self._add_back_button()
        
        self.protocol("WM_DELETE_WINDOW", self._go_back)
    
    def _add_image(self):
        """Добавление изображения"""
        image_frame = ttk.Frame(self)
        image_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        image_path = os.path.join(os.path.dirname(__file__), "foto.jpg")
        
        if os.path.exists(image_path):
            try:
                from PIL import Image, ImageTk
                pil_image = Image.open(image_path)
                pil_image.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(pil_image)
                
                label = ttk.Label(image_frame, image=photo)
                label.image = photo
                label.pack()
                
                ttk.Label(image_frame, text="foto.jpg",
                         font=('Arial', 9, 'italic')).pack(pady=5)
            except ImportError:
                ttk.Label(image_frame, 
                         text="PIL не установлен. Изображение не отображается.",
                         foreground='red').pack()
            except Exception as e:
                ttk.Label(image_frame, text=f"Ошибка: {e}").pack()
        else:
            ttk.Label(image_frame, 
                     text="Файл foto.jpg не найден",
                     foreground='red').pack()
    
    def _add_info_text(self):
        """Добавление текстовой информации"""
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(info_frame, text="Программа фиксации проезда автомобилей",
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        info_text = f"""
Формат данных:
{ DATE_FORMAT },НомерАвтомобиля

Примеры:
2025.05.11,А123ВС77
2025.05.12,В456ОК777

Формат номера:
• Буква + 3 цифры + 2 буквы + 2-3 цифры
• Допустимые буквы: { VALID_PLATE_LETTERS }

Функции:
• Загрузка/сохранение в файл
• Добавление/удаление записей
• Выполнение команд из файла (ADD, REM, SAVE)
"""
        text_area = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD,
                                               height=10, font=('Courier', 10))
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, info_text)
        text_area.config(state=tk.DISABLED)
    
    def _add_back_button(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="← Назад", command=self._go_back, width=20).pack()
    
    def _go_back(self):
        self.destroy()
        self.parent.focus_set()


# ============================================================
# Диалог добавления записи
# ============================================================

class AddDialog:
    """Диалоговое окно для добавления записи"""
    
    def __init__(self, parent, on_add: Callable):
        """
        Args:
            parent: родительское окно
            on_add: callback при добавлении (date, plate_number)
        """
        self.parent = parent
        self.on_add = on_add
        
        self.window = tk.Toplevel(parent)
        self.window.title("Добавить запись")
        self.window.geometry("450x250")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._center_window()
        
        self.window.bind('<Return>', lambda e: self._ok())
        self.date_entry.focus()
    
    def _create_widgets(self):
        main = ttk.Frame(self.window, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Дата
        ttk.Label(main, text=f"Дата ({DATE_FORMAT}):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(main, width=25)
        self.date_entry.grid(row=0, column=1, pady=5, padx=10)
        ttk.Label(main, text=f"Пример: {DATE_EXAMPLE}", font=('Arial', 8), foreground='gray')\
            .grid(row=1, column=1, sticky=tk.W)
        
        # Номер
        ttk.Label(main, text="Номер автомобиля:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.plate_entry = ttk.Entry(main, width=25)
        self.plate_entry.grid(row=2, column=1, pady=5, padx=10)
        ttk.Label(main, text="Формат: А123ВС77 или А123ВС777", font=('Arial', 8), foreground='gray')\
            .grid(row=3, column=1, sticky=tk.W)
        
        # Кнопки
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="OK", command=self._ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)
    
    def _center_window(self):
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.window.winfo_height()) // 2
        self.window.geometry(f'+{x}+{y}')
    
    def _ok(self):
        date_str = self.date_entry.get().strip()
        plate_str = self.plate_entry.get().strip()
        
        if not date_str or not plate_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены", parent=self.window)
            return
        
        is_valid, error = Validation.valid_date(date_str)
        if not is_valid:
            messagebox.showerror("Ошибка", f"Неверный формат даты.\n{error}", parent=self.window)
            return
        
        is_valid, error = Validation.valid_plate_number(plate_str)
        if not is_valid:
            messagebox.showerror("Ошибка", f"Неверный формат номера.\n{error}", parent=self.window)
            return
        
        self.on_add(date_str, plate_str.upper())
        self.window.destroy()


# ============================================================
# Рабочее окно с таблицей
# ============================================================

class WorkWindow(tk.Toplevel):
    """Окно для работы с таблицей фиксаций проезда"""
    
    COLUMNS = ["Дата", "Номер автомобиля"]
    
    def __init__(self, parent, data: List[CarPass], 
                 on_load: Callable, on_save: Callable, on_save_as: Callable,
                 on_add: Callable, on_delete: Callable, on_back: Callable,
                 on_execute_commands: Callable = None):
        """
        Args:
            parent: родительское окно
            data: список записей
            on_load: callback для загрузки
            on_save: callback для сохранения
            on_save_as: callback для сохранения как
            on_add: callback для добавления
            on_delete: callback для удаления (принимает список индексов)
            on_back: callback для возврата
            on_execute_commands: callback для выполнения команд из файла (лаба 4)
        """
        super().__init__(parent)
        self.parent = parent
        self.on_load = on_load
        self.on_save = on_save
        self.on_save_as = on_save_as
        self.on_add = on_add
        self.on_delete = on_delete
        self.on_back = on_back
        self.on_execute_commands = on_execute_commands
        
        self.title("Фиксация проезда автомобилей")
        self.geometry("750x450")
        self.data = data
        self.status_var = tk.StringVar(value="Готов")
        
        self._create_menu()
        self._create_toolbar()
        self._create_table()
        self._create_status_bar()
        
        self._refresh_table()
        self.protocol("WM_DELETE_WINDOW", self._go_back)
        self.lift()
        self.focus_force()
    
    def _create_menu(self):
        """Создание главного меню окна"""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть файл", command=self.on_load)
        file_menu.add_command(label="Сохранить", command=self.on_save)
        file_menu.add_command(label="Сохранить как...", command=self.on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выполнить команды...", command=self._show_commands_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Закрыть окно", command=self._go_back)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню Команды (лаба 4)
        commands_menu = tk.Menu(menubar, tearoff=0)
        commands_menu.add_command(label="Выполнить из файла...", command=self._show_commands_dialog)
        menubar.add_cascade(label="Команды", menu=commands_menu)
        
        self.config(menu=menubar)
    
    def _create_toolbar(self):
        """Создание панели инструментов"""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Добавить", command=self._show_add_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить", command=self._delete_selected).pack(side=tk.LEFT, padx=2)
        
        # Кнопка выполнения команд (лаба 4)
        if self.on_execute_commands:
            ttk.Button(btn_frame, text="Выполнить команды", command=self._show_commands_dialog).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_frame, text="← Назад", command=self._go_back).pack(side=tk.LEFT, padx=20)
    
    def _create_table(self):
        """Создание таблицы для отображения данных"""
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создаём Treeview с прокруткой
        self.tree = ttk.Treeview(frame, show="headings", columns=self.COLUMNS, height=15)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Настройка колонок
        for i, col in enumerate(self.COLUMNS):
            self.tree.heading(col, text=col)
            width = 120 if i == 0 else 300
            anchor = 'center' if i == 0 else 'w'
            self.tree.column(col, width=width, anchor=anchor)
        
        # Вертикальная прокрутка
        scrollbar_v = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar_v.set)
        
        # Горизонтальная прокрутка (если нужно)
        scrollbar_h = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=scrollbar_h.set)
    
    def _create_status_bar(self):
        """Создание строки статуса"""
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _refresh_table(self):
        """Обновление таблицы из данных"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Заполняем заново
        for item in self.data:
            self.tree.insert("", tk.END, values=(item.date, item.plate_number))
        
        # Обновляем статус
        self.status_var.set(f"Всего записей: {len(self.data)}")
    
    def update_data(self, new_data: List[CarPass]):
        """Обновление данных и таблицы"""
        self.data = new_data
        self._refresh_table()
    
    def _go_back(self):
        """Возврат в главное меню"""
        self.on_back()
    
    def _delete_selected(self):
        """Удаление выбранных записей"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Ничего не выбрано", parent=self)
            return
        
        indices = [self.tree.index(item) for item in selected]
        
        if messagebox.askyesno("Подтверждение", f"Удалить {len(selected)} запись(и)?", parent=self):
            self.on_delete(indices)
    
    def _show_add_dialog(self):
        """Показать диалог добавления"""
        AddDialog(self, self._on_add_callback)
    
    def _on_add_callback(self, date_str: str, plate_str: str):
        """Callback после добавления записи"""
        self.on_add(date_str, plate_str)
    
    def _show_commands_dialog(self):
        """Показать диалог выбора файла с командами (лаба 4)"""
        if not self.on_execute_commands:
            messagebox.showinfo("Информация", "Функция выполнения команд недоступна", parent=self)
            return
        
        filename = filedialog.askopenfilename(
            title="Выберите файл с командами",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            parent=self
        )
        
        if filename:
            self.status_var.set(f"Выполняются команды из {os.path.basename(filename)}...")
            self.update()  # Принудительно обновляем интерфейс
            self.on_execute_commands(filename)
