"""Интерфейс и отрисовка"""
import pygame
from settings import *
from resources import ResourceType
from buildings import BuildingType


class UI:
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.bottom_panel_open = False
    
    def draw_menu(self, menu_options, menu_selected):
        """Отрисовка главного меню"""
        self.screen.fill(COLORS['background'])
        
        title = self.font.render("ГРАДОСТРОИТЕЛЬНЫЙ СИМУЛЯТОР", True, COLORS['text'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.small_font.render("Выберите размер карты", True, COLORS['text'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        for i, option in enumerate(menu_options):
            color = COLORS['text_highlight'] if i == menu_selected else COLORS['text']
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 70))
            self.screen.blit(text, text_rect)
        
        hint = self.small_font.render("Используйте стрелки и Enter для выбора", True, COLORS['text'])
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 600))
        self.screen.blit(hint, hint_rect)
    
    def draw_resources(self, resource_manager, x=10, y=10):
        """Отрисовка панели ресурсов"""
        panel_width = 280
        panel_height = 220
        
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill(COLORS['ui_background'][:3])
        panel.set_alpha(COLORS['ui_background'][3])
        self.screen.blit(panel, (x, y))
        
        pygame.draw.rect(self.screen, COLORS['ui_border'], (x, y, panel_width, panel_height), 2)
        
        resources = [
            f"Дерево: {resource_manager.get(ResourceType.WOOD)}",
            f"Камень: {resource_manager.get(ResourceType.STONE)}",
            f"Еда: {resource_manager.get(ResourceType.FOOD):.1f}",
            f"Золото: {resource_manager.get(ResourceType.GOLD)}",
            f"Население: {resource_manager.get(ResourceType.POPULATION)}/{resource_manager.max_population}",
            f"Стоимость рабочего: {resource_manager.worker_cost} золота",
        ]
        
        for i, text in enumerate(resources):
            surface = self.small_font.render(text, True, COLORS['text'])
            self.screen.blit(surface, (x + 10, y + 10 + i * 30))
    
    def draw_bottom_panel(self, buildings_data):
        """Отрисовка нижней панели с постройками"""
        panel_height = 100 if not self.bottom_panel_open else 200
        panel_y = SCREEN_HEIGHT - panel_height
        
        panel = pygame.Surface((SCREEN_WIDTH, panel_height))
        panel.fill((40, 40, 40))
        panel.set_alpha(230)
        self.screen.blit(panel, (0, panel_y))
        
        pygame.draw.rect(self.screen, COLORS['ui_border'], (0, panel_y, SCREEN_WIDTH, panel_height), 2)
        
        button_width = 100
        button_height = 30
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = panel_y - button_height
        
        pygame.draw.rect(self.screen, (60, 60, 60), (button_x, button_y, button_width, button_height))
        pygame.draw.rect(self.screen, COLORS['ui_border'], (button_x, button_y, button_width, button_height), 2)
        
        arrow = "▼" if not self.bottom_panel_open else "▲"
        button_text = self.small_font.render(f"Постройки {arrow}", True, COLORS['text'])
        button_rect = button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        self.screen.blit(button_text, button_rect)
        
        self.panel_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if self.bottom_panel_open:
            self.draw_building_buttons(buildings_data, panel_y)
    
    def draw_building_buttons(self, buildings_data, panel_y):
        """Отрисовка кнопок зданий"""
        button_size = 60
        spacing = 10
        start_x = 20
        start_y = panel_y + 20
        
        self.building_buttons = []
        
        for i, building_data in enumerate(buildings_data):
            x = start_x + i * (button_size + spacing)
            y = start_y
            
            pygame.draw.rect(self.screen, building_data['color'], (x, y, button_size, button_size))
            pygame.draw.rect(self.screen, COLORS['ui_border'], (x, y, button_size, button_size), 2)
            
            name_text = self.small_font.render(building_data['name'][:8], True, COLORS['text'])
            name_rect = name_text.get_rect(center=(x + button_size // 2, y + button_size + 10))
            self.screen.blit(name_text, name_rect)
            
            self.building_buttons.append({
                'rect': pygame.Rect(x, y, button_size, button_size),
                'type': building_data['type']
            })
    
    def draw_building_info(self, building, x, y):
        """Отрисовка информации о здании"""
        panel_width = 300
        panel_height = 150
        
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill(COLORS['ui_background'][:3])
        panel.set_alpha(COLORS['ui_background'][3])
        self.screen.blit(panel, (x, y))
        
        pygame.draw.rect(self.screen, COLORS['selected'], (x, y, panel_width, panel_height), 2)
        
        name_text = self.font.render(building.name, True, COLORS['text'])
        self.screen.blit(name_text, (x + 10, y + 10))
        
        desc_text = self.small_font.render(building.description, True, COLORS['text'])
        self.screen.blit(desc_text, (x + 10, y + 40))
        
        size_text = self.small_font.render(f"Размер: {building.width}x{building.height}", True, COLORS['text'])
        self.screen.blit(size_text, (x + 10, y + 70))
        
        cost_text = self.small_font.render(f"Стоимость: {building.get_cost_text()}", True, COLORS['text'])
        self.screen.blit(cost_text, (x + 10, y + 100))
        
        hint_text = self.small_font.render("Кликните для размещения", True, COLORS['text_highlight'])
        self.screen.blit(hint_text, (x + 10, y + 130))
    
    def draw_warehouse_panel(self, warehouse, x, y):
        """Отрисовка панели управления складом"""
        panel_width = 350
        panel_height = 250
        x = SCREEN_WIDTH - panel_width - 10
        y = 10
        
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill(COLORS['ui_background'][:3])
        panel.set_alpha(COLORS['ui_background'][3])
        self.screen.blit(panel, (x, y))
        pygame.draw.rect(self.screen, COLORS['selected'], (x, y, panel_width, panel_height), 2)
        
        name_text = self.font.render("Склад", True, COLORS['text'])
        self.screen.blit(name_text, (x + 10, y + 10))
        
        workers_text = self.small_font.render(
            f"Всего рабочих: {len(warehouse.workers)}/{warehouse.max_workers}", 
            True, COLORS['text']
        )
        self.screen.blit(workers_text, (x + 10, y + 40))
        
        wood_text = self.small_font.render(
            f"Добывают дерево: {warehouse.assigned_wood_workers}", 
            True, COLORS['text']
        )
        self.screen.blit(wood_text, (x + 10, y + 65))
        
        stone_text = self.small_font.render(
            f"Добывают камень: {warehouse.assigned_stone_workers}", 
            True, COLORS['text']
        )
        self.screen.blit(stone_text, (x + 10, y + 90))
        
        button_width = 150
        button_height = 30
        button_x = x + 10
        button_y = y + 120
        
        pygame.draw.rect(self.screen, (100, 150, 50), (button_x, button_y, button_width, button_height))
        pygame.draw.rect(self.screen, COLORS['ui_border'], (button_x, button_y, button_width, button_height), 2)
        wood_button_text = self.small_font.render("+ Дерево", True, COLORS['text'])
        wood_button_rect = wood_button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        self.screen.blit(wood_button_text, wood_button_rect)
        self.wood_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        button_y += button_height + 10
        pygame.draw.rect(self.screen, (100, 100, 150), (button_x, button_y, button_width, button_height))
        pygame.draw.rect(self.screen, COLORS['ui_border'], (button_x, button_y, button_width, button_height), 2)
        stone_button_text = self.small_font.render("+ Камень", True, COLORS['text'])
        stone_button_rect = stone_button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        self.screen.blit(stone_button_text, stone_button_rect)
        self.stone_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        button_y += button_height + 10
        pygame.draw.rect(self.screen, (150, 50, 50), (button_x, button_y, button_width, button_height))
        pygame.draw.rect(self.screen, COLORS['ui_border'], (button_x, button_y, button_width, button_height), 2)
        reset_button_text = self.small_font.render("Сбросить", True, COLORS['text'])
        reset_button_rect = reset_button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        self.screen.blit(reset_button_text, reset_button_rect)
        self.reset_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    def draw_hints(self, hints, x=10, y=None):
        """Отрисовка подсказок (перемещены выше)"""
        if y is None:
            y = SCREEN_HEIGHT - 130  # Выше нижней панели
        
        for i, hint in enumerate(hints):
            surface = self.small_font.render(hint, True, COLORS['text'])
            self.screen.blit(surface, (x, y + i * 25))
