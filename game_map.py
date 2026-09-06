"""Генерация и управление картой"""
import random
from settings import TERRAIN_TYPES


class GameMap:
    def __init__(self, size):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.buildings = []
        self.generate_map()
    
    def generate_map(self):
        """Генерация карты"""
        print(f"Генерация карты {self.size}x{self.size}...")
        
        self.create_lake()
        self.create_river()
        self.create_mountains()
        self.create_forests()
        self.create_fertile_land()
        
        print("Карта готова!")
    
    def create_lake(self):
        """Создание озера"""
        lake_x = random.randint(self.size // 4, self.size * 3 // 4)
        lake_y = random.randint(self.size // 4, self.size * 3 // 4)
        lake_radius = random.randint(self.size // 16, self.size // 8)
        
        for x in range(max(0, lake_x - lake_radius), min(self.size, lake_x + lake_radius)):
            for y in range(max(0, lake_y - lake_radius), min(self.size, lake_y + lake_radius)):
                if ((x - lake_x) ** 2 + (y - lake_y) ** 2) < lake_radius ** 2:
                    self.grid[x][y] = 1
    
    def create_river(self):
        """Создание реки"""
        river_x = random.randint(self.size // 3, self.size * 2 // 3)
        direction = random.choice([-1, 1])
        
        for y in range(self.size):
            if 0 <= river_x < self.size:
                self.grid[river_x][y] = 1
                
                if river_x > 0 and self.grid[river_x - 1][y] == 0:
                    if random.random() < 0.3:
                        self.grid[river_x - 1][y] = 4
                if river_x < self.size - 1 and self.grid[river_x + 1][y] == 0:
                    if random.random() < 0.3:
                        self.grid[river_x + 1][y] = 4
                
                if random.random() < 0.3:
                    river_x += direction
                    river_x = max(0, min(self.size - 1, river_x))
                if random.random() < 0.1:
                    direction *= -1
    
    def create_mountains(self):
        """Создание гор"""
        num_mountains = max(5, self.size // 10)
        
        for _ in range(num_mountains):
            mx = random.randint(0, self.size - 1)
            my = random.randint(0, self.size - 1)
            
            if self.grid[mx][my] == 0:
                mountain_size = random.randint(2, 5)
                
                for x in range(max(0, mx - mountain_size), min(self.size, mx + mountain_size)):
                    for y in range(max(0, my - mountain_size), min(self.size, my + mountain_size)):
                        if self.grid[x][y] == 0:
                            if random.random() < 0.7:
                                self.grid[x][y] = 3
                            elif random.random() < 0.5:
                                self.grid[x][y] = 4
    
    def create_forests(self):
        """Создание лесов"""
        num_forests = max(10, self.size // 5)
        
        for _ in range(num_forests):
            fx = random.randint(0, self.size - 1)
            fy = random.randint(0, self.size - 1)
            
            if self.grid[fx][fy] == 0:
                forest_size = random.randint(3, 8)
                
                for x in range(max(0, fx - forest_size), min(self.size, fx + forest_size)):
                    for y in range(max(0, fy - forest_size), min(self.size, fy + forest_size)):
                        if self.grid[x][y] == 0 and random.random() < 0.7:
                            self.grid[x][y] = 2
    
    def create_fertile_land(self):
        """Создание плодородных земель возле воды"""
        for x in range(self.size):
            for y in range(self.size):
                if self.grid[x][y] == 0:
                    near_water = False
                    for dx in [-3, -2, -1, 0, 1, 2, 3]:
                        for dy in [-3, -2, -1, 0, 1, 2, 3]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.size and 0 <= ny < self.size:
                                if self.grid[nx][ny] == 1:
                                    near_water = True
                                    break
                        if near_water:
                            break
                    
                    if near_water and random.random() < 0.4:
                        self.grid[x][y] = 5
    
    def can_place_building(self, building, x, y):
        """Проверка возможности размещения здания"""
        if x < 0 or y < 0:
            return False
        if x + building.width > self.size or y + building.height > self.size:
            return False
        
        for dx in range(building.width):
            for dy in range(building.height):
                tile_x = x + dx
                tile_y = y + dy
                
                if not TERRAIN_TYPES[self.grid[tile_x][tile_y]]['buildable']:
                    return False
                
                for other_building in self.buildings:
                    if (other_building.x <= tile_x < other_building.x + other_building.width and
                        other_building.y <= tile_y < other_building.y + other_building.height):
                        return False
        
        return True
    
    def place_building(self, building, x, y):
        """Размещение здания"""
        if self.can_place_building(building, x, y):
            building.x = x
            building.y = y
            self.buildings.append(building)
            return True
        return False
    
    def get_tile(self, x, y):
        """Получить тип тайла"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[x][y]
        return 1
    
    def is_buildable(self, x, y):
        """Можно ли строить на этом тайле"""
        return TERRAIN_TYPES[self.get_tile(x, y)]['buildable']
