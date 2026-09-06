"""Управление ресурсами"""
from enum import Enum


class ResourceType(Enum):
    WOOD = "wood"
    STONE = "stone"
    FOOD = "food"
    GOLD = "gold"
    POPULATION = "population"


class ResourceManager:
    def __init__(self):
        self.resources = {
            ResourceType.WOOD: 100,
            ResourceType.STONE: 100,
            ResourceType.FOOD: 100,
            ResourceType.GOLD: 50,
            ResourceType.POPULATION: 0,
        }
        self.max_population = 0
        self.worker_cost = 50
    
    def add(self, resource_type, amount):
        """Добавить ресурс"""
        if resource_type in self.resources:
            self.resources[resource_type] += amount
    
    def remove(self, resource_type, amount):
        """Удалить ресурс, если хватает"""
        if resource_type in self.resources and self.resources[resource_type] >= amount:
            self.resources[resource_type] -= amount
            return True
        return False
    
    def can_afford(self, costs):
        """Проверка, хватает ли ресурсов"""
        for resource_type, amount in costs.items():
            if resource_type not in self.resources or self.resources[resource_type] < amount:
                return False
        return True
    
    def get(self, resource_type):
        """Получить количество ресурса"""
        return self.resources.get(resource_type, 0)
    
    def hire_worker(self):
        """Нанять рабочего"""
        if self.resources[ResourceType.GOLD] >= self.worker_cost:
            self.resources[ResourceType.GOLD] -= self.worker_cost
            self.resources[ResourceType.POPULATION] += 1
            return True
        return False
