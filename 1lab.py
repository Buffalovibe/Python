# AAA ZOMBIE SHOOTER 3D
# Полноценная 3D игра с современной архитектурой

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader
import random
import math
import time

app = Ursina()

# Настройки окна
window.title = 'AAA Zombie Shooter'
window.borderless = False
window.exit_button.visible = False
window.fps_counter.enabled = True
window.color = color.black

# Глобальные переменные
game_state = 'playing'  # playing, paused, game_over
score = 0
wave = 1
ammo = 30
max_ammo = 30
is_reloading = False
reload_timer = 0
last_shot_time = 0
shot_cooldown = 0.1
zombies_killed = 0
spawn_timer = 0
spawn_interval = 3.0

# Списки объектов
zombies = []
bullets = []
particles = []
decals = []

# === КЛАСС ОРУЖИЯ ===
class WeaponSystem:
    def __init__(self):
        self.parent = Entity(parent=camera)
        self.recoil_offset = Vec3(0, 0, 0)
        self.sway_offset = Vec3(0, 0, 0)
        
        # Основное тело оружия
        self.body = Entity(
            parent=self.parent,
            model='cube',
            position=Vec3(0.35, -0.25, 0.6),
            scale=Vec3(0.08, 0.12, 0.4),
            color=color.rgb(40, 40, 40)
        )
        
        # Рукоять
        self.grip = Entity(
            parent=self.body,
            model='cube',
            position=Vec3(0, -0.12, -0.1),
            scale=Vec3(0.9, 0.8, 0.6),
            color=color.rgb(30, 30, 30)
        )
        
        # Ствол
        self.barrel = Entity(
            parent=self.body,
            model='cylinder',
            position=Vec3(0, 0.02, 0.25),
            scale=Vec3(0.04, 0.15, 0.04),
            color=color.rgb(20, 20, 20),
            rotation=Vec3(90, 0, 0)
        )
        
        # Мушка
        self.sight = Entity(
            parent=self.body,
            model='cube',
            position=Vec3(0, 0.08, 0.05),
            scale=Vec3(0.02, 0.06, 0.1),
            color=color.rgb(50, 50, 50)
        )
        
        # Магазин
        self.mag = Entity(
            parent=self.body,
            model='cube',
            position=Vec3(0, -0.08, 0),
            scale=Vec3(0.07, 0.15, 0.15),
            color=color.rgb(25, 25, 25),
            rotation=Vec3(15, 0, 0)
        )
        
        # Дульная вспышка
        self.muzzle_flash = Entity(
            parent=self.barrel,
            model='quad',
            position=Vec3(0, 0.08, 0),
            scale=0.15,
            color=color.yellow,
            enabled=False,
            billboard=True
        )
        
        # Свет от выстрела
        self.flash_light = PointLight(
            parent=self.barrel,
            position=Vec3(0, 0.1, 0),
            color=color.yellow,
            range=5,
            enabled=False
        )
        
    def update(self):
        # Покачивание оружия при движении
        sway_x = math.sin(time.time() * 2) * 0.005 if held_keys['a'] or held_keys['d'] else 0
        sway_y = math.cos(time.time() * 3) * 0.005 if held_keys['w'] or held_keys['s'] else 0
        
        # Плавное возвращение после отдачи
        self.recoil_offset = lerp(self.recoil_offset, Vec3(0, 0, 0), 5 * time.dt)
        
        target_pos = Vec3(0.35 + sway_x, -0.25 + sway_y, 0.6) + self.recoil_offset
        self.body.position = lerp(self.body.position, target_pos, 10 * time.dt)
        
    def shoot(self):
        global last_shot_time
        
        current_time = time.time()
        if current_time - last_shot_time < shot_cooldown:
            return False
            
        last_shot_time = current_time
        
        # Отдача
        self.recoil_offset = Vec3(0, 0.05, 0.1)
        
        # Вспышка
        self.muzzle_flash.enabled = True
        self.flash_light.enabled = True
        
        # Эффект случайного размера вспышки
        self.muzzle_flash.scale = random.uniform(0.1, 0.2)
        
        invoke(setattr, self.muzzle_flash, 'enabled', False, delay=0.05)
        invoke(setattr, self.flash_light, 'enabled', False, delay=0.05)
        
        return True
        
    def reload_animation(self):
        # Анимация перезарядки
        self.body.animate_position(Vec3(0.35, -0.4, 0.4), duration=0.3, curve=curve.out_expo)
        self.body.animate_rotation(Vec3(-30, 0, 0), duration=0.3)
        
    def reset_position(self):
        self.body.animate_position(Vec3(0.35, -0.25, 0.6), duration=0.3)
        self.body.animate_rotation(Vec3(0, 0, 0), duration=0.3)

# === КЛАСС ПУЛИ ===
class Bullet(Entity):
    def __init__(self, start_pos, direction):
        super().__init__(
            model='sphere',
            scale=0.06,
            position=start_pos,
            color=color.yellow,
            collider='sphere'
        )
        self.direction = direction
        self.speed = 150
        self.lifetime = 2.0
        self.trail_positions = []
        
        # Создаем след
        self.create_trail()
        
    def create_trail(self):
        # Визуальный след от пули
        trail = Entity(
            model='cube',
            scale=Vec3(0.02, 0.02, 0.5),
            position=self.position - self.direction * 0.3,
            rotation=Vec3(
                math.degrees(math.asin(self.direction.y)),
                math.degrees(math.atan2(self.direction.x, self.direction.z)) + 180,
                0
            ),
            color=color.orange,
            alpha=0.6
        )
        destroy(trail, delay=0.1)
        
    def update(self):
        self.lifetime -= time.dt
        
        # Движение
        self.position += self.direction * self.speed * time.dt
        
        # Проверка столкновений
        hit_info = self.intersects()
        if hit_info.hit:
            if hasattr(hit_info.entity, 'is_zombie') and hit_info.entity.is_zombie:
                hit_info.entity.take_damage(34, self.position)
                self.create_impact(hit_info.entity.position)
                destroy(self)
                return
            elif hit_info.entity not in [player, weapon.body, weapon.grip, weapon.barrel]:
                self.create_impact(self.position)
                create_bullet_hole(self.position, hit_info.normal)
                destroy(self)
                return
                
        if self.lifetime <= 0:
            destroy(self)
            
    def create_impact(self, pos):
        # Эффект попадания
        for i in range(5):
            Particle(
                position=pos + Vec3(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)),
                color=color.yellow,
                size=random.uniform(0.02, 0.05),
                velocity=Vec3(random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)),
                lifetime=0.2
            )

# === КЛАСС ЧАСТИЦ ===
class Particle(Entity):
    def __init__(self, position, color, size, velocity, lifetime):
        super().__init__(
            model='quad',
            position=position,
            scale=size,
            color=color,
            billboard=True
        )
        self.velocity = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        
    def update(self):
        self.lifetime -= time.dt
        self.position += self.velocity * time.dt
        self.alpha = self.lifetime / self.max_lifetime
        
        if self.lifetime <= 0:
            destroy(self)

# === КЛАСС ЗОМБИ ===
class Zombie(Entity):
    def __init__(self, spawn_pos):
        super().__init__(
            model='cube',
            position=spawn_pos,
            scale=Vec3(0.6, 1.8, 0.4),
            color=color.rgb(80, 120, 60),
            collider='box'
        )
        self.is_zombie = True
        self.health = 100
        self.max_health = 100
        self.speed = random.uniform(2.5, 4.0)
        self.attack_damage = 10
        self.attack_cooldown = 0
        self.animation_time = 0
        self.is_dead = False
        
        # Голова
        self.head = Entity(
            parent=self,
            model='sphere',
            position=Vec3(0, 0.9, 0),
            scale=0.35,
            color=color.rgb(80, 120, 60)
        )
        
        # Лицо
        self.face = Entity(
            parent=self.head,
            model='plane',
            position=Vec3(0, 0, 0.3),
            scale=0.25,
            color=color.rgb(60, 90, 40),
            rotation=Vec3(0, 180, 0)
        )
        
        # Глаза (светящиеся)
        self.eye_left = Entity(
            parent=self.head,
            model='sphere',
            position=Vec3(-0.1, 0.05, 0.25),
            scale=0.05,
            color=color.red
        )
        self.eye_right = Entity(
            parent=self.head,
            model='sphere',
            position=Vec3(0.1, 0.05, 0.25),
            scale=0.05,
            color=color.red
        )
        
        # Руки
        self.arm_left = Entity(
            parent=self,
            model='cube',
            position=Vec3(-0.45, 0.2, 0.2),
            scale=Vec3(0.15, 0.7, 0.15),
            color=color.rgb(70, 110, 50)
        )
        self.arm_right = Entity(
            parent=self,
            model='cube',
            position=Vec3(0.45, 0.2, 0.2),
            scale=Vec3(0.15, 0.7, 0.15),
            color=color.rgb(70, 110, 50)
        )
        
        # Ноги
        self.leg_left = Entity(
            parent=self,
            model='cube',
            position=Vec3(-0.2, -0.9, 0),
            scale=Vec3(0.2, 0.9, 0.2),
            color=color.rgb(60, 100, 40)
        )
        self.leg_right = Entity(
            parent=self,
            model='cube',
            position=Vec3(0.2, -0.9, 0),
            scale=Vec3(0.2, 0.9, 0.2),
            color=color.rgb(60, 100, 40)
        )
        
        # HP bar над головой
        self.hp_bg = Entity(
            parent=self,
            model='quad',
            position=Vec3(0, 1.4, 0),
            scale=Vec3(0.5, 0.05, 1),
            color=color.black,
            billboard=True,
            enabled=False
        )
        self.hp_bar = Entity(
            parent=self.hp_bg,
            model='quad',
            position=Vec3(-0.5, 0, 0),
            scale=Vec3(1, 1, 1),
            color=color.red,
            origin=Vec3(-0.5, 0, 0)
        )
        
    def take_damage(self, damage, hit_pos):
        if self.is_dead:
            return
            
        self.health -= damage
        
        # Показываем HP bar
        self.hp_bg.enabled = True
        self.hp_bar.scale_x = max(0, self.health / self.max_health)
        
        # Эффект попадания
        self.flash_white()
        
        # Кровь
        create_blood_splash(hit_pos)
        
        if self.health <= 0:
            self.die()
            
    def flash_white(self):
        # Мигание белым при уроне
        original_colors = [self.color, self.head.color, self.arm_left.color, self.arm_right.color]
        self.color = color.white
        self.head.color = color.white
        self.arm_left.color = color.white
        self.arm_right.color = color.white
        
        invoke(self.restore_color, original_colors, delay=0.1)
        
    def restore_color(self, colors):
        self.color = colors[0]
        self.head.color = colors[1]
        self.arm_left.color = colors[2]
        self.arm_right.color = colors[3]
        
    def die(self):
        global score, zombies_killed
        if self.is_dead:
            return
            
        self.is_dead = True
        score += 10
        zombies_killed += 1
        update_ui()
        
        # Ragdoll эффект (простая версия)
        self.color = color.dark_gray
        self.head.color = color.dark_gray
        
        # Удаляем через время
        destroy(self.hp_bg)
        destroy(self, delay=3)
        if self in zombies:
            zombies.remove(self)
            
    def update(self):
        if self.is_dead or not player.enabled:
            return
            
        # Преследование игрока
        direction = (player.position - self.position).normalized()
        direction.y = 0
        
        distance_to_player = distance(self.position, player.position)
        
        if distance_to_player > 1.2:
            # Движение
            self.position += direction * self.speed * time.dt
            self.look_at(player.position)
            
            # Анимация ходьбы
            self.animation_time += time.dt * 8
            self.leg_left.rotation_x = math.sin(self.animation_time) * 30
            self.leg_right.rotation_x = -math.sin(self.animation_time) * 30
            self.arm_left.rotation_x = -math.sin(self.animation_time) * 20
            self.arm_right.rotation_x = math.sin(self.animation_time) * 20
            
            # Покачивание тела
            self.position.y = 0.9 + abs(math.sin(self.animation_time * 2)) * 0.05
            
        else:
            # Атака
            self.attack_cooldown -= time.dt
            if self.attack_cooldown <= 0:
                self.attack()
                self.attack_cooldown = 1.0
                
    def attack(self):
        global health
        health -= self.attack_damage
        update_ui()
        
        # Эффект атаки
        camera.shake(duration=0.3, magnitude=0.15)
        
        # Красный всплеск на экране
        damage_overlay = Entity(
            parent=camera.ui,
            model='quad',
            color=color.red,
            scale=Vec3(2, 2, 1),
            alpha=0.3
        )
        destroy(damage_overlay, delay=0.1)
        
        if health <= 0:
            game_over()

# === ЭФФЕКТЫ ===
def create_blood_splash(pos):
    # Эффект крови
    for i in range(8):
        Particle(
            position=pos + Vec3(random.uniform(-0.2, 0.2), random.uniform(0, 0.5), random.uniform(-0.2, 0.2)),
            color=color.red,
            size=random.uniform(0.05, 0.15),
            velocity=Vec3(random.uniform(-3, 3), random.uniform(1, 5), random.uniform(-3, 3)),
            lifetime=0.5
        )
        
    # Лужа крови (decal)
    blood = Entity(
        model='circle',
        position=Vec3(pos.x, 0.02, pos.z),
        scale=random.uniform(0.5, 1.0),
        color=color.rgb(100, 0, 0),
        rotation=Vec3(90, random.uniform(0, 360), 0)
    )
    destroy(blood, delay=10)

def create_bullet_hole(pos, normal):
    # Отверстие от пули
    hole = Entity(
        model='circle',
        position=pos + normal * 0.01,
        scale=0.05,
        color=color.black,
        rotation=Vec3(90, 0, 0)
    )
    # Ориентация по нормали
    hole.look_at(pos + normal)
    destroy(hole, delay=5)

# === ИГРОВОЙ МИР ===
def create_world():
    # Земля с текстурой-шашечкой
    ground = Entity(
        model='plane',
        scale=Vec3(100, 1, 100),
        color=color.rgb(50, 70, 50),
        collider='box'
    )
    
    # Сетка на земле
    for i in range(-10, 11, 2):
        Entity(
            model='cube',
            scale=Vec3(0.1, 0.01, 100),
            position=Vec3(i * 5, 0.01, 0),
            color=color.rgb(40, 60, 40)
        )
        Entity(
            model='cube',
            scale=Vec3(100, 0.01, 0.1),
            position=Vec3(0, 0.01, i * 5),
            color=color.rgb(40, 60, 40)
        )
    
    # Препятствия
    for i in range(20):
        x = random.uniform(-45, 45)
        z = random.uniform(-45, 45)
        if abs(x) > 10 or abs(z) > 10:
            size = random.uniform(2, 5)
            height = random.uniform(3, 8)
            Entity(
                model='cube',
                scale=Vec3(size, height, size),
                position=Vec3(x, height/2, z),
                color=color.rgb(60, 60, 60),
                collider='box'
            )

# === UI ===
def create_ui():
    # Прицел
    global crosshair, crosshair_dot
    crosshair = Entity(
        parent=camera.ui,
        model='circle',
        color=color.red,
        scale=0.02
    )
    crosshair_dot = Entity(
        parent=camera.ui,
        model='circle',
        color=color.black,
        scale=0.005
    )
    
    # Патроны
    global ammo_text, ammo_label
    ammo_label = Text(
        text='AMMO',
        position=Vec2(0.65, -0.42),
        scale=1.2,
        color=color.gray
    )
    ammo_text = Text(
        text='30 / 30',
        position=Vec2(0.65, -0.46),
        scale=1.8,
        color=color.yellow
    )
    
    # Здоровье
    global health_bar, health_bg, health_text
    health_bg = Entity(
        parent=camera.ui,
        model='quad',
        color=color.dark_gray,
        scale=Vec3(0.3, 0.04, 1),
        position=Vec3(-0.65, -0.44, 0)
    )
    health_bar = Entity(
        parent=camera.ui,
        model='quad',
        color=color.red,
        scale=Vec3(0.28, 0.03, 1),
        position=Vec3(-0.79, -0.44, 0),
        origin=Vec3(-0.5, 0, 0)
    )
    health_text = Text(
        text='100 HP',
        position=Vec2(-0.78, -0.445),
        scale=1.2,
        color=color.white
    )
    
    # Счет
    global score_text, wave_text
    score_text = Text(
        text='Score: 0',
        position=Vec2(-0.85, 0.45),
        scale=1.5,
        color=color.white
    )
    wave_text = Text(
        text='Wave 1',
        position=Vec2(0.75, 0.45),
        scale=1.5,
        color=color.orange
    )
    
    # Сообщения
    global reload_text, no_ammo_text
    reload_text = Text(
        text='RELOADING',
        position=Vec2(0, 0.1),
        scale=3,
        color=color.orange,
        enabled=False
    )
    no_ammo_text = Text(
        text='PRESS R TO RELOAD',
        position=Vec2(0, 0.1),
        scale=2,
        color=color.red,
        enabled=False
    )

def update_ui():
    ammo_text.text = f'{ammo} / {max_ammo}'
    score_text.text = f'Score: {score}'
    wave_text.text = f'Wave {wave}'
    health_bar.scale_x = max(0.001, health / 100 * 0.28)
    health_text.text = f'{int(max(0, health))} HP'
    
    # Цвет здоровья
    if health > 60:
        health_bar.color = color.green
    elif health > 30:
        health_bar.color = color.yellow
    else:
        health_bar.color = color.red

# === ИГРОВАЯ ЛОГИКА ===
def spawn_zombie():
    angle = random.uniform(0, 360)
    dist = random.uniform(25, 40)
    x = player.position.x + math.cos(math.radians(angle)) * dist
    z = player.position.z + math.sin(math.radians(angle)) * dist
    
    zombie = Zombie(Vec3(x, 0.9, z))
    zombies.append(zombie)

def shoot():
    global ammo, last_shot_time
    
    if is_reloading:
        return
        
    if ammo <= 0:
        no_ammo_text.enabled = True
        invoke(setattr, no_ammo_text, 'enabled', False, delay=1.0)
        return
    
    if not weapon.shoot():
        return
        
    ammo -= 1
    update_ui()
    
    # Создание пули
    bullet_start = camera.position + camera.forward * 1.5
    bullet = Bullet(bullet_start, camera.forward)
    bullets.append(bullet)
    
    # Тряска камеры
    camera.shake(duration=0.05, magnitude=0.02)

def reload():
    global is_reloading, reload_timer
    
    if is_reloading or ammo == max_ammo:
        return
        
    is_reloading = True
    reload_timer = 2.0
    reload_text.enabled = True
    
    weapon.reload_animation()
    
    invoke(finish_reload, delay=2.0)

def finish_reload():
    global is_reloading, ammo
    is_reloading = False
    ammo = max_ammo
    update_ui()
    reload_text.enabled = False
    weapon.reset_position()

def game_over():
    global game_state
    game_state = 'game_over'
    player.enabled = False
    mouse.visible = True
    
    # Экран смерти
    bg = Entity(
        parent=camera.ui,
        model='quad',
        color=color.black,
        scale=Vec3(2, 2, 1),
        alpha=0.8
    )
    
    Text(
        parent=camera.ui,
        text='MISSION FAILED',
        position=Vec2(0, 0.15),
        scale=4,
        color=color.red,
        origin=Vec2(0, 0)
    )
    
    Text(
        parent=camera.ui,
        text=f'Final Score: {score}',
        position=Vec2(0, 0),
        scale=2,
        origin=Vec2(0, 0)
    )
    
    Text(
        parent=camera.ui,
        text='Press R to restart',
        position=Vec2(0, -0.15),
        scale=1.5,
        color=color.yellow,
        origin=Vec2(0, 0)
    )

def restart():
    global score, wave, ammo, health, zombies_killed, is_reloading, game_state
    
    # Сброс переменных
    score = 0
    wave = 1
    ammo = 30
    health = 100
    zombies_killed = 0
    is_reloading = False
    game_state = 'playing'
    
    # Сброс игрока
    player.position = Vec3(0, 2, 0)
    player.health = 100
    player.enabled = True
    mouse.visible = False
    
    # Очистка зомби
    for z in zombies[:]:
        destroy(z)
    zombies.clear()
    
    # Очистка UI
    for child in camera.ui.children[:]:
        destroy(child)
    create_ui()
    update_ui()

# === ИНИЦИАЛИЗАЦИЯ ===
create_world()
create_ui()

player = FirstPersonController(
    position=Vec3(0, 2, 0),
    speed=10,
    jump_height=1.2,
    mouse_sensitivity=Vec2(40, 40)
)
player.health = 100
player.cursor.visible = False

weapon = WeaponSystem()

# Освещение
sun = DirectionalLight()
sun.look_at(Vec3(1, -2, -1))
sun.shadows = True

ambient = AmbientLight(color=color.rgb(80, 80, 80))

sky = Sky(color=color.rgb(100, 150, 200))

# === ГЛАВНЫЙ ЦИКЛ ===
def update():
    global spawn_timer, spawn_interval, wave
    
    if game_state != 'playing':
        if held_keys['r']:
            restart()
        return
    
    # Обновление оружия
    weapon.update()
    
    # Стрельба
    if mouse.left:
        shoot()
    
    # Прицеливание
    if mouse.right:
        camera.fov = lerp(camera.fov, 60, 10 * time.dt)
        crosshair.scale = lerp(crosshair.scale, Vec3(0.01, 0.01, 1), 10 * time.dt)
    else:
        camera.fov = lerp(camera.fov, 90, 10 * time.dt)
        crosshair.scale = lerp(crosshair.scale, Vec3(0.02, 0.02, 1), 10 * time.dt)
    
    # Перезарядка
    if held_keys['r']:
        reload()
    
    # Спавн зомби
    spawn_timer += time.dt
    if spawn_timer >= spawn_interval:
        spawn_zombie()
        spawn_timer = 0
        
        # Увеличение сложности
        if zombies_killed > 0 and zombies_killed % 10 == 0:
            wave += 1
            spawn_interval = max(1.0, spawn_interval - 0.15)
            update_ui()

print("=" * 50)
print("AAA ZOMBIE SHOOTER")
print("=" * 50)
print("WASD - Move")
print("Mouse - Look")
print("LMB - Shoot")
print("RMB - Aim")
print("R - Reload")
print("Space - Jump")
print("=" * 50)

app.run()