from .base import FoodEnemy
from snakelite.settings import *
import random
import pygame

class BombFood(FoodEnemy):
    def __init__(self, x, y, food_type):
        super().__init__(x, y, food_type)
        self.active_bombs = []

    def create_effect(self, current_time):
        if random.random() < 0.66 and len(self.active_bombs) < 1:
            current_age = current_time - self.creation_time
            radius = 1 + int(4 * (current_age / FOOD_MAX_AGE))
            return (self.position[0], self.position[1], current_time, radius)
        return None

    def create_bomb(self, current_time):
        # if random.random() < 0.5:  # 50% chance to create a bomb
            radius = 3  # Default radius
            return (self.position[0], self.position[1], current_time, radius)
        # return None

    def get_color(self):
        # Red color gradient based on age
        current_time = pygame.time.get_ticks()
        age = current_time - self.creation_time
        ratio = min(age / FOOD_MAX_AGE, 1.0)
        r = int(255 - (116 * ratio))  # 255 -> 139
        g = int(69 - (69 * ratio))    # 69 -> 0
        return (r, g, 0) 