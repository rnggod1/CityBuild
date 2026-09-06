"""Классы зданий"""
from enum import Enum
from resources import ResourceType


class BuildingType(Enum):
    HOUSE = "house"
    FARM = "farm"
    LUMBERJACK = "lumberjack"
    QUARRY = "quarry"
    MARKET = "market"
    TOWN_HALL = "town_hall"
    WAREHOUSE = "warehouse"


class Building:
    def __init__(self, building_type, x=0, y=0):
        self.type = building_type
        self.x = x
        self.y = y
        self.level = 1
        self.workers = []
        self.max_workers = 5
        self.assigned_wood_workers = 0
        self.assigned_stone_workers = 0
        
        self.set_parameters()
    
    def set_parameters(self):
        """Установка параметров в зависимости от типа"""
        params = {
            BuildingType.HOUSE: {
                'width': 4,
                'height': 4,
                'max_workers': 0,
                'cost': {ResourceType.WOOD: 20, ResourceType.STONE: 10},
                'production': {},
                'consumption': {},
                'color': (200, 150, 100),
                'name': 'Дом',
                'description': 'Увеличивает лимит населения на 5',
                'population_bonus': 5,
            },
            BuildingType.FARM: {
                'width': 6,
                'height': 4,
                'max_workers': 5,
                'cost': {ResourceType.WOOD: 15, ResourceType.STONE: 5},
                'production': {ResourceType.FOOD: 2},
                'consumption': {},
                'color': (255, 200, 100),
                'name': 'Ферма',
                'description': 'Производит 2 еды за 10 секунд',
            },
            BuildingType.LUMBERJACK: {
                'width': 6,
                'height': 4,
                'max_workers': 0,
                'cost': {ResourceType.WOOD: 10, ResourceType.STONE: 5},
                'production': {},
                'consumption': {},
                'color': (150, 100, 50),
                'name': 'Лесопилка',
                'description': 'Увеличивает добычу дерева в 2 раза',
                'wood_multiplier': 2,
            },
            BuildingType.QUARRY: {
                'width': 8,
                'height': 5,
                'max_workers': 0,
                'cost': {ResourceType.WOOD: 15, ResourceType.STONE: 20},
                'production': {},
                'consumption': {},
                'color': (150, 150, 150),
                'name': 'Каменоломня',
                'description': 'Увеличивает добычу камня в 2 раза',
                'stone_multiplier': 2,
            },
            BuildingType.MARKET: {
                'width': 5,
                'height': 5,
                'max_workers': 5,
                'cost': {ResourceType.WOOD: 30, ResourceType.STONE: 20},
                'production': {ResourceType.GOLD: 2},
                'consumption': {},
                'color': (255, 200, 200),
                'name': 'Рынок',
                'description': 'Производит 2 золота за 10 секунд',
            },
            BuildingType.TOWN_HALL: {
                'width': 7,
                'height': 5,
                'max_workers': 10,
                'cost': {},
                'production': {ResourceType.GOLD: 1},
                'consumption': {},
                'color': (200, 200, 255),
                'name': 'Ратуша',
                'description': 'Центр города, управление населением (бесплатно)',
            },
            BuildingType.WAREHOUSE: {
                'width': 6,
                'height': 6,
                'max_workers': 20,
                'cost': {},
                'production': {},
                'consumption': {},
                'color': (139, 119, 101),
                'name': 'Склад',
                'description': 'Центр управления добычей ресурсов (бесплатно)',
            },
        }
        
        params = params[self.type]
        self.width = params['width']
        self.height = params['height']
        self.max_workers = params['max_workers']
        self.cost = params['cost']
        self.production = params['production']
        self.consumption = params['consumption']
        self.color = params['color']
        self.name = params['name']
        self.description = params['description']
        self.population_bonus = params.get('population_bonus', 0)
        self.wood_multiplier = params.get('wood_multiplier', 1)
        self.stone_multiplier = params.get('stone_multiplier', 1)
    
    def get_cost_text(self):
        """Получить текст стоимости"""
        if not self.cost:
            return "Бесплатно"
        costs = []
        for resource, amount in self.cost.items():
            costs.append(f"{resource.value}: {amount}")
        return ", ".join(costs)
    
    def get_center(self):
        """Получить центр здания в тайлах"""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def can_add_worker(self):
        """Можно ли добавить рабочего"""
        if self.max_workers == 0:
            return False
        return len(self.workers) < self.max_workers
    
    def get_worker_progress(self):
        """Получить прогресс заполнения рабочими (0-1)"""
        if self.max_workers == 0:
            return 0
        return len(self.workers) / self.max_workers
