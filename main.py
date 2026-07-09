import pygame as pg
import pygame_menu as pgm
from Game import Game
from UI import UserInterface
from functools import partial
from pathlib import Path
import json
from random import randint


class Application:
    def __init__(self) -> None:
        pg.init()
        if Path("Assets/Icons/Game.png").is_file():
            pg.display.set_icon(pg.image.load("Assets/Icons/Game.png"))
        pg.display.set_caption("Баррикада!")
        width, height = 1500, 1000
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.fps = 60
        try:
            with open("Assets/data.json", encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"PlayerOne": "Игрок 1", "PlayerTwo": "Игрок 2", "Time": 300, "Music": 50,
                         "Theme": 0, "SFX": 100}
            self.save_parameters()

        pg.mixer.init()
        path = Path("Assets/Music")
        self.soundtrack = [[f"Assets/Music/{file.name}" for file in path.iterdir() if file.name[0] == "0"],
                           [f"Assets/Music/{file.name}" for file in path.iterdir() if file.name[0] == "1"]]
        self.order = [0, -1] # [0, номер песни] - Прямой порядок, [1, номер песни] - Случайный порядок
        self.SONG_END_EVENT = pg.USEREVENT + 1
        pg.mixer.music.set_endevent(self.SONG_END_EVENT)
        pg.mixer.music.set_volume(self.data["Music"] / 100)
        self.menu_music = None

        self.game_manager = None
        self.UI = None
        self.game_started = False
        self.save_game = False

        try:
            main_bg = pgm.BaseImage('Assets/Images/MainMenu.png')
        except AssertionError:
            main_bg = (226, 232, 240)
        try:
            game_bg = pgm.BaseImage('Assets/Images/GameMenu.png')
        except AssertionError:
            game_bg = (226, 232, 240)
        main_theme = pgm.Theme(background_color=main_bg, widget_font_size=75, title=False, selection_color=(0, 0, 0))
        main_theme.widget_selection_effect = pgm.widgets.HighlightSelection(border_width=0)
        secondary_theme = pgm.Theme(background_color=(226, 232, 240), widget_font_size=40, title=False,
                                    selection_color=(0, 0, 0))
        game_theme = pgm.Theme(background_color=game_bg, widget_font_size=30, title=False, selection_color=(0, 0, 0))
        self.menu = pgm.Menu('', width, height, theme=main_theme)
        self.options_menu = pgm.Menu('', width, height, theme=secondary_theme)
        self.rules_menu = pgm.Menu('', width, height, theme=secondary_theme)
        self.select_menu = pgm.Menu('', width, height, theme=secondary_theme)
        self.game_menu = pgm.Menu('', width, height, theme=game_theme)

        self.menu.add.label("Баррикада!", margin=(15, 0))
        self.menu.add.vertical_margin(130)
        self.menu.add.button('Играть', partial(self.start_game, True), margin=(-100, 0))
        self.menu.add.vertical_margin(120)
        frame = self.menu.add.frame_h(width=1050, height=200, margin=(30, 0))
        frame.pack(self.menu.add.button('Опции', self.options_menu),
                   align=pgm.locals.ALIGN_LEFT)
        frame.pack(self.menu.add.button('Правила', self.rules_menu),
                   align=pgm.locals.ALIGN_RIGHT)
        self.menu.add.vertical_margin(50)
        self.menu.add.button('Выйти', self.terminate, margin=(140, 0))

        self.options_menu.add.label("Опции")
        self.options_menu.add.vertical_margin(100)
        times = [
            ('1:00', 60),
            ('3:00', 180),
            ('5:00', 300),
            ('10:00', 600)
        ]
        self.options_menu.add.label("Громкость")
        self.options_menu.add.vertical_margin(50)
        self.options_menu.add.range_slider(title="Музыки: ", default=self.data["Music"],
                                           range_values=(0, 100), increment=1, value_format=lambda x: str(int(x)),
                                           onchange=lambda x: self.update_value("Music", int(x)))
        self.options_menu.add.range_slider(title="Звуков: ", default=self.data["SFX"], range_values=(0, 100),
                                           increment=1, value_format=lambda x: str(int(x)),
                                           onchange=lambda x: self.update_value("SFX", int(x)))
        self.options_menu.add.vertical_margin(100)
        self.options_menu.add.selector(title='Музыкальная тема: ', items=[('Chill', 0), ('Action', 1)],
                                       onchange=lambda x, y: self.update_value("Theme", y),
                                       default=self.data["Theme"])
        self.options_menu.add.selector(title='Порядок песен: ', items=[('Прямой', [0, -1]), ('Случайный', [1, -1])],
                                       onchange=lambda x, y: self.update_value("order", y), default=0)
        self.options_menu.add.vertical_margin(100)
        self.options_menu.add.dropselect(title="Время: ", onchange=lambda x, y: self.update_value("Time", y),
                                         items=times, default={60: 0, 180: 1, 300: 2, 600: 3}[self.data["Time"]],
                                         placeholder_add_to_selection_box=False)
        self.options_menu.add.vertical_margin(100)
        self.options_menu.add.button('Назад', pgm.events.BACK)

        self.rules_text = []
        for i in ("Rules.txt", "Controls.txt"):
            if Path(f"Assets/{i}").is_file():
                with open(f"Assets/{i}", encoding="UTF-8") as f:
                    self.rules_text += [f.read()]
            else:
                self.rules_text += [f"Проверьте наличие файла {i}"]
        self.rules_menu.add.selector(title="", items=[("Правила", 0), ("Управление", 1)], align=pgm.locals.ALIGN_LEFT,
                                     onchange=lambda x, y: self.change_rules(y), default=0)
        self.rules_menu.add.label(self.rules_text[0], align=pgm.locals.ALIGN_LEFT, font_size=20)
        self.rules_menu.add.button("Назад", pgm.events.BACK, align=pgm.locals.ALIGN_LEFT)

        self.select_menu.add.vertical_margin(20)
        self.select_menu.add.label("Каковы имена игроков этого раунда?", font_size=50)
        self.select_menu.add.vertical_margin(230)
        frame_select = self.select_menu.add.frame_h(width=1000, height=320)
        try:
            frame_select.pack(self.select_menu.add.image("Assets/Icons/Red.png", scale=(2, 2)),
                              align=pgm.locals.ALIGN_LEFT)
        except AssertionError:
            frame_select.pack(self.select_menu.add.label("Red.png не найден!", align=pgm.locals.ALIGN_LEFT))
        try:
            frame_select.pack(self.select_menu.add.image("Assets/Icons/Blue.png", scale=(2, 2)),
                              align=pgm.locals.ALIGN_RIGHT)
        except AssertionError:
            frame_select.pack(self.select_menu.add.label("Blue.png не найден!", align=pgm.locals.ALIGN_RIGHT))
        input_one = self.select_menu.add.text_input("", default=self.data["PlayerOne"], maxchar=9,
                                                         onchange=lambda x: self.update_value("PlayerOne", x))
        input_two = self.select_menu.add.text_input("", default=self.data["PlayerTwo"], maxchar=9,
                                                         onchange=lambda x: self.update_value("PlayerTwo", x))
        input_one.set_float(True, origin_position=True)
        input_one.translate(330, 700)
        input_two.set_float(True, origin_position=True)
        input_two.translate(1000, 700)
        self.select_menu.add.vertical_margin(130)
        self.select_menu.add.button("Начать!", partial(self.start_game, False))
        self.select_menu.add.vertical_margin(20)
        self.select_menu.add.button("Назад", pgm.events.BACK)

    def run_application(self) -> None:
        self.menu.enable()
        if Path("Assets/Music/menu.mp3").is_file():
            self.menu_music = "Assets/Music/menu.mp3"
            pg.mixer.music.load(self.menu_music)
            pg.mixer.music.play(-1)

        while True:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.terminate()
                if self.game_started:
                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                        self.game_manager.mouse_handler(event.pos, True)
                    if event.type == pg.KEYUP:
                        self.game_manager.key_handler(event.key)
                    if event.type == self.SONG_END_EVENT or (self.game_manager.state < 2
                                                             and event.type == pg.KEYUP and event.key == pg.K_z):
                        self.change_music() # Меняем музыку по её завершении или нажатии клавиши Z

            if self.menu.is_enabled():
                self.menu.update(events)
                self.menu.draw(self.screen)

            if self.game_started:
                self.game_manager.mouse_handler(pg.mouse.get_pos(), False)
                self.game_manager.update(self.screen)

            self.clock.tick(self.fps)
            pg.display.flip()

    def change_music(self) -> None:
        if self.order[0]:
            r = randint(0, len(self.soundtrack[self.data["Theme"]]) - 1)
            while r == self.order[1]:
                r = randint(0, len(self.soundtrack[self.data["Theme"]]) - 1)
            self.order[1] = r
        else:
            self.order[1] = (self.order[1] + 1) % len(self.soundtrack[self.data["Theme"]])
        pg.mixer.music.load(self.soundtrack[self.data["Theme"]][self.order[1]])
        pg.mixer.music.play()

    def change_rules(self, index: int) -> None:
        widgets = self.rules_menu.get_widgets()
        self.rules_menu.clear()
        self.rules_menu.add.generic_widget(widgets[0])
        self.rules_menu.add.label(self.rules_text[index], align=pgm.locals.ALIGN_LEFT, font_size=20)
        self.rules_menu.add.button("Назад", pgm.events.BACK, align=pgm.locals.ALIGN_LEFT)
        self.menu._open(self.rules_menu)

    def update_value(self, key: str, value: str | int | list[int]) -> None:
        if key == "order":
            self.order = value
            return
        if key == "Music":
            pg.mixer.music.set_volume(value / 100)
        self.data[key] = value

    def save_parameters(self) -> None:
        with open("Assets/data.json", 'w', encoding='utf-8') as file:
            json.dump(self.data, file)

    def start_game(self, from_main_menu: bool) -> None:
        if not from_main_menu:
            self.game_started = True
            self.game_menu.clear()
            self.game_menu.add.vertical_margin(830)
            self.game_menu.add.button("Выйти с сохранением", partial(self.end_game, True), margin=(383, 0))
            self.game_menu.add.button("Выйти без сохранения", partial(self.end_game, False), margin=(390, 0))
            self.UI = UserInterface(self.game_menu, (self.data["PlayerOne"], self.data["PlayerTwo"]))
            self.game_manager = Game(self.UI, self.data["Time"])
            self.game_manager.set_sfx_volume(self.data["SFX"] / 100)
            pg.mixer.music.fadeout(2000)
            pg.mixer.music.load("Assets/Music/menu.mp3")
            self.menu._open(self.game_menu)
        else:
            self.save_parameters()
            if self.save_game:
                if self.game_manager.state < 2:
                    pg.mixer.music.fadeout(2000)
                    pg.mixer.music.load("Assets/Music/menu.mp3")
                else:
                    pg.mixer.music.pause()
                self.menu._open(self.game_menu)
                self.game_started = True
            else:
                self.menu._open(self.select_menu)

    def end_game(self, save_game: bool) -> None:
        self.save_game = save_game
        self.game_started = False
        self.order[1] = -1
        pg.mixer.music.fadeout(2000)
        if self.menu_music is not None:
            pg.mixer.music.load(self.menu_music)
            pg.mixer.music.play(-1)
        pg.mixer.music.unpause()
        self.menu.reset(2)

    def terminate(self) -> None:
        self.save_parameters()
        pg.quit()
        exit()


if __name__ == "__main__":
    app = Application()
    app.run_application()
