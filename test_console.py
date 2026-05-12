#!/usr/bin/env python3
"""test_console.py - Автоматическое тестирование консольной версии"""

import subprocess
import sys
import os

def run_test(test_name, input_data, expected_output):
    """Запуск теста с передачей входных данных"""
    try:
        # Запускаем программу и передаём ей ввод
        result = subprocess.run(
            [sys.executable, "1laba.py"],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Проверяем наличие ожидаемого текста в выводе
        if expected_output in result.stdout:
            print(f"✓ {test_name} - ПРОЙДЕН")
            return True
        else:
            print(f"✗ {test_name} - НЕ ПРОЙДЕН")
            print(f"  Ожидалось: {expected_output}")
            print(f"  Получено: {result.stdout[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ {test_name} - ТАЙМАУТ")
        return False
    except Exception as e:
        print(f"✗ {test_name} - ОШИБКА: {e}")
        return False


def test_valid_date():
    """Тест проверки корректных дат"""
    # Эмулируем ввод: добавить запись -> ввести дату -> ввести номер -> выйти
    inputs = "1\n2025.05.11\nА123ВС77\n5\n"
    return run_test("Добавление корректной записи", inputs, "Фиксация добавлена")


def test_invalid_date():
    """Тест проверки некорректной даты"""
    inputs = "1\n2025.13.01\n2025.05.11\nА123ВС77\n5\n"
    return run_test("Проверка некорректной даты", inputs, "неверный формат даты")


def test_invalid_plate():
    """Тест проверки некорректного номера"""
    inputs = "1\n2025.05.11\nA123BC77\nА123ВС77\n5\n"
    return run_test("Проверка некорректного номера", inputs, "Ошибка")


def test_search_by_plate():
    """Тест поиска по номеру"""
    inputs = "1\n2025.05.11\nА123ВС77\n3\nА123ВС77\n5\n"
    return run_test("Поиск по номеру", inputs, "Дата проезда: 2025.05.11")


def test_search_not_found():
    """Тест поиска несуществующего номера"""
    inputs = "1\n2025.05.11\nА123ВС77\n3\nХ000ХХ00\n5\n"
    return run_test("Поиск несуществующего номера", inputs, "не найдено")


def test_exit():
    """Тест выхода из программы"""
    inputs = "5\n"
    return run_test("Выход из программы", inputs, "Программа завершена")


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*50)
    print("Запуск тестов для консольной версии")
    print("="*50 + "\n")
    
    tests = [
        ("Валидная дата", test_valid_date),
        ("Невалидная дата", test_invalid_date),
        ("Невалидный номер", test_invalid_plate),
        ("Поиск по номеру", test_search_by_plate),
        ("Поиск несуществующего", test_search_not_found),
        ("Выход из программы", test_exit),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- Тест: {name} ---")
        results.append(test_func())
    
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    print(f"Пройдено: {passed}/{total}")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print(f"⚠️ Не пройдено тестов: {total - passed}")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
