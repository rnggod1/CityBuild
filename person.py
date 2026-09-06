"""Класс жителя"""
import random
import pygame
from settings import TILE_SIZE, TERRAIN_TYPES


class Person:
    def __init__(self, x, y, person_id):
        self.id = person_id
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = 0.2
        self.state = "idle"
        self.workplace = None
        self.color = (255, 255, 255)
        self.size = 8
        self.wander_timer = 0
        self.wander_interval = random.randint(10, 30)
        self.visible = True
        self.spawn_building = None
        self.mining_target = None
        self.mining_resource = None
        self.carrying = None
        self.mining_progress = 0
        self.mining_time = 180
    
    def update(self, game_map):
        """Обновление состояния жителя"""
        if self.state == "idle":
            self.wander_timer += 1
            if self.wander_timer >= self.wander_interval:
                self.wander(game_map)
                self.wander_timer = 0
                self.wander_interval = random.randint(10, 30)
        
        elif self.state == "walking":
            self.move_to_target(game_map)
        
        elif self.state == "working":
            self.visible = False
        
        elif self.state == "mining":
            self.update_mining()
        
        elif self.state == "returning":
            self.move_to_target(game_map)
    
    def can_move_to(self, x, y, game_map):
        """Проверка, можно ли переместиться на позицию"""
        if not game_map:
            return True
        
        # Проверяем границы карты
        if x < 0 or y < 0 or x >= game_map.size or y >= game_map.size:
            return False
        
        # Проверяем тип местности
        tile_x = int(x)
        tile_y = int(y)
        terrain_type = game_map.grid[tile_x][tile_y]
        
        # Нельзя ходить по воде
        if terrain_type == 1:  # Вода
            return False
        
        # Нельзя ходить по горам
        if terrain_type == 3:  # Горы
            return False
        
        # Проверяем здания
        for building in game_map.buildings:
            if (building.x <= x < building.x + building.width and
                building.y <= y < building.y + building.height):
                return False
        
        return True
    
    def wander(self, game_map):
        """Бесцельное блуждание"""
        if self.workplace:
            if self.mining_resource:
                center = self.workplace.get_center()
                self.target_x = center[0] + random.uniform(-1, 1)
                self.target_y = center[1] + random.uniform(-1, 1)
            else:
                center = self.workplace.get_center()
                self.target_x = center[0] + random.uniform(-0.5, 0.5)
                self.target_y = center[1] + random.uniform(-0.5, 0.5)
            self.state = "walking"
        else:
            # Случайное движение с проверкой коллизии
            for _ in range(10):  # Пробуем найти валидную точку
                new_x = self.x + random.uniform(-5, 5)
                new_y = self.y + random.uniform(-5, 5)
                if self.can_move_to(new_x, new_y, game_map):
                    self.target_x = new_x
                    self.target_y = new_y
                    self.state = "walking"
                    break
    
    def move_to_target(self, game_map):
        """Движение к цели с коллизией"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < 0.2:
            self.x = self.target_x
            self.y = self.target_y
            
            if self.state == "walking":
                if self.workplace and self.mining_target:
                    self.state = "mining"
                    self.mining_progress = 0
                    self.visible = True
                elif self.workplace and self.mining_resource:
                    self.state = "idle"
                    self.visible = True
                elif self.workplace:
                    self.state = "working"
                    self.visible = False
                    if self not in self.workplace.workers:
                        self.workplace.workers.append(self)
                else:
                    self.state = "idle"
                    self.visible = True
        else:
            dx /= distance
            dy /= distance
            
            # Проверяем коллизию перед движением
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if self.can_move_to(new_x, new_y, game_map):
                self.x = new_x
                self.y = new_y
            else:
                # Пробуем обойти препятствие
                # Движение по X
                if self.can_move_to(new_x, self.y, game_map):
                    self.x = new_x
                # Движение по Y
                elif self.can_move_to(self.x, new_y, game_map):
                    self.y = new_y
                else:
                    # Застряли, ищем новую цель
                    self.state = "idle"
    
    def update_mining(self):
        """Обновление добычи (3 секунды)"""
        if not self.mining_target:
            return
        
        self.mining_progress += 1
        
        if self.mining_progress >= self.mining_time:
            self.carrying = self.mining_resource
            self.state = "returning"
            self.mining_target = None
            self.mining_progress = 0
            
            if self.workplace:
                center = self.workplace.get_center()
                self.target_x = center[0]
                self.target_y = center[1]
    
    def assign_work(self, building):
        """Назначить работу"""
        if building.can_add_worker():
            self.workplace = building
            self.state = "walking"
            self.visible = True
            center = building.get_center()
            self.target_x = center[0]
            self.target_y = center[1]
            return True
        return False
    
    def assign_mining(self, warehouse, resource_type):
        """Назначить на добычу ресурса"""
        self.workplace = warehouse
        self.mining_resource = resource_type
        self.state = "idle"
        self.visible = True
        
        center = warehouse.get_center()
        self.x = center[0] + random.uniform(-1, 1)
        self.y = center[1] + random.uniform(-1, 1)
        self.target_x = self.x
        self.target_y = self.y
        
        return True
    
    def find_free_spot_near_building(self, building, game_map):
        """Найти свободную точку рядом со зданием"""
        # Пробуем разные позиции вокруг здания
        for distance in [1, 2, 3, 4, 5]:
            for angle in range(0, 360, 45):
                rad = angle * 3.14159 / 180
                new_x = building.x + building.width / 2 + distance * 1.5 * (0.5 + angle % 2) * (1 if angle < 180 else -1)
                new_y = building.y + building.height / 2 + distance * 1.5 * (0.5 + (angle // 90) % 2) * (1 if angle % 180 < 90 else -1)
                
                if self.can_move_to(new_x, new_y, game_map):
                    return new_x, new_y
        
        # Если не нашли, пробуем случайные точки
        for _ in range(50):
            new_x = building.x + random.uniform(-5, building.width + 5)
            new_y = building.y + random.uniform(-5, building.height + 5)
            if self.can_move_to(new_x, new_y, game_map):
                return new_x, new_y
        
        # Если совсем не нашли, возвращаем текущую позицию
        return self.x, self.y
    
    def remove_work(self, game_map=None):
        """Убрать с работы"""
        if self.workplace:
            if self in self.workplace.workers:
                self.workplace.workers.remove(self)
            
            building = self.workplace
            self.workplace = None
            self.mining_target = None
            self.mining_resource = None
            self.carrying = None
            self.state = "idle"
            self.visible = True
            
            # Ищем свободную точку рядом со зданием
            if game_map:
                self.x, self.y = self.find_free_spot_near_building(building, game_map)
            else:
                self.x = building.x + building.width + random.uniform(0.5, 1.5)
                self.y = building.y + building.height / 2
            
            self.target_x = self.x
            self.target_y = self.y
    
    def draw(self, screen, camera_x, camera_y, tile_size):
        """Отрисовка жителя"""
        if not self.visible:
            return
        
        screen_x = camera_x + self.x * tile_size
        screen_y = camera_y + self.y * tile_size
        
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.size)
        
        if self.state == "mining":
            pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y - 12)), 3)
            progress = self.mining_progress / self.mining_time
            pygame.draw.rect(screen, (255, 255, 0), 
                           (int(screen_x - 10), int(screen_y - 20), 
                            int(20 * progress), 5))
        elif self.carrying:
            pygame.draw.circle(screen, (0, 255, 0), (int(screen_x), int(screen_y - 12)), 3)
        elif self.state == "walking" and self.mining_resource:
            pygame.draw.circle(screen, (255, 165, 0), (int(screen_x), int(screen_y - 12)), 3)
