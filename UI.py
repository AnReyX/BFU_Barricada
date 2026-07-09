import pygame as pg
import pygame_menu as pgm
from Graphics import Image
from Loader import load_image

class UserInterface:
    def __init__(self, menu: pgm.Menu, names: tuple[str, str]) -> None:
        self.font = pg.font.SysFont("Calibri", 35)
        self.small_font = pg.font.SysFont("Calibri", 20)
        self.icons = [Image(load_image("Icons/Red.png")), Image(load_image("Icons/Blue.png"))]

        self._names = names
        self.numeration = []
        for i in "987654321abcdefghi":
            self.numeration += [self.small_font.render(i, True, (0, 0, 0))]
        self.display_names = [self.font.render(self._names[0], True, (0, 0, 0)),
                                self.font.render(self._names[1], True, (0, 0, 0))]
        self.display_bars = [self.font.render("10/10", True, (0, 0, 0)),
                                self.font.render("10/10", True, (0, 0, 0))]
        self.turn = "Текущий ход: 1."
        self.play = f"Ходит: {self._names[0]}."
        self._display = ["", "История ходов:"]

        self.resign_button = menu.add.button('СДАТЬСЯ', self._resign, selection_color=(0, 0, 0),
                                             selection_effect=pgm.widgets.HighlightSelection(margin_x=3, margin_y=43))
        self.resign_button.set_float(True, origin_position=True)
        self.resign_button.translate(1317, 893)

        self.move = 1
        self._resign_time = 0
        self.start_index = 0
        self._move_history = []

        self.icons[0].move((964, 140))
        self.icons[1].move((964, 294))
        self.icons[1].set_opacity(128)
        self.icons_group = pg.sprite.Group()
        for i in self.icons:
            self.icons_group.add(i)

    def add_move(self, move_text: str) -> None:
        self._display[0] = "" # Стираем предупреждение о неверном ходе
        if not self.move % 2:
            self._move_history += [f"{self.move // 2}.  {move_text}"]
            if len(self._move_history) > 7:
                self.start_index += 1 # Автоматически обновляем индекс
        else:
            self._move_history[-1] += f" | {move_text}"

    def show_error(self, msg: str) -> None:
        self._display[0] = msg

    def scroll(self, where: int) -> None:
        if len(self._move_history) <= 7:
            return
        if where < 0:
            self.start_index = max(0, self.start_index - 1)
        else:
            self.start_index = min(len(self._move_history) - 7, self.start_index + 1)

    def _resign(self) -> None:
        if self._resign_time is None:
            return
        if self._resign_time:
            self.move += 1
            self.resign_button.set_title("Сдались")
            self.icons[self.move % 2].set_opacity(256)
            self.icons[1 - self.move % 2].set_opacity(128)
            self.turn = f"{self._names[1 - self.move % 2]} победил! (Ход {self.move // 2})"
            self.play = f'{self._names[self.move % 2]} сдался.'
            self.add_move("Resign")
            pg.mixer.music.pause()
            self.start_index = max(0, len(self._move_history) - 7)
            self.move -= 1
            self._resign_time = None
        else:
            self._resign_time = pg.time.get_ticks()
            self.resign_button.set_title("ТОЧНО?")

    def has_resigned(self) -> bool:
        return self._resign_time is None

    def time_win(self) -> None:
        self.move += 1
        self.icons[1 - self.move % 2].set_opacity(256)
        self.icons[self.move % 2].set_opacity(128)
        self.add_move("Timeout")
        self.turn = f"{self._names[1 - self.move % 2]} победил! (Ход {self.move // 2})"
        self.play = f'{self._names[self.move % 2]} просрочил время.'
        pg.mixer.music.pause()
        self.start_index = max(0, len(self._move_history) - 7)
        self.move -= 1
        self._resign_time = None

    def update_turn(self, notation: str, win: bool, barricades: int | None = None) -> None:
        self.move += 1
        if barricades is not None:
            self.display_bars[self.move % 2] = self.font.render(f"{barricades}/10",
                                                                        True, (0, 0, 0))
        if win:
            self.turn = "Победа!"
            self.play = f'{self._names[self.move % 2]} выиграл в ход {self.move // 2}.'
            self.add_move(f"{notation}W")
            self.start_index = max(0, len(self._move_history) - 7)
            self.move -= 1
            self._resign_time = None
        else:
            self.icons[1 - self.move % 2].set_opacity(256)
            self.icons[self.move % 2].set_opacity(128)
            self.add_move(notation)
            self.start_index = max(0, len(self._move_history) - 7)
            self.turn = f'Текущий ход: {(self.move + 1) // 2}.'
            self.play = f'Ходит: {self._names[1 - self.move % 2]}.'

    def update(self, screen: pg.Surface, time: int) -> None:
        if self._resign_time is not None and self._resign_time > 0:
            if pg.time.get_ticks() - self._resign_time >= 1500:
                self.resign_button.set_title("Сдаться")
                self._resign_time = 0

        for i in range(9):
            screen.blit(self.numeration[i], (938, 95 + i * 100))
            screen.blit(self.numeration[i + 9], (85 + i * 100, 942))
        screen.blit(self.font.render(self.play, True, (0, 0, 0)), (975, 45))
        screen.blit(self.font.render(self.turn, True, (0, 0, 0)), (975, 95))
        for i in range(2):
            screen.blit(self.font.render(self._display[i], True, (0, 0, 0)), (975, 460 + i * 45))
        self.icons_group.draw(screen)

        for i in range(0, min(7, len(self._move_history))):
            screen.blit(self.font.render(self._move_history[self.start_index + i],
                                              True, (0, 0, 0)), (970, 570 + i * 40))
        if self.move % 2:
            pg.draw.rect(screen, (225, 125, 125), (1114, 140, 356, 150))
        else:
            pg.draw.rect(screen, (125, 125, 225), (1114, 294, 356, 150))
        for i in range(2):
            pg.draw.rect(screen, (10, 10, 10), (1325, 224 + i * 154, 5, 55))
            screen.blit(self.display_names[i], (1145, 170 + i * 154))
            screen.blit(self.display_bars[i], (1345, 234 + i * 154))
            m, s = divmod(time[i], 60)
            screen.blit(self.font.render(f"{m:02}:{s:02}", True, (0, 0, 0)), (1145, 234 + i * 154))
