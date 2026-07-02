import pygame as pg

class Player(pg.sprite.Sprite):
    def __init__(self, sprite: pg.Surface, position: tuple[int, int]) -> None:
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position # 450, (860, 60)[color]

        self.barricade_count = 10
        self.pos = pg.math.Vector2(*position)
        self.target_pos = pg.math.Vector2(*position)
        self.is_moving = False
        self.speed = 6.0

    def lower_barricades(self):
        self.barricade_count -= 1

    @property
    def barricades(self):
        return self.barricade_count

    def move(self, pos: tuple[int, int]) -> None:
        self.target_pos = pg.math.Vector2(*pos)
        self.is_moving = True

        for group in self.groups():
            group.remove(self)
            group.add(self)

    def update(self) -> None:
        if self.is_moving:
            direction = self.target_pos - self.pos

            distance = direction.length()

            if distance <= self.speed:
                self.pos = pg.math.Vector2(self.target_pos)  # Прилипаем ровно к цели
                self.is_moving = False  # Останавливаемся
            else:
                direction.normalize_ip() # Нормализуем вектор
                self.pos += direction * self.speed

            self.rect.topleft = (round(self.pos.x), round(self.pos.y)) # ВАЖНО: Обновляем сам Rect


class Preview(pg.sprite.Sprite):
    def __init__(self, sprite: pg.Surface) -> None:
        super().__init__()
        self.image = sprite
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, 0


    def move(self, pos: tuple[int, int]) -> None:
        self.rect.x, self.rect.y = pos