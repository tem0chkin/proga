"""models.py - Модели данных, валидация и работа с файлами"""

import re
from typing import List, Optional

# ========== КОНСТАНТЫ ==========
DEFAULT_FILENAME = "car_passes.txt"
DATE_FORMAT = "ГГГГ.ММ.ДД"
DATE_EXAMPLE = "2025.05.11"
PLATE_PATTERN = r'^[АВЕКМНОРСТУХ]{1}\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$'
VALID_PLATE_LETTERS = "А, В, Е, К, М, Н, О, Р, С, Т, У, Х"

# ========== ВАЛИДАЦИЯ ==========
def valid_date(date_str: str) -> bool:
    """Проверка корректности даты в формате ГГГГ.ММ.ДД"""
    if len(date_str) != 10 or date_str[4] != '.' or date_str[7] != '.':
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
        if year < 2000 or year > 2100 or month < 1 or month > 12 or day < 1 or day > 31:
            return False
        days_in_month = [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30,
                         31, 31, 30, 31, 30, 31]
        return day <= days_in_month[month - 1]
    except Exception:
        return False

def valid_plate_number(plate: str) -> bool:
    """Проверка корректности номера автомобиля"""
    if not plate:
        return False
    return bool(re.match(PLATE_PATTERN, plate.upper()))

# ========== КЛАСС МОДЕЛИ ==========
class CarPass:
    """Фиксация проезда автомобиля"""
    
    def __init__(self, date: str = "", plate_number: str = "") -> None:
        self.date = date
        self.plate_number = plate_number
    
    def __str__(self) -> str:
        return f"{self.date},{self.plate_number}"
    
    @classmethod
    def from_string(cls, line: str) -> Optional['CarPass']:
        try:
            parts = [x.strip() for x in line.strip().split(',')]
            if len(parts) != 2:
                return None
            date_str, plate_str = parts
            if not valid_date(date_str) or not valid_plate_number(plate_str):
                return None
            return cls(date_str, plate_str.upper())
        except Exception:
            return None

# ========== РАБОТА С ФАЙЛАМИ ==========
class FileManager:
    @staticmethod
    def load(filename: str) -> List[CarPass]:
        data = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        cp = CarPass.from_string(line)
                        if cp:
                            data.append(cp)
        except FileNotFoundError:
            pass
        return data
    
    @staticmethod
    def save(filename: str, data: List[CarPass]) -> bool:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(f"{item}\n")
            return True
        except Exception:
            return False
