"""Основная логика игры"""
import pygame
import sys
import random
from settings import *
from game_map import GameMap
from buildings import Building, BuildingType
from resources import ResourceManager, ResourceType
from person import Person
from ui import UI
from game_actions import GameActions
from texture_manager import TextureManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Градостроительный симулятор")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        self.ui = UI(self.screen, self.font, self.small_font)
        self.resources = ResourceManager()
        self.actions = GameActions(self)
        self.textures = TextureManager()
        
        self.show_menu = True
        self.menu_options = ["64x64", "128x128", "256x256", "Выход"]
        self.menu_selected = 0
        
        self.game_map = None
        self.selected_building = None
        self.selected_person = None
        self.selected_existing_building = None
        self.people = []
        self.person_counter = 0
        
        self.camera_x = 0
        self.camera_y = 0
        self.tile_size = TILE_SIZE
        
        self.show_grid = False
        self.paused = False
        self.mouse_pos = (0, 0)
        
        self.plus_button_rect = None
        self.minus_button_rect = None
        
        self.buildings_data = [
            {'type': BuildingType.HOUSE, 'name': 'Дом', 'color': (200, 150, 100)},
            {'type': BuildingType.FARM, 'name': 'Ферма', 'color': (255, 200, 100)},
            {'type': BuildingType.WAREHOUSE, 'name': 'Склад', 'color': (139, 119, 101)},
            {'type': BuildingType.LUMBERJACK, 'name': 'Лесопилка', 'color': (150, 100, 50)},
            {'type': BuildingType.QUARRY, 'name': 'Каменоломня', 'color': (150, 150, 150)},
            {'type': BuildingType.MARKET, 'name': 'Рынок', 'color': (255, 200, 200)},
            {'type': BuildingType.TOWN_HALL, 'name': 'Ратуша', 'color': (200, 200, 255)},
        ]
        
        print("Игра инициализирована")
    
    def run(self):
        """Основной игровой цикл"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse(event.button, event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
            
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def handle_key(self, key):
        """Обработка нажатий клавиш"""
        if self.show_menu:
            if key == pygame.K_UP:
                self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
            elif key == pygame.K_DOWN:
                self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
            elif key == pygame.K_RETURN:
                self.actions.select_menu_option()
        else:
            if key == pygame.K_ESCAPE:
                self.show_menu = True
                self.actions.clear_selection()
            elif key == pygame.K_SPACE:
                self.paused = not self.paused
            elif key == pygame.K_b:
                self.ui.bottom_panel_open = not self.ui.bottom_panel_open
            elif key == pygame.K_1:
                self.actions.select_building(BuildingType.HOUSE)
            elif key == pygame.K_2:
                self.actions.select_building(BuildingType.FARM)
            elif key == pygame.K_3:
                self.actions.select_building(BuildingType.WAREHOUSE)
            elif key == pygame.K_4:
                self.actions.select_building(BuildingType.LUMBERJACK)
            elif key == pygame.K_5:
                self.actions.select_building(BuildingType.QUARRY)
            elif key == pygame.K_6:
                self.actions.select_building(BuildingType.MARKET)
            elif key == pygame.K_7:
                self.actions.select_building(BuildingType.TOWN_HALL)
    
    def handle_mouse(self, button, pos):
        """Обработка мыши"""
        if self.show_menu:
            return
        
        self.actions.handle_mouse(button, pos)
    
    def update(self):
        """Обновление состояния"""
        if not self.show_menu and not self.paused:
            keys = pygame.key.get_pressed()
            camera_speed = 15
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.camera_x += camera_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.camera_x -= camera_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.camera_y += camera_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.camera_y -= camera_speed
            
            for person in self.people:
                person.update(self.game_map)
            
            self.actions.update_production()
            self.actions.update_food_consumption()
            self.actions.update_mining()
    
    def draw(self):
        """Отрисовка"""
        if self.show_menu:
            self.ui.draw_menu(self.menu_options, self.menu_selected)
        else:
            self.draw_game()
    
    def draw_game(self):
        """Отрисовка игры"""
        self.screen.fill(COLORS['background'])
        
        if not self.game_map:
            return
        
        self.draw_tiles()
        self.draw_buildings()
        self.draw_people()
        self.actions.draw_selection()
        
        self.ui.draw_resources(self.resources)
        
        if self.selected_building:
            self.ui.draw_building_info(self.selected_building, SCREEN_WIDTH - 310, 10)
        elif self.selected_person:
            self.actions.draw_person_info()
        elif self.selected_existing_building:
            self.actions.draw_building_info()
        
        self.ui.draw_bottom_panel(self.buildings_data)
        
        if not self.ui.bottom_panel_open:
            hints = [
                "B: Панель построек | Space: Пауза | Esc: Меню",
                "Постройте склад, чтобы начать добычу ресурсов",
                f"Карта: {self.game_map.size}x{self.game_map.size} | Население: {len(self.people)}",
            ]
            self.ui.draw_hints(hints, 10, SCREEN_HEIGHT - 150)
    
    def draw_tiles(self):
        """Отрисовка тайлов с текстурами"""
        for x in range(self.game_map.size):
            for y in range(self.game_map.size):
                rect = pygame.Rect(
                    self.camera_x + x * self.tile_size,
                    self.camera_y + y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                
                if rect.right < 0 or rect.left > SCREEN_WIDTH:
                    continue
                if rect.bottom < 0 or rect.top > SCREEN_HEIGHT:
                    continue
                
                terrain_type = self.game_map.grid[x][y]
                terrain_info = TERRAIN_TYPES[terrain_type]
                
                texture_name = terrain_info.get('texture', 'plain')
                texture = self.textures.get_scaled_texture(texture_name, self.tile_size)
                self.screen.blit(texture, rect)
    
    def draw_buildings(self):
        """Отрисовка зданий"""
        for building in self.game_map.buildings:
            rect = pygame.Rect(
                self.camera_x + building.x * self.tile_size,
                self.camera_y + building.y * self.tile_size,
                building.width * self.tile_size,
                building.height * self.tile_size
            )
            
            if rect.right < 0 or rect.left > SCREEN_WIDTH:
                continue
            if rect.bottom < 0 or rect.top > SCREEN_HEIGHT:
                continue
            
            pygame.draw.rect(self.screen, building.color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 3)
            
            if self.tile_size >= 32:
                name_surface = self.small_font.render(building.name, True, COLORS['text'])
                name_rect = name_surface.get_rect(center=rect.center)
                self.screen.blit(name_surface, name_rect)
            
            if building.workers and building.max_workers > 0:
                worker_text = f"{len(building.workers)}/{building.max_workers}"
                worker_surface = self.small_font.render(worker_text, True, COLORS['text_highlight'])
                worker_rect = worker_surface.get_rect(center=(rect.centerx, rect.bottom - 15))
                self.screen.blit(worker_surface, worker_rect)
    
    def draw_people(self):
        """Отрисовка жителей"""
        for person in self.people:
            person.draw(self.screen, self.camera_x, self.camera_y, self.tile_size)
