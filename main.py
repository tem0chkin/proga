"""
main.py - Точка входа для программы фиксации проезда автомобилей (Лаба 3)

Связывает модель (model.py) и представление (view.py)
"""

import os
from tkinter import filedialog, messagebox

from model import CarPass, FileManager, Logger, DEFAULT_FILENAME
from view import MainMenu, WorkWindow


class Application:
    """Главный класс приложения - Контроллер"""
    
    def __init__(self):
        self.data: list = []
        self.current_file = DEFAULT_FILENAME
        self.logger = Logger()
        self.work_window = None
        
        # Загружаем данные при старте
        self._load_data()
        
        # Создаём главное меню
        self.main_menu = MainMenu(
            on_work_click=self._open_work_window,
            on_help_click=self._open_help,
            on_exit_click=self._quit
        )
    
    def _load_data(self):
        """Загрузка данных из файла по умолчанию"""
        if os.path.exists(self.current_file):
            self.data = FileManager.load(self.current_file)
            self.logger.logger.info(f"Загружено {len(self.data)} записей из {self.current_file}")
    
    def _save_data(self):
        """Сохранение данных в текущий файл"""
        if FileManager.save(self.current_file, self.data):
            messagebox.showinfo("Успех", "Данные сохранены")
            self.logger.logger.info(f"Сохранено {len(self.data)} записей в {self.current_file}")
            return True
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные")
            return False
    
    def _open_work_window(self):
        """Открытие рабочего окна"""
        self.main_menu.hide()
        
        self.work_window = WorkWindow(
            parent=self.main_menu,
            data=self.data,
            on_load=self._load_from_file,
            on_save=self._save_data,
            on_save_as=self._save_as,
            on_add=self._add_record,
            on_delete=self._delete_records,
            on_back=self._close_work_window
        )
    
    def _close_work_window(self):
        """Закрытие рабочего окна и возврат в меню"""
        if self.work_window:
            self.work_window.destroy()
            self.work_window = None
        self.main_menu.show()
    
    def _load_from_file(self):
        """Загрузка из выбранного файла"""
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.current_file = filename
            self.data = FileManager.load(self.current_file)
            self.logger.logger.info(f"Загружено {len(self.data)} записей из {filename}")
            
            if self.work_window:
                self.work_window.update_data(self.data)
                self.work_window.status_var.set(f"Загружено: {os.path.basename(filename)}")
    
    def _save_as(self):
        """Сохранить как..."""
        filename = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        if filename:
            self.current_file = filename
            self._save_data()
    
    def _add_record(self, date_str: str, plate_str: str):
        """Добавление новой записи"""
        new_record = CarPass(date_str, plate_str.upper())
        self.data.append(new_record)
        self.logger.logger.info(f"Добавлена запись: {date_str}, {plate_str}")
        
        if self.work_window:
            self.work_window.update_data(self.data)
            self.work_window.status_var.set(f"Добавлена запись: {date_str}")
    
    def _delete_records(self, indices: list):
        """Удаление записей по индексам"""
        for index in sorted(indices, reverse=True):
            deleted = self.data.pop(index)
            self.logger.logger.info(f"Удалена запись: {deleted.date}, {deleted.plate_number}")
        
        if self.work_window:
            self.work_window.update_data(self.data)
            self.work_window.status_var.set(f"Удалено записей: {len(indices)}")
    
    def _open_help(self):
        """Открытие окна справки"""
        from view import HelpWindow
        HelpWindow(self.main_menu)
    
    def _quit(self):
        """Выход из программы"""
        self.main_menu.quit()
        self.main_menu.destroy()
    
    def run(self):
        """Запуск приложения"""
        self.main_menu.mainloop()


if __name__ == "__main__":
    if os.name == 'nt':
        os.system('chcp 1251 > nul')
    
    app = Application()
    app.run()
