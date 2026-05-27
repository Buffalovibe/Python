"""
Лабораторная работа по ООП в Python
Все варианты заданий (1-10)
Каждый вариант содержит:
- Базовый класс с полями и методом обработки данных
- Иерархию из двух дочерних классов
- Реализацию метода обработки данных в дочерних классах
- Перегрузку оператора __add__ (дополнительное задание)
"""

import math
from abc import ABC, abstractmethod


# ============================================================================
# ВАРИАНТ 1: Здание
# ============================================================================
class Building:
    """Базовый класс Здание"""
    class_name = "Здание"
    objects_count = 0
    
    def __init__(self, area, cost_per_sqm, residents):
        self._area = area
        self._cost_per_sqm = cost_per_sqm
        self._residents = residents
        Building.objects_count += 1
    
    def get_area(self): return self._area
    def get_cost_per_sqm(self): return self._cost_per_sqm
    def get_residents(self): return self._residents
    
    def get_total_cost(self):
        """Метод 1: рассчитать общую стоимость"""
        return self._area * self._cost_per_sqm
    
    def get_cost_per_resident(self):
        """Базовый метод соотношения стоимости к числу проживающих"""
        if self._residents > 0:
            return self.get_total_cost() / self._residents
        return 0
    
    def get_info(self):
        return f"{self.class_name}: {self._area}м², {self.get_total_cost():,.0f}руб, {self._residents} чел."
    
    def __add__(self, other):
        if isinstance(other, Building):
            new_area = self._area + other._area
            total_cost = self.get_total_cost() + other.get_total_cost()
            new_cost_per_sqm = total_cost / new_area if new_area > 0 else 0
            return Building(new_area, new_cost_per_sqm, self._residents + other._residents)
        return NotImplemented


class CountryHouse(Building):
    """Деревенский дом"""
    class_name = "Деревенский дом"
    
    def __init__(self, area, cost_per_sqm, residents, land_area, has_garden):
        super().__init__(area, cost_per_sqm, residents)
        self.land_area = land_area
        self.has_garden = has_garden
    
    def get_cost_per_resident(self):
        """Метод 2: соотношение стоимости к числу проживающих с учетом участка"""
        total_cost = self.get_total_cost() + self.land_area * 50000
        return total_cost / self._residents if self._residents > 0 else 0


class CityApartmentBuilding(Building):
    """Многоквартирный городской дом"""
    class_name = "Многоквартирный дом"
    
    def __init__(self, area, cost_per_sqm, residents, floors, apartments, has_elevator):
        super().__init__(area, cost_per_sqm, residents)
        self.floors = floors
        self.apartments = apartments
        self.has_elevator = has_elevator
    
    def get_cost_per_resident(self):
        """Метод 2: соотношение стоимости к числу проживающих с учетом комфорта"""
        total_cost = self.get_total_cost()
        if self.has_elevator:
            total_cost *= 1.05
        if self.floors > 10:
            total_cost *= 1.03
        return total_cost / self._residents if self._residents > 0 else 0


# ============================================================================
# ВАРИАНТ 2: Станок
# ============================================================================
class Machine:
    """Базовый класс Станок"""
    class_name = "Станок"
    objects_count = 0
    
    def __init__(self, productivity, cost, part_price):
        self._productivity = productivity  # изделий в час
        self._cost = cost  # стоимость станка
        self._part_price = part_price  # средняя цена детали
        Machine.objects_count += 1
    
    def get_productivity(self): return self._productivity
    def get_cost(self): return self._cost
    def get_part_price(self): return self._part_price
    
    def get_parts_for_payback(self):
        """Метод 1: количество деталей для окупаемости"""
        if self._part_price > 0:
            return math.ceil(self._cost / self._part_price)
        return float('inf')
    
    def get_payback_time_hours(self):
        """Базовый метод времени окупаемости"""
        parts_needed = self.get_parts_for_payback()
        if parts_needed != float('inf') and self._productivity > 0:
            return parts_needed / self._productivity
        return float('inf')
    
    def __add__(self, other):
        if isinstance(other, Machine):
            return Machine(
                self._productivity + other._productivity,
                self._cost + other._cost,
                (self._part_price + other._part_price) / 2
            )
        return NotImplemented


class MillingMachine(Machine):
    """Фрезерный станок"""
    class_name = "Фрезерный станок"
    
    def __init__(self, productivity, cost, part_price, spindle_speed, tool_life):
        super().__init__(productivity, cost, part_price)
        self.spindle_speed = spindle_speed  # обороты шпинделя
        self.tool_life = tool_life  # срок службы инструмента (часов)
    
    def get_payback_time_hours(self):
        """Метод 2: время окупаемости с учетом смены инструмента"""
        parts_needed = self.get_parts_for_payback()
        time_hours = parts_needed / self._productivity if self._productivity > 0 else float('inf')
        # Добавляем время на замену инструмента
        tool_changes = time_hours / self.tool_life if self.tool_life > 0 else 0
        return time_hours + tool_changes * 0.5  # 0.5 часа на замену


class CNCMachine(Machine):
    """Станок с ЧПУ"""
    class_name = "Станок с ЧПУ"
    
    def __init__(self, productivity, cost, part_price, accuracy, programming_time):
        super().__init__(productivity, cost, part_price)
        self.accuracy = accuracy  # точность обработки (мм)
        self.programming_time = programming_time  # время программирования (часов)
    
    def get_payback_time_hours(self):
        """Метод 2: время окупаемости с учетом времени программирования"""
        parts_needed = self.get_parts_for_payback()
        production_time = parts_needed / self._productivity if self._productivity > 0 else float('inf')
        return production_time + self.programming_time


# ============================================================================
# ВАРИАНТ 3: Автомобиль
# ============================================================================
class Vehicle:
    """Базовый класс Автомобиль"""
    class_name = "Автомобиль"
    objects_count = 0
    
    def __init__(self, tank_capacity, fuel_consumption, avg_speed):
        self._tank_capacity = tank_capacity  # литры
        self._fuel_consumption = fuel_consumption  # л/100км
        self._avg_speed = avg_speed  # км/ч
        Vehicle.objects_count += 1
    
    def get_tank_capacity(self): return self._tank_capacity
    def get_fuel_consumption(self): return self._fuel_consumption
    def get_avg_speed(self): return self._avg_speed
    
    def get_max_distance(self):
        """Метод 1: расстояние до полного опустошения бака"""
        if self._fuel_consumption > 0:
            return (self._tank_capacity / self._fuel_consumption) * 100
        return 0
    
    def get_fuel_per_250km(self):
        """Базовый метод: топливо на 250 км"""
        return 250 * self._fuel_consumption / 100
    
    def __add__(self, other):
        if isinstance(other, Vehicle):
            return Vehicle(
                self._tank_capacity + other._tank_capacity,
                (self._fuel_consumption + other._fuel_consumption) / 2,
                (self._avg_speed + other._avg_speed) / 2
            )
        return NotImplemented


class Truck(Vehicle):
    """Грузовик"""
    class_name = "Грузовик"
    
    def __init__(self, tank_capacity, fuel_consumption, avg_speed, cargo_weight, max_load):
        super().__init__(tank_capacity, fuel_consumption, avg_speed)
        self.cargo_weight = cargo_weight  # текущий вес груза (кг)
        self.max_load = max_load  # максимальная грузоподъемность (кг)
    
    def get_ratio(self):
        """Метод 2: соотношение веса груза к количеству топлива на 250 км"""
        fuel = self.get_fuel_per_250km()
        if fuel > 0:
            return self.cargo_weight / fuel
        return 0


class Bus(Vehicle):
    """Автобус"""
    class_name = "Автобус"
    
    def __init__(self, tank_capacity, fuel_consumption, avg_speed, passengers, seating_capacity):
        super().__init__(tank_capacity, fuel_consumption, avg_speed)
        self.passengers = passengers  # количество пассажиров
        self.seating_capacity = seating_capacity  # вместимость
    
    def get_ratio(self):
        """Метод 2: соотношение числа пассажиров к количеству топлива на 250 км"""
        fuel = self.get_fuel_per_250km()
        if fuel > 0:
            return self.passengers / fuel
        return 0


# ============================================================================
# ВАРИАНТ 4: Огнестрельное оружие
# ============================================================================
class Firearm:
    """Базовый класс Огнестрельное оружие"""
    class_name = "Огнестрельное оружие"
    objects_count = 0
    
    def __init__(self, ammo_capacity, fire_rate, range_meters):
        self._ammo_capacity = ammo_capacity  # патронов в магазине
        self._fire_rate = fire_rate  # выстрелов в минуту
        self._range = range_meters  # дальность стрельбы (м)
        Firearm.objects_count += 1
    
    def get_empty_time_seconds(self):
        """Метод 1: за сколько секунд опустеет магазин"""
        if self._fire_rate > 0:
            return (self._ammo_capacity / self._fire_rate) * 60
        return float('inf')
    
    def get_ratio(self):
        """Базовый метод: соотношение скорострельности к дальности"""
        if self._range > 0:
            return self._fire_rate / self._range
        return 0
    
    def __add__(self, other):
        if isinstance(other, Firearm):
            return Firearm(
                self._ammo_capacity + other._ammo_capacity,
                (self._fire_rate + other._fire_rate) / 2,
                (self._range + other._range) / 2
            )
        return NotImplemented


class AssaultRifle(Firearm):
    """Штурмовая винтовка"""
    class_name = "Штурмовая винтовка"
    
    def __init__(self, ammo_capacity, fire_rate, range_meters, caliber, weight):
        super().__init__(ammo_capacity, fire_rate, range_meters)
        self.caliber = caliber  # калибр (мм)
        self.weight = weight  # вес (кг)
    
    def get_ratio(self):
        """Метод 2: соотношение скорострельности к дальности с учетом калибра"""
        base_ratio = super().get_ratio()
        return base_ratio * (1 + self.caliber / 10)


class SniperRifle(Firearm):
    """Снайперская винтовка"""
    class_name = "Снайперская винтовка"
    
    def __init__(self, ammo_capacity, fire_rate, range_meters, scope_magnification, accuracy):
        super().__init__(ammo_capacity, fire_rate, range_meters)
        self.scope_magnification = scope_magnification  # кратность прицела
        self.accuracy = accuracy  # точность (MOA)
    
    def get_ratio(self):
        """Метод 2: соотношение скорострельности к дальности с учетом точности"""
        base_ratio = super().get_ratio()
        return base_ratio * (self.accuracy / 2)


# ============================================================================
# ВАРИАНТ 5: Оптический диск
# ============================================================================
class OpticalDisc:
    """Базовый класс Оптический диск"""
    class_name = "Оптический диск"
    objects_count = 0
    
    def __init__(self, capacity_gb, rpm, laser_nm):
        self._capacity = capacity_gb  # ёмкость (ГБ)
        self._rpm = rpm  # обороты в минуту
        self._laser_nm = laser_nm  # размер лазерного пучка (нм)
        OpticalDisc.objects_count += 1
    
    def get_bytes_per_second(self):
        """Базовый метод: сколько байт считывает головка за секунду"""
        # Упрощенная формула: длина окружности * обороты в секунду * плотность записи
        circumference_mm = 120 * math.pi  # диаметр 120мм
        rpm_per_sec = self._rpm / 60
        density = self._capacity * 1e9 / (circumference_mm * 1000)  # байт на мм
        return circumference_mm * rpm_per_sec * density
    
    def get_bytes_in_20_seconds(self):
        """Метод 1: сколько байт считывает лазерная головка за 20 секунд"""
        return self.get_bytes_per_second() * 20
    
    def get_rotation_time_seconds(self):
        """Базовый метод: время одного оборота"""
        if self._rpm > 0:
            return 60 / self._rpm
        return 0
    
    def __add__(self, other):
        if isinstance(other, OpticalDisc):
            return OpticalDisc(
                self._capacity + other._capacity,
                (self._rpm + other._rpm) / 2,
                (self._laser_nm + other._laser_nm) / 2
            )
        return NotImplemented


class CD(OpticalDisc):
    """CD диск"""
    class_name = "CD"
    
    def __init__(self, capacity_gb, rpm, laser_nm, recording_speed, disc_type):
        super().__init__(capacity_gb, rpm, laser_nm)
        self.recording_speed = recording_speed  # скорость записи
        self.disc_type = disc_type  # CD-R, CD-RW и т.д.
    
    def get_rotation_time_seconds(self):
        """Метод 2: среднее время одного оборота (CD имеет постоянную линейную скорость)"""
        # Для CD время оборота меняется, берем среднее
        base_time = super().get_rotation_time_seconds()
        return base_time * 1.2  # коррекция для CD


class DVD(OpticalDisc):
    """DVD диск"""
    class_name = "DVD"
    
    def __init__(self, capacity_gb, rpm, laser_nm, layers, side_type):
        super().__init__(capacity_gb, rpm, laser_nm)
        self.layers = layers  # количество слоев
        self.side_type = side_type  # одно- или двухсторонний
    
    def get_rotation_time_seconds(self):
        """Метод 2: среднее время одного оборота (DVD имеет более высокую плотность)"""
        base_time = super().get_rotation_time_seconds()
        return base_time * 0.8  # коррекция для DVD


# ============================================================================
# ВАРИАНТ 6: Фигура
# ============================================================================
class Shape:
    """Базовый класс Фигура"""
    class_name = "Фигура"
    objects_count = 0
    
    def __init__(self, a, b, c):
        self._a = a
        self._b = b
        self._c = c
        Shape.objects_count += 1
    
    def get_volume(self):
        """Метод 1: объем V = a * b * c"""
        return self._a * self._b * self._c
    
    def get_total_volume(self, count):
        """Базовый метод: суммарный объем нескольких фигур"""
        return self.get_volume() * count
    
    def __add__(self, other):
        if isinstance(other, Shape):
            return Shape(
                self._a + other._a,
                self._b + other._b,
                self._c + other._c
            )
        return NotImplemented


class HollowShape(Shape):
    """Тело с внутренней полостью"""
    class_name = "Тело с полостью"
    
    def __init__(self, a, b, c, d):
        super().__init__(a, b, c)
        self._d = d  # толщина стенки/уменьшение параметров
    
    def get_hollow_volume(self):
        """Объем тела за вычетом пустоты"""
        if self._a > self._d and self._b > self._d and self._c > self._d:
            hollow = Shape(self._a - self._d, self._b - self._d, self._c - self._d)
            return self.get_volume() - hollow.get_volume()
        return self.get_volume()
    
    def get_total_volume(self, count):
        """Метод 2: суммарный объем нескольких одинаковых фигур (с полостью)"""
        return self.get_hollow_volume() * count


class ShapeArray(Shape):
    """Массив из фигур"""
    class_name = "Массив фигур"
    
    def __init__(self, shapes):
        self.shapes = shapes
        Shape.objects_count += 1
    
    def get_total_volume(self, count=None):
        """Метод 2: суммарный объем всех фигур в массиве"""
        total = 0
        for shape in self.shapes:
            total += shape.get_volume()
        return total


# ============================================================================
# ВАРИАНТ 7: Лампа
# ============================================================================
class Lamp:
    """Базовый класс Лампа"""
    class_name = "Лампа"
    objects_count = 0
    
    def __init__(self, power_watts, consumption_watts, lifespan_hours):
        self._power = power_watts  # мощность излучения (Вт)
        self._consumption = consumption_watts  # потребление энергии (Вт)
        self._lifespan = lifespan_hours  # срок службы (часов)
        Lamp.objects_count += 1
    
    def get_days_until_burnout(self, hours_per_day=8):
        """Метод 1: через сколько дней лампа перегорит"""
        if hours_per_day > 0:
            return self._lifespan / hours_per_day
        return 0
    
    def get_efficiency_ratio(self):
        """Базовый метод: соотношение мощности излучения к энергопотреблению"""
        if self._consumption > 0:
            return self._power / self._consumption
        return 0
    
    def __add__(self, other):
        if isinstance(other, Lamp):
            return Lamp(
                self._power + other._power,
                self._consumption + other._consumption,
                (self._lifespan + other._lifespan) / 2
            )
        return NotImplemented


class DaylightLamp(Lamp):
    """Лампа дневного освещения"""
    class_name = "Лампа дневного освещения"
    
    def __init__(self, power_watts, consumption_watts, lifespan_hours, color_temp, cri):
        super().__init__(power_watts, consumption_watts, lifespan_hours)
        self.color_temp = color_temp  # цветовая температура (K)
        self.cri = cri  # индекс цветопередачи
    
    def get_efficiency_ratio(self):
        """Метод 2: соотношение с учетом цветопередачи"""
        base_ratio = super().get_efficiency_ratio()
        return base_ratio * (self.cri / 100)


class Floodlight(Lamp):
    """Прожектор"""
    class_name = "Прожектор"
    
    def __init__(self, power_watts, consumption_watts, lifespan_hours, beam_angle, waterproof):
        super().__init__(power_watts, consumption_watts, lifespan_hours)
        self.beam_angle = beam_angle  # угол луча (градусы)
        self.waterproof = waterproof  # влагозащита (IP)
    
    def get_efficiency_ratio(self):
        """Метод 2: соотношение с учетом угла луча"""
        base_ratio = super().get_efficiency_ratio()
        return base_ratio * (180 / self.beam_angle) if self.beam_angle > 0 else 0


# ============================================================================
# ВАРИАНТ 8: Книга
# ============================================================================
class Book:
    """Базовый класс Книга"""
    class_name = "Книга"
    objects_count = 0
    
    def __init__(self, pages, time_per_page_min, pictures):
        self._pages = pages
        self._time_per_page = time_per_page_min  # минут на страницу
        self._pictures = pictures  # количество картинок
        Book.objects_count += 1
    
    def get_reading_time_minutes(self):
        """Метод 1: время чтения книги (минуты)"""
        return self._pages * self._time_per_page
    
    def get_items_per_page(self):
        """Базовый метод: количество элементов на страницу"""
        if self._pages > 0:
            return 0  # базовый класс не имеет специфических элементов
        return 0
    
    def __add__(self, other):
        if isinstance(other, Book):
            return Book(
                self._pages + other._pages,
                (self._time_per_page + other._time_per_page) / 2,
                self._pictures + other._pictures
            )
        return NotImplemented


class Encyclopedia(Book):
    """Энциклопедия"""
    class_name = "Энциклопедия"
    
    def __init__(self, pages, time_per_page_min, pictures, articles, volumes):
        super().__init__(pages, time_per_page_min, pictures)
        self.articles = articles  # количество статей
        self.volumes = volumes  # количество томов
    
    def get_items_per_page(self):
        """Метод 2: количество статей на страницу"""
        if self._pages > 0:
            return self.articles / self._pages
        return 0


class PhoneBook(Book):
    """Телефонный справочник"""
    class_name = "Телефонный справочник"
    
    def __init__(self, pages, time_per_page_min, pictures, numbers, companies):
        super().__init__(pages, time_per_page_min, pictures)
        self.numbers = numbers  # количество номеров
        self.companies = companies  # количество компаний
    
    def get_items_per_page(self):
        """Метод 2: количество номеров на страницу"""
        if self._pages > 0:
            return self.numbers / self._pages
        return 0


# ============================================================================
# ВАРИАНТ 9: Персонаж видеоигры
# ============================================================================
class Character:
    """Базовый класс Персонаж"""
    class_name = "Персонаж"
    objects_count = 0
    
    def __init__(self, hp, stamina, damage):
        self._hp = hp  # очки здоровья
        self._stamina = stamina  # очки выносливости
        self._damage = damage  # урон
        Character.objects_count += 1
    
    def get_attacks_before_tired(self):
        """Метод 1: сколько ударов наносит персонаж, пока выносливость не кончится"""
        if self._damage > 0:
            return int(self._stamina / self._damage)
        return 0
    
    def get_hits_to_kill(self, target_hp):
        """Базовый метод: сколько ударов понадобится до смерти врага"""
        if self._damage > 0:
            return math.ceil(target_hp / self._damage)
        return float('inf')
    
    def __add__(self, other):
        if isinstance(other, Character):
            return Character(
                self._hp + other._hp,
                self._stamina + other._stamina,
                (self._damage + other._damage) / 2
            )
        return NotImplemented


class WeakEnemy(Character):
    """Слабый враг"""
    class_name = "Слабый враг"
    
    def __init__(self, hp, stamina, damage, experience_reward, drop_chance):
        super().__init__(hp, stamina, damage)
        self.experience_reward = experience_reward
        self.drop_chance = drop_chance
    
    def get_hits_to_kill(self, target_hp):
        """Метод 2: сколько ударов понадобится до смерти (с учетом критического урона)"""
        # Слабые враги имеют шанс на критический урон
        avg_damage = self._damage * (1 + self.drop_chance * 0.5)
        if avg_damage > 0:
            return math.ceil(target_hp / avg_damage)
        return float('inf')


class Boss(Character):
    """Босс"""
    class_name = "Босс"
    
    def __init__(self, hp, stamina, damage, special_attack_damage, special_cooldown):
        super().__init__(hp, stamina, damage)
        self.special_attack_damage = special_attack_damage
        self.special_cooldown = special_cooldown
    
    def get_hits_to_kill(self, target_hp):
        """Метод 2: сколько ударов понадобится до смерти (с учетом спец. атак)"""
        # Босс использует специальные атаки каждые special_cooldown ударов
        normal_hits = math.ceil(target_hp / self._damage) if self._damage > 0 else float('inf')
        # Упрощенная формула с учетом спец. атак
        return normal_hits * 0.7  # босс эффективнее обычных врагов


# ============================================================================
# ВАРИАНТ 10: Сотрудник
# ============================================================================
class Employee:
    """Базовый класс Сотрудник"""
    class_name = "Сотрудник"
    objects_count = 0
    
    def __init__(self, work_hours, rate, bonus_coefficient):
        self._work_hours = work_hours  # количество рабочих часов
        self._rate = rate  # ставка (руб/час)
        self._bonus_coeff = bonus_coefficient  # коэффициент премии
        Employee.objects_count += 1
    
    def get_bonus_amount(self):
        """Метод 1: рассчитать размер премии"""
        base_salary = self._work_hours * self._rate
        return base_salary * self._bonus_coeff
    
    def get_salary_per_hour(self):
        """Базовый метод: соотношение зарплаты к рабочим часам"""
        base_salary = self._work_hours * self._rate
        bonus = self.get_bonus_amount()
        if self._work_hours > 0:
            return (base_salary + bonus) / self._work_hours
        return 0
    
    def __add__(self, other):
        if isinstance(other, Employee):
            return Employee(
                self._work_hours + other._work_hours,
                (self._rate + other._rate) / 2,
                (self._bonus_coeff + other._bonus_coeff) / 2
            )
        return NotImplemented


class SeniorEmployee(Employee):
    """Старший сотрудник"""
    class_name = "Старший сотрудник"
    
    def __init__(self, work_hours, rate, bonus_coefficient, experience_years, projects_managed):
        super().__init__(work_hours, rate, bonus_coefficient)
        self.experience_years = experience_years
        self.projects_managed = projects_managed
    
    def get_salary_per_hour(self):
        """Метод 2: соотношение зарплаты к рабочим часам с учетом опыта"""
        base_per_hour = super().get_salary_per_hour()
        return base_per_hour * (1 + self.experience_years / 100)


class Director(Employee):
    """Директор"""
    class_name = "Директор"
    
    def __init__(self, work_hours, rate, bonus_coefficient, employees_count, company_profit):
        super().__init__(work_hours, rate, bonus_coefficient)
        self.employees_count = employees_count
        self.company_profit = company_profit
    
    def get_salary_per_hour(self):
        """Метод 2: соотношение зарплаты к рабочим часам с учетом прибыли компании"""
        base_per_hour = super().get_salary_per_hour()
        profit_bonus = self.company_profit / 10000  # бонус от прибыли
        return base_per_hour + profit_bonus


# ============================================================================
# ДЕМОНСТРАЦИЯ ВСЕХ ВАРИАНТОВ
# ============================================================================

def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def demo_variant1():
    print_header("ВАРИАНТ 1: Здание")
    
    building = Building(150, 50000, 4)
    country = CountryHouse(120, 45000, 3, 15, True)
    city = CityApartmentBuilding(5000, 120000, 320, 16, 120, True)
    
    print(f"Базовый: {building.get_info()}")
    print(f"Общая стоимость: {building.get_total_cost():,.0f} руб.")
    print(f"Деревенский дом: {country.get_info()}")
    print(f"Стоимость на проживающего: {country.get_cost_per_resident():,.0f} руб.")
    print(f"Многоквартирный: {city.get_info()}")
    print(f"Стоимость на проживающего: {city.get_cost_per_resident():,.0f} руб.")
    
    # Демонстрация __add__
    combined = building + country
    print(f"Сложение зданий: {combined.get_info()}")


def demo_variant2():
    print_header("ВАРИАНТ 2: Станок")
    
    machine = Machine(50, 500000, 1000)
    milling = MillingMachine(40, 600000, 1200, 12000, 500)
    cnc = CNCMachine(60, 800000, 1000, 0.01, 8)
    
    print(f"Базовый станок: деталей для окупаемости = {machine.get_parts_for_payback()}")
    print(f"Фрезерный: время окупаемости = {milling.get_payback_time_hours():.1f} ч")
    print(f"Станок с ЧПУ: время окупаемости = {cnc.get_payback_time_hours():.1f} ч")
    
    combined = machine + cnc
    print(f"Сложение станков: деталей для окупаемости = {combined.get_parts_for_payback()}")


def demo_variant3():
    print_header("ВАРИАНТ 3: Автомобиль")
    
    vehicle = Vehicle(60, 8.5, 90)
    truck = Truck(120, 15, 80, 5000, 8000)
    bus = Bus(200, 12, 70, 40, 50)
    
    print(f"Базовый: максимальное расстояние = {vehicle.get_max_distance():.1f} км")
    print(f"Грузовик: соотношение веса/топливо на 250км = {truck.get_ratio():.2f}")
    print(f"Автобус: соотношение пассажиров/топливо на 250км = {bus.get_ratio():.2f}")
    
    combined = vehicle + bus
    print(f"Сложение авто: расстояние = {combined.get_max_distance():.1f} км")


def demo_variant4():
    print_header("ВАРИАНТ 4: Огнестрельное оружие")
    
    firearm = Firearm(30, 600, 500)
    assault = AssaultRifle(30, 700, 400, 5.56, 3.5)
    sniper = SniperRifle(5, 60, 1200, 10, 0.5)
    
    print(f"Базовый: время опустошения магазина = {firearm.get_empty_time_seconds():.1f} сек")
    print(f"Штурмовая: соотношение = {assault.get_ratio():.3f}")
    print(f"Снайперская: соотношение = {sniper.get_ratio():.3f}")
    
    combined = assault + sniper
    print(f"Сложение оружия: время = {combined.get_empty_time_seconds():.1f} сек")


def demo_variant5():
    print_header("ВАРИАНТ 5: Оптический диск")
    
    disc = OpticalDisc(4.7, 5000, 780)
    cd = CD(0.7, 4000, 780, 52, "CD-R")
    dvd = DVD(4.7, 10000, 650, 2, "двухсторонний")
    
    print(f"Базовый: байт за 20 сек = {disc.get_bytes_in_20_seconds() / 1e6:.2f} МБ")
    print(f"CD: время оборота = {cd.get_rotation_time_seconds():.4f} сек")
    print(f"DVD: время оборота = {dvd.get_rotation_time_seconds():.4f} сек")
    
    combined = cd + dvd
    print(f"Сложение дисков: МБ за 20 сек = {combined.get_bytes_in_20_seconds() / 1e6:.2f}")


def demo_variant6():
    print_header("ВАРИАНТ 6: Фигура")
    
    shape = Shape(10, 20, 30)
    hollow = HollowShape(10, 20, 30, 2)
    shape_array = ShapeArray([Shape(5, 5, 5), Shape(3, 4, 5), Shape(2, 3, 4)])
    
    print(f"Базовый: объем = {shape.get_volume()}")
    print(f"С полостью: объем полого тела = {hollow.get_hollow_volume()}")
    print(f"Суммарный объем 3 фигур = {hollow.get_total_volume(3)}")
    print(f"Массив фигур: суммарный объем = {shape_array.get_total_volume()}")
    
    combined = shape + hollow
    print(f"Сложение фигур: объем = {combined.get_volume()}")


def demo_variant7():
    print_header("ВАРИАНТ 7: Лампа")
    
    lamp = Lamp(800, 60, 20000)
    daylight = DaylightLamp(1000, 50, 25000, 5000, 85)
    floodlight = Floodlight(2000, 150, 10000, 120, "IP65")
    
    print(f"Базовый: дней до перегорания = {lamp.get_days_until_burnout():.0f}")
    print(f"Дневного света: эффективность = {daylight.get_efficiency_ratio():.3f}")
    print(f"Прожектор: эффективность = {floodlight.get_efficiency_ratio():.3f}")
    
    combined = lamp + floodlight
    print(f"Сложение ламп: дней = {combined.get_days_until_burnout():.0f}")


def demo_variant8():
    print_header("ВАРИАНТ 8: Книга")
    
    book = Book(300, 1.5, 20)
    encyclopedia = Encyclopedia(1000, 2, 500, 5000, 10)
    phonebook = PhoneBook(500, 0.5, 0, 10000, 2000)
    
    print(f"Базовый: время чтения = {book.get_reading_time_minutes():.0f} мин")
    print(f"Энциклопедия: статей на страницу = {encyclopedia.get_items_per_page():.2f}")
    print(f"Телефонный справочник: номеров на страницу = {phonebook.get_items_per_page():.2f}")
    
    combined = book + encyclopedia
    print(f"Сложение книг: время = {combined.get_reading_time_minutes():.0f} мин")


def demo_variant9():
    print_header("ВАРИАНТ 9: Персонаж видеоигры")
    
    char = Character(100, 100, 20)
    weak = WeakEnemy(30, 50, 8, 100, 0.3)
    boss = Boss(500, 200, 25, 50, 5)
    
    print(f"Базовый: ударов до усталости = {char.get_attacks_before_tired()}")
    print(f"Слабый враг: ударов до смерти = {weak.get_hits_to_kill(100)}")
    print(f"Босс: ударов до смерти = {boss.get_hits_to_kill(500)}")
    
    combined = weak + boss
    print(f"Сложение персонажей: ударов до усталости = {combined.get_attacks_before_tired()}")


def demo_variant10():
    print_header("ВАРИАНТ 10: Сотрудник")
    
    emp = Employee(160, 500, 0.2)
    senior = SeniorEmployee(160, 800, 0.3, 10, 15)
    director = Director(180, 1500, 0.5, 100, 5000000)
    
    print(f"Базовый: премия = {emp.get_bonus_amount():,.0f} руб")
    print(f"Старший сотрудник: зарплата/час = {senior.get_salary_per_hour():.0f} руб")
    print(f"Директор: зарплата/час = {director.get_salary_per_hour():.0f} руб")
    
    combined = emp + director
    print(f"Сложение сотрудников: премия = {combined.get_bonus_amount():,.0f} руб")


def main():
    print("\n" + "█" * 80)
    print("ЛАБОРАТОРНАЯ РАБОТА ПО ООП В PYTHON")
    print("РЕАЛИЗАЦИЯ ВСЕХ 10 ВАРИАНТОВ ЗАДАНИЙ")
    print("█" * 80)
    
    demo_variant1()
    demo_variant2()
    demo_variant3()
    demo_variant4()
    demo_variant5()
    demo_variant6()
    demo_variant7()
    demo_variant8()
    demo_variant9()
    demo_variant10()

    print_header("ИТОГОВАЯ СТАТИСТИКА")
    print(f"Всего создано объектов класса Building: {Building.objects_count}")
    print(f"Всего создано объектов класса Machine: {Machine.objects_count}")
    print(f"Всего создано объектов класса Vehicle: {Vehicle.objects_count}")
    print(f"Всего создано объектов класса Firearm: {Firearm.objects_count}")
    print(f"Всего создано объектов класса OpticalDisc: {OpticalDisc.objects_count}")
    print(f"Всего создано объектов класса Shape: {Shape.objects_count}")
    print(f"Всего создано объектов класса Lamp: {Lamp.objects_count}")
    print(f"Всего создано объектов класса Book: {Book.objects_count}")
    print(f"Всего создано объектов класса Character: {Character.objects_count}")
    print(f"Всего создано объектов класса Employee: {Employee.objects_count}")
    print("\n" + "█" * 80)


if __name__ == "__main__":
    main()