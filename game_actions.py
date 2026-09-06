"""Действия игры"""
import pygame
import random
import sys
import math
from settings import *
from buildings import BuildingType, Building
from resources import ResourceType
from game_map import GameMap
from person import Person


class GameActions:
    def __init__(self, game):
        self.game = game
        self.production_timer = 0
        self.production_interval = 600
        self.food_consumption_timer = 0
        self.food_consumption_interval = 600
        self.mining_timer = 0
        self.mining_interval = 1
    
    def select_building(self, building_type):
        """Выбор здания для строительства"""
        self.game.selected_building = Building(building_type)
        self.game.selected_person = None
        self.game.selected_existing_building = None
        self.game.plus_button_rect = None
        self.game.minus_button_rect = None
    
    def clear_selection(self):
        """Очистка выделения"""
        self.game.selected_building = None
        self.game.selected_person = None
        self.game.selected_existing_building = None
        self.game.plus_button_rect = None
        self.game.minus_button_rect = None
    
    def handle_mouse(self, button, pos):
        """Обработка мыши"""
        x, y = pos
        tile_x = int((x - self.game.camera_x) // self.game.tile_size)
        tile_y = int((y - self.game.camera_y) // self.game.tile_size)
        
        if button == 1:  # ЛКМ
            if hasattr(self.game.ui, 'panel_button_rect') and self.game.ui.panel_button_rect.collidepoint(pos):
                self.game.ui.bottom_panel_open = not self.game.ui.bottom_panel_open
                return
            
            if self.game.ui.bottom_panel_open and hasattr(self.game.ui, 'building_buttons'):
                for button_data in self.game.ui.building_buttons:
                    if button_data['rect'].collidepoint(pos):
                        self.select_building(button_data['type'])
                        return
            
            if self.game.selected_existing_building and self.game.selected_existing_building.type == BuildingType.WAREHOUSE:
                if hasattr(self.game.ui, 'wood_button_rect') and self.game.ui.wood_button_rect.collidepoint(pos):
                    self.assign_worker_to_mining(ResourceType.WOOD)
                    return
                if hasattr(self.game.ui, 'stone_button_rect') and self.game.ui.stone_button_rect.collidepoint(pos):
                    self.assign_worker_to_mining(ResourceType.STONE)
                    return
                if hasattr(self.game.ui, 'reset_button_rect') and self.game.ui.reset_button_rect.collidepoint(pos):
                    self.reset_mining_assignments()
                    return
            
            if self.game.plus_button_rect and self.game.plus_button_rect.collidepoint(pos):
                if self.game.selected_existing_building:
                    if self.game.selected_existing_building.type == BuildingType.TOWN_HALL:
                        self.try_hire_worker()
                    else:
                        self.add_worker_to_building()
                return
            
            if self.game.minus_button_rect and self.game.minus_button_rect.collidepoint(pos):
                self.remove_worker_from_building()
                return
            
            if self.game.selected_building:
                self.try_place_building(tile_x, tile_y)
            elif self.game.selected_person:
                self.try_assign_work(tile_x, tile_y)
            else:
                self.check_person_click(x, y)
                self.check_building_click(tile_x, tile_y)
        
        elif button == 3:  # ПКМ
            self.clear_selection()
        
        elif button == 4:  # Колесо вверх
            self.game.tile_size = min(64, self.game.tile_size + 2)
        
        elif button == 5:  # Колесо вниз
            self.game.tile_size = max(16, self.game.tile_size - 2)
    
    def try_place_building(self, tile_x, tile_y):
        """Попытка разместить здание"""
        if not self.game.game_map or not self.game.selected_building:
            return
        
        building_type = self.game.selected_building.type
        
        # Проверяем ограничения
        if building_type == BuildingType.TOWN_HALL:
            town_halls = [b for b in self.game.game_map.buildings if b.type == BuildingType.TOWN_HALL]
            if len(town_halls) >= 1:
                print("Можно построить только одну ратушу!")
                return
        
        if building_type == BuildingType.WAREHOUSE:
            warehouses = [b for b in self.game.game_map.buildings if b.type == BuildingType.WAREHOUSE]
            if len(warehouses) >= 2:
                print("Можно построить только 2 склада!")
                return
        
        if self.game.game_map.can_place_building(self.game.selected_building, tile_x, tile_y):
            if self.game.resources.can_afford(self.game.selected_building.cost):
                if self.game.game_map.place_building(self.game.selected_building, tile_x, tile_y):
                    for resource, amount in self.game.selected_building.cost.items():
                        self.game.resources.remove(resource, amount)
                    
                    if building_type == BuildingType.TOWN_HALL:
                        self.add_initial_population()
                    elif building_type == BuildingType.HOUSE:
                        self.game.resources.max_population += self.game.selected_building.population_bonus
                        print(f"Лимит населения увеличен на {self.game.selected_building.population_bonus}")
                    elif building_type == BuildingType.WAREHOUSE:
                        print("Склад построен! Теперь можно добывать ресурсы.")
                    
                    print(f"Построено: {self.game.selected_building.name}")
                    # НЕ сбрасываем selected_building для множественного строительства
            else:
                print("Недостаточно ресурсов!")
    
    def add_initial_population(self):
        """Добавление начального населения"""
        town_hall = None
        for building in self.game.game_map.buildings:
            if building.type == BuildingType.TOWN_HALL:
                town_hall = building
                break
        
        if town_hall:
            for i in range(5):
                self.spawn_person(town_hall)
            
            self.game.resources.resources[ResourceType.POPULATION] += 5
            self.game.resources.max_population += 5
            print("Появилось 5 жителей!")
    
    def find_free_spot_near_building(self, building):
        """Найти свободную точку рядом со зданием"""
        if not self.game.game_map:
            return building.get_center()
        
        # Пробуем точки вокруг здания
        for distance in range(1, 10):
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                
                check_x = building.x + building.width / 2 + math.cos(rad) * (building.width / 2 + distance)
                check_y = building.y + building.height / 2 + math.sin(rad) * (building.height / 2 + distance)
                
                if 0 <= check_x < self.game.game_map.size and 0 <= check_y < self.game.game_map.size:
                    tile_x = int(check_x)
                    tile_y = int(check_y)
                    terrain_type = self.game.game_map.grid[tile_x][tile_y]
                    
                    if terrain_type in [1, 3]:  # Вода или горы
                        continue
                    
                    inside_building = False
                    for b in self.game.game_map.buildings:
                        if (b.x <= check_x < b.x + b.width and
                            b.y <= check_y < b.y + b.height):
                            inside_building = True
                            break
                    
                    if not inside_building:
                        return check_x, check_y
        
        # Случайные точки
        for _ in range(100):
            check_x = building.x + random.uniform(-5, building.width + 5)
            check_y = building.y + random.uniform(-5, building.height + 5)
            
            if 0 <= check_x < self.game.game_map.size and 0 <= check_y < self.game.game_map.size:
                tile_x = int(check_x)
                tile_y = int(check_y)
                terrain_type = self.game.game_map.grid[tile_x][tile_y]
                
                if terrain_type not in [1, 3]:
                    inside_building = False
                    for b in self.game.game_map.buildings:
                        if (b.x <= check_x < b.x + b.width and
                            b.y <= check_y < b.y + b.height):
                            inside_building = True
                            break
                    
                    if not inside_building:
                        return check_x, check_y
        
        return building.x + building.width + 1, building.y + building.height + 1
    
    def spawn_person(self, building):
        """Создание нового жителя возле здания"""
        spawn_x, spawn_y = self.find_free_spot_near_building(building)
        
        person = Person(spawn_x, spawn_y, self.game.person_counter)
        person.spawn_building = building
        self.game.person_counter += 1
        self.game.people.append(person)
        return person
    
    def assign_worker_to_mining(self, resource_type):
        """Назначить рабочего на добычу"""
        if not self.game.selected_existing_building:
            return
        
        warehouse = self.game.selected_existing_building
        
        busy_workers = sum(1 for p in self.game.people if p.workplace is not None)
        available_workers = len(self.game.people) - busy_workers
        
        if available_workers <= 0:
            print("Нет свободных рабочих!")
            return
        
        if len(warehouse.workers) >= warehouse.max_workers:
            print("Склад переполнен!")
            return
        
        for person in self.game.people:
            if person.workplace is None:
                person.workplace = warehouse
                person.mining_resource = resource_type
                person.state = "idle"
                person.visible = True
                
                free_x, free_y = self.find_free_spot_near_building(warehouse)
                person.x = free_x
                person.y = free_y
                person.target_x = person.x
                person.target_y = person.y
                
                warehouse.workers.append(person)
                
                if resource_type == ResourceType.WOOD:
                    warehouse.assigned_wood_workers += 1
                    print(f"Рабочий {person.id} назначен на добычу дерева")
                elif resource_type == ResourceType.STONE:
                    warehouse.assigned_stone_workers += 1
                    print(f"Рабочий {person.id} назначен на добычу камня")
                
                self.find_mining_target_for_person(person)
                break
    
    def find_mining_target_for_person(self, person):
        """Найти ближайший ресурс"""
        if not person.mining_resource or not self.game.game_map:
            return
        
        target_terrain = 2 if person.mining_resource == ResourceType.WOOD else 4
        
        best_distance = float('inf')
        best_target = None
        
        search_radius = 50
        
        for dx in range(-search_radius, search_radius + 1):
            for dy in range(-search_radius, search_radius + 1):
                tile_x = int(person.x) + dx
                tile_y = int(person.y) + dy
                
                if 0 <= tile_x < self.game.game_map.size and 0 <= tile_y < self.game.game_map.size:
                    if self.game.game_map.grid[tile_x][tile_y] == target_terrain:
                        distance = (dx ** 2 + dy ** 2) ** 0.5
                        if distance < best_distance:
                            best_distance = distance
                            best_target = (tile_x + 0.5, tile_y + 0.5)
        
        if best_target:
            person.mining_target = best_target
            person.target_x = best_target[0]
            person.target_y = best_target[1]
            person.state = "walking"
            person.visible = True
        else:
            print(f"Нет ресурсов поблизости для рабочего {person.id}")
    
    def update_production(self):
        """Обновление производства"""
        if not self.game.game_map:
            return
        
        self.production_timer += 1
        
        if self.production_timer >= self.production_interval:
            self.production_timer = 0
            
            for building in self.game.game_map.buildings:
                if building.workers and building.type in [BuildingType.FARM, BuildingType.MARKET, BuildingType.TOWN_HALL]:
                    for resource, amount in building.production.items():
                        production_amount = amount * len(building.workers)
                        if resource in self.game.resources.resources:
                            self.game.resources.resources[resource] += production_amount
    
    def update_mining(self):
        """Обновление добычи - проверка КАЖДЫЙ КАДР"""
        if not self.game.game_map:
            return
        
        for person in self.game.people:
            if person.state == "returning" and person.carrying:
                if person.workplace:
                    center = person.workplace.get_center()
                    distance = ((person.x - center[0]) ** 2 + (person.y - center[1]) ** 2) ** 0.5
                    
                    if distance < 3.0:
                        if person.carrying == ResourceType.WOOD:
                            multiplier = self.get_wood_multiplier()
                            amount = 1 * multiplier
                            self.game.resources.add(ResourceType.WOOD, amount)
                            print(f"ДОСТАВЛЕНО ДЕРЕВО: +{amount}")
                        elif person.carrying == ResourceType.STONE:
                            multiplier = self.get_stone_multiplier()
                            amount = 1 * multiplier
                            self.game.resources.add(ResourceType.STONE, amount)
                            print(f"ДОСТАВЛЕН КАМЕНЬ: +{amount}")
                        
                        person.carrying = None
                        person.mining_target = None
                        person.mining_progress = 0
                        person.state = "idle"
                        
                        self.find_mining_target_for_person(person)
            
            elif person.state == "idle" and person.workplace and person.mining_resource:
                self.find_mining_target_for_person(person)
    
    def update_food_consumption(self):
        """Обновление потребления еды"""
        if not self.game.game_map:
            return
        
        self.food_consumption_timer += 1
        
        if self.food_consumption_timer >= self.food_consumption_interval:
            self.food_consumption_timer = 0
            
            population = self.game.resources.get(ResourceType.POPULATION)
            food_consumption = population * 0.05
            
            if food_consumption > 0:
                if self.game.resources.resources[ResourceType.FOOD] >= food_consumption:
                    self.game.resources.resources[ResourceType.FOOD] -= food_consumption
                else:
                    self.game.resources.resources[ResourceType.FOOD] = 0
                    print("Население голодает!")
    
    def get_wood_multiplier(self):
        """Множитель дерева"""
        multiplier = 1
        if self.game.game_map:
            for building in self.game.game_map.buildings:
                if building.type == BuildingType.LUMBERJACK:
                    multiplier = building.wood_multiplier
        return multiplier
    
    def get_stone_multiplier(self):
        """Множитель камня"""
        multiplier = 1
        if self.game.game_map:
            for building in self.game.game_map.buildings:
                if building.type == BuildingType.QUARRY:
                    multiplier = building.stone_multiplier
        return multiplier
    
    def draw_selection(self):
        """Отрисовка выделения"""
        if self.game.selected_person and self.game.selected_person.visible:
            screen_x = self.game.camera_x + self.game.selected_person.x * self.game.tile_size
            screen_y = self.game.camera_y + self.game.selected_person.y * self.game.tile_size
            pygame.draw.circle(self.game.screen, COLORS['selected'], 
                             (int(screen_x), int(screen_y)), 
                             self.game.selected_person.size + 5, 2)
        
        if self.game.selected_building and self.game.game_map:
            x, y = self.game.mouse_pos
            tile_x = int((x - self.game.camera_x) // self.game.tile_size)
            tile_y = int((y - self.game.camera_y) // self.game.tile_size)
            
            rect = pygame.Rect(
                self.game.camera_x + tile_x * self.game.tile_size,
                self.game.camera_y + tile_y * self.game.tile_size,
                self.game.selected_building.width * self.game.tile_size,
                self.game.selected_building.height * self.game.tile_size
            )
            
            can_place = self.game.game_map.can_place_building(self.game.selected_building, tile_x, tile_y)
            has_resources = self.game.resources.can_afford(self.game.selected_building.cost)
            
            color = COLORS['valid'] if (can_place and has_resources) else COLORS['invalid']
            
            preview = pygame.Surface((rect.width, rect.height))
            preview.fill(color)
            preview.set_alpha(100)
            self.game.screen.blit(preview, rect)
            pygame.draw.rect(self.game.screen, color, rect, 3)
    
    def draw_person_info(self):
        """Информация о жителе"""
        if not self.game.selected_person:
            return
        
        panel_width = 300
        panel_height = 120
        x = SCREEN_WIDTH - panel_width - 10
        y = 10
        
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill(COLORS['ui_background'][:3])
        panel.set_alpha(COLORS['ui_background'][3])
        self.game.screen.blit(panel, (x, y))
        pygame.draw.rect(self.game.screen, COLORS['selected'], (x, y, panel_width, panel_height), 2)
        
        texts = [
            f"Житель #{self.game.selected_person.id}",
            f"Состояние: {self.game.selected_person.state}",
            f"Работа: {self.game.selected_person.workplace.name if self.game.selected_person.workplace else 'Нет'}",
        ]
        
        for i, text in enumerate(texts):
            surface = self.game.small_font.render(text, True, COLORS['text'])
            self.game.screen.blit(surface, (x + 10, y + 10 + i * 25))
    
    def draw_building_info(self):
        """Информация о здании"""
        if not self.game.selected_existing_building:
            return
        
        building = self.game.selected_existing_building
        
        if building.type == BuildingType.WAREHOUSE:
            self.game.ui.draw_warehouse_panel(building, SCREEN_WIDTH - 360, 10)
        else:
            panel_width = 350
            panel_height = 220
            x = SCREEN_WIDTH - panel_width - 10
            y = 10
            
            panel = pygame.Surface((panel_width, panel_height))
            panel.fill(COLORS['ui_background'][:3])
            panel.set_alpha(COLORS['ui_background'][3])
            self.game.screen.blit(panel, (x, y))
            pygame.draw.rect(self.game.screen, COLORS['selected'], (x, y, panel_width, panel_height), 2)
            
            name_text = self.game.font.render(building.name, True, COLORS['text'])
            self.game.screen.blit(name_text, (x + 10, y + 10))
            
            if building.max_workers > 0:
                bar_x = x + 10
                bar_y = y + 50
                bar_width = panel_width - 20
                bar_height = 30
                
                pygame.draw.rect(self.game.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
                
                progress = building.get_worker_progress()
                fill_width = int(bar_width * progress)
                if fill_width > 0:
                    pygame.draw.rect(self.game.screen, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))
                
                pygame.draw.rect(self.game.screen, COLORS['ui_border'], (bar_x, bar_y, bar_width, bar_height), 2)
                
                worker_text = self.game.small_font.render(
                    f"Рабочие: {len(building.workers)}/{building.max_workers}", 
                    True, COLORS['text']
                )
                text_rect = worker_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
                self.game.screen.blit(worker_text, text_rect)
                
                button_size = 30
                minus_x = x + 10
                plus_x = x + panel_width - button_size - 10
                button_y = y + 90
                
                pygame.draw.rect(self.game.screen, (200, 50, 50), (minus_x, button_y, button_size, button_size))
                pygame.draw.rect(self.game.screen, COLORS['ui_border'], (minus_x, button_y, button_size, button_size), 2)
                minus_text = self.game.font.render("-", True, COLORS['text'])
                minus_rect = minus_text.get_rect(center=(minus_x + button_size // 2, button_y + button_size // 2))
                self.game.screen.blit(minus_text, minus_rect)
                
                pygame.draw.rect(self.game.screen, (50, 200, 50), (plus_x, button_y, button_size, button_size))
                pygame.draw.rect(self.game.screen, COLORS['ui_border'], (plus_x, button_y, button_size, button_size), 2)
                plus_text = self.game.font.render("+", True, COLORS['text'])
                plus_rect = plus_text.get_rect(center=(plus_x + button_size // 2, button_y + button_size // 2))
                self.game.screen.blit(plus_text, plus_rect)
                
                self.game.plus_button_rect = pygame.Rect(plus_x, button_y, button_size, button_size)
                self.game.minus_button_rect = pygame.Rect(minus_x, button_y, button_size, button_size)
    
    def select_menu_option(self):
        """Выбор пункта меню"""
        option = self.game.menu_options[self.game.menu_selected]
        
        if option == "Выход":
            pygame.quit()
            sys.exit()
        else:
            size = int(option.split('x')[0])
            self.game.game_map = GameMap(size)
            self.game.show_menu = False
            self.game.camera_x = 0
            self.game.camera_y = 0
            self.game.tile_size = TILE_SIZE
            self.game.people = []
            self.game.person_counter = 0
            self.clear_selection()
            print(f"Начата игра с картой {size}x{size}")
    
    def check_person_click(self, mouse_x, mouse_y):
        """Проверка клика по жителю"""
        for person in self.game.people:
            if not person.visible:
                continue
            
            screen_x = self.game.camera_x + person.x * self.game.tile_size
            screen_y = self.game.camera_y + person.y * self.game.tile_size
            distance = ((mouse_x - screen_x) ** 2 + (mouse_y - screen_y) ** 2) ** 0.5
            
            if distance < person.size + 5:
                self.game.selected_person = person
                self.game.selected_building = None
                self.game.selected_existing_building = None
                print(f"Выбран житель {person.id}")
                return
    
    def check_building_click(self, tile_x, tile_y):
        """Проверка клика по зданию"""
        if not self.game.game_map:
            return
        
        for building in self.game.game_map.buildings:
            if (building.x <= tile_x < building.x + building.width and
                building.y <= tile_y < building.y + building.height):
                self.game.selected_existing_building = building
                self.game.selected_person = None
                self.game.selected_building = None
                print(f"Выбрано: {building.name}")
                return
    
    def try_assign_work(self, tile_x, tile_y):
        """Назначить на работу"""
        if not self.game.game_map or not self.game.selected_person:
            return
        
        for building in self.game.game_map.buildings:
            if (building.x <= tile_x < building.x + building.width and
                building.y <= tile_y < building.y + building.height):
                
                if building.type in [BuildingType.FARM, BuildingType.MARKET]:
                    if self.game.selected_person.assign_work(building):
                        print(f"Житель направлен на работу в {building.name}")
                        self.game.selected_person = None
                return
        
        self.game.selected_person = None
    
    def add_worker_to_building(self):
        """Добавить рабочего"""
        if not self.game.selected_existing_building:
            return
        
        building = self.game.selected_existing_building
        
        busy_workers = sum(1 for p in self.game.people if p.workplace is not None)
        available_workers = len(self.game.people) - busy_workers
        
        if available_workers <= 0:
            print("Нет свободных рабочих!")
            return
        
        if not building.can_add_worker():
            print(f"В здании {building.name} нет свободных мест!")
            return
        
        for person in self.game.people:
            if person.workplace is None:
                if person.assign_work(building):
                    print(f"Рабочий {person.id} направлен в {building.name}")
                    break
    
    def remove_worker_from_building(self):
        """Убрать рабочего"""
        if not self.game.selected_existing_building:
            return
        
        building = self.game.selected_existing_building
        
        if not building.workers:
            print(f"В здании {building.name} нет рабочих!")
            return
        
        worker = building.workers[-1]
        worker.remove_work(self.game.game_map)
        
        free_x, free_y = self.find_free_spot_near_building(building)
        worker.x = free_x
        worker.y = free_y
        worker.target_x = free_x
        worker.target_y = free_y
        
        print(f"Рабочий {worker.id} уволен из {building.name}")
    
    def try_hire_worker(self):
        """Нанять рабочего"""
        if not self.game.selected_existing_building:
            return
        
        if self.game.selected_existing_building.type == BuildingType.TOWN_HALL:
            if self.game.resources.get(ResourceType.POPULATION) >= self.game.resources.max_population:
                print("Достигнут лимит населения!")
                return
            
            if self.game.resources.hire_worker():
                self.spawn_person(self.game.selected_existing_building)
                print(f"Нанят новый рабочий!")
            else:
                print(f"Недостаточно золота!")
    
    def reset_mining_assignments(self):
        """Сбросить назначения"""
        if not self.game.selected_existing_building:
            return
        
        warehouse = self.game.selected_existing_building
        warehouse.assigned_wood_workers = 0
        warehouse.assigned_stone_workers = 0
        
        for worker in warehouse.workers[:]:
            worker.remove_work(self.game.game_map)
            
            free_x, free_y = self.find_free_spot_near_building(warehouse)
            worker.x = free_x
            worker.y = free_y
            worker.target_x = free_x
            worker.target_y = free_y
        
        print("Назначения сброшены")
