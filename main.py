"""
main.py - Точка входа для программы фиксации проезда автомобилей (Лаба 4)

Связывает модель (model.py) и представление (view.py)
Добавлена поддержка файлов с командами
"""

import os
from tkinter import filedialog, messagebox

from model import CarPass, FileManager, Logger, CommandProcessor, DEFAULT_FILENAME
from view import MainMenu, WorkWindow


class Application:
    """Главный класс приложения - Контроллер"""
    
    def __init__(self):
        self.data: list = []
        self.current_file = DEFAULT_FILENAME
        self.logger = Logger()
        self.work_window = None
        
        self._load_data()
        
        self.main_menu = MainMenu(
            on_work_click=self._open_work_window,
            on_help_click=self._open_help,
            on_exit_click=self._quit
        )
    
    def _load_data(self):
        if os.path.exists(self.current_file):
            self.data = FileManager.load(self.current_file)
            self.logger.log_info(f"Загружено {len(self.data)} записей")
    
    def _save_data(self):
        if FileManager.save(self.current_file, self.data):
            messagebox.showinfo("Успех", "Данные сохранены")
            return True
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные")
            return False
    
    def _open_work_window(self):
        self.main_menu.hide()
        
        self.work_window = WorkWindow(
            parent=self.main_menu,
            data=self.data,
            on_load=self._load_from_file,
            on_save=self._save_data,
            on_save_as=self._save_as,
            on_add=self._add_record,
            on_delete=self._delete_records,
            on_back=self._close_work_window,
            on_execute_commands=self._execute_commands_file  # НОВЫЙ callback
        )
    
    def _close_work_window(self):
        if self.work_window:
            self.work_window.destroy()
            self.work_window = None
        self.main_menu.show()
    
    def _load_from_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.current_file = filename
            self.data = FileManager.load(self.current_file)
            self.logger.log_info(f"Загружено {len(self.data)} записей из {filename}")
            
            if self.work_window:
                self.work_window.update_data(self.data)
                self.work_window.status_var.set(f"Загружено: {os.path.basename(filename)}")
    
    def _save_as(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        if filename:
            self.current_file = filename
            self._save_data()
    
    def _add_record(self, date_str: str, plate_str: str):
        new_record = CarPass(date_str, plate_str.upper())
        self.data.append(new_record)
        self.logger.log_info(f"Добавлена запись: {date_str}, {plate_str}")
        
        if self.work_window:
            self.work_window.update_data(self.data)
            self.work_window.status_var.set(f"Добавлена запись: {date_str}")
    
    def _delete_records(self, indices: list):
        for index in sorted(indices, reverse=True):
            deleted = self.data.pop(index)
            self.logger.log_info(f"Удалена запись: {deleted.date}, {deleted.plate_number}")
        
        if self.work_window:
            self.work_window.update_data(self.data)
            self.work_window.status_var.set(f"Удалено записей: {len(indices)}")
    
    def _execute_commands_file(self, filename: str):
        """НОВЫЙ МЕТОД: выполнение команд из файла"""
        self.data, errors = CommandProcessor.process_commands_file(
            self.data, filename, self._on_data_changed
        )
        
        if self.work_window:
            self.work_window.update_data(self.data)
        
        # Показываем результат
        if errors:
            error_msg = "\n".join(errors[:10])  # первые 10 ошибок
            if len(errors) > 10:
                error_msg += f"\n... и ещё {len(errors) - 10} ошибок"
            messagebox.showwarning("Ошибки в командах", 
                                   f"При выполнении команд произошли ошибки:\n\n{error_msg}")
        else:
            messagebox.showinfo("Успех", "Все команды выполнены успешно")
        
        # Обновляем статус
        if self.work_window:
            self.work_window.status_var.set(f"Выполнены команды из {os.path.basename(filename)}")
    
    def _on_data_changed(self, new_data: list):
        """Callback при изменении данных через команды"""
        self.data = new_data
        self.logger.log_info(f"Данные изменены через команды: {len(self.data)} записей")
    
    def _open_help(self):
        from view import HelpWindow
        HelpWindow(self.main_menu)
    
    def _quit(self):
        self.main_menu.quit()
        self.main_menu.destroy()
    
    def run(self):
        self.main_menu.mainloop()


if __name__ == "__main__":
    if os.name == 'nt':
        os.system('chcp 1251 > nul')
    
    app = Application()
    app.run()
