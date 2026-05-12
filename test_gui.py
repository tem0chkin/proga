#!/usr/bin/env python3
"""test_gui.py - Альтернативная версия без импорта из lab2"""

import unittest
import os
import tempfile
import re

# ===== ДУБЛИРУЕМ ФУНКЦИИ ВАЛИДАЦИИ ЗДЕСЬ =====
# (скопируйте функции из lab2.py)

def valid_date(date_str: str) -> bool:
    """Проверка корректности даты"""
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
        
        days_in_month = [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30,
                         31, 31, 30, 31, 30, 31]
        return day <= days_in_month[month - 1]
    except Exception:
        return False


def valid_plate_number(plate: str) -> bool:
    """Проверка номера автомобиля"""
    if not plate:
        return False
    pattern = r'^[АВЕКМНОРСТУХ]{1}\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$'
    return bool(re.match(pattern, plate.upper()))


class CarPass:
    """Класс фиксации проезда"""
    def __init__(self, date: str = "", plate_number: str = "") -> None:
        self.date = date
        self.plate_number = plate_number
    
    def __str__(self) -> str:
        return f"{self.date},{self.plate_number}"
    
    @classmethod
    def from_string(cls, line: str):
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


class FileManager:
    """Работа с файлами"""
    @staticmethod
    def load(filename: str):
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
        return data
    
    @staticmethod
    def save(filename: str, data):
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                for item in data:
                    file.write(f"{item}\n")
            return True
        except Exception:
            return False


# ===== ТЕСТЫ (те же самые) =====

class TestDateValidation(unittest.TestCase):
    def test_valid_dates(self):
        valid_dates = [
            "2025.05.11",
            "2024.02.29",
            "2000.12.31",
            "2099.01.01",
        ]
        for date in valid_dates:
            with self.subTest(date=date):
                self.assertTrue(valid_date(date))
    
    def test_invalid_dates(self):
        invalid_dates = [
            "2025.13.01",
            "2025.02.30",
            "25.05.11",
            "2025/05/11",
        ]
        for date in invalid_dates:
            with self.subTest(date=date):
                self.assertFalse(valid_date(date))


class TestPlateValidation(unittest.TestCase):
    def test_valid_plates(self):
        valid_plates = [
            "А123ВС77",
            "В456ОК777",
            "М789НР12",
        ]
        for plate in valid_plates:
            with self.subTest(plate=plate):
                self.assertTrue(valid_plate_number(plate))
    
    def test_invalid_plates(self):
        invalid_plates = [
            "A123BC77",
            "А1234ВС77",
            "А123ВС",
            "А123ГТ77",
        ]
        for plate in invalid_plates:
            with self.subTest(plate=plate):
                self.assertFalse(valid_plate_number(plate))


class TestCarPassClass(unittest.TestCase):
    def test_from_string_valid(self):
        cp = CarPass.from_string("2025.05.11,А123ВС77")
        self.assertIsNotNone(cp)
        self.assertEqual(cp.date, "2025.05.11")
        self.assertEqual(cp.plate_number, "А123ВС77")
    
    def test_from_string_invalid(self):
        cp = CarPass.from_string("2025.13.01,А123ВС77")
        self.assertIsNone(cp)


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        self.temp_file.close()
        self.filename = self.temp_file.name
    
    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
    
    def test_save_and_load(self):
        test_data = [CarPass("2025.05.11", "А123ВС77")]
        FileManager.save(self.filename, test_data)
        loaded = FileManager.load(self.filename)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].date, "2025.05.11")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("ЗАПУСК ТЕСТОВ (автономная версия)")
    print("="*50 + "\n")
    unittest.main(verbosity=2)
