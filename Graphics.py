import pygame as pg

class Player(pg.sprite.Sprite):
    def __init__(self, sprite: pg.Surface, position: tuple[int, int], walk_sound: pg.mixer.Sound, time: int) -> None:
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.walk_sound = walk_sound

        self._barricade_count = 10
        self._move_time = time
        self._count_time = 0
        self.pos = pg.math.Vector2(*position)
        self.target_pos = pg.math.Vector2(*position)
        self.is_moving = False
        self.speed = 6.0

    def lower_barricades(self) -> None:
        self._count_time = pg.time.get_ticks()
        self._barricade_count -= 1

    @property
    def time(self) -> int:
        return self._move_time

    @property
    def barricades(self) -> int:
        return self._barricade_count

    def move(self, pos: tuple[int, int]) -> None:
        self._count_time = pg.time.get_ticks()
        self.target_pos = pg.math.Vector2(*pos)
        self.is_moving = True

        for group in self.groups():
            group.remove(self)
            group.add(self)

    def handle_time(self):
        if pg.time.get_ticks() - self._count_time >= 1000:
            self._move_time -= 1
            self._count_time = pg.time.get_ticks()

    def update(self) -> None:
        if self.is_moving:
            direction = self.target_pos - self.pos # Направление движения

            distance = direction.length() # Расстояние до цели

            if distance <= self.speed: # Когда игрок достаточно близок к цели
                self.pos = pg.math.Vector2(self.target_pos)
                self.is_moving = False  # Останавливаемся
                self.walk_sound.play()
            else:
                direction.normalize_ip() # Нормализуем вектор
                self.pos += direction * self.speed

            self.rect.topleft = (round(self.pos.x), round(self.pos.y)) # ВАЖНО: Обновляем сам Rect


class Image(pg.sprite.Sprite):
    def __init__(self, sprite: pg.Surface) -> None:
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, 0

    def move(self, pos: tuple[int, int]) -> None:
        self.rect.x, self.rect.y = pos

    def set_opacity(self, value: int) -> None:
        self.image.set_alpha(value)
