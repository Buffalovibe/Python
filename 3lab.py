import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

class KeygenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keygen Generator - Все варианты")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        
        # Цвета
        self.bg_color = "#f0f0f0"
        self.accent_color = "#4CAF50"
        self.root.configure(bg=self.bg_color)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Заголовок
        title = tk.Label(self.root, text="🔐 ГЕНЕРАТОР КЛЮЧЕЙ", 
                        font=("Arial", 18, "bold"), bg=self.bg_color, fg="#333")
        title.pack(pady=10)
        
        # === БЛОК ВЫБОРА ВАРИАНТА ===
        variant_frame = tk.LabelFrame(self.root, text="Выбор варианта", 
                                     font=("Arial", 11, "bold"),
                                     bg=self.bg_color, padx=10, pady=10)
        variant_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(variant_frame, text="Вариант:", 
                font=("Arial", 12), bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        
        self.variant_var = tk.StringVar(value="1")
        self.variant_combo = ttk.Combobox(variant_frame, textvariable=self.variant_var,
                                         values=[f"Вариант {i}" for i in range(1, 11)],
                                         width=15, state="readonly", font=("Arial", 11))
        self.variant_combo.pack(side=tk.LEFT, padx=5)
        self.variant_combo.bind("<<ComboboxSelected>>", self.on_variant_change)
        
        # === БЛОК ВВОДА ДАННЫХ (ВСЕГДА ВИДЕН) ===
        self.input_frame = tk.LabelFrame(self.root, text="Ввод данных (если требуется)", 
                                        font=("Arial", 11, "bold"),
                                        bg="#FFF3E0", padx=10, pady=10)
        self.input_frame.pack(pady=10, padx=20, fill="x")
        
        # Лейбл подсказки
        self.input_hint = tk.Label(self.input_frame, 
                                  text="Для этого варианта ввод не требуется",
                                  font=("Arial", 10, "italic"), 
                                  bg="#FFF3E0", fg="#666")
        self.input_hint.pack(pady=5)
        
        # Поле ввода с рамкой
        input_row = tk.Frame(self.input_frame, bg="#FFF3E0")
        input_row.pack(pady=5)
        
        self.input_label = tk.Label(input_row, text="Значение:", 
                                   font=("Arial", 12, "bold"), 
                                   bg="#FFF3E0", fg="#333")
        self.input_label.pack(side=tk.LEFT, padx=5)
        
        self.input_entry = tk.Entry(input_row, width=35, font=("Courier", 12),
                                   justify="center", relief="solid", bd=2)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_entry.config(state="disabled", disabledbackground="#e0e0e0")
        
        # === КНОПКА ГЕНЕРАЦИИ ===
        self.btn_generate = tk.Button(self.root, text="▶ СГЕНЕРИРОВАТЬ КЛЮЧ", 
                                     command=self.generate_key,
                                     font=("Arial", 14, "bold"),
                                     bg=self.accent_color, fg="white",
                                     activebackground="#45a049",
                                     padx=30, pady=12, relief="raised", bd=3)
        self.btn_generate.pack(pady=15)
        
        # === БЛОК ВЫВОДА КЛЮЧА ===
        output_frame = tk.LabelFrame(self.root, text="Сгенерированный ключ", 
                                    font=("Arial", 11, "bold"),
                                    bg="#E3F2FD", padx=10, pady=10)
        output_frame.pack(pady=10, padx=20, fill="x")
        
        self.key_var = tk.StringVar(value="Нажмите кнопку для генерации")
        self.key_entry = tk.Entry(output_frame, textvariable=self.key_var,
                                 font=("Courier", 16, "bold"),
                                 justify="center", width=35,
                                 fg="#1976D2", bg="white", relief="solid", bd=2,
                                 state="readonly")
        self.key_entry.pack(pady=10)
        
        # Кнопка копирования
        self.btn_copy = tk.Button(output_frame, text="📋 Копировать", 
                                 command=self.copy_key,
                                 font=("Arial", 10), bg="#2196F3", fg="white")
        self.btn_copy.pack(pady=5)
        
        # === ОПИСАНИЕ ВАРИАНТА ===
        desc_frame = tk.LabelFrame(self.root, text="Описание варианта", 
                                  font=("Arial", 11, "bold"),
                                  bg=self.bg_color, padx=10, pady=10)
        desc_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.desc_text = tk.Text(desc_frame, height=8, width=70, 
                                wrap=tk.WORD, font=("Arial", 10),
                                bg="#FAFAFA", relief="solid", bd=1)
        self.desc_text.pack(fill="both", expand=True)
        self.desc_text.config(state=tk.DISABLED)
        
        # Инициализация
        self.current_variant = 1  # Устанавливаем начальное значение
        self.on_variant_change(None)
    
    def on_variant_change(self, event):
        """Обновление интерфейса при смене варианта"""
        # Получаем номер варианта (из строки "Вариант X")
        variant_str = self.variant_var.get()
        try:
            if " " in variant_str:
                variant = int(variant_str.split()[1])
            else:
                variant = int(variant_str)
        except (ValueError, IndexError):
            variant = 1
        
        self.current_variant = variant
        
        # Настройка поля ввода - ИСПРАВЛЕННЫЙ СЛОВАРЬ (всегда 3 значения!)
        input_configs = {
            1: (False, "Для этого варианта ввод не требуется", ""),
            2: (False, "Для этого варианта ввод не требуется", ""),
            3: (True, "HEX-число из 5 знаков (например: 54CD1)", "54CD1"),
            4: (False, "Для этого варианта ввод не требуется", ""),
            5: (False, "Для этого варианта ввод не требуется", ""),
            6: (False, "Для этого варианта ввод не требуется", ""),
            7: (True, "Слово из 6 букв (например: MASTER)", "MASTER"),
            8: (True, "DEC-число из 3 цифр (например: 123)", "123"),
            9: (False, "Для этого варианта ввод не требуется", ""),
            10: (True, "DEC-число из 6 цифр (например: 726911)", "726911")
        }
        
        # Получаем конфигурацию с значением по умолчанию (3 элемента!)
        needs_input, hint_text, placeholder = input_configs.get(variant, (False, "Для этого варианта ввод не требуется", ""))
        
        if needs_input:
            self.input_entry.config(state="normal", bg="white")
            self.input_entry.delete(0, tk.END)
            if placeholder:
                self.input_entry.insert(0, placeholder)
            self.input_hint.config(text=f"⚠ {hint_text}", fg="#D32F2F", font=("Arial", 10, "bold"))
            self.input_frame.config(text="⚠ ТРЕБУЕТСЯ ВВОД ДАННЫХ", fg="#D32F2F")
        else:
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(state="disabled", disabledbackground="#e0e0e0")
            self.input_hint.config(text=f"✓ {hint_text}", fg="#388E3C", font=("Arial", 10, "italic"))
            self.input_frame.config(text="Ввод данных (не требуется)", fg="black")
        
        # Обновление описания
        descriptions = {
            1: "ВАРИАНТ 1: XXXXX-XXXXX-XXXXX\n\nКаждый блок имеет две цифры и три буквы в случайном порядке.\nПример: FX26N-N3RT7-AZ0J8",
            2: "ВАРИАНТ 2: XXXX-XXXX-XXXX-XXXX\n\nКаждый блок имеет одну цифру и три буквы в случайном порядке.\nПример: AB8U-Z0MI-7FYK-K9GT",
            3: "ВАРИАНТ 3: XXXXX-XXXXX-XXXXX XX\n\nТребуется ввод HEX-числа (5 знаков), которое переводится в DEC.\nПервые три цифры числа в DEC — по одной в каждом блоке.\nПоследние две цифры — в конце ключа.\nПример: ввод 54CD1(HEX)=347345(DEC) → DS3BG-409KJ-T67K8 45",
            4: "ВАРИАНТ 4: XXXX-XXXX-XXXX\n\nНазначены весовые коэффициенты: A=1, B=2, ..., Z=26.\nСумма весов одного блока должна попасть в интервал 30-35.\nПример: YABD-NBCO-DGIK (суммы: 32-34-31)",
            5: "ВАРИАНТ 5: XXXXX-XXXXX-XXXXX\n\nПервый блок — случайный.\nВторой блок: сдвиг на 3 символа вправо.\nТретий блок: сдвиг на 5 символов влево.\nПример: JINOS-MLQRV-EDIJN",
            6: "ВАРИАНТ 6: XXXXX-XXXX-XXXX\n\nВесовые коэффициенты: A=1, B=2, ..., Z=26.\nСреднее значение букв блока должно быть в интервале 10-15.\nПример: YAND-NZCQ-WGIK (средние: 11-15-12)",
            7: "ВАРИАНТ 7: XXX-XXXXXX-XXX\n\nТребуется ввод слова из 6 букв.\n1 и 3 блок — буквы из слова (по 3).\n2 блок — цифры, соответствующие порядковым номерам букв (только единицы).\nПример: ввод MASTER → TMR 319058 AES",
            8: "ВАРИАНТ 8: XXXXX-XXXX-XXX-XX\n\nТребуется ввод DEC-числа (3 знака).\n1 блок — случайные буквы.\nКаждый следующий блок убирает последнюю букву и сдвигает на цифру из числа.\nНаправление сдвига чередуется: вправо-влево-вправо.\nПример: ввод 123 → DRITF-ESJY-CPR-FS",
            9: "ВАРИАНТ 9: XX XXXXXXXX XX\n\n1 и 3 блок — порядковые номера двух случайных букв (границы интервала).\n2 блок — буквы из этого интервала в случайном порядке.\nПример: выпали A и J → 01 DEBBVHSCI 10",
            10: "ВАРИАНТ 10: XXXXX-XXXXX-XXXX\n\nТребуется ввод DEC-числа (6 знаков).\n1 блок: цифры 4,5,6 из числа + случайные буквы.\n2 блок: цифры 1,2,3 из числа + случайные буквы.\n3 блок: сумма чисел из 1 и 2 блоков.\nПример: ввод 726911 → 276DL-191GO-0467"
        }
        
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, descriptions.get(variant, "Описание отсутствует"))
        self.desc_text.config(state=tk.DISABLED)
    
    def generate_key(self):
        """Генерация ключа в зависимости от варианта"""
        try:
            if self.current_variant == 1:
                key = self.variant_1()
            elif self.current_variant == 2:
                key = self.variant_2()
            elif self.current_variant == 3:
                key = self.variant_3()
            elif self.current_variant == 4:
                key = self.variant_4()
            elif self.current_variant == 5:
                key = self.variant_5()
            elif self.current_variant == 6:
                key = self.variant_6()
            elif self.current_variant == 7:
                key = self.variant_7()
            elif self.current_variant == 8:
                key = self.variant_8()
            elif self.current_variant == 9:
                key = self.variant_9()
            elif self.current_variant == 10:
                key = self.variant_10()
            else:
                raise ValueError(f"Неизвестный вариант: {self.current_variant}")
            
            self.key_var.set(key)
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    # ========== ВАРИАНТЫ ГЕНЕРАЦИИ ==========
    
    def variant_1(self):
        """XXXXX-XXXXX-XXXXX: 2 цифры + 3 буквы в случайном порядке"""
        blocks = []
        for _ in range(3):
            chars = [random.choice(string.digits) for _ in range(2)]
            chars += [random.choice(string.ascii_uppercase) for _ in range(3)]
            random.shuffle(chars)
            blocks.append(''.join(chars))
        return '-'.join(blocks)
    
    def variant_2(self):
        """XXXX-XXXX-XXXX-XXXX: 1 цифра + 3 буквы в случайном порядке"""
        blocks = []
        for _ in range(4):
            chars = [random.choice(string.digits)]
            chars += [random.choice(string.ascii_uppercase) for _ in range(3)]
            random.shuffle(chars)
            blocks.append(''.join(chars))
        return '-'.join(blocks)
    
    def variant_3(self):
        """XXXXX-XXXXX-XXXXX XX: на основе HEX-числа"""
        hex_input = self.input_entry.get().strip().upper()
        if len(hex_input) != 5 or not all(c in string.hexdigits for c in hex_input):
            raise ValueError("Введите HEX-число из 5 знаков (0-9, A-F)!\n\nПример: 54CD1")
        
        dec_num = int(hex_input, 16)
        dec_str = str(dec_num).zfill(6)
        
        blocks = []
        for i in range(3):
            letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
            digit = dec_str[i]
            block_chars = list(letters + digit)
            random.shuffle(block_chars)
            blocks.append(''.join(block_chars))
        
        return '-'.join(blocks) + ' ' + dec_str[4:6]
    
    def variant_4(self):
        """XXXX-XXXX-XXXX: сумма весов в интервале 30-35"""
        def generate_block():
            while True:
                letters = [random.choice(string.ascii_uppercase) for _ in range(4)]
                weight_sum = sum(ord(c) - ord('A') + 1 for c in letters)
                if 30 <= weight_sum <= 35:
                    return ''.join(letters), weight_sum
        
        blocks = []
        sums = []
        for _ in range(3):
            block, s = generate_block()
            blocks.append(block)
            sums.append(s)
        
        print(f"Вариант 4 - Суммы: {'-'.join(map(str, sums))}")
        return '-'.join(blocks)
    
    def variant_5(self):
        """XXXXX-XXXXX-XXXXX: на основе первого блока"""
        first_block = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
        
        second_block = ''
        for char in first_block:
            new_pos = (ord(char) - ord('A') + 3) % 26
            second_block += chr(new_pos + ord('A'))
        
        third_block = ''
        for char in first_block:
            new_pos = (ord(char) - ord('A') - 5) % 26
            third_block += chr(new_pos + ord('A'))
        
        return f"{first_block}-{second_block}-{third_block}"
    
    def variant_6(self):
        """XXXXX-XXXX-XXXX: среднее весов в интервале 10-15"""
        def generate_block(length):
            while True:
                letters = [random.choice(string.ascii_uppercase) for _ in range(length)]
                weights = [ord(c) - ord('A') + 1 for c in letters]
                avg = sum(weights) / len(weights)
                if 10 <= avg <= 15:
                    return ''.join(letters), avg
        
        blocks = []
        avgs = []
        
        block, avg = generate_block(5)
        blocks.append(block)
        avgs.append(round(avg))
        
        for _ in range(2):
            block, avg = generate_block(4)
            blocks.append(block)
            avgs.append(round(avg))
        
        print(f"Вариант 6 - Средние: {'-'.join(map(str, avgs))}")
        return '-'.join(blocks)
    
    def variant_7(self):
        """XXX-XXXXXX-XXX: на основе слова из 6 букв"""
        word = self.input_entry.get().strip().upper()
        if len(word) != 6 or not word.isalpha():
            raise ValueError("Введите слово из 6 букв!\n\nПример: MASTER")
        
        block1 = word[:3]
        block3 = word[3:]
        
        block2 = ''
        for char in word:
            pos = ord(char) - ord('A') + 1
            unit_digit = pos % 10
            block2 += str(unit_digit)
        
        return f"{block1} {block2} {block3}"
    
    def variant_8(self):
        """XXXXX-XXXX-XXX-XX: на основе DEC-числа (3 знака)"""
        dec_input = self.input_entry.get().strip()
        if len(dec_input) != 3 or not dec_input.isdigit():
            raise ValueError("Введите DEC-число из 3 цифр!\n\nПример: 123")
        
        digits = [int(d) for d in dec_input]
        
        base = [random.choice(string.ascii_uppercase) for _ in range(5)]
        blocks = [''.join(base)]
        
        directions = [1, -1, 1]
        
        for i in range(3):
            base = base[:-1]
            shifted = []
            for char in base:
                shift = digits[i]
                if directions[i] == 1:
                    new_pos = (ord(char) - ord('A') + shift) % 26
                else:
                    new_pos = (ord(char) - ord('A') - shift) % 26
                shifted.append(chr(new_pos + ord('A')))
            base = shifted
            blocks.append(''.join(base))
        
        return '-'.join(blocks)
    
    def variant_9(self):
        """XX XXXXXXXX XX: интервал букв"""
        letter1 = random.choice(string.ascii_uppercase)
        letter2 = random.choice(string.ascii_uppercase)
        
        start = min(ord(letter1), ord(letter2))
        end = max(ord(letter1), ord(letter2))
        
        pos1 = start - ord('A') + 1
        pos2 = end - ord('A') + 1
        
        interval_letters = [chr(i) for i in range(start, end + 1)]
        if len(interval_letters) < 8:
            block2_letters = (interval_letters * ((8 // len(interval_letters)) + 1))[:8]
        else:
            block2_letters = random.sample(interval_letters, 8)
        
        random.shuffle(block2_letters)
        block2 = ''.join(block2_letters)
        
        return f"{pos1:02d} {block2} {pos2:02d}"
    
    def variant_10(self):
        """XXXXX-XXXXX-XXXX: на основе DEC-числа (6 знаков)"""
        dec_input = self.input_entry.get().strip()
        if len(dec_input) != 6 or not dec_input.isdigit():
            raise ValueError("Введите DEC-число из 6 цифр!\n\nПример: 726911")
        
        digits1 = dec_input[3:6]
        letters1 = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
        block1_chars = list(digits1 + letters1)
        random.shuffle(block1_chars)
        block1 = ''.join(block1_chars)
        
        digits2 = dec_input[0:3]
        letters2 = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
        block2_chars = list(digits2 + letters2)
        random.shuffle(block2_chars)
        block2 = ''.join(block2_chars)
        
        num1 = int(digits1)
        num2 = int(digits2)
        sum_num = num1 + num2
        block3 = str(sum_num).zfill(4)
        
        return f"{block1}-{block2}-{block3}"
    
    def copy_key(self):
        """Копирование ключа в буфер обмена"""
        key = self.key_var.get()
        if key and "Нажмите" not in key:
            self.root.clipboard_clear()
            self.root.clipboard_append(key)
            messagebox.showinfo("Успех", "Ключ скопирован в буфер обмена!")


def main():
    root = tk.Tk()
    app = KeygenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()