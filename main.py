import pygame as pg
import pygame_menu as pgm
from game import Game

class Application:
    def __init__(self) -> None:
        pg.init()
        pg.display.set_caption("Баррикада!")
        self.size = self.width, self.height = 1500, 1000
        self.screen = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        self.fps = 60
        self.game_manager = None
        self.game_started = False

        image = pgm.BaseImage('Assets/MenuBG1500.png')
        self.mainTheme = pgm.Theme(background_color=image, widget_font_size=75, title=False)
        self.mainTheme.widget_selection_effect = pgm.widgets.HighlightSelection(border_width=0)
        self.secondTheme = pgm.Theme(background_color=(226, 232, 240), widget_font_size=40, title=False)
        self.gameTheme = pgm.Theme(background_color=(226, 232, 240), widget_font_size=50, title=False)

        self.menu = pgm.Menu('', self.width, self.height, theme=self.mainTheme)
        self.options_menu = pgm.Menu('', self.width, self.height, theme=self.secondTheme)
        self.select_menu = pgm.Menu('', self.width, self.height, theme=self.secondTheme)
        self.game_menu = pgm.Menu('', self.width, self.height, theme=self.gameTheme)

        self.menu.add.label("Баррикада!", margin=(-250, 0))
        self.menu.add.vertical_margin(130)
        self.menu.add.button('Играть', self.select_menu, margin=(-125, 0), selection_color=(0, 0, 0))
        self.menu.add.vertical_margin(130)
        self.menu.add.button('Опции', self.options_menu, margin=(-375, 0), selection_color=(0, 0, 0))
        self.menu.add.vertical_margin(130)
        self.menu.add.button('Выйти', self.terminate, margin=(-125, 0), selection_color=(0, 0, 0))

        self.options_menu.add.label("Опции")
        self.options_menu.add.vertical_margin(500)
        self.options_menu.add.button('Назад', pgm.events.BACK, selection_color=(0, 0, 0))

        self.select_menu.add.label("Перед началом игры...") # Эта часть будет записывать параметры в json файл
        self.select_menu.add.label("Позже тут можно будет выбрать имя игроков", margin=(-50, 0))
        self.select_menu.add.label("Позже тут можно будет выбрать режимы", margin=(50, 0))
        self.select_menu.add.button("Начать!", self.start_game, selection_color=(0, 0, 0))
        self.select_menu.add.button("Назад", pgm.events.BACK, selection_color=(0, 0, 0))

        self.game_menu.add.label("Ход игрока 1", margin=(575, 0))
        self.game_menu.add.vertical_margin(800)
        self.game_menu.add.button("Выход в меню", self.end_game, selection_color=(0, 0, 0), margin=(550, 0))

    def run_application(self) -> None:
        self.menu.enable()

        while True:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.terminate()
                if self.game_started and event.type == pg.KEYUP:
                    self.game_manager.key_handler(event.key)
                if self.game_started and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.game_manager.mouse_handler(event.pos, True)

            if self.menu.is_enabled():
                self.menu.update(events)
                self.menu.draw(self.screen)

            if self.game_started:
                self.game_manager.mouse_handler(pg.mouse.get_pos(), False)
                self.game_manager.update(self.screen)

            self.clock.tick(self.fps)
            pg.display.flip()

    def save_parameters(self, name: str, value: str) -> None:
        pass

    def start_game(self) -> None:
        self.game_manager = Game()
        self.game_started = True
        self.menu._open(self.game_menu)

    def end_game(self) -> None:
        self.game_started = False
        self.menu.reset(2)

    @staticmethod
    def terminate() -> None:
        pg.quit()
        exit()


if __name__ == "__main__":
    app = Application()
    app.run_application()