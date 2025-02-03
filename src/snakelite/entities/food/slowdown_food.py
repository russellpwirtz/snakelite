from .base import FoodEnemy
from snakelite.settings import *
import random
import pygame

class SlowdownFood(FoodEnemy):
    def __init__(self, x, y, food_type):
        super().__init__(x, y, food_type)
        self.active_slowdowns = []

    def create_effect(self, current_time):
        if random.random() < 0.3 and len(self.active_slowdowns) < 2:
            return (self.position[0], self.position[1], current_time)
        return None

    def create_slowdown(self, current_time):
        # if random.random() < 0.5:  # 50% chance to create slowdown
        return (self.position[0], self.position[1], current_time)
        # return None

    def get_color(self):
        # Blue color gradient based on age
        current_time = pygame.time.get_ticks()
        age = current_time - self.creation_time
        ratio = min(age / FOOD_MAX_AGE, 1.0)
        r = int(255 * (1 - ratio))  # 255 -> 0
        g = int(255 * (1 - ratio))  # 255 -> 0
        return (0, r, g) 