import pygame as pg
from Graphics import Player, Image
from UI import UserInterface
from Loader import load_image, load_sound
from collections import deque

class Game:
    def __init__(self, ui: UserInterface, time: int) -> None:
        self.colors = {0: (50, 100, 50), 1: (10, 10, 10), 2: [(240, 203, 203), (255, 255, 255), (200, 214, 232)],
                       3: (150, 150, 150), 4: (150, 150, 150)}
        sprites = [load_image("Images/Red.png"), load_image("Images/Blue.png"),
                   load_image("Images/Red.png"), load_image("Images/Blue.png")]
        self._sfx = [load_sound("Walk.mp3"), load_sound("Barricade.mp3"), load_sound("Win.mp3")]
        self.UI = ui
        self.players = [Player(sprites[0], (450, 860), self._sfx[0], time),
                        Player(sprites[1], (450, 60), self._sfx[0], time)]
        self.previews = [Image(sprites[2]), Image(sprites[3])]
        for i in self.previews:
            i.set_opacity(128)
        # Второе число: 0 - Нет баррикады, 1 - Есть баррикада, 2 - Клеточка, 3 - Превью вместо 0, 4 - Превью вместо 1
        self.grid = [[] for _ in range(17)] # Поле рисуется сверху вниз
        for y in range(0, 17, 2):
            for x in range(0, 17, 2):
                self.grid[y] += [[pg.Rect(50 + x * 50, 60 + y * 50, 80, 80), 2]]
                if x != 16: self.grid[y] += [[pg.Rect(130 + x * 50, 60 + y * 50, 20, 80), 0]]
                if y != 16: self.grid[y + 1] += [[pg.Rect(50 + x * 50, 140 + y * 50, 80, 20), 0]]
                if x != 16 and y != 16: self.grid[y + 1] += [[pg.Rect(130 + x * 50, 140 + y * 50, 20, 20), 0]]

        self._game_state = 0 # 0 - Ход красного, 1 - Ход синего, 2 - Победа
        self.draw_preview = 0  # 0 - Ничего не показывается, 1 - Игрок, [точ.1, точ.2, точ.3] - Баррикада
        self.locations = [[16, 8], [0, 8]] # Позиция красного, позиция синего
        self.legal_squares = []
        self._get_legal_moves()

        self.hovered_index = None  # Индексы невыставленной баррикады, над которой мышка
        self.hover_start_time = 0  # Время, когда мышка зашла на этот индекс
        self.preview_delay = 200 # Сколько надо подождать
        self.can_place = False # Можно ли поставить стену (только когда превью видно)

        self.preview_one = pg.sprite.Group()
        self.preview_one.add(self.previews[0])
        self.preview_two = pg.sprite.Group()
        self.preview_two.add(self.previews[1])
        self.all_sprites = pg.sprite.Group()
        for i in range(2):
            self.all_sprites.add(self.players[i])

    def set_sfx_volume(self, value: float) -> None:
        for i in self._sfx:
            i.set_volume(value)

    def key_handler(self, key: int) -> None:
        if key == pg.K_q or key == pg.K_PAGEDOWN:
            self.UI.scroll(-1)
        elif key == pg.K_e or key == pg.K_PAGEUP:
            self.UI.scroll(1)
        elif self._game_state == 2:
            return
        elif key == pg.K_UP or key == pg.K_w:
            self._move_player([self.locations[self._game_state][0] - 2, self.locations[self._game_state][1]])
        elif key == pg.K_DOWN or key == pg.K_s:
            self._move_player([self.locations[self._game_state][0] + 2, self.locations[self._game_state][1]])
        elif key == pg.K_RIGHT or key == pg.K_d:
            self._move_player([self.locations[self._game_state][0], self.locations[self._game_state][1] + 2])
        elif key == pg.K_LEFT or key == pg.K_a:
            self._move_player([self.locations[self._game_state][0], self.locations[self._game_state][1] - 2])

    def mouse_handler(self, pos: tuple, clicked: bool) -> None:
        if self._game_state == 2:
            return

        if not (50 <= pos[0] <= 930 and 60 <= pos[1] <= 940): # Если да, мы точно за полем
            if self.draw_preview:
                self._remove_preview()
            return

        for i in self.legal_squares:
            square = self.grid[i[0]][i[1]][0]
            if square.collidepoint(pos): # Мы точно на легальной клетке
                self.previews[self._game_state].move(square.topleft)
                if self.draw_preview: self._remove_preview()
                self.draw_preview = 1 # Создаём превью хода
                if clicked:
                    self._move_player(i)
                return

        temp = 0 # Точно на нелегальной клетке / любой баррикаде
        for i in range(0, 17, 2):
            if temp: break
            for j in range(1, 16, 2):
                bar = self.grid[i][j]
                if bar[0].collidepoint(pos): # 0 - Ширина 80, 1 - Оба измерения 20, 2 - Высота 80
                    temp = 1 if bar[1] == 1 else ((i, j), 2)
                    break
        for i in range(1, 16, 2):
            if temp: break
            for j in range(17):
                bar = self.grid[i][j]
                if bar[0].collidepoint(pos):
                    temp = 1 if bar[1] == 1 else ((i, j), j % 2)
                    break
        # temp: 0 нелегальная клетка; 1 - Выставленная баррикада; ((x, y), type) - невыставленная баррикада
        if temp in (0, 1):
            if clicked and not temp:
                self.UI.show_error("Нелегальный ход!")
            if self.draw_preview:
                self._remove_preview()
            return
        # Мы на невыставленной баррикаде, необходимо выставить превью.
        if self.draw_preview and temp != self.hovered_index:
            self._remove_preview() # Стираем предыдущее превью
        if temp != self.hovered_index:
            self.hovered_index = temp
            self.hover_start_time = pg.time.get_ticks()
        self._do_wall_preview(temp[0], temp[1])
        if clicked:
            self._place_wall()

    def update(self, screen: pg.Surface) -> None:
        self.all_sprites.update()
        for i in range(17):
            for j in range(17):
                rec = self.grid[j][i]
                if rec[1] == 2:
                    pg.draw.rect(screen, self.colors[2][0 if not j else (2 if j == 16 else 1)], rec[0], border_radius=5)
                    if [j, i] in self.legal_squares:
                        pg.draw.rect(screen, self.colors[0], rec[0], 5)
                elif rec[1]:
                    pg.draw.rect(screen, self.colors[rec[1]], rec[0])

        self.all_sprites.draw(screen)
        if self.draw_preview == 1:
            if not self._game_state:
                self.preview_one.draw(screen)
            else:
                self.preview_two.draw(screen)
        self.UI.update(screen, (self.players[0].time, self.players[1].time))
        if self._game_state < 2:
            self.players[self._game_state].handle_time()
            if self.UI.has_resigned():
                self._game_state, self.legal_squares = 2, []
                self._remove_preview()
            elif self.players[self._game_state].time <= 0:
                self._game_state, self.legal_squares = 2, []
                self._remove_preview()
                self.UI.time_win()

    def _move_player(self, end: list[int]) -> None:
        if end not in self.legal_squares:
            return
        if self.players[self._game_state].is_moving:
            return
        self.players[self._game_state].move((50 + end[1] * 50, 60 + end[0] * 50))
        self.locations[self._game_state] = end
        if not end[0] and not self._game_state:
            self._game_state, self.legal_squares = 2, []
            self._remove_preview()
            pg.mixer.music.pause()
            self._sfx[2].play()
            self.UI.update_turn(self.notate_move(end, 0), True)
            return
        elif end[0] == 16 and self._game_state:
            self._game_state, self.legal_squares = 2, []
            self._remove_preview()
            self.UI.update_turn(self.notate_move(end, 0), True)
            pg.mixer.music.pause()
            self._sfx[2].play()
            return
        self._game_state = 1 - self._game_state
        self.UI.update_turn(self.notate_move(end, 0), False)
        self._get_legal_moves()

    def _place_wall(self) -> None:
        if self.can_place and self._check_wall_legality():
            for i in self.draw_preview[:-1]:
                self.grid[i[0]][i[1]][1] = 1
            self._sfx[1].play()
            self.players[1 - self._game_state].lower_barricades()
            self._game_state = 1 - self._game_state
            self.UI.update_turn(self.notate_move(*self.draw_preview[-1]), False,
                                self.players[self._game_state].barricades)
            self.draw_preview = []
            self._get_legal_moves()

    def _get_legal_moves(self) -> None:
        self.legal_squares = []
        start = self.locations[self._game_state] # (y_н, x_н)
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

    def _check_wall_legality(self) -> bool:
        if self.players[1 - self._game_state].barricades == 0:
            self.UI.show_error("Закончились баррикады!")
            return False
        for i in self.draw_preview[:-1]:
            if self.grid[i[0]][i[1]][1] == 4:
                self.UI.show_error("Здесь уже стоит баррикада!")
                return False
        if not (self._bfs_algorithm(self.locations[0], 0) and self._bfs_algorithm(self.locations[1], 16)):
            self.UI.show_error("Кому-то нет победных путей!")
            return False
        return True

    def _bfs_algorithm(self, start: list[int], target_row: int) -> bool:
        queue = deque([start])
        visited = set()
        visited.add(tuple(start))
        # Две координаты, куда идти, две координаты, куда смотреть для стены
        directions = [
            (-2, 0, -1, 0),  # Вверх
            (2, 0, 1, 0),  # Вниз
            (0, -2, 0, -1),  # Влево
            (0, 2, 0, 1)  # Вправо
        ]

        while queue:
            r, c = queue.popleft()
            if r == target_row:
                return True
            for dr, dc, wr, wc in directions:
                next_r, next_c = r + dr, c + dc  # Куда прыгнет игрок
                wall_r, wall_c = r + wr, c + wc  # Где находится потенциальная стена

                if 0 <= next_r < 17 and 0 <= next_c < 17: #Всё ещё ли мы в поле, проверка на стену и посещение клетки
                    if not self.grid[wall_r][wall_c][1] and (next_r, next_c) not in visited:
                        visited.add((next_r, next_c))
                        queue.append([next_r, next_c])
        return False

    def _do_wall_preview(self, pos: tuple[int, int], how: int) -> None:
        if self.hovered_index is not None and pg.time.get_ticks() - self.hover_start_time < self.preview_delay:
            self.can_place = False
            return
        self.can_place = True
        self.draw_preview = []
        # how отвечает за направление превью и зависит от формы промежутка, где находится курсор
        if not how:
            k = -1 if pos[1] == 16 else 1
            for i in range(3):
                placing = [pos[0], pos[1] + i * k]
                typ = self.grid[placing[0]][placing[1]][1]
                if typ == 0:
                    self.grid[placing[0]][placing[1]][1] = 3
                elif typ == 1:
                    self.grid[placing[0]][placing[1]][1] = 4
                self.draw_preview += [placing]
        elif how == 2:
            k = -1 if pos[0] == 16 else 1
            for i in range(3):
                placing = [pos[0] + i * k, pos[1]]
                typ = self.grid[placing[0]][placing[1]][1]
                if typ == 0:
                    self.grid[placing[0]][placing[1]][1] = 3
                elif typ == 1:
                    self.grid[placing[0]][placing[1]][1] = 4
                self.draw_preview += [placing]
        else:
            for i in range(-1, 2):
                placing = [pos[0] + i, pos[1]]
                typ = self.grid[placing[0]][placing[1]][1]
                if typ == 0:
                    self.grid[placing[0]][placing[1]][1] = 3
                elif typ == 1:
                    self.grid[placing[0]][placing[1]][1] = 4
                self.draw_preview += [placing]
        self.draw_preview += [[[pos[0], pos[1]], how + 1]]

    def _remove_preview(self) -> None:
        if self.draw_preview not in (0, 1):
            for i in self.draw_preview[:-1]:
                square = self.grid[i[0]][i[1]]
                if square[1] == 3:
                    square[1] = 0
                elif square[1] == 4:
                    square[1] = 1
        self.draw_preview = 0

    @staticmethod
    def notate_move(coord: list[int], is_wall_type: int) -> str:
        if not is_wall_type:
            return f"{chr(97 + coord[1] // 2)}{(16 - coord[0]) // 2 + 1}"
        else:
            if is_wall_type == 1:
                return f"h{chr(97 + coord[1] // 2)}{(17 - coord[0]) // 2}"
            elif is_wall_type == 3:
                return f"v{chr(97 + (coord[1] - 1) // 2)}{(16 - coord[0]) // 2 + 1}"
            return f"v{chr(97 + (coord[1] - 1) // 2)}{(17 - coord[0]) // 2}"

    @property
    def state(self) -> int:
        return self._game_state