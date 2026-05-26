"""
model.py - Модель для программы фиксации проезда автомобилей

Содержит:
- Класс CarPass (данные о проезде)
- Класс Validation (валидация даты и номера)
- Класс FileManager (работа с файлами)
- Класс Logger (логирование ошибок)
- Класс CommandProcessor (обработка команд ADD, REM, SAVE) - НОВЫЙ
"""

import re
import os
import logging
from typing import List, Optional, Tuple, Callable

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
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        self.logger = logging.getLogger("CarPassLogger")
        self.logger.setLevel(logging.ERROR)
        self.logger.handlers.clear()
        
        file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log_error(self, message: str):
        self.logger.error(message)
    
    def log_warning(self, message: str):
        self.logger.warning(message)
    
    def log_info(self, message: str):
        self.logger.info(message)


# ============================================================
# Валидация
# ============================================================

class Validation:
    """Класс для валидации данных"""
    
    @staticmethod
    def valid_date(date_str: str) -> Tuple[bool, Optional[str]]:
        if len(date_str) != 10:
            return False, f"Неверная длина даты: '{date_str}'"
        if date_str[4] != '.' or date_str[7] != '.':
            return False, f"Неверные разделители: '{date_str}'"
        
        for i in range(10):
            if i in (4, 7):
                continue
            if not date_str[i].isdigit():
                return False, f"Неверный символ в дате: '{date_str}'"
        
        try:
            year = int(date_str[0:4])
            month = int(date_str[5:7])
            day = int(date_str[8:10])
            
            if year < 2000 or year > 2100:
                return False, f"Год {year} вне диапазона 2000-2100"
            if month < 1 or month > 12:
                return False, f"Месяц {month} вне диапазона 1-12"
            if day < 1 or day > 31:
                return False, f"День {day} вне диапазона 1-31"
            
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
        if not plate:
            return False, "Номер автомобиля пуст"
        
        plate_upper = plate.upper()
        
        if not re.match(PLATE_PATTERN, plate_upper):
            if len(plate_upper) < 7:
                return False, f"Номер '{plate}' слишком короткий"
            if len(plate_upper) > 10:
                return False, f"Номер '{plate}' слишком длинный"
            
            first_char = plate_upper[0]
            if first_char not in VALID_PLATE_LETTERS.replace(', ', ''):
                return False, f"Первая буква '{first_char}' недопустима"
            
            if not plate_upper[1:4].isdigit():
                return False, f"После буквы должны идти 3 цифры"
            
            return False, f"Номер '{plate}' не соответствует формату"
        
        return True, None


# ============================================================
# Класс CarPass
# ============================================================

class CarPass:
    """Класс, представляющий одну фиксацию проезда автомобиля."""
    
    def __init__(self, date: str = "", plate_number: str = "") -> None:
        self.date = date
        self.plate_number = plate_number.upper()
    
    def __str__(self) -> str:
        return f"{self.date},{self.plate_number}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, CarPass):
            return False
        return self.date == other.date and self.plate_number == other.plate_number
    
    @classmethod
    def from_string(cls, line: str) -> Optional['CarPass']:
        logger = Logger()
        
        try:
            line = line.strip()
            if not line:
                logger.log_warning(f"Пустая строка в файле")
                return None
            
            parts = [x.strip() for x in line.split(',')]
            if len(parts) != 2:
                logger.log_error(f"Неверный формат строки: '{line}'")
                return None
            
            date_str, plate_str = parts
            
            is_valid, error_msg = Validation.valid_date(date_str)
            if not is_valid:
                logger.log_error(f"Ошибка в дате '{date_str}': {error_msg}")
                return None
            
            is_valid, error_msg = Validation.valid_plate_number(plate_str)
            if not is_valid:
                logger.log_error(f"Ошибка в номере '{plate_str}': {error_msg}")
                return None
            
            return cls(date_str, plate_str.upper())
        except Exception as e:
            logger.log_error(f"Неожиданная ошибка при парсинге строки '{line}': {e}")
            return None


# ============================================================
# FileManager
# ============================================================

class FileManager:
    """Класс для работы с файловым хранилищем"""
    
    @staticmethod
    def load(filename: str) -> List[CarPass]:
        data = []
        logger = Logger()
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            for line_num, line in enumerate(lines, 1):
                car_pass = CarPass.from_string(line)
                if car_pass:
                    data.append(car_pass)
        except FileNotFoundError:
            logger.log_warning(f"Файл {filename} не найден")
        except Exception as e:
            logger.log_error(f"Ошибка при чтении файла {filename}: {e}")
        
        return data
    
    @staticmethod
    def save(filename: str, data: List[CarPass]) -> bool:
        logger = Logger()
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                for item in data:
                    file.write(f"{item}\n")
            logger.log_info(f"Сохранено {len(data)} записей в {filename}")
            return True
        except Exception as e:
            logger.log_error(f"Ошибка при сохранении файла {filename}: {e}")
            return False


# ============================================================
# CommandProcessor (НОВЫЙ для лабы 4)
# ============================================================

class CommandProcessor:
    """Класс для обработки команд ADD, REM, SAVE из файла"""
    
    @staticmethod
    def parse_condition(condition: str, car_pass: CarPass) -> bool:
        """
        Парсит условие и проверяет, удовлетворяет ли ему объект CarPass
        
        Поддерживаемые условия:
        - date == "2025.05.11"
        - date < "2025.05.11"
        - date > "2025.05.11"
        - plate == "А123ВС77"
        - plate != "А123ВС77"
        - date contains "05" (если подстрока в дате)
        - plate contains "ВС"
        """
        condition = condition.strip()
        
        # Разбор условия: поле, оператор, значение
        operators = ['==', '!=', 'contains', '<', '>']
        operator_found = None
        
        for op in operators:
            if op in condition:
                operator_found = op
                break
        
        if not operator_found:
            return False
        
        # Разделяем по оператору
        parts = condition.split(operator_found, 1)
        if len(parts) != 2:
            return False
        
        field = parts[0].strip().lower()
        value = parts[1].strip().strip('"').strip("'")
        
        # Получаем значение из объекта CarPass
        if field == 'date':
            obj_value = car_pass.date
        elif field == 'plate':
            obj_value = car_pass.plate_number
        else:
            return False
        
        # Применяем оператор
        try:
            if operator_found == '==':
                return obj_value == value
            elif operator_found == '!=':
                return obj_value != value
            elif operator_found == 'contains':
                return value in obj_value
            elif operator_found == '<':
                return obj_value < value
            elif operator_found == '>':
                return obj_value > value
        except Exception:
            return False
        
        return False
    
    @staticmethod
    def process_add(data: List[CarPass], args: str, logger: Logger) -> Tuple[List[CarPass], List[str]]:
        """
        Обработка команды ADD
        
        Формат: ADD date,plate_number
        Пример: ADD 2025.05.11,А123ВС77
        """
        errors = []
        args = args.strip()
        
        new_car = CarPass.from_string(args)
        if new_car:
            data.append(new_car)
            logger.log_info(f"ADD: добавлена запись {args}")
        else:
            error = f"ADD: не удалось добавить запись '{args}'"
            errors.append(error)
            logger.log_error(error)
        
        return data, errors
    
    @staticmethod
    def process_rem(data: List[CarPass], condition: str, logger: Logger) -> Tuple[List[CarPass], List[str]]:
        """
        Обработка команды REM
        
        Формат: REM <условие>
        Пример: REM date == "2025.05.11"
        Пример: REM plate contains "ВС"
        """
        errors = []
        original_count = len(data)
        new_data = []
        
        for item in data:
            if not CommandProcessor.parse_condition(condition, item):
                new_data.append(item)
        
        removed_count = original_count - len(new_data)
        logger.log_info(f"REM: удалено {removed_count} записей по условию '{condition}'")
        
        return new_data, errors
    
    @staticmethod
    def process_save(data: List[CarPass], filename: str, logger: Logger) -> Tuple[bool, List[str]]:
        """
        Обработка команды SAVE
        
        Формат: SAVE <путь_к_файлу>
        Пример: SAVE file.txt
        """
        errors = []
        filename = filename.strip()
        
        if FileManager.save(filename, data):
            logger.log_info(f"SAVE: сохранено {len(data)} записей в {filename}")
            return True, errors
        else:
            error = f"SAVE: не удалось сохранить файл {filename}"
            errors.append(error)
            logger.log_error(error)
            return False, errors
    
    @staticmethod
    def process_commands_file(data: List[CarPass], filename: str, on_data_changed: Callable = None) -> Tuple[List[CarPass], List[str]]:
        """
        Обработка файла с командами
        
        Args:
            data: текущий список данных
            filename: путь к файлу с командами
            on_data_changed: callback при изменении данных
        
        Returns:
            (обновлённые данные, список ошибок)
        """
        logger = Logger()
        errors = []
        current_data = data.copy()
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Разбор команды
                parts = line.split(' ', 1)
                if len(parts) < 1:
                    errors.append(f"Строка {line_num}: пустая команда")
                    continue
                
                cmd = parts[0].upper()
                args = parts[1] if len(parts) > 1 else ""
                
                if cmd == 'ADD':
                    current_data, cmd_errors = CommandProcessor.process_add(current_data, args, logger)
                    errors.extend(cmd_errors)
                
                elif cmd == 'REM':
                    current_data, cmd_errors = CommandProcessor.process_rem(current_data, args, logger)
                    errors.extend(cmd_errors)
                
                elif cmd == 'SAVE':
                    _, cmd_errors = CommandProcessor.process_save(current_data, args, logger)
                    errors.extend(cmd_errors)
                
                else:
                    error = f"Строка {line_num}: неизвестная команда '{cmd}'"
                    errors.append(error)
                    logger.log_error(error)
            
            if on_data_changed and current_data != data:
                on_data_changed(current_data)
            
        except FileNotFoundError:
            error = f"Файл команд {filename} не найден"
            errors.append(error)
            logger.log_error(error)
        except Exception as e:
            error = f"Ошибка при чтении файла команд: {e}"
            errors.append(error)
            logger.log_error(error)
        
        return current_data, errors
