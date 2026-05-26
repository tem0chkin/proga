"""
model.py - Модель для программы фиксации проезда автомобилей

Содержит:
- Класс CarPass (данные о проезде)
- Класс Validation (валидация даты и номера)
- Класс FileManager (работа с файлами)
- Класс Logger (логирование ошибок)
"""

import re
import os
import logging
from datetime import datetime
from typing import List, Optional, Tuple


# ============================================================
# Константы
# ============================================================

DATE_FORMAT = "ГГГГ.ММ.ДД"
DATE_EXAMPLE = "2025.05.11"
PLATE_PATTERN = r'^[АВЕКМНОРСТУХ]{1}\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$'
VALID_PLATE_LETTERS = "А, В, Е, К, М, Н, О, Р, С, Т, У, Х"
DEFAULT_FILENAME = "car_passes.txt"
LOG_FILENAME = "error.log"


# ============================================================
# Логирование ошибок
# ============================================================

class Logger:
    """Класс для логирования ошибок в файл"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton паттерн - один логгер на всю программу"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Настройка логгера"""
        self.logger = logging.getLogger("CarPassLogger")
        self.logger.setLevel(logging.ERROR)
        
        # Очищаем старые обработчики
        self.logger.handlers.clear()
        
        # Файловый обработчик
        file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        
        # Формат лога: время - уровень - сообщение
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_error(self, message: str):
        """Запись ошибки в лог"""
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """Запись предупреждения в лог"""
        self.logger.warning(message)


# ============================================================
# Валидация
# ============================================================

class Validation:
    """Класс для валидации данных"""
    
    @staticmethod
    def valid_date(date_str: str) -> Tuple[bool, Optional[str]]:
        """
        Проверка корректности даты в формате ГГГГ.ММ.ДД
        
        Returns:
            (True, None) если дата корректна
            (False, сообщение_об_ошибке) если некорректна
        """
        # Проверка длины
        if len(date_str) != 10:
            return False, f"Неверная длина даты: '{date_str}' (ожидается 10 символов)"
        
        # Проверка разделителей
        if date_str[4] != '.' or date_str[7] != '.':
            return False, f"Неверные разделители: '{date_str}' (ожидаются точки на позициях 4 и 7)"
        
        # Проверка что все символы кроме разделителей - цифры
        for i in range(10):
            if i in (4, 7):
                continue
            if not date_str[i].isdigit():
                return False, f"Неверный символ в дате: '{date_str}' (ожидаются цифры)"
        
        try:
            year = int(date_str[0:4])
            month = int(date_str[5:7])
            day = int(date_str[8:10])
            
            # Проверка года
            if year < 2000 or year > 2100:
                return False, f"Год {year} вне диапазона 2000-2100"
            
            # Проверка месяца
            if month < 1 or month > 12:
                return False, f"Месяц {month} вне диапазона 1-12"
            
            # Проверка дня
            if day < 1 or day > 31:
                return False, f"День {day} вне диапазона 1-31"
            
            # Проверка количества дней в месяце
            days_in_month = [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30,
                             31, 31, 30, 31, 30, 31]
            if day <= days_in_month[month - 1]:
                return True, None
            else:
                max_day = days_in_month[month - 1]
                return False, f"В {month}-м месяце {max_day} дней, а указан {day}"
                
        except Exception as e:
            return False, f"Ошибка парсинга даты: {e}"
    
    @staticmethod
    def valid_plate_number(plate: str) -> Tuple[bool, Optional[str]]:
        """
        Проверка корректности номера автомобиля
        
        Returns:
            (True, None) если номер корректен
            (False, сообщение_об_ошибке) если некорректен
        """
        if not plate:
            return False, "Номер автомобиля пуст"
        
        plate_upper = plate.upper()
        
        if not re.match(PLATE_PATTERN, plate_upper):
            # Детальный разбор ошибки
            if len(plate_upper) < 7:
                return False, f"Номер '{plate}' слишком короткий"
            if len(plate_upper) > 10:
                return False, f"Номер '{plate}' слишком длинный"
            
            # Проверка первой буквы
            first_char = plate_upper[0]
            if first_char not in VALID_PLATE_LETTERS.replace(', ', ''):
                return False, f"Первая буква '{first_char}' недопустима. Допустимые: {VALID_PLATE_LETTERS}"
            
            # Проверка, что дальше идут цифры
            if not plate_upper[1:4].isdigit():
                return False, f"После буквы должны идти 3 цифры, а не '{plate_upper[1:4]}'"
            
            return False, f"Номер '{plate}' не соответствует формату. Пример: А123ВС77"
        
        return True, None


# ============================================================
# Класс CarPass (Модель данных)
# ============================================================

class CarPass:
    """Класс, представляющий одну фиксацию проезда автомобиля."""
    
    def __init__(self, date: str = "", plate_number: str = "") -> None:
        """Инициализация фиксации проезда"""
        self.date = date
        self.plate_number = plate_number.upper()
    
    def __str__(self) -> str:
        return f"{self.date},{self.plate_number}"
    
    def __eq__(self, other) -> bool:
        """Для сравнения объектов в тестах"""
        if not isinstance(other, CarPass):
            return False
        return self.date == other.date and self.plate_number == other.plate_number
    
    @classmethod
    def from_string(cls, line: str) -> Optional['CarPass']:
        """
        Создание объекта из строки файла.
        При ошибке возвращает None и записывает в лог
        """
        logger = Logger()
        
        try:
            line = line.strip()
            if not line:
                logger.log_warning(f"Пустая строка в файле")
                return None
            
            parts = [x.strip() for x in line.split(',')]
            if len(parts) != 2:
                logger.log_error(f"Неверный формат строки: '{line}' (ожидается 2 части, получено {len(parts)})")
                return None
            
            date_str, plate_str = parts
            
            # Валидация даты
            is_valid, error_msg = Validation.valid_date(date_str)
            if not is_valid:
                logger.log_error(f"Ошибка в дате '{date_str}': {error_msg}")
                return None
            
            # Валидация номера
            is_valid, error_msg = Validation.valid_plate_number(plate_str)
            if not is_valid:
                logger.log_error(f"Ошибка в номере '{plate_str}': {error_msg}")
                return None
            
            return cls(date_str, plate_str.upper())
            
        except Exception as e:
            logger.log_error(f"Неожиданная ошибка при парсинге строки '{line}': {e}")
            return None


# ============================================================
# FileManager (Работа с файлами)
# ============================================================

class FileManager:
    """Класс для работы с файловым хранилищем"""
    
    @staticmethod
    def load(filename: str) -> List[CarPass]:
        """
        Загрузка данных из файла.
        Некорректные строки пропускаются, информация о них пишется в лог
        """
        data = []
        logger = Logger()
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            if not lines:
                logger.log_warning(f"Файл {filename} пуст")
            
            for line_num, line in enumerate(lines, 1):
                car_pass = CarPass.from_string(line)
                if car_pass:
                    data.append(car_pass)
                # else: ошибка уже залогирована в from_string
                    
        except FileNotFoundError:
            logger.log_warning(f"Файл {filename} не найден, будет создан при сохранении")
        except PermissionError:
            logger.log_error(f"Нет прав на чтение файла {filename}")
        except Exception as e:
            logger.log_error(f"Ошибка при чтении файла {filename}: {e}")
        
        return data
    
    @staticmethod
    def save(filename: str, data: List[CarPass]) -> bool:
        """Сохранение данных в файл"""
        logger = Logger()
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                for item in data:
                    file.write(f"{item}\n")
            return True
        except PermissionError:
            logger.log_error(f"Нет прав на запись в файл {filename}")
            return False
        except Exception as e:
            logger.log_error(f"Ошибка при сохранении файла {filename}: {e}")
            return False
