"""Настройки игры"""
import pygame
import os

# Размеры окна
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Размер тайла
TILE_SIZE = 32

# Пути к текстурам
SPRITE_DIR = "sprite"
TEXTURES = {
    'water': os.path.join(SPRITE_DIR, "water.jpg"),
    'forest': os.path.join(SPRITE_DIR, "tree.jpg"),
    'stone': os.path.join(SPRITE_DIR, "stone.jpg"),
    'plain': os.path.join(SPRITE_DIR, "grass.jpg"),
}

# Цвета
COLORS = {
    'water': (65, 105, 225),
    'forest': (34, 139, 34),
    'mountain': (139, 137, 137),
    'plain': (144, 238, 144),
    'stone': (105, 105, 105),
    'fertile': (152, 251, 152),
    'background': (0, 0, 0),
    'ui_background': (50, 50, 50, 180),
    'ui_border': (255, 255, 255),
    'selected': (255, 255, 0),
    'invalid': (255, 0, 0),
    'valid': (0, 255, 0),
    'text': (255, 255, 255),
    'text_highlight': (255, 255, 0),
}

# Типы местности
TERRAIN_TYPES = {
    0: {'name': 'plain', 'color': COLORS['plain'], 'buildable': True, 'texture': 'plain'},
    1: {'name': 'water', 'color': COLORS['water'], 'buildable': False, 'texture': 'water'},
    2: {'name': 'forest', 'color': COLORS['forest'], 'buildable': True, 'texture': 'forest'},
    3: {'name': 'mountain', 'color': COLORS['mountain'], 'buildable': False, 'texture': 'stone'},
    4: {'name': 'stone', 'color': COLORS['stone'], 'buildable': True, 'texture': 'stone'},
    5: {'name': 'fertile', 'color': COLORS['fertile'], 'buildable': True, 'texture': 'plain'},
}
