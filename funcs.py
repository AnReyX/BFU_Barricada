import pygame as pg
import os
from collections import deque

def find_player(board, player_marker):
    """Ищет текущие координаты игрока ('R' или 'B') на поле 17x17."""
    for r in range(17):
        for c in range(17):
            if board[r][c] == player_marker:
                return (r, c)
    return None


def has_path(board, start_pos, target_marker):
    """
    BFS алгоритм. Проверяет, есть ли путь от start_pos до клетки target_marker.
    """
    # Если игрок не найден (на всякий случай)
    if not start_pos:
        return False

    queue = deque([start_pos])
    visited = set()
    visited.add(start_pos)

    # Векторы движения:
    # (смещение_игрока_строка, смещение_игрока_столбец, смещение_стены_строка, смещение_стены_столбец)
    # Игрок прыгает на 2 индекса, а стена проверяется на 1 индексе между ними.
    directions = [
        (-2, 0, -1, 0),  # Вверх
        (2, 0, 1, 0),  # Вниз
        (0, -2, 0, -1),  # Влево
        (0, 2, 0, 1)  # Вправо
    ]

    while queue:
        r, c = queue.popleft()

        # Если мы наступили на финишную клетку, путь найден!
        if board[r][c] == target_marker:
            return True

        # Проверяем 4 направления
        for dr, dc, wr, wc in directions:
            next_r, next_c = r + dr, c + dc  # Куда прыгнет игрок
            wall_r, wall_c = r + wr, c + wc  # Где находится потенциальная стена

            # Проверяем, не вышли ли мы за границы поля 17x17
            if 0 <= next_r < 17 and 0 <= next_c < 17:
                # ГЛАВНАЯ ПРОВЕРКА: Если на промежутке НЕТ стены (False) и клетка не посещалась
                if board[wall_r][wall_c] is False and (next_r, next_c) not in visited:
                    visited.add((next_r, next_c))
                    queue.append((next_r, next_c))

    # Если очередь опустела, а мы так и не нашли финиш - пути нет
    return False

def get_grid_indices(pos):
    x, y = pos

    shifted_x = x - 50
    shifted_y = y - 60

    if shifted_x < 0 or shifted_y < 0:
        return None

    col_block = shifted_x // 100
    row_block = shifted_y // 100

    local_x = shifted_x % 100
    local_y = shifted_y % 100

    if local_x <= 80:
        i = col_block * 2
    else:
        i = col_block * 2 + 1

    if local_y <= 80:
        j = row_block * 2
    else:
        j = row_block * 2 + 1

    if 0 <= i < 17 and 0 <= j < 17:
        return [16 - j, i]
    else:
        return None

def check_legal_wall(board):
    """
    Главная функция для твоей игры.
    Вызывай её ПОСЛЕ того, как временно поставил стену в матрицу.
    Возвращает True, если стена легальна, и False, если блокирует путь.
    """
    # 1. Находим игроков
    pos_R = find_player(board, 'R')
    pos_B = find_player(board, 'B')

    # 2. Проверяем, есть ли путь для Красного к 'FR'
    path_for_R = has_path(board, pos_R, 'FR')

    # 3. Проверяем, есть ли путь для Синего к 'FB'
    path_for_B = has_path(board, pos_B, 'FB')

    # 4. Ход легален ТОЛЬКО если оба игрока могут дойти до финиша
    return path_for_R and path_for_B

def load_image(name):
    fullname = os.path.join('Assets', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        exit()
    im = pg.image.load(fullname).convert_alpha()
    return im