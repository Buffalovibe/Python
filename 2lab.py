import csv
import random
import xml.etree.ElementTree as ET
from collections import Counter
import os
import sys

# Функция для создания тестовых файлов
def create_test_files():
    """Создание всех необходимых файлов для работы программы"""
    
    print("Создание тестовых файлов...")
    
    # 1. Создание books.csv
    if not os.path.exists('books.csv'):
        print("Создание books.csv...")
        with open('books.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            # Заголовки
            writer.writerow(['Id', 'Title', 'Author', 'Price', 'Year', 'Publisher'])
            
            # Данные
            books_data = [
                [1, 'Война и мир (том 1)', 'Толстой Л.Н.', 250.50, 1869, 'АСТ'],
                [2, 'Преступление и наказание', 'Достоевский Ф.М.', 180.00, 1866, 'Эксмо'],
                [3, 'Анна Каренина', 'Толстой Л.Н.', 220.00, 1877, 'АСТ'],
                [4, 'Мастер и Маргарита', 'Булгаков М.А.', 190.50, 1967, 'Эксмо'],
                [5, 'Евгений Онегин', 'Пушкин А.С.', 150.00, 1833, 'Просвещение'],
                [6, 'Мертвые души', 'Гоголь Н.В.', 170.00, 1842, 'Просвещение'],
                [7, 'Идиот', 'Достоевский Ф.М.', 200.00, 1869, 'Эксмо'],
                [8, 'Тихий Дон', 'Шолохов М.А.', 350.00, 1940, 'АСТ'],
                [9, 'Доктор Живаго', 'Пастернак Б.Л.', 280.00, 1957, 'Эксмо'],
                [10, 'Собачье сердце', 'Булгаков М.А.', 140.00, 1925, 'АСТ'],
                [11, 'Отцы и дети', 'Тургенев И.С.', 160.00, 1862, 'Просвещение'],
                [12, 'Обломов', 'Гончаров И.А.', 190.00, 1859, 'АСТ'],
                [13, 'Герой нашего времени', 'Лермонтов М.Ю.', 155.00, 1840, 'Просвещение'],
                [14, 'Ревизор', 'Гоголь Н.В.', 130.00, 1836, 'Эксмо'],
                [15, 'Вишневый сад', 'Чехов А.П.', 145.00, 1904, 'АСТ'],
                [16, 'Три сестры', 'Чехов А.П.', 135.00, 1901, 'Эксмо'],
                [17, 'На дне', 'Горький М.', 125.00, 1902, 'Просвещение'],
                [18, 'Пиковая дама', 'Пушкин А.С.', 115.00, 1834, 'АСТ'],
                [19, 'Капитанская дочка', 'Пушкин А.С.', 165.00, 1836, 'Просвещение'],
                [20, 'Белая гвардия', 'Булгаков М.А.', 210.00, 1925, 'Эксмо'],
                [21, 'Чевенгур', 'Платонов А.П.', 195.00, 1929, 'АСТ'],
                [22, 'Котлован', 'Платонов А.П.', 175.00, 1930, 'Эксмо'],
                [23, 'Записки охотника', 'Тургенев И.С.', 185.00, 1852, 'Просвещение'],
                [24, 'Дворянское гнездо', 'Тургенев И.С.', 170.00, 1859, 'АСТ'],
                [25, 'Рудин', 'Тургенев И.С.', 140.00, 1856, 'Эксмо'],
            ]
            writer.writerows(books_data)
        print("✓ books.csv создан")
    
    # 2. Создание books-en.csv (англоязычные книги)
    if not os.path.exists('books-en.csv'):
        print("Создание books-en.csv...")
        with open('books-en.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            # Заголовки
            writer.writerow(['Id', 'BookTitle', 'Author', 'Price', 'Year', 'Publisher'])
            
            # Данные
            en_books = [
                [1, '1984', 'George Orwell', 299.99, 1949, 'Penguin Books'],
                [2, 'To Kill a Mockingbird', 'Harper Lee', 259.50, 1960, 'J.B. Lippincott'],
                [3, 'The Great Gatsby', 'F. Scott Fitzgerald', 199.00, 1925, "Charles Scribner's Sons"],
                [4, 'One Hundred Years of Solitude', 'Gabriel Garcia Marquez', 349.00, 1967, 'Harper & Row'],
                [5, 'Brave New World', 'Aldous Huxley', 279.99, 1932, 'Chatto & Windus'],
                [6, 'The Catcher in the Rye', 'J.D. Salinger', 239.50, 1951, 'Little, Brown'],
                [7, 'Animal Farm', 'George Orwell', 189.00, 1945, 'Secker & Warburg'],
                [8, 'Lord of the Flies', 'William Golding', 219.99, 1954, 'Faber and Faber'],
                [9, 'The Old Man and the Sea', 'Ernest Hemingway', 169.00, 1952, "Charles Scribner's Sons"],
                [10, 'Fahrenheit 451', 'Ray Bradbury', 229.50, 1953, 'Ballantine Books'],
                [11, 'Crime and Punishment', 'Fyodor Dostoevsky', 289.00, 1866, 'The Russian Messenger'],
                [12, 'War and Peace', 'Leo Tolstoy', 399.00, 1869, 'The Russian Messenger'],
                [13, 'Anna Karenina', 'Leo Tolstoy', 359.00, 1877, 'The Russian Messenger'],
                [14, 'The Brothers Karamazov', 'Fyodor Dostoevsky', 379.00, 1880, 'The Russian Messenger'],
                [15, 'The Hobbit', 'J.R.R. Tolkien', 449.00, 1937, 'Allen & Unwin'],
                [16, 'The Lord of the Rings', 'J.R.R. Tolkien', 599.00, 1954, 'Allen & Unwin'],
                [17, 'The Chronicles of Narnia', 'C.S. Lewis', 499.00, 1950, 'Geoffrey Bles'],
                [18, 'The Da Vinci Code', 'Dan Brown', 399.00, 2003, 'Doubleday'],
                [19, 'Harry Potter', 'J.K. Rowling', 459.00, 1997, 'Bloomsbury'],
                [20, 'The Alchemist', 'Paulo Coelho', 279.00, 1988, 'HarperTorch'],
                [21, 'The Little Prince', 'Antoine de Saint-Exupery', 159.00, 1943, 'Reynal & Hitchcock'],
                [22, 'The Grapes of Wrath', 'John Steinbeck', 289.00, 1939, 'The Viking Press'],
                [23, 'For Whom the Bell Tolls', 'Ernest Hemingway', 299.00, 1940, "Charles Scribner's Sons"],
                [24, 'The Sun Also Rises', 'Ernest Hemingway', 249.00, 1926, "Charles Scribner's Sons"],
                [25, 'A Farewell to Arms', 'Ernest Hemingway', 269.00, 1929, "Charles Scribner's Sons"],
            ]
            writer.writerows(en_books)
        print("✓ books-en.csv создан")
    
    # 3. Создание currency.xml
    if not os.path.exists('currency.xml'):
        print("Создание currency.xml...")
        root = ET.Element("ValCurs")
        root.set("Date", "02.03.2024")
        root.set("name", "Foreign Currency Market")
        
        currencies = [
            {"NumCode": "036", "CharCode": "AUD", "Nominal": "1", "Name": "Австралийский доллар", "Value": "59,2345"},
            {"NumCode": "944", "CharCode": "AZN", "Nominal": "1", "Name": "Азербайджанский манат", "Value": "52,9876"},
            {"NumCode": "826", "CharCode": "GBP", "Nominal": "1", "Name": "Фунт стерлингов", "Value": "114,5678"},
            {"NumCode": "051", "CharCode": "AMD", "Nominal": "100", "Name": "Армянских драмов", "Value": "23,1234"},
            {"NumCode": "974", "CharCode": "BYN", "Nominal": "1", "Name": "Белорусский рубль", "Value": "28,9012"},
            {"NumCode": "986", "CharCode": "BRL", "Nominal": "1", "Name": "Бразильский реал", "Value": "18,3456"},
            {"NumCode": "348", "CharCode": "HUF", "Nominal": "100", "Name": "Венгерских форинтов", "Value": "25,6789"},
            {"NumCode": "704", "CharCode": "VND", "Nominal": "10000", "Name": "Вьетнамских донгов", "Value": "36,7890"},
            {"NumCode": "344", "CharCode": "HKD", "Nominal": "1", "Name": "Гонконгский доллар", "Value": "11,4567"},
            {"NumCode": "840", "CharCode": "USD", "Nominal": "1", "Name": "Доллар США", "Value": "91,2345"},
            {"NumCode": "978", "CharCode": "EUR", "Nominal": "1", "Name": "Евро", "Value": "99,8765"},
            {"NumCode": "356", "CharCode": "INR", "Nominal": "1", "Name": "Индийская рупия", "Value": "1,0987"},
            {"NumCode": "398", "CharCode": "KZT", "Nominal": "100", "Name": "Казахстанских тенге", "Value": "20,1234"},
            {"NumCode": "124", "CharCode": "CAD", "Nominal": "1", "Name": "Канадский доллар", "Value": "67,8901"},
            {"NumCode": "156", "CharCode": "CNY", "Nominal": "1", "Name": "Китайский юань", "Value": "12,6543"},
            {"NumCode": "417", "CharCode": "KGS", "Nominal": "100", "Name": "Киргизских сомов", "Value": "102,3456"},
            {"NumCode": "498", "CharCode": "MDL", "Nominal": "10", "Name": "Молдавских леев", "Value": "51,2345"},
            {"NumCode": "578", "CharCode": "NOK", "Nominal": "1", "Name": "Норвежская крона", "Value": "8,7654"},
            {"NumCode": "643", "CharCode": "RUB", "Nominal": "1", "Name": "Российский рубль", "Value": "1,0000"},
            {"NumCode": "752", "CharCode": "SEK", "Nominal": "1", "Name": "Шведская крона", "Value": "8,9012"},
            {"NumCode": "756", "CharCode": "CHF", "Nominal": "1", "Name": "Швейцарский франк", "Value": "103,4567"},
            {"NumCode": "949", "CharCode": "TRY", "Nominal": "1", "Name": "Турецкая лира", "Value": "2,9876"},
            {"NumCode": "860", "CharCode": "UZS", "Nominal": "10000", "Name": "Узбекских сумов", "Value": "72,3456"},
            {"NumCode": "980", "CharCode": "UAH", "Nominal": "1", "Name": "Украинская гривна", "Value": "2,3456"},
            {"NumCode": "203", "CharCode": "CZK", "Nominal": "1", "Name": "Чешская крона", "Value": "3,9876"},
            {"NumCode": "710", "CharCode": "ZAR", "Nominal": "1", "Name": "Южноафриканский рэнд", "Value": "4,8765"},
            {"NumCode": "410", "CharCode": "KRW", "Nominal": "1000", "Name": "Вон Республики Корея", "Value": "68,9012"},
            {"NumCode": "392", "CharCode": "JPY", "Nominal": "100", "Name": "Японских иен", "Value": "61,2345"},
        ]
        
        for curr in currencies:
            valute = ET.SubElement(root, "Valute")
            for key, value in curr.items():
                elem = ET.SubElement(valute, key)
                elem.text = value
        
        tree = ET.ElementTree(root)
        tree.write("currency.xml", encoding="utf-8", xml_declaration=True)
        print("✓ currency.xml создан")
    
    print("\n✅ Все файлы успешно созданы!\n")

# Функция для проверки наличия файлов
def check_files():
    """Проверка наличия необходимых файлов и их создание при отсутствии"""
    files = ['books.csv', 'books-en.csv', 'currency.xml']
    missing_files = []
    
    for file in files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"Отсутствуют файлы: {', '.join(missing_files)}")
        create_test_files()
        return True
    return True

# Часть 1: Работа с books.csv (или books-en.csv)
def part1_books(variant=1):
    """Задания для работы с файлами книг"""
    print("\n" + "=" * 60)
    print("ЧАСТЬ 1: Работа с файлами книг")
    print("=" * 60)
    
    # Определяем, какой файл использовать (по умолчанию books.csv для варианта 1)
    if variant <= 5:
        books_file = 'books.csv'
    else:
        books_file = 'books-en.csv'
    
    if not os.path.exists(books_file):
        print(f"❌ Файл {books_file} не найден. Запустите программу сначала для создания файлов.")
        return
    
    print(f"📚 Используется файл: {books_file}")
    
    # Определяем названия полей в зависимости от файла
    if books_file == 'books.csv':
        title_field = 'Title'
        author_field = 'Author'
        price_field = 'Price'
        year_field = 'Year'
        publisher_field = 'Publisher'
        delimiter = ';'
    else:  # books-en.csv
        title_field = 'BookTitle'
        author_field = 'Author'
        price_field = 'Price'
        year_field = 'Year'
        publisher_field = 'Publisher'
        delimiter = ';'
    
    # 1.1 Подсчет записей с названием длиннее 30 символов
    print("\n📊 1.1 Подсчет записей с названием длиннее 30 символов:")
    
    long_titles_count = 0
    long_titles = []
    
    with open(books_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            title = row[title_field].strip()
            if len(title) > 30:
                long_titles_count += 1
                long_titles.append(title)
    
    print(f"   Найдено записей: {long_titles_count}")
    if long_titles:
        print("   Примеры:")
        for title in long_titles[:5]:
            print(f"   • {title[:50]}...")
    
    # 1.2 Поиск книги по автору с ограничением (для варианта 1: цена до 150 рублей)
    print(f"\n🔍 1.2 Поиск книги по автору (для варианта {variant}):")
    
    # Устанавливаем ограничение согласно варианту
    if variant == 1:
        price_limit = 150
        limit_text = f"цена до {price_limit} рублей"
    elif variant == 2:
        year_limit = 2016
        limit_text = f"год до {year_limit}"
    elif variant == 3:
        years = [2014, 2016, 2017]
        limit_text = f"года {years}"
    elif variant == 4:
        price_limit = 200
        limit_text = f"цена до {price_limit} рублей"
    elif variant == 5:
        limit_text = "без ограничений"
    else:
        price_limit = 150
        limit_text = f"цена до {price_limit} рублей"
    
    print(f"   Ограничение: {limit_text}")
    
    search_author = input("   Введите имя автора для поиска: ").strip().lower()
    
    found_books = []
    with open(books_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            if search_author in row[author_field].strip().lower():
                try:
                    if variant == 1 or variant == 4:
                        price = float(row[price_field].strip().replace(',', '.'))
                        if price <= price_limit:
                            found_books.append(row)
                    elif variant == 2:
                        year = int(row[year_field].strip())
                        if year <= year_limit:
                            found_books.append(row)
                    elif variant == 3:
                        year = int(row[year_field].strip())
                        if year in years:
                            found_books.append(row)
                    else:
                        found_books.append(row)
                except (ValueError, KeyError):
                    found_books.append(row)
    
    if found_books:
        print(f"   ✅ Найдено {len(found_books)} книг:")
        for i, book in enumerate(found_books[:10], 1):
            print(f"   {i}. {book[author_field]}: {book[title_field]} - {book.get(year_field, '?')} г.")
    else:
        print(f"   ❌ Книги не найдены")
    
    # 1.3 Генератор библиографических ссылок
    print("\n📝 1.3 Генератор библиографических ссылок:")
    
    all_books = []
    with open(books_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            all_books.append(row)
    
    num_samples = min(20, len(all_books))
    selected_books = random.sample(all_books, num_samples)
    
    references = []
    for book in selected_books:
        author = book[author_field].strip()
        title = book[title_field].strip()
        year = book.get(year_field, '').strip()
        
        if year:
            ref = f"{author}. {title} - {year}"
        else:
            ref = f"{author}. {title}"
        
        references.append(ref)
    
    output_file = 'bibliographic_references.txt'
    with open(output_file, 'w', encoding='utf-8') as file:
        for i, ref in enumerate(references, 1):
            file.write(f"{i}. {ref}\n")
    
    print(f"   ✅ Создано {num_samples} ссылок в файле '{output_file}'")
    
    # Дополнительные задания
    print("\n" + "=" * 60)
    print("ДОПОЛНИТЕЛЬНЫЕ ЗАДАНИЯ")
    print("=" * 60)
    
    # 2.1 Перечень всех издательств без повторений
    print("\n🏢 2.1 Уникальные издательства:")
    
    publishers = set()
    with open(books_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            if publisher_field in row and row[publisher_field].strip():
                publishers.add(row[publisher_field].strip())
    
    print(f"   Всего: {len(publishers)} издательств")
    if publishers:
        print("   Список:")
        for i, publisher in enumerate(sorted(publishers)[:15], 1):
            print(f"   {i}. {publisher}")
    
    # 2.2 Самые популярные 20 книг
    print("\n⭐ 2.2 Топ-20 самых популярных книг:")
    
    book_counter = Counter()
    with open(books_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            book_title = row[title_field].strip()
            book_counter[book_title] += 1
    
    popular_books = book_counter.most_common(20)
    
    for i, (book, count) in enumerate(popular_books, 1):
        print(f"   {i}. '{book[:50]}...' - {count} раз(а)" if len(book) > 50 else f"   {i}. '{book}' - {count} раз(а)")

# Часть 2: Работа с currency.xml
def part2_currency(variant=1):
    """Задания для работы с currency.xml"""
    print("\n" + "=" * 60)
    print("ЧАСТЬ 2: Работа с currency.xml")
    print("=" * 60)
    
    xml_file = 'currency.xml'
    
    if not os.path.exists(xml_file):
        print(f"❌ Файл {xml_file} не найден. Запустите программу сначала для создания файлов.")
        return
    
    print(f"📄 Используется файл: {xml_file}")
    print(f"📊 Вариант {variant}: ", end="")
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        if variant == 1:  # Словарь "Name - Value"
            print("Словарь 'Name - Value'")
            currency_dict = {}
            
            for valute in root.findall('.//Valute'):
                name = valute.find('Name')
                value = valute.find('Value')
                
                if name is not None and value is not None:
                    currency_dict[name.text] = value.text
            
            print(f"\n   Найдено {len(currency_dict)} валют:")
            for i, (name, value) in enumerate(list(currency_dict.items())[:10], 1):
                print(f"   {i}. {name}: {value} рублей")
            
            if len(currency_dict) > 10:
                print(f"   ... и еще {len(currency_dict) - 10}")
            
            # Сохраняем
            with open('currency_dict.txt', 'w', encoding='utf-8') as f:
                for name, value in currency_dict.items():
                    f.write(f"{name}: {value}\n")
            print(f"   ✅ Сохранено в currency_dict.txt")
        
        elif variant == 2:  # Два отдельных списка Name и Value
            print("Два списка: Name и Value")
            names = []
            values = []
            
            for valute in root.findall('.//Valute'):
                name = valute.find('Name')
                value = valute.find('Value')
                
                if name is not None:
                    names.append(name.text)
                if value is not None:
                    values.append(value.text)
            
            print(f"\n   📋 Name ({len(names)}):")
            for i, name in enumerate(names[:10], 1):
                print(f"   {i}. {name}")
            
            print(f"\n   💰 Value ({len(values)}):")
            for i, value in enumerate(values[:10], 1):
                print(f"   {i}. {value}")
            
            # Сохраняем
            with open('currency_lists.txt', 'w', encoding='utf-8') as f:
                f.write("NAMES:\n")
                for name in names:
                    f.write(f"{name}\n")
                f.write("\nVALUES:\n")
                for value in values:
                    f.write(f"{value}\n")
            print(f"   ✅ Сохранено в currency_lists.txt")
        
        elif variant == 3:  # Список Name для валют с Nominal=1
            print("Список Name для валют с Nominal=1")
            names = []
            
            for valute in root.findall('.//Valute'):
                nominal = valute.find('Nominal')
                name = valute.find('Name')
                
                if nominal is not None and name is not None and nominal.text == '1':
                    names.append(name.text)
            
            print(f"\n   Найдено {len(names)} валют:")
            for i, name in enumerate(names[:15], 1):
                print(f"   {i}. {name}")
            
            # Сохраняем
            with open('currency_nominal1.txt', 'w', encoding='utf-8') as f:
                for name in names:
                    f.write(f"{name}\n")
            print(f"   ✅ Сохранено в currency_nominal1.txt")
        
        elif variant == 4:  # Словарь "NumCode - CharCode"
            print("Словарь 'NumCode - CharCode'")
            code_dict = {}
            
            for valute in root.findall('.//Valute'):
                numcode = valute.find('NumCode')
                charcode = valute.find('CharCode')
                
                if numcode is not None and charcode is not None:
                    code_dict[numcode.text] = charcode.text
            
            print(f"\n   Найдено {len(code_dict)} записей:")
            for i, (num, char) in enumerate(list(code_dict.items())[:15], 1):
                print(f"   {i}. {num} -> {char}")
            
            with open('currency_numcode_charcode.txt', 'w', encoding='utf-8') as f:
                for num, char in code_dict.items():
                    f.write(f"{num}: {char}\n")
            print(f"   ✅ Сохранено")
        
        elif variant == 5:  # Два списка CharCode и Value
            print("Два списка: CharCode и Value")
            charcodes = []
            values = []
            
            for valute in root.findall('.//Valute'):
                charcode = valute.find('CharCode')
                value = valute.find('Value')
                
                if charcode is not None:
                    charcodes.append(charcode.text)
                if value is not None:
                    values.append(value.text)
            
            print(f"\n   🔤 CharCode ({len(charcodes)}):")
            for i, code in enumerate(charcodes[:10], 1):
                print(f"   {i}. {code}")
            
            print(f"\n   💰 Value ({len(values)}):")
            for i, val in enumerate(values[:10], 1):
                print(f"   {i}. {val}")
            
            with open('currency_charcode_value.txt', 'w', encoding='utf-8') as f:
                f.write("CHARCODES:\n")
                for code in charcodes:
                    f.write(f"{code}\n")
                f.write("\nVALUES:\n")
                for val in values:
                    f.write(f"{val}\n")
            print(f"   ✅ Сохранено")
        
        elif variant == 6:  # Средний показатель Value
            print("Среднее значение Value")
            values = []
            
            for valute in root.findall('.//Valute'):
                value = valute.find('Value')
                if value is not None:
                    try:
                        val = float(value.text.replace(',', '.'))
                        values.append(val)
                    except ValueError:
                        pass
            
            if values:
                avg = sum(values) / len(values)
                print(f"\n   📊 Среднее значение: {avg:.4f} рублей")
                print(f"   📈 Всего значений: {len(values)}")
                print(f"   📉 Минимум: {min(values):.4f}")
                print(f"   📈 Максимум: {max(values):.4f}")
                
                with open('currency_average.txt', 'w', encoding='utf-8') as f:
                    f.write(f"Среднее значение: {avg:.4f}\n")
                    f.write(f"Количество: {len(values)}\n")
                    f.write(f"Минимум: {min(values):.4f}\n")
                    f.write(f"Максимум: {max(values):.4f}\n")
                print(f"   ✅ Сохранено")
        
        else:
            print("Вариант не реализован")
    
    except ET.ParseError:
        print("❌ Ошибка при парсинге XML файла")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Главная функция
def main():
    """Основная функция программы"""
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №2")
    print("=" * 60)
    
    # Проверяем и создаем файлы при необходимости
    check_files()
    
    # Запрашиваем вариант
    try:
        variant = int(input("\nВведите номер варианта (1-10): "))
        if variant < 1 or variant > 10:
            print("⚠️ Неверный вариант. Используется вариант 1")
            variant = 1
    except ValueError:
        print("⚠️ Используется вариант 1")
        variant = 1
    
    print(f"\n✅ Выбран вариант {variant}")
    
    # Выполняем задания
    part1_books(variant)
    part2_currency(variant)
    
    print("\n" + "=" * 60)
    print("✅ РАБОТА ЗАВЕРШЕНА")
    print("=" * 60)
    print("\nСозданные файлы:")
    print("📁 books.csv - русские книги")
    print("📁 books-en.csv - английские книги")
    print("📁 currency.xml - курсы валют")
    print("📁 bibliographic_references.txt - библиографические ссылки")
    print("📁 currency_dict.txt/lists.txt и др. - результаты обработки XML")

if __name__ == "__main__":
    main()