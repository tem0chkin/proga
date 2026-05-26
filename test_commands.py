"""
test_commands.py - Тесты для обработки команд (лаба 4)
"""

import unittest
import os
import tempfile
from model import CarPass, CommandProcessor, Logger


class TestCommandProcessor(unittest.TestCase):
    """Тесты для CommandProcessor"""
    
    def setUp(self):
        self.logger = Logger()
        self.test_data = [
            CarPass("2025.05.11", "А123ВС77"),
            CarPass("2025.05.12", "В456ОК777"),
            CarPass("2025.05.13", "М789НР12"),
            CarPass("2025.05.14", "К001АА99"),
        ]
    
    def test_parse_condition_equal_date(self):
        """Проверка условия date == значение"""
        cp = CarPass("2025.05.11", "А123ВС77")
        self.assertTrue(CommandProcessor.parse_condition('date == "2025.05.11"', cp))
        self.assertFalse(CommandProcessor.parse_condition('date == "2025.05.12"', cp))
    
    def test_parse_condition_equal_plate(self):
        """Проверка условия plate == значение"""
        cp = CarPass("2025.05.11", "А123ВС77")
        self.assertTrue(CommandProcessor.parse_condition('plate == "А123ВС77"', cp))
        self.assertFalse(CommandProcessor.parse_condition('plate == "В456ОК777"', cp))
    
    def test_parse_condition_not_equal(self):
        """Проверка условия !="""
        cp = CarPass("2025.05.11", "А123ВС77")
        self.assertTrue(CommandProcessor.parse_condition('date != "2025.05.12"', cp))
        self.assertFalse(CommandProcessor.parse_condition('date != "2025.05.11"', cp))
    
    def test_parse_condition_contains(self):
        """Проверка условия contains"""
        cp = CarPass("2025.05.11", "А123ВС77")
        self.assertTrue(CommandProcessor.parse_condition('date contains "05"', cp))
        self.assertTrue(CommandProcessor.parse_condition('plate contains "ВС"', cp))
        self.assertFalse(CommandProcessor.parse_condition('date contains "06"', cp))
    
    def test_parse_condition_less_than(self):
        """Проверка условия < (меньше)"""
        cp1 = CarPass("2025.05.11", "А123ВС77")
        cp2 = CarPass("2025.05.13", "М789НР12")
        self.assertTrue(CommandProcessor.parse_condition('date < "2025.05.12"', cp1))
        self.assertFalse(CommandProcessor.parse_condition('date < "2025.05.12"', cp2))
    
    def test_parse_condition_greater_than(self):
        """Проверка условия > (больше)"""
        cp1 = CarPass("2025.05.11", "А123ВС77")
        cp2 = CarPass("2025.05.13", "М789НР12")
        self.assertTrue(CommandProcessor.parse_condition('date > "2025.05.12"', cp2))
        self.assertFalse(CommandProcessor.parse_condition('date > "2025.05.12"', cp1))
    
    def test_process_add_valid(self):
        """Добавление корректной записи"""
        new_data, errors = CommandProcessor.process_add(
            self.test_data.copy(), "2025.05.15,Т999УХ777", self.logger
        )
        self.assertEqual(len(new_data), 5)
        self.assertEqual(len(errors), 0)
    
    def test_process_add_invalid(self):
        """Добавление некорректной записи"""
        new_data, errors = CommandProcessor.process_add(
            self.test_data.copy(), "2025.13.01,А123ВС77", self.logger
        )
        self.assertEqual(len(new_data), 4)
        self.assertEqual(len(errors), 1)
    
    def test_process_rem_by_date(self):
        """Удаление по дате"""
        new_data, errors = CommandProcessor.process_rem(
            self.test_data.copy(), 'date == "2025.05.11"', self.logger
        )
        self.assertEqual(len(new_data), 3)
        self.assertNotIn(CarPass("2025.05.11", "А123ВС77"), new_data)
    
    def test_process_rem_by_plate_contains(self):
        """Удаление по содержанию в номере"""
        new_data, errors = CommandProcessor.process_rem(
            self.test_data.copy(), 'plate contains "ВС"', self.logger
        )
        self.assertEqual(len(new_data), 3)
    
    def test_process_rem_by_date_greater(self):
        """Удаление с условием date >"""
        new_data, errors = CommandProcessor.process_rem(
            self.test_data.copy(), 'date > "2025.05.12"', self.logger
        )
        self.assertEqual(len(new_data), 2)  # остаются 05.11 и 05.12
    
    def test_process_save(self):
        """Сохранение в файл"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name
        
        success, errors = CommandProcessor.process_save(self.test_data, temp_file, self.logger)
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(temp_file))
        
        # Очистка
        os.remove(temp_file)
    
    def test_process_commands_file(self):
        """Обработка файла с несколькими командами"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("ADD 2025.05.15,Т999УХ777\n")
            f.write("REM date == \"2025.05.11\"\n")
            f.write("SAVE test_output.txt\n")
            temp_file = f.name
        
        new_data, errors = CommandProcessor.process_commands_file(
            self.test_data.copy(), temp_file
        )
        
        # Проверяем результат: добавили 1, удалили 1, осталось 4
        self.assertEqual(len(new_data), 4)
        self.assertEqual(len(errors), 0)
        
        # Очистка
        os.remove(temp_file)
        if os.path.exists("test_output.txt"):
            os.remove("test_output.txt")
    
    def test_process_commands_file_with_errors(self):
        """Обработка файла с ошибочными командами"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("ADD 2025.13.01,А123ВС77\n")  # Неверная дата
            f.write("UNKNOWN_COMMAND bla-bla\n")
            f.write("REM invalid condition\n")
            temp_file = f.name
        
        new_data, errors = CommandProcessor.process_commands_file(
            self.test_data.copy(), temp_file
        )
        
        # Проверяем, что ошибки записаны
        self.assertGreater(len(errors), 0)
        
        # Очистка
        os.remove(temp_file)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ТЕСТЫ ОБРАБОТЧИКА КОМАНД (ЛАБА 4)")
    print("="*60 + "\n")
    unittest.main(verbosity=2)
