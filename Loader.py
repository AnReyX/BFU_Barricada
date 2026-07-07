import pygame as pg
from pathlib import Path

def load_image(name):
    fullname = f"Assets/{name}"
    if not Path(fullname).is_file():
        print(f"Файл с изображением '{fullname}' не найден")
        exit()
    im = pg.image.load(fullname).convert_alpha()
    return im

def load_sound(name):
    fullname = f"Assets/Sounds/{name}"
    if not Path(fullname).is_file():
        print(f"Файл со звуком '{fullname}' не найден")
        exit()
    return pg.mixer.Sound(fullname)