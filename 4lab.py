def solve_knapsack(items, capacity, required_item=None):
    """
    Решает задачу о рюкзаке методом динамического программирования.
    items: список кортежей (название, размер, ценность)
    capacity: максимальная вместимость хранилища
    required_item: обязательный предмет (если есть)
    Возвращает: (максимальная ценность, список выбранных предметов)
    """
    n = len(items)
    if required_item:
        required_size = None
        required_value = None
        required_index = None
        for i, (name, size, value) in enumerate(items):
            if name == required_item:
                required_size = size
                required_value = value
                required_index = i
                break
        if required_size is None:
            raise ValueError(f"Обязательный предмет {required_item} не найден в списке")
        if required_size > capacity:
            return 0, [] 
        remaining_items = [item for j, item in enumerate(items) if j != required_index]
        new_capacity = capacity - required_size
        value, chosen = solve_knapsack(remaining_items, new_capacity, required_item=None)
        return value + required_value, [required_item] + chosen
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    choice = [[None] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        name, size, value = items[i - 1]
        for w in range(capacity + 1):
            if size <= w and dp[i - 1][w - size] + value > dp[i - 1][w]:
                dp[i][w] = dp[i - 1][w - size] + value
                choice[i][w] = (i - 1, w - size)
            else:
                dp[i][w] = dp[i - 1][w]
                choice[i][w] = (i - 1, w)
    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        if choice[i][w] != (i - 1, w):
            selected_items.append(items[i - 1][0])
            w = choice[i][w][1]
    return dp[n][capacity], selected_items[::-1]
def display_solution(selected_items, item_sizes):
    """
    Отображает решение в виде набора ячеек, как в примере:
    [r], [r], [r]
    [p], [p], [a], [a] и т.д.    """
    grid = []
    for item in selected_items:
        size = item_sizes[item]
        for _ in range(size):
            grid.append(item)
    print("Решение в виде набора ячеек:")
    row_size = 3
    for i in range(0, len(grid), row_size):
        row = grid[i:i + row_size]
        print(" ".join(f"[{x}]" for x in row))
def main():
    items = [
        ("r", 3, 25),("p", 2, 15),("a", 2, 15),("m", 2, 20),("l", 1, 5),("k", 1, 15),("x", 3, 20),("h", 1, 25),("f", 1, 15),("d", 1, 10),("s", 2, 20),("c", 2, 20)     
    ]
    item_sizes = {name: size for name, size, _ in items}
    variant_data = {
        1: ((2, 4), None, 15),2: ((3, 3), "l", 10),3: ((2, 4), "d", 10),4: ((3, 3), None, 15),5: ((2, 4), "l", 20),6: ((3, 3), "d", 13),7: ((2, 4), None, 15),8: ((3, 3), "l", 15), 9: ((2, 4), "d", 20), 10: ((3, 3), None, 10),
    }
    print("Доступные варианты: 1-10")
    try:
        variant = int(input("Введите номер варианта (1-10): "))
    except ValueError:
        print("Ошибка: введите число")
        return
    if variant not in variant_data:
        print("Неверный номер варианта")
        return
    (rows, cols), required, start_points = variant_data[variant]
    capacity = rows * cols
    print(f"\nВариант {variant}: хранилище {rows}x{cols} (вместимость {capacity}), стартовые очки {start_points}")
    working_items = items.copy()
    if required:
        required_found = False
        for item in working_items:
            if item[0] == required:
                required_found = True
                break        
        if not required_found:
            print(f"Ошибка: обязательный предмет '{required}' не найден в списке")
            return
        if required == "l":
            start_points += 5
            print(f"Ингалятор обязателен. Добавлено +5 очков. Стартовые очки: {start_points}")
        elif required == "d":
            start_points += 10
            print(f"Антидот обязателен. Добавлено +10 очков. Стартовые очки: {start_points}")
        working_items = [item for item in working_items if item[0] != required]
        print(f"Обязательный предмет '{required}' удалён из списка выбора")
    max_value, selected = solve_knapsack(working_items, capacity, required_item=None)
    if required:
        selected = [required] + selected
    total_points = start_points + max_value
    print(f"\nОчки выживания от выбранных предметов: {max_value}")
    print(f"Итоговые очки выживания (с учётом стартовых): {total_points}")
    if total_points <= 0:
        print("\nВНИМАНИЕ: итоговые очки выживания не положительны! Решение недопустимо.")
    else:
        print("\nОптимальный набор предметов:")
        print(selected)
        total_size = sum(item_sizes[item] for item in selected)
        print(f"\nОбщий размер выбранных предметов: {total_size} ячеек")
        print(f"Вместимость хранилища: {capacity} ячеек")        
        if total_size <= capacity:
            print("✓ Все предметы помещаются в хранилище")
        else:
            print("✗ ОШИБКА: Предметы не помещаются в хранилище!")       
        display_solution(selected, item_sizes)
if __name__ == "__main__":
    main()