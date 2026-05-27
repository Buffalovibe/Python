import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import threading
import winsound
import time

class KeygenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🇷🇺 КЕЙГЕН РОССИИ - Все варианты")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        # Цвета флага России
        self.white = "#FFFFFF"
        self.blue = "#0039A6"      # Синий флаг России
        self.red = "#D52B1E"       # Красный флаг России
        self.dark_blue = "#002D82"
        self.gold = "#FFD700"      # Золото для акцентов
        
        self.root.configure(bg=self.white)
        
        # Флаг музыки
        self.music_playing = False
        self.music_thread = None
        
        self.setup_ui()
        self.start_music()
    
    def setup_ui(self):
        # === ВЕРХНЯЯ ПАНЕЛЬ (СИНЯЯ) ===
        top_frame = tk.Frame(self.root, bg=self.blue, height=80)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)
        
        # Флаг России (эмодзи)
        flag_label = tk.Label(top_frame, text="🇷🇺", font=("Segoe UI Emoji", 40), 
                             bg=self.blue)
        flag_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Заголовок
        title = tk.Label(top_frame, text="КЕЙГЕН РОССИИ", 
                        font=("Impact", 28), bg=self.blue, fg=self.white)
        title.pack(side=tk.LEFT, padx=10)
        
        subtitle = tk.Label(top_frame, text="Генератор ключей для отечественного ПО", 
                           font=("Arial", 10), bg=self.blue, fg=self.gold)
        subtitle.pack(side=tk.LEFT, padx=10, pady=20)
        
        # Кнопка музыки
        self.btn_music = tk.Button(top_frame, text="🔊 Музыка: ВКЛ", 
                                  command=self.toggle_music,
                                  font=("Arial", 9, "bold"),
                                  bg=self.red, fg=self.white,
                                  activebackground="#B22222")
        self.btn_music.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # === КРАСНАЯ ЛИНИЯ ===
        red_line = tk.Frame(self.root, bg=self.red, height=5)
        red_line.pack(fill="x")
        
        # === ОСНОВНОЕ СОДЕРЖИМОЕ ===
        content_frame = tk.Frame(self.root, bg=self.white)
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # === БЛОК ВЫБОРА ВАРИАНТА ===
        variant_frame = tk.LabelFrame(content_frame, text=" Выбор варианта задания ", 
                                     font=("Arial", 12, "bold"),
                                     bg=self.white, fg=self.blue,
                                     relief="groove", bd=3)
        variant_frame.pack(pady=10, fill="x")
        
        tk.Label(variant_frame, text="Вариант:", 
                font=("Arial", 11, "bold"), bg=self.white, fg=self.dark_blue).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.variant_var = tk.StringVar(value="1")
        self.variant_combo = ttk.Combobox(variant_frame, textvariable=self.variant_var,
                                         values=[f"Вариант {i}" for i in range(1, 11)],
                                         width=15, state="readonly", font=("Arial", 11))
        self.variant_combo.pack(side=tk.LEFT, padx=5, pady=10)
        self.variant_combo.bind("<<ComboboxSelected>>", self.on_variant_change)
        
        # === БЛОК ВВОДА ДАННЫХ ===
        self.input_frame = tk.LabelFrame(content_frame, text=" Ввод данных ", 
                                        font=("Arial", 12, "bold"),
                                        bg="#F0F8FF", fg=self.dark_blue,
                                        relief="groove", bd=3)
        self.input_frame.pack(pady=10, fill="x")
        
        # Лейбл подсказки
        self.input_hint = tk.Label(self.input_frame, 
                                  text="Для этого варианта ввод не требуется",
                                  font=("Arial", 10, "italic"), 
                                  bg="#F0F8FF", fg="#666")
        self.input_hint.pack(pady=5)
        
        # Поле ввода
        input_row = tk.Frame(self.input_frame, bg="#F0F8FF")
        input_row.pack(pady=5)
        
        self.input_label = tk.Label(input_row, text="Значение:", 
                                   font=("Arial", 11, "bold"), 
                                   bg="#F0F8FF", fg=self.dark_blue)
        self.input_label.pack(side=tk.LEFT, padx=10)
        
        self.input_entry = tk.Entry(input_row, width=35, font=("Courier", 12, "bold"),
                                   justify="center", relief="solid", bd=2,
                                   fg=self.dark_blue)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_entry.config(state="disabled", disabledbackground="#e0e0e0")
        
        # === КНОПКА ГЕНЕРАЦИИ (КРАСНАЯ) ===
        self.btn_generate = tk.Button(content_frame, text="🛡️ СГЕНЕРИРОВАТЬ КЛЮЧ", 
                                     command=self.generate_key,
                                     font=("Arial", 14, "bold"),
                                     bg=self.red, fg=self.white,
                                     activebackground="#B22222",
                                     padx=40, pady=12, relief="raised", bd=4,
                                     cursor="hand2")
        self.btn_generate.pack(pady=15)
        
        # === БЛОК ВЫВОДА КЛЮЧА (СИНИЙ) ===
        output_frame = tk.LabelFrame(content_frame, text=" Сгенерированный ключ ", 
                                    font=("Arial", 12, "bold"),
                                    bg="#E6F3FF", fg=self.blue,
                                    relief="groove", bd=3)
        output_frame.pack(pady=10, fill="x")
        
        self.key_var = tk.StringVar(value="Нажмите кнопку для генерации")
        self.key_entry = tk.Entry(output_frame, textvariable=self.key_var,
                                 font=("Courier", 18, "bold"),
                                 justify="center", width=30,
                                 fg=self.red, bg=self.white, 
                                 relief="solid", bd=3,
                                 state="readonly",
                                 readonlybackground=self.white)
        self.key_entry.pack(pady=15)
        
        # Кнопка копирования
        self.btn_copy = tk.Button(output_frame, text="📋 Копировать в буфер", 
                                 command=self.copy_key,
                                 font=("Arial", 10, "bold"), 
                                 bg=self.blue, fg=self.white,
                                 activebackground=self.dark_blue)
        self.btn_copy.pack(pady=5)
        
        # === ОПИСАНИЕ ВАРИАНТА ===
        desc_frame = tk.LabelFrame(content_frame, text=" Описание варианта ", 
                                  font=("Arial", 11, "bold"),
                                  bg=self.white, fg=self.dark_blue,
                                  relief="groove", bd=2)
        desc_frame.pack(pady=10, fill="both", expand=True)
        
        self.desc_text = tk.Text(desc_frame, height=6, width=65, 
                                wrap=tk.WORD, font=("Arial", 10),
                                bg="#FAFAFA", fg="#333",
                                relief="flat", padx=10, pady=10)
        self.desc_text.pack(fill="both", expand=True)
        self.desc_text.config(state=tk.DISABLED)
        
        # === НИЖНЯЯ ПАНЕЛЬ (КРАСНАЯ) ===
        bottom_frame = tk.Frame(self.root, bg=self.red, height=40)
        bottom_frame.pack(fill="x", side=tk.BOTTOM)
        bottom_frame.pack_propagate(False)
        
        footer_text = tk.Label(bottom_frame, 
                              text="Сделано в России • 2024 • Слава Родине!", 
                              font=("Arial", 10, "bold"),
                              bg=self.red, fg=self.white)
        footer_text.pack(pady=10)
        
        # Инициализация
        self.current_variant = 1
        self.on_variant_change(None)
    
    def play_anthem(self):
        """Воспроизведение гимна России (8-bit версия)"""
        # Ноты гимна России (часть мелодии) - частоты в Гц
        # Темп: умеренный
        
        notes = [
            # "Союз нерушимый..."
            (392, 500), (392, 500), (440, 1000),  # G4, G4, A4
            (392, 500), (349, 500), (392, 1000),  # G4, F4, G4
            (523, 500), (523, 500), (587, 1000),  # C5, C5, D5
            (523, 500), (494, 500), (523, 1000),  # C5, B4, C5
            
            # "Россия священная..."
            (392, 500), (392, 500), (440, 1000),  # G4, G4, A4
            (392, 500), (349, 500), (392, 1000),  # G4, F4, G4
            (659, 500), (587, 500), (523, 1000),  # E5, D5, C5
            (494, 500), (523, 500), (392, 1500),  # B4, C5, G4
            
            # Повторение для цикла
            (392, 500), (392, 500), (440, 1000),
            (392, 500), (349, 500), (392, 1000),
        ]
        
        while self.music_playing:
            for freq, duration in notes:
                if not self.music_playing:
                    break
                try:
                    winsound.Beep(freq, duration)
                except:
                    pass
                time.sleep(0.05)  # Пауза между нотами
    
    def start_music(self):
        """Запуск музыки"""
        self.music_playing = True
        self.music_thread = threading.Thread(target=self.play_anthem, daemon=True)
        self.music_thread.start()
    
    def stop_music(self):
        """Остановка музыки"""
        self.music_playing = False
    
    def toggle_music(self):
        """Переключение музыки"""
        if self.music_playing:
            self.stop_music()
            self.btn_music.config(text="🔇 Музыка: ВЫКЛ", bg="#666")
        else:
            self.start_music()
            self.btn_music.config(text="🔊 Музыка: ВКЛ", bg=self.red)
    
    def on_variant_change(self, event):
        """Обновление интерфейса при смене варианта"""
        variant_str = self.variant_var.get()
        try:
            if " " in variant_str:
                variant = int(variant_str.split()[1])
            else:
                variant = int(variant_str)
        except (ValueError, IndexError):
            variant = 1
        
        self.current_variant = variant
        
        # Конфигурации ввода
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
        
        needs_input, hint_text, placeholder = input_configs.get(variant, (False, "Для этого варианта ввод не требуется", ""))
        
        if needs_input:
            self.input_entry.config(state="normal", bg=self.white)
            self.input_entry.delete(0, tk.END)
            if placeholder:
                self.input_entry.insert(0, placeholder)
            self.input_hint.config(text=f"⚠ {hint_text}", fg=self.red, font=("Arial", 10, "bold"))
            self.input_frame.config(text=" ⚠ ТРЕБУЕТСЯ ВВОД ДАННЫХ ", fg=self.red)
        else:
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(state="disabled", disabledbackground="#e0e0e0")
            self.input_hint.config(text=f"✓ {hint_text}", fg=self.blue, font=("Arial", 10, "italic"))
            self.input_frame.config(text=" Ввод данных (не требуется) ", fg=self.dark_blue)
        
        # Описания
        descriptions = {
            1: "ВАРИАНТ 1: XXXXX-XXXXX-XXXXX\nКаждый блок имеет две цифры и три буквы в случайном порядке.\nПример: FX26N-N3RT7-AZ0J8",
            2: "ВАРИАНТ 2: XXXX-XXXX-XXXX-XXXX\nКаждый блок имеет одну цифру и три буквы в случайном порядке.\nПример: AB8U-Z0MI-7FYK-K9GT",
            3: "ВАРИАНТ 3: XXXXX-XXXXX-XXXXX XX\nТребуется ввод HEX-числа (5 знаков), которое переводится в DEC.\nПервые три цифры DEC — по одной в каждом блоке, последние две — в конце.\nПример: 54CD1(HEX)=347345(DEC) → DS3BG-409KJ-T67K8 45",
            4: "ВАРИАНТ 4: XXXX-XXXX-XXXX\nВесовые коэффициенты: A=1, B=2, ..., Z=26.\nСумма весов блока должна быть в интервале 30-35.\nПример: YABD-NBCO-DGIK (суммы: 32-34-31)",
            5: "ВАРИАНТ 5: XXXXX-XXXXX-XXXXX\nПервый блок случайный. Второй: сдвиг на 3 вправо. Третий: сдвиг на 5 влево.\nПример: JINOS-MLQRV-EDIJN",
            6: "ВАРИАНТ 6: XXXXX-XXXX-XXXX\nСреднее значение весов букв блока в интервале 10-15.\nПример: YAND-NZCQ-WGIK (средние: 11-15-12)",
            7: "ВАРИАНТ 7: XXX-XXXXXX-XXX\nТребуется слово из 6 букв. 1 и 3 блок — буквы слова.\n2 блок — порядковые номера букв (только единицы).\nПример: MASTER → TMR 319058 AES",
            8: "ВАРИАНТ 8: XXXXX-XXXX-XXX-XX\nТребуется DEC-число (3 знака). Каждый блок убирает букву и сдвигает.\nНаправление чередуется: вправо-влево-вправо.\nПример: 123 → DRITF-ESJY-CPR-FS",
            9: "ВАРИАНТ 9: XX XXXXXXXX XX\n1 и 3 блок — границы интервала (порядковые номера букв).\n2 блок — буквы из интервала в случайном порядке.\nПример: A и J → 01 DEBBVHSCI 10",
            10: "ВАРИАНТ 10: XXXXX-XXXXX-XXXX\nТребуется DEC-число (6 знаков).\n1 блок: цифры 4,5,6; 2 блок: цифры 1,2,3; 3 блок: их сумма.\nПример: 726911 → 276DL-191GO-0467"
        }
        
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, descriptions.get(variant, "Описание отсутствует"))
        self.desc_text.config(state=tk.DISABLED)
    
    def generate_key(self):
        """Генерация ключа"""
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
    
    # ========== ВАРИАНТЫ ==========
    
    def variant_1(self):
        blocks = []
        for _ in range(3):
            chars = [random.choice(string.digits) for _ in range(2)]
            chars += [random.choice(string.ascii_uppercase) for _ in range(3)]
            random.shuffle(chars)
            blocks.append(''.join(chars))
        return '-'.join(blocks)
    
    def variant_2(self):
        blocks = []
        for _ in range(4):
            chars = [random.choice(string.digits)]
            chars += [random.choice(string.ascii_uppercase) for _ in range(3)]
            random.shuffle(chars)
            blocks.append(''.join(chars))
        return '-'.join(blocks)
    
    def variant_3(self):
        hex_input = self.input_entry.get().strip().upper()
        if len(hex_input) != 5 or not all(c in string.hexdigits for c in hex_input):
            raise ValueError("Введите HEX-число из 5 знаков (0-9, A-F)!\nПример: 54CD1")
        
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
        def generate_block():
            while True:
                letters = [random.choice(string.ascii_uppercase) for _ in range(4)]
                weight_sum = sum(ord(c) - ord('A') + 1 for c in letters)
                if 30 <= weight_sum <= 35:
                    return ''.join(letters), weight_sum
        
        blocks = []
        for _ in range(3):
            block, _ = generate_block()
            blocks.append(block)
        return '-'.join(blocks)
    
    def variant_5(self):
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
        def generate_block(length):
            while True:
                letters = [random.choice(string.ascii_uppercase) for _ in range(length)]
                weights = [ord(c) - ord('A') + 1 for c in letters]
                avg = sum(weights) / len(weights)
                if 10 <= avg <= 15:
                    return ''.join(letters)
        
        blocks = [generate_block(5), generate_block(4), generate_block(4)]
        return '-'.join(blocks)
    
    def variant_7(self):
        word = self.input_entry.get().strip().upper()
        if len(word) != 6 or not word.isalpha():
            raise ValueError("Введите слово из 6 букв!\nПример: MASTER")
        
        block1 = word[:3]
        block3 = word[3:]
        
        block2 = ''
        for char in word:
            pos = ord(char) - ord('A') + 1
            block2 += str(pos % 10)
        
        return f"{block1} {block2} {block3}"
    
    def variant_8(self):
        dec_input = self.input_entry.get().strip()
        if len(dec_input) != 3 or not dec_input.isdigit():
            raise ValueError("Введите DEC-число из 3 цифр!\nПример: 123")
        
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
        letter1 = random.choice(string.ascii_uppercase)
        letter2 = random.choice(string.ascii_uppercase)
        
        start = min(ord(letter1), ord(letter2))
        end = max(ord(letter1), ord(letter2))
        
        pos1 = start - ord('A') + 1
        pos2 = end - ord('A') + 1
        
        interval_letters = [chr(i) for i in range(start, end + 1)]
        if len(interval_letters) < 8:
            block2_letters = (interval_letters * 2)[:8]
        else:
            block2_letters = random.sample(interval_letters, 8)
        
        random.shuffle(block2_letters)
        
        return f"{pos1:02d} {''.join(block2_letters)} {pos2:02d}"
    
    def variant_10(self):
        dec_input = self.input_entry.get().strip()
        if len(dec_input) != 6 or not dec_input.isdigit():
            raise ValueError("Введите DEC-число из 6 цифр!\nПример: 726911")
        
        digits1 = dec_input[3:6]
        digits2 = dec_input[0:3]
        
        letters1 = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
        block1_chars = list(digits1 + letters1)
        random.shuffle(block1_chars)
        
        letters2 = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
        block2_chars = list(digits2 + letters2)
        random.shuffle(block2_chars)
        
        sum_num = int(digits1) + int(digits2)
        
        return f"{''.join(block1_chars)}-{''.join(block2_chars)}-{str(sum_num).zfill(4)}"
    
    def copy_key(self):
        key = self.key_var.get()
        if key and "Нажмите" not in key:
            self.root.clipboard_clear()
            self.root.clipboard_append(key)
            messagebox.showinfo("Успех", "Ключ скопирован!\nСлава России! 🇷🇺")


def main():
    root = tk.Tk()
    app = KeygenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()