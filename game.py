import pygame as pg
from openpyxl.pivot.fields import Boolean
from Sprites import Player, Preview
from funcs import load_image

class Game:
    def __init__(self) -> None:
        self.colors = ((240, 203, 203), (200, 214, 232), (255, 255, 255))
        self.sprites = [load_image("Red.png"), load_image("Blue.png"), load_image("Red.png"), load_image("Blue.png")]
        self.players = [Player(self.sprites[0], (450, 860)), Player(self.sprites[1], (450, 60))]
        self.previews = [Preview(self.sprites[2]), Preview(self.sprites[3])]
        self.grid = [[] for _ in range(17)] # 0 - Баррикада не выставлена, 1 - Баррикада выставлена, 2 - Клеточка
        for y in range(0, 17, 2): # Поле рисуется сверху вниз
            for x in range(0, 17, 2):
                self.grid[y] += [[pg.Rect(50 + x * 50, 60 + y * 50, 80, 80), 2]]
                if x != 16: self.grid[y] += [[pg.Rect(130 + x * 50, 60 + y * 50, 20, 80), 0]]
                if y != 16: self.grid[y + 1] += [[pg.Rect(50 + x * 50, 140 + y * 50, 80, 20), 0]]
                if x != 16 and y != 16: self.grid[y + 1] += [[pg.Rect(130 + x * 50, 140 + y * 50, 20, 20), 0]]

        self.game_state = 0 # 0 - ход красного, 1 - ход синего, 2 - победа красного, 3 - победа синего
        self.draw_preview = 0  # 0 - Ничего не показывается, 1 - Игрок, 2 - Баррикада
        self.locations = [[16, 8], [0, 8]] # Позиция красного, позиция синего
        self.legal_squares = []
        self._get_legal_moves()

        self.preview_one = pg.sprite.Group()
        self.preview_one.add(self.previews[0])
        self.preview_two = pg.sprite.Group()
        self.preview_two.add(self.previews[1])
        self.all_sprites = pg.sprite.Group()
        for i in range(2):
            self.all_sprites.add(self.players[i])

    def key_handler(self, key: int) -> None:
        if key == pg.K_UP or key == pg.K_w:
            self._move_player([self.locations[self.game_state][0] - 2, self.locations[self.game_state][1]])
        elif key == pg.K_DOWN or key == pg.K_s:
            self._move_player([self.locations[self.game_state][0] + 2, self.locations[self.game_state][1]])
        elif key == pg.K_RIGHT or key == pg.K_d:
            self._move_player([self.locations[self.game_state][0], self.locations[self.game_state][1] + 2])
        elif key == pg.K_LEFT or key == pg.K_a:
            self._move_player([self.locations[self.game_state][0], self.locations[self.game_state][1] - 2])

    def mouse_handler(self, pos: tuple, clicked: bool) -> None:
        if not (40 <= pos[0] <= 940 and 50 <= pos[1] <= 950):
            return
        if self.draw_preview:
            self.draw_preview = 0
        for i in self.legal_squares:
            square = self.grid[i[0]][i[1]][0]
            if square.collidepoint(pos):
                if clicked:
                    self._move_player(i)
                elif not self.draw_preview:
                    self.previews[self.game_state].move(square.topleft)
                    self.draw_preview = 1
                return


    def update(self, screen: pg.Surface) -> None:
        self.all_sprites.update()
        for i in range(0, 17, 2):
            for j in range(0, 17, 2):
                pg.draw.rect(screen, self.colors[0 if not j else (1 if j == 16 else 2)], self.grid[j][i][0])
                if [j, i] in self.legal_squares:
                    pg.draw.rect(screen, (100, 100, 100), self.grid[j][i][0], 5)
        self.all_sprites.draw(screen)
        if self.draw_preview == 1:
            if not self.game_state:
                self.preview_one.draw(screen)
            else:
                self.preview_two.draw(screen)

    def _move_player(self, end: list) -> None:
        if end not in self.legal_squares or self.players[self.game_state].is_moving:
            return
        self.players[self.game_state].move((50 + end[1] * 50, 60 + end[0] * 50))
        self.locations[self.game_state] = end
        self.game_state = 1 - self.game_state
        self._get_legal_moves()

    def _get_legal_moves(self):
        self.legal_squares = []
        start = self.locations[self.game_state] # (y_н, x_н)
        for i in range(-1, 2, 2):
            for j in range(2):
                check = [start[0] + i * (1 - j), start[1] + i * j] # Проверка 1: попали ли за границу / в баррикаду?
                if not (0 <= check[j] < 17) or self.grid[check[0]][check[1]][1]:
                    continue
                check[j] += i # Проверка 2: попали ли в игрока?
                if check in self.locations:
                    # Проверка 3: перепрыгиваем через игрока?
                    if 0 <= check[j] + i < 17 and not self.grid[check[0] + i * (1 - j)][check[1] + i * j][1]:
                        check[j] += 2 * i
                        self.legal_squares += [check]
                        continue
                    for k in range(-1, 2, 2):
                        if 0 <= check[1 - j] + k < 17 and not self.grid[check[0] + k * j][check[1] + k * (1 - j)][1]:
                            self.legal_squares += [[check[0] + 2 * k * j, check[1] + 2 * k * (1 - j)]]
                else:
                    self.legal_squares += [check]

    def _get_barricade_coord(self, pos) -> None | tuple[int, int]:
        for i in range(1, 16, 2):
            for j in range(1, 16, 2):
                if self.grid[i][j][0].collidepoint(pos):
                    return i, j