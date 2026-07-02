import pygame as pg
import os

def load_image(name):
    fullname = os.path.join('Assets', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        exit()
    im = pg.image.load(fullname).convert_alpha()
    return im