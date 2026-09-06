"""Управление текстурами"""
import pygame
from settings import TEXTURES, TILE_SIZE


class TextureManager:
    def __init__(self):
        self.textures = {}
        self.load_textures()
    
    def load_textures(self):
        """Загрузка всех текстур"""
        for texture_name, texture_path in TEXTURES.items():
            try:
                texture = pygame.image.load(texture_path)
                texture = pygame.transform.scale(texture, (TILE_SIZE, TILE_SIZE))
                self.textures[texture_name] = texture
                print(f"Текстура '{texture_name}' загружена")
            except Exception as e:
                print(f"Ошибка загрузки текстуры '{texture_name}': {e}")
                self.textures[texture_name] = self.create_placeholder(texture_name)
    
    def create_placeholder(self, texture_name):
        """Создание заглушки если текстура не загрузилась"""
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        colors = {
            'water': (65, 105, 225),
            'forest': (34, 139, 34),
            'stone': (105, 105, 105),
            'plain': (144, 238, 144),
        }
        
        color = colors.get(texture_name, (128, 128, 128))
        surface.fill(color)
        return surface
    
    def get_texture(self, texture_name):
        """Получить текстуру по имени"""
        return self.textures.get(texture_name, self.textures.get('plain'))
    
    def get_scaled_texture(self, texture_name, size):
        """Получить текстуру нужного размера"""
        texture = self.get_texture(texture_name)
        return pygame.transform.scale(texture, (size, size))
