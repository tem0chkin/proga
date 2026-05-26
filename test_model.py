"""
test_model.py - Модульные тесты для модели программы
Запуск: python -m pytest tests/test_model.py
     или: python tests/test_model.py
"""

import unittest
import os
import tempfile
from model import CarPass, Validation, FileManager, Logger


class TestValidation(unittest.TestCase):
    """Тесты для валидации"""
    
    def test_valid_dates(self):
        """Проверка корректных дат"""
        valid_dates = [
            "2025.05.11",
            "2024.02.29",  # Високосный год
            "2000.12.31",
            "2099.01.01",
            "2023.01.15",
        ]
        for date in valid_dates:
            with self.subTest(date=date):
                is_valid, error = Validation.valid_date(date)
                self.assertTrue(is_valid, f"Дата {date} должна быть корректной. Ошибка: {error}")
    
    def test_invalid_dates_formats(self):
        """Проверка некорректных форматов даты"""
        invalid_dates = [
            ("25.05.11", "короткая"),
            ("2025/05/11", "разделители"),
            ("2025.5.11", "месяц без нуля"),
            ("2025.05.1", "день без нуля"),
        ]
        for date, reason in invalid_dates:
            with self.subTest(date=date, reason=reason):
                is_valid, error = Validation.valid_date(date)
                self.assertFalse(is_valid, f"Дата {date} должна быть некорректной ({reason})")
    
    def test_invalid_dates_values(self):
        """Проверка несуществующих дат"""
        invalid_dates = [
            ("2025.13.01", "месяц 13"),
            ("2025.00.01", "месяц 0"),
            ("2025.04.31", "30 дней в апреле"),
            ("2025.02.30", "30 февраля"),
            ("2025.02.29", "2025 не високосный"),
            ("2023.02.29", "2023 не високосный"),
        ]
        for date, reason in invalid_dates:
            with self.subTest(date=date, reason=reason):
                is_valid, error = Validation.valid_date(date)
                self.assertFalse(is_valid, f"Дата {date} должна быть некорректной ({reason})")
    
    def test_leap_years(self):
        """Проверка високосных годов"""
        # Високосные
        self.assertTrue(Validation.valid_date("2024.02.29")[0])
        self.assertTrue(Validation.valid_date("2000.02.29")[0])
        self.assertTrue(Validation.valid_date("2020.02.29")[0])
        
        # Не високосные
        self.assertFalse(Validation.valid_date("2023.02.29")[0])
        self.assertFalse(Validation.valid_date("1900.02.29")[0])
    
    def test_valid_plates(self):
        """Проверка корректных номеров"""
        valid_plates = [
            "А123ВС77",
            "В456ОК777",
            "М789НР12",
            "К001АА99",
            "Т999УХ777",
            "О777ОО77",
        ]
        for plate in valid_plates:
            with self.subTest(plate=plate):
                is_valid, error = Validation.valid_plate_number(plate)
                self.assertTrue(is_valid, f"Номер {plate} должен быть корректным. Ошибка: {error}")
    
    def test_invalid_plates_letters(self):
        """Проверка номеров с недопустимыми буквами"""
        invalid_plates = [
            ("Г123ВС77", "буква Г"),
            ("А123ГТ77", "буква Г в середине"),
            ("Л123ПР77", "недопустимые буквы"),
            ("A123BC77", "латиница"),
        ]
        for plate, reason in invalid_plates:
            with self.subTest(plate=plate, reason=reason):
                is_valid, error = Validation.valid_plate_number(plate)
                self.assertFalse(is_valid, f"Номер {plate} должен быть некорректным ({reason})")
    
    def test_invalid_plates_format(self):
        """Проверка номеров с неправильным форматом"""
        invalid_plates = [
            ("А123ВС", "нет региона"),
            ("А1234ВС77", "4 цифры"),
            ("А12ВС77", "2 цифры"),
            ("", "пустой"),
        ]
        for plate, reason in invalid_plates:
            with self.subTest(plate=plate, reason=reason):
                is_valid, error = Validation.valid_plate_number(plate)
                self.assertFalse(is_valid, f"Номер {plate} должен быть некорректным ({reason})")


class TestCarPass(unittest.TestCase):
    """Тесты для класса CarPass"""
    
    def test_create_car_pass(self):
        """Создание объекта"""
        cp = CarPass("2025.05.11", "А123ВС77")
        self.assertEqual(cp.date, "2025.05.11")
        self.assertEqual(cp.plate_number, "А123ВС77")
    
    def test_string_representation(self):
        """Строковое представление"""
        cp = CarPass("2025.05.11", "А123ВС77")
        self.assertEqual(str(cp), "2025.05.11,А123ВС77")
    
    def test_from_string_valid(self):
        """Создание из корректной строки"""
        cp = CarPass.from_string("2025.05.11,А123ВС77")
        self.assertIsNotNone(cp)
        self.assertEqual(cp.date, "2025.05.11")
        self.assertEqual(cp.plate_number, "А123ВС77")
    
    def test_from_string_invalid_dates(self):
        """Создание из строки с некорректной датой"""
        cp = CarPass.from_string("2025.13.01,А123ВС77")
        self.assertIsNone(cp)
    
    def test_from_string_invalid_plates(self):
        """Создание из строки с некорректным номером"""
        cp = CarPass.from_string("2025.05.11,A123BC77")
        self.assertIsNone(cp)
    
    def test_from_string_wrong_format(self):
        """Создание из строки с неверным форматом"""
        cp = CarPass.from_string("2025.05.11,А123ВС77,лишнее")
        self.assertIsNone(cp)
        
        cp = CarPass.from_string("только одна часть")
        self.assertIsNone(cp)
        
        cp = CarPass.from_string("")
        self.assertIsNone(cp)
    
    def test_equality(self):
        """Сравнение объектов"""
        cp1 = CarPass("2025.05.11", "А123ВС77")
        cp2 = CarPass("2025.05.11", "А123ВС77")
        cp3 = CarPass("2025.05.12", "В456ОК777")
        
        self.assertEqual(cp1, cp2)
        self.assertNotEqual(cp1, cp3)


class TestFileManager(unittest.TestCase):
    """Тесты для FileManager"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False,
            encoding='utf-8'
        )
        self.temp_file.close()
        self.filename = self.temp_file.name
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.filename):
            os.remove(self.filename)
    
    def test_save_and_load_empty(self):
        """Сохранение и загрузка пустого списка"""
        result = FileManager.save(self.filename, [])
        self.assertTrue(result)
        
        loaded = FileManager.load(self.filename)
        self.assertEqual(loaded, [])
    
    def test_save_and_load_one_record(self):
        """Сохранение и загрузка одной записи"""
        test_data = [CarPass("2025.05.11", "А123ВС77")]
        
        FileManager.save(self.filename, test_data)
        loaded = FileManager.load(self.filename)
        
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0], test_data[0])
    
    def test_save_and_load_multiple_records(self):
        """Сохранение и загрузка нескольких записей"""
        test_data = [
            CarPass("2025.05.11", "А123ВС77"),
            CarPass("2025.05.12", "В456ОК777"),
            CarPass("2025.05.13", "М789НР12"),
        ]
        
        FileManager.save(self.filename, test_data)
        loaded = FileManager.load(self.filename)
        
        self.assertEqual(len(loaded), 3)
        for i in range(3):
            self.assertEqual(loaded[i], test_data[i])
    
    def test_load_corrupted_file(self):
        """Загрузка файла с некорректными строками"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write("2025.05.11,А123ВС77\n")
            f.write("bad,data,line\n")
            f.write("2025.13.01,В456ОК777\n")
            f.write("2025.05.13,М789НР12\n")
        
        loaded = FileManager.load(self.filename)
        # Должны загрузиться только корректные строки
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].date, "2025.05.11")
        self.assertEqual(loaded[1].date, "2025.05.13")
    
    def test_load_nonexistent_file(self):
        """Загрузка несуществующего файла"""
        loaded = FileManager.load("nonexistent_file_12345.txt")
        self.assertEqual(loaded, [])


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ЗАПУСК МОДУЛЬНЫХ ТЕСТОВ ДЛЯ МОДЕЛИ")
    print("="*60 + "\n")
    unittest.main(verbosity=2)
