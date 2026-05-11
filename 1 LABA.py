import os
import re

class CarPass:
    def __init__(self, date="", plate_number=""):
        self.date = date
        self.plate_number = plate_number

# Проверка даты в формате ГГГГ.ММ.ДД
def valid_date(date):
    if len(date) != 10:
        return False
    if date[4] != '.' or date[7] != '.':
        return False
    
    for i in range(10):
        if i == 4 or i == 7:
            continue
        if not date[i].isdigit():
            return False
    
    year = int(date[0:4])
    if year < 2000 or year > 2100:
        return False
    
    month = int(date[5:7])
    if month < 1 or month > 12:
        return False
    
    day = int(date[8:10])
    if day < 1 or day > 31:
        return False
    
    return True

# Проверка формата номера автомобиля
def valid_plate_number(plate):
    # Российский формат: Буква, 3 цифры, 2 буквы, 2 или 3 цифры региона
    # Допустимые буквы: А, В, Е, К, М, Н, О, Р, С, Т, У, Х (русские)
    pattern = r'^[АВЕКМНОРСТУХ]{1}\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$'
    
    if re.match(pattern, plate.upper()):
        return True
    else:
        return False

def input_pass():
    p = CarPass()
    
    # Ввод даты с проверкой
    while True:
        p.date = input("Введите дату проезда (в формате ГГГГ.ММ.ДД): ")
        if valid_date(p.date):
            break
        print("Ошибка: неверный формат даты! Используйте ГГГГ.ММ.ДД (например: 2025.05.11)")
    
    # Ввод номера автомобиля с проверкой формата
    while True:
        p.plate_number = input("Введите номер автомобиля (формат: А123ВС77 или А123ВС777): ")
        if valid_plate_number(p.plate_number):
            p.plate_number = p.plate_number.upper()  # Приводим к верхнему регистру
            break
        print("Ошибка! Номер должен соответствовать формату:")
        print("  - Буква, затем 3 цифры, затем 2 буквы, затем 2 или 3 цифры")
        print("  - Допустимые буквы: А, В, Е, К, М, Н, О, Р, С, Т, У, Х")
        print("  - Примеры: А123ВС77, В456ОК777, М789НР12")
    
    return p

def show(pass_list):
    if not pass_list:
        print("Список фиксаций проезда пуст!")
        return
    
    print("\n=== Список всех фиксаций проезда автомобилей ===")
    print(f"{'Дата':<12} | Номер автомобиля")
    print("-" * 35)
    
    for p in pass_list:
        print(f"{p.date:<12} | {p.plate_number}")

def search_by_plate(pass_list, plate):
    found = False
    print(f"\n=== Результаты поиска по номеру '{plate.upper()}' ===")
    
    for p in pass_list:
        if p.plate_number == plate.upper():
            print(f"Дата проезда: {p.date}")
            found = True
    
    if not found:
        print(f"Фиксаций для номера '{plate}' не найдено.")

def search_by_date(pass_list, date):
    found = False
    print(f"\n=== Результаты поиска по дате '{date}' ===")
    
    for p in pass_list:
        if p.date == date:
            print(f"Номер автомобиля: {p.plate_number}")
            found = True
    
    if not found:
        print(f"Фиксаций для даты '{date}' не найдено.")

def main():
    if os.name == 'nt':
        os.system('chcp 1251 > nul')
    
    passes = []
    print("=== Программа фиксации проезда автомобилей ===")
    
    while True:
        print("\nМеню:")
        print("1. Добавить новую фиксацию проезда")
        print("2. Показать все фиксации")
        print("3. Поиск по номеру автомобиля")
        print("4. Поиск по дате")
        print("5. Выход")
        
        try:
            choice = int(input("Выберите действие (1-5): "))
        except ValueError:
            print("Ошибка: введите число!")
            continue
        
        if choice == 1:
            print("\n--- Добавление новой фиксации проезда ---")
            passes.append(input_pass())
            print("✓ Фиксация добавлена!")
        
        elif choice == 2:
            show(passes)
        
        elif choice == 3:
            if not passes:
                print("Сначала добавьте хотя бы одну фиксацию!")
                continue
            plate = input("Введите номер автомобиля для поиска: ")
            search_by_plate(passes, plate)
        
        elif choice == 4:
            if not passes:
                print("Сначала добавьте хотя бы одну фиксацию!")
                continue
            while True:
                date = input("Введите дату для поиска (в формате ГГГГ.ММ.ДД): ")
                if valid_date(date):
                    search_by_date(passes, date)
                    break
                print("Ошибка: неверный формат даты! Используйте ГГГГ.ММ.ДД")
        
        elif choice == 5:
            print("Программа завершена.")
            break
        
        else:
            print("Неверный выбор! Выберите от 1 до 5.")

if __name__ == "__main__":
    main()
