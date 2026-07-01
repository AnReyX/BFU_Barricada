import pygame as pg
import os
from funcs import load_image

class Player(pg.sprite.Sprite):
    def __init__(self, sprite: pg.Surface, position: tuple[int, int]) -> None:
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position # 450, (860, 60)[color]

        self.pos = pg.math.Vector2(*position)
        self.target_pos = pg.math.Vector2(*position)
        self.is_moving = False
        self.speed = 6.0


    def move(self, pos: tuple[int, int]) -> None:
        self.target_pos = pg.math.Vector2(*pos)
        self.is_moving = True

        for group in self.groups():
            group.remove(self)
            group.add(self)

    def update(self):
        if self.is_moving:
            direction = self.target_pos - self.pos

            distance = direction.length()

            if distance <= self.speed:
                self.pos = pg.math.Vector2(self.target_pos)  # Прилипаем ровно к цели
                self.is_moving = False  # Останавливаемся
            else:
                direction.normalize_ip() # Нормализуем вектор
                self.pos += direction * self.speed

            # ВАЖНО: Обновляем сам Rect
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))


class Preview(pg.sprite.Sprite):
    def __init__(self, sprite: pg.Surface) -> None:
        super().__init__()
        self.image = sprite
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, 0


    def move(self, pos: tuple[int, int]) -> None:
        self.rect.x, self.rect.y = pos

"""self.rect.topleft = (x, y)
        
        # --- НОВЫЕ ПЕРЕМЕННЫЕ ДЛЯ ПЛАВНОГО ДВИЖЕНИЯ ---
        # Вектор для хранения ТОЧНЫХ (дробных) координат
        self.pos = pg.math.Vector2(x, y) 
        # Вектор цели, куда мы стремимся
        self.target_pos = pg.math.Vector2(x, y) 
        
        self.is_moving = False
        
        # СКОРОСТЬ:
        # Если мы хотим пройти 100 пикселей примерно за 0.5 секунды при 60 FPS:
        # 60 FPS * 0.5 сек = 30 кадров. 100 пикс / 30 кадров ≈ 3.3 пикселя в кадр.
        # Если хочешь почти целую секунду (будет довольно медленно), ставь скорость 2.0
        self.speed = 4.0 

    def move(self, new_pos):
        Теперь этот метод не телепортирует, а задает цель
        self.target_pos = pg.math.Vector2(new_pos)
        self.is_moving = True

    def update(self):
        Этот метод должен вызываться каждый кадр (в цикле while True)
        if self.is_moving:
            # 1. Вычисляем вектор направления от текущей позиции к цели
            direction = self.target_pos - self.pos
            
            # 2. Узнаем оставшуюся дистанцию
            distance = direction.length()
            
            # 3. Если мы уже очень близко к цели (ближе, чем шаг скорости)
            if distance <= self.speed:
                self.pos = pg.math.Vector2(self.target_pos) # Прилипаем ровно к цели
                self.is_moving = False                      # Останавливаемся
            else:
                # 4. Нормализуем вектор (делаем его длину равной 1)
                direction.normalize_ip()
                # 5. Двигаем точную позицию на величину скорости
                self.pos += direction * self.speed
                
            # 6. ВАЖНО: Обновляем сам Rect, округляя дробные координаты до целых
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))"""