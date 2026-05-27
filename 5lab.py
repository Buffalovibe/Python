import re
import csv
from collections import Counter

# ==================== ЧАСТЬ 1: Работа с текстовым файлом ====================

def part1_task1_ru(text):
    """Вариант 1: Все слова от 3 до 5 букв"""
    words = re.findall(r'\b[а-яА-ЯёЁ]{3,5}\b', text)
    return words

def part1_task2_ru(text):
    """Вариант 2: Все слова, начинающиеся с большой буквы"""
    words = re.findall(r'\b[А-ЯЁ][а-яё]*\b', text)
    return words

def part1_task3_ru(text):
    """Вариант 3: Все слова, после которых стоят запятая"""
    words = re.findall(r'\b[а-яА-ЯёЁ]+\b,', text)
    return [w[:-1] for w in words]  # удаляем запятую

def part1_task4_ru(text):
    """Вариант 4: Все слова, в которых есть дефис"""
    words = re.findall(r'\b[а-яА-ЯёЁ-]+-[а-яА-ЯёЁ-]+\b', text)
    return words

def part1_task5_ru(text):
    """Вариант 5: Все числа, целые и дробные"""
    numbers = re.findall(r'-?\d+[,.]?\d*', text)
    return numbers

def part1_task6_ru(text):
    """Вариант 6: Все числа больше 100"""
    numbers = re.findall(r'\b\d+\b', text)
    return [n for n in numbers if int(n) > 100]

def part1_task7_ru(text):
    """Вариант 7: Все слова, начинающиеся с буквы 'с'"""
    words = re.findall(r'\b[сС][а-яё]*\b', text)
    return words

def part1_task8_ru(text):
    """Вариант 8: Все отрицательные числа, целые и дробные"""
    numbers = re.findall(r'-\d+[,.]?\d*', text)
    return numbers

def part1_task9_ru(text):
    """Вариант 9: Все слова, заканчивающиеся на букву 'а'"""
    words = re.findall(r'\b[а-яА-ЯёЁ]+[аА]\b', text)
    return words

def part1_task10_ru(text):
    """Вариант 10: Все слова, после которых стоит любой символ пунктуации"""
    words = re.findall(r'\b[а-яА-ЯёЁ]+\b[.,!?;:]', text)
    return [w[:-1] for w in words]  # удаляем символ пунктуации

# ==================== ЧАСТЬ 2: Работа с HTML файлом ====================

def part2_task1(html):
    """Вариант 1: Все открывающие теги без повторений"""
    tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)\s*[^>]*>', html)
    return list(set(tags))

def part2_task2(html):
    """Вариант 2: Все закрывающие теги без повторений"""
    tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', html)
    return list(set(tags))

def part2_task3(html):
    """Вариант 3: Все ссылки"""
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    return links

def part2_task4(html):
    """Вариант 4: Все ссылки в домене .edu"""
    links = re.findall(r'href=["\']([^"\']*\.edu[^"\']*)["\']', html)
    return links

def part2_task5(html):
    """Вариант 5: Все строки, находящиеся в атрибуте .org/.edu тега"""
    strings = re.findall(r'(?:org|edu)["\']\s*[^>]*>([^<]+)', html)
    return strings

def part2_task6(html):
    """Вариант 6: Все ссылки на изображения"""
    images = re.findall(r'src=["\']([^"\']+\.(?:jpg|jpeg|png|gif|svg))["\']', html, re.IGNORECASE)
    return images

def part2_task7(html):
    """Вариант 7: Все заголовки статей"""
    titles = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', html)
    return titles

def part2_task8(html):
    """Вариант 8: Параметры используемых шрифтов: название, размер"""
    fonts = re.findall(r'font-family:\s*([^;]+);\s*font-size:\s*([^;]+);', html)
    return fonts

def part2_task9(html):
    """Вариант 9: Все названия классов"""
    classes = re.findall(r'class=["\']([^"\']+)["\']', html)
    # Разбиваем классы, если их несколько
    all_classes = []
    for cls in classes:
        all_classes.extend(cls.split())
    return list(set(all_classes))

def part2_task10(html):
    """Вариант 10: Количество пустых строк"""
    empty_lines = re.findall(r'\n\s*\n', html)
    return len(empty_lines)

# ==================== ЧАСТЬ 3: Приведение данных в порядок ====================

def part3_process_data(filename):
    """
    Читает файл с перепутанными данными и приводит их к формату:
    ID, фамилия, электронная почта, дата регистрации, сайт
    """
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Паттерны для поиска данных
    patterns = {
        'id': r'\b\d{1,5}\b',  # ID (число от 1 до 5 цифр)
        'surname': r'\b[А-ЯЁ][а-яё]+\b',  # Фамилия (начинается с большой буквы)
        'email': r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',  # Email
        'date': r'\b\d{2}[./-]\d{2}[./-]\d{4}\b',  # Дата (DD/MM/YYYY)
        'website': r'\b(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/\S*)?\b'  # Сайт
    }
    
    # Находим все данные
    data = {}
    for key, pattern in patterns.items():
        data[key] = re.findall(pattern, content)
    
    # Определяем минимальное количество записей
    min_length = min(len(v) for v in data.values())
    
    # Обрезаем все списки до минимальной длины
    for key in data:
        data[key] = data[key][:min_length]
    
    # Создаём таблицу
    table = []
    for i in range(min_length):
        row = [
            data['id'][i],
            data['surname'][i],
            data['email'][i],
            data['date'][i],
            data['website'][i]
        ]
        table.append(row)
    
    # Сохраняем в CSV файл
    output_file = 'task3_result.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Фамилия', 'Email', 'Дата регистрации', 'Сайт'])
        writer.writerows(table)
    
    print(f"Данные сохранены в файл: {output_file}")
    return table

# ==================== ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ ====================

def additional_task(filename):
    """
    Поиск скрытых данных в файле со случайными символами
    """
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Паттерны для поиска дат в разных форматах
    date_patterns = [
        r'\b\d{2}[./-]\d{2}[./-]\d{4}\b',  # DD/MM/YYYY
        r'\b\d{4}[./-]\d{2}[./-]\d{2}\b',  # YYYY/MM/DD
        r'\b\d{1,2}\s+(?:янв|фев|мар|апр|мая|июн|июл|авг|сен|окт|ноя|дек)\s+\d{4}\b'  # DD Month YYYY
    ]
    
    # Поиск email
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    
    # Поиск сайтов
    website_pattern = r'\b(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/\S*)?\b'
    
    # Собираем все данные
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, content))
    
    emails = re.findall(email_pattern, content)
    websites = re.findall(website_pattern, content)
    
    # Удаляем дубликаты и берем первые 5
    dates = list(dict.fromkeys(dates))[:5]
    emails = list(dict.fromkeys(emails))[:5]
    websites = list(dict.fromkeys(websites))[:5]
    
    print("=" * 50)
    print("ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ: Найденные данные")
    print("=" * 50)
    print(f"\nНайдено дат ({len(dates)}):")
    for date in dates:
        print(f"  - {date}")
    
    print(f"\nНайдено email ({len(emails)}):")
    for email in emails:
        print(f"  - {email}")
    
    print(f"\nНайдено сайтов ({len(websites)}):")
    for website in websites:
        print(f"  - {website}")
    
    return {
        'dates': dates,
        'emails': emails,
        'websites': websites
    }

# ==================== ДЕМОНСТРАЦИЯ РАБОТЫ ====================

def demo():
    """Демонстрация работы всех функций"""
    
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №5")
    print("Работа с регулярными выражениями")
    print("=" * 60)
    
    # Демонстрация для части 1
    print("\n" + "=" * 60)
    print("ЧАСТЬ 1: Поиск в текстовом файле")
    print("=" * 60)
    
    # Создаём тестовый текст
    test_text = """
    Москва — столица России, крупнейший город страны.
    В 2023 году в Москве проживало более 13 миллионов человек.
    Температура зимой может опускаться до -25.5 градусов.
    Летом воздух прогревается до +30.5 градусов.
    Среди достопримечательностей: Кремль, Красная площадь, Большой театр.
    """
    
    print("\nВариант 1 (слова от 3 до 5 букв):")
    print(part1_task1_ru(test_text))
    
    print("\nВариант 2 (слова с большой буквы):")
    print(part1_task2_ru(test_text))
    
    print("\nВариант 3 (слова с запятой):")
    print(part1_task3_ru(test_text))
    
    # Демонстрация для части 2
    print("\n" + "=" * 60)
    print("ЧАСТЬ 2: Поиск в HTML файле")
    print("=" * 60)
    
    # Создаём тестовый HTML
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Тестовая страница</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <h1>Заголовок статьи</h1>
        <a href="https://example.com">Ссылка</a>
        <a href="https://university.edu">Образовательный сайт</a>
        <img src="image.jpg" alt="Изображение">
        <div class="container main-content">
            <p class="text">Содержимое</p>
        </div>
    </body>
    </html>
    """
    
    print("\nВариант 1 (открывающие теги):")
    print(part2_task1(test_html))
    
    print("\nВариант 3 (все ссылки):")
    print(part2_task3(test_html))
    
    print("\nВариант 6 (ссылки на изображения):")
    print(part2_task6(test_html))
    
    # Демонстрация для части 3
    print("\n" + "=" * 60)
    print("ЧАСТЬ 3: Приведение данных в порядок")
    print("=" * 60)
    
    # Создаём тестовый файл с перепутанными данными
    test_data = """
    123 Иванов ivanov@email.com 15/03/2024 example.com
    petrov@mail.ru 456 Петров 20/03/2024 test.ru
    789 25/04/2024 sidorov@yandex.ru Сидоров site.org
    """
    
    with open('test_data.txt', 'w', encoding='utf-8') as f:
        f.write(test_data)
    
    print("\nОбработка данных...")
    result = part3_process_data('test_data.txt')
    print("\nРезультат:")
    for row in result:
        print(f"  {row}")
    
    # Демонстрация дополнительного задания
    print("\n" + "=" * 60)
    print("ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ")
    print("=" * 60)
    
    # Создаём тестовый файл со случайными символами
    random_content = """
    asdf1234 25/12/2023 qwerty test@email.com uiop
    https://example.com zxcv 15.03.2024 asdfgh
    another@domain.org 2024-03-20 hjkl www.test.com
    """
    
    with open('task_add.txt', 'w', encoding='utf-8') as f:
        f.write(random_content)
    
    additional_task('task_add.txt')
    
    print("\n" + "=" * 60)
    print("Демонстрация завершена!")
    print("=" * 60)

# ==================== КЛАСС ДЛЯ РАБОТЫ С РЕГУЛЯРНЫМИ ВЫРАЖЕНИЯМИ ====================

class RegexHelper:
    """Вспомогательный класс для работы с регулярными выражениями"""
    
    def __init__(self, pattern, text):
        self.pattern = pattern
        self.text = text
        self.compiled = re.compile(pattern)
    
    def find_all(self):
        """Найти все совпадения"""
        return self.compiled.findall(self.text)
    
    def search_first(self):
        """Найти первое совпадение"""
        match = self.compiled.search(self.text)
        return match.group() if match else None
    
    def replace(self, replacement):
        """Заменить все совпадения"""
        return self.compiled.sub(replacement, self.text)
    
    def split(self):
        """Разбить строку по шаблону"""
        return self.compiled.split(self.text)

# Запуск демонстрации
if __name__ == "__main__":
    demo()