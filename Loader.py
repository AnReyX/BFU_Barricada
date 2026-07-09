import pygame as pg
import numpy as np

def load_image(name):
    fullname = f"Assets/{name}"
    try:
        im = pg.image.load(fullname).convert_alpha()
        return im
    except FileNotFoundError:
        placeholder = pg.Surface((50, 50))
        placeholder.fill("Red")
        return placeholder

def load_sound(name):
    fullname = f"Assets/Sounds/{name}"
    try:
        so = pg.mixer.Sound(fullname)
        return so
    except FileNotFoundError:
        sample_rate = 44100
        n_samples = int(sample_rate * 0.1)
        t = np.linspace(0, 0.1, n_samples, False)
        wave = np.sin(440.0 * t * 2 * np.pi)
        audio = wave * (2 ** 15 - 1) * 0.3
        audio = audio.astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))

        return pg.mixer.Sound(buffer=stereo_audio)