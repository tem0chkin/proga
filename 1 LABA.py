"""Программа для учета фиксации проезда автомобилей.

Каждая строка файла содержит данные о проезде в формате:
ГГГГ.ММ.ДД,НомерАвтомобиля

Интерфейс:
- Главное окно — меню с тремя кнопками: «Работать», «Справка», «Выход».
- «Работать» открывает окно с таблицей проездов.
- «Справка» открывает окно с изображением foto.jpg.
- «Выход» завершает программу.
"""

import datetime
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List, Optional


# ============================================================
# Константы
# ============================================================

DEFAULT_FILENAME = "car_passes.txt"
DATE_FORMAT = "ГГГГ.ММ.ДД"
DATE_EXAMPLE = "2025.05.11"
PLATE_PATTERN = r'^[АВЕКМНОРСТУХ]{1}\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$'
VALID_PLATE_LETTERS = "А, В, Е, К, М, Н, О, Р, С, Т, У, Х"


# ============================================================
# Классы для работы с данными (модель)
# ============================================================

class CarPass:
    """Класс, представляющий одну фиксацию проезда автомобиля."""
    
    def __init__(self, date: str = "", plate_number: str = "") -> None:
        """Инициализация фиксации проезда.
        
        Args:
            date: Дата проезда в формате ГГГГ.ММ.ДД
            plate_number: Номер автомобиля
        """
        self.date = date
        self.plate_number = plate_number
    
    def __str__(self) -> str:
        """Строковое представление для сохранения в файл."""
        return f"{self.date},{self.plate_number}"
    
    @classmethod
    def from_string(cls, line: str) -> Optional['CarPass']:
        """Создание объекта из строки файла.
        
        Args:
            line: Строка вида "ГГГГ.ММ.ДД,НомерАвтомобиля"
            
        Returns:
            Объект CarPass или None при ошибке
        """
        try:
            parts = [x.strip() for x in line.strip().split(',')]
            if len(parts) != 2:
                return None
            
            date_str, plate_str = parts
            
            if not valid_date(date_str):
                return None
            
            if not valid_plate_number(plate_str):
                return None
            
            return cls(date_str, plate_str.upper())
        except Exception:
            return None


# ============================================================
# Функции валидации
# ============================================================

def valid_date(date_str: str) -> bool:
    """Проверка корректности даты в формате ГГГГ.ММ.ДД.
    
    Args:
        date_str: Строка с датой
        
    Returns:
        True если дата корректна, иначе False
    """
    if len(date_str) != 10:
        return False
    if date_str[4] != '.' or date_str[7] != '.':
        return False
    
    for i in range(10):
        if i in (4, 7):
            continue
        if not date_str[i].isdigit():
            return False
    
    try:
        year = int(date_str[0:4])
        month = int(date_str[5:7])
        day = int(date_str[8:10])
        
        if year < 2000 or year > 2100:
            return False
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        
        # Проверка количества дней в месяце
        days_in_month = [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30,
                         31, 31, 30, 31, 30, 31]
        return day <= days_in_month[month - 1]
    except Exception:
        return False


def valid_plate_number(plate: str) -> bool:
    """Проверка корректности номера автомобиля.
    
    Формат: Буква, 3 цифры, 2 буквы, 2-3 цифры региона.
    Допустимые буквы: А, В, Е, К, М, Н, О, Р, С, Т, У, Х.
    
    Args:
        plate: Номер автомобиля
        
    Returns:
        True если номер корректен, иначе False
    """
    if not plate:
        return False
    return bool(re.match(PLATE_PATTERN, plate.upper()))


# ============================================================
# Работа с файлами
# ============================================================

class FileManager:
    """Класс для работы с файловым хранилищем."""
    
    @staticmethod
    def load(filename: str) -> List[CarPass]:
        """Загрузка данных из файла.
        
        Args:
            filename: Путь к файлу
            
        Returns:
            Список объектов CarPass
        """
        data = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        car_pass = CarPass.from_string(line)
                        if car_pass:
                            data.append(car_pass)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
        return data
    
    @staticmethod
    def save(filename: str, data: List[CarPass]) -> bool:
        """Сохранение данных в файл.
        
        Args:
            filename: Путь к файлу
            data: Список объектов CarPass
            
        Returns:
            True при успешном сохранении, иначе False
        """
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                for item in data:
                    file.write(f"{item}\n")
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False


# ============================================================
# Окно справки
# ============================================================

class HelpWindow(tk.Toplevel):
    """Окно с информацией о программе и изображением."""
    
    def __init__(self, parent_menu: tk.Tk) -> None:
        """Инициализация окна справки.
        
        Args:
            parent_menu: Родительское окно меню
        """
        super().__init__(parent_menu)
        self.parent_menu = parent_menu
        self.title("Справка")
        self.geometry("600x500")
        self.transient(parent_menu)
        self.grab_set()
        
        self._add_image()
        self._add_info_text()
        self._add_back_button()
        
        self.protocol("WM_DELETE_WINDOW", self._go_back)
    
    def _add_image(self) -> None:
        """Добавление изображения в окно справки."""
        image_frame = ttk.Frame(self)
        image_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        image_path = os.path.join(os.path.dirname(__file__), "foto.jpg")
        
        if os.path.exists(image_path):
            try:
                # Попытка использовать PIL для отображения изображения
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
                ttk.Label(image_frame, 
                         text=f"Ошибка загрузки: {e}").pack()
        else:
            ttk.Label(image_frame, 
                     text="Файл foto.jpg не найден в папке программы",
                     foreground='red').pack()
    
    def _add_info_text(self) -> None:
        """Добавление текстовой информации о программе."""
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
2025.05.13,М789НР12

Формат номера автомобиля:
• Буква
• 3 цифры
• 2 буквы
• 2-3 цифры региона

Допустимые буквы: { VALID_PLATE_LETTERS }

Функции программы:
• Загрузка данных из файла
• Сохранение данных в файл
• Добавление новых записей
• Удаление выбранных записей
"""
        
        text_area = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD,
                                               height=10, font=('Courier', 10))
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, info_text)
        text_area.config(state=tk.DISABLED)
    
    def _add_back_button(self) -> None:
        """Добавление кнопки возврата."""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="← Назад", command=self._go_back,
                  width=20).pack()
    
    def _go_back(self) -> None:
        """Возврат в главное меню."""
        self.destroy()
        self.parent_menu.focus_set()


# ============================================================
# Окно работы с данными
# ============================================================

class WorkWindow(tk.Toplevel):
    """Окно для работы с таблицей фиксаций проезда."""
    
    COLUMNS = ["Дата", "Номер автомобиля"]
    
    def __init__(self, parent_menu: tk.Tk) -> None:
        """Инициализация рабочего окна.
        
        Args:
            parent_menu: Родительское окно меню
        """
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
        self.lift()
        self.focus_force()
    
    def _create_menu(self) -> None:
        """Создание главного меню окна."""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть файл", command=self._open_file)
        file_menu.add_command(label="Сохранить", command=self._save)
        file_menu.add_command(label="Сохранить как...", command=self._save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Закрыть окно", command=self._go_back)
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.config(menu=menubar)
    
    def _create_toolbar(self) -> None:
        """Создание панели инструментов."""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Добавить",
                  command=self._show_add_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить",
                  command=self._delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="← Назад",
                  command=self._go_back).pack(side=tk.LEFT, padx=20)
    
    def _create_table(self) -> None:
        """Создание таблицы для отображения данных."""
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(frame, show="headings", columns=self.COLUMNS)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for i, col in enumerate(self.COLUMNS):
            self.tree.heading(col, text=col)
            width = 120 if i == 0 else 250
            anchor = 'center' if i == 0 else 'w'
            self.tree.column(col, width=width, anchor=anchor)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL,
                                   command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def _create_status_bar(self) -> None:
        """Создание строки статуса."""
        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(self, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _load_default_file(self) -> None:
        """Загрузка данных из файла по умолчанию."""
        if os.path.exists(self.current_file):
            self.data = FileManager.load(self.current_file)
            self._refresh_table()
            self.status_var.set(f"Загружено из {self.current_file}")
    
    def _refresh_table(self) -> None:
        """Обновление отображения таблицы."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for item in self.data:
            self.tree.insert("", tk.END, values=(item.date, item.plate_number))
        
        self.status_var.set(f"Всего записей: {len(self.data)}")
    
    def _go_back(self) -> None:
        """Возврат в главное меню."""
        self.parent_menu.show_menu()
        self.destroy()
    
    def _open_file(self) -> None:
        """Открытие файла с данными."""
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.data = FileManager.load(filename)
            self.current_file = filename
            self._refresh_table()
            self.status_var.set(f"Загружено: {os.path.basename(filename)}")
    
    def _save(self) -> None:
        """Сохранение данных в текущий файл."""
        if FileManager.save(self.current_file, self.data):
            messagebox.showinfo("Успех", "Данные сохранены")
            self.status_var.set("Сохранено")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные")
    
    def _save_as(self) -> None:
        """Сохранение данных в новый файл."""
        filename = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        if filename:
            self.current_file = filename
            self._save()
    
    def _delete_selected(self) -> None:
        """Удаление выбранных записей из таблицы."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Ничего не выбрано")
            return
        
        if messagebox.askyesno("Подтверждение",
                               f"Удалить {len(selected)} запись(и)?"):
            for item in reversed(selected):
                index = self.tree.index(item)
                del self.data[index]
            self._refresh_table()
            self.status_var.set(f"Удалено записей: {len(selected)}")
    
    def _show_add_dialog(self) -> None:
        """Отображение диалога добавления записи."""
        AddDialog(self)
    
    def add_record(self, date_str: str, plate_number: str) -> None:
        """Добавление новой записи.
        
        Args:
            date_str: Дата проезда
            plate_number: Номер автомобиля
        """
        self.data.append(CarPass(date_str, plate_number.upper()))
        self._refresh_table()
        self.status_var.set(f"Добавлена запись: {date_str}")


# ============================================================
# Диалог добавления записи
# ============================================================

class AddDialog:
    """Диалоговое окно для добавления новой фиксации проезда."""
    
    def __init__(self, parent: WorkWindow) -> None:
        """Инициализация диалога.
        
        Args:
            parent: Родительское окно
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Добавить запись")
        self.window.geometry("450x250")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._center_window()
        
        self.window.bind('<Return>', lambda e: self._ok())
        self.date_entry.focus()
    
    def _create_widgets(self) -> None:
        """Создание виджетов диалога."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поле для даты
        ttk.Label(main_frame, text=f"Дата ({DATE_FORMAT}):").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(main_frame, width=25)
        self.date_entry.grid(row=0, column=1, pady=5, padx=10)
        ttk.Label(main_frame, text=f"Пример: {DATE_EXAMPLE}",
                 font=('Arial', 8), foreground='gray').grid(
                     row=1, column=1, sticky=tk.W)
        
        # Поле для номера автомобиля
        ttk.Label(main_frame, text="Номер автомобиля:").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.plate_entry = ttk.Entry(main_frame, width=25)
        self.plate_entry.grid(row=2, column=1, pady=5, padx=10)
        ttk.Label(main_frame, text=f"Формат: А123ВС77 или А123ВС777",
                 font=('Arial', 8), foreground='gray').grid(
                     row=3, column=1, sticky=tk.W)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="OK", command=self._ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)
    
    def _center_window(self) -> None:
        """Центрирование окна относительно родителя."""
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.window.winfo_height()) // 2
        self.window.geometry(f'+{x}+{y}')
    
    def _ok(self) -> None:
        """Обработка нажатия кнопки OK."""
        date_str = self.date_entry.get().strip()
        plate_str = self.plate_entry.get().strip()
        
        # Проверка заполнения полей
        if not date_str or not plate_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return
        
        # Проверка даты
        if not valid_date(date_str):
            messagebox.showerror("Ошибка",
                               f"Неверный формат даты. Используйте {DATE_FORMAT}")
            return
        
        # Проверка номера
        if not valid_plate_number(plate_str):
            messagebox.showerror("Ошибка",
                               f"Неверный формат номера.\n"
                               f"Формат: буква + 3 цифры + 2 буквы + 2-3 цифры\n"
                               f"Примеры: А123ВС77, В456ОК777\n"
                               f"Допустимые буквы: {VALID_PLATE_LETTERS}")
            return
        
        self.parent.add_record(date_str, plate_str.upper())
        self.window.destroy()


# ============================================================
# Главное окно меню
# ============================================================

class MainMenu(tk.Tk):
    """Главное окно с меню программы."""
    
    def __init__(self) -> None:
        """Инициализация главного меню."""
        super().__init__()
        self.title("Главное меню")
        self.geometry("300x250")
        self.resizable(False, False)
        
        self._create_widgets()
        self.work_window = None
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
    
    def _create_widgets(self) -> None:
        """Создание виджетов главного меню."""
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
            ("Работать", self._open_work, '#4CAF50'),
            ("Справка", self._open_help, '#2196F3'),
            ("Выход", self.quit_app, '#f44336')
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
        
        # Статусная строка
        self._create_status_label()
    
    def _create_status_label(self) -> None:
        """Создание статусной метки."""
        foto_path = os.path.join(os.path.dirname(__file__), "foto.jpg")
        foto_exists = os.path.exists(foto_path)
        
        status_text = "foto.jpg" if foto_exists else "foto.jpg"
        status_color = '#4CAF50' if foto_exists else '#f44336'
        
        status_label = tk.Label(
            self,
            text=status_text,
            font=('Arial', 8),
            fg=status_color
        )
        status_label.pack(side=tk.BOTTOM, pady=5)
    
    def _open_work(self) -> None:
        """Открытие рабочего окна."""
        self.withdraw()
        self.work_window = WorkWindow(self)
    
    def _open_help(self) -> None:
        """Открытие окна справки."""
        HelpWindow(self)
    
    def show_menu(self) -> None:
        """Показ главного меню (возврат из рабочего окна)."""
        self.deiconify()
        self.work_window = None
        self.focus_force()
    
    def quit_app(self) -> None:
        """Корректный выход из программы."""
        self.quit()
        self.destroy()


# ============================================================
# Точка входа
# ============================================================

def main() -> None:
    """Главная функция программы."""
    if os.name == 'nt':
        os.system('chcp 1251 > nul')
    
    app = MainMenu()
    app.mainloop()


if __name__ == "__main__":
    main()
