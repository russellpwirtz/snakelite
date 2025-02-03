import pygame
import random
from snakelite.settings import *

class Food:
    def __init__(self, x, y):
        self.position = (x, y)
        self.last_move_time = pygame.time.get_ticks()
        self.active_bombs = []
        self.active_slowdowns = []
        self.creation_time = pygame.time.get_ticks()
        self.eaten_remaining = 5

    @classmethod
    def generate(cls, existing_positions):
        while True:
            x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            if (x, y) not in existing_positions:
                return cls(x, y)

    def move(self, head_position, blocked_positions):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= FOOD_MOVE_INTERVAL:
            current_x, current_y = self.position
            head_x, head_y = head_position
            
            # Filter directions that don't lead to blocked positions
            valid_directions = []
            for direction in [UP, DOWN, LEFT, RIGHT]:
                new_x = (current_x + direction[0] * BLOCK_SIZE) % WIDTH
                new_y = (current_y + direction[1] * BLOCK_SIZE) % HEIGHT
                if (new_x, new_y) not in blocked_positions:
                    valid_directions.append(direction)
            
            if valid_directions:
                best_dir = max(
                    valid_directions,
                    key=lambda d: ((current_x + d[0]*BLOCK_SIZE - head_x) % WIDTH)**2 +
                                ((current_y + d[1]*BLOCK_SIZE - head_y) % HEIGHT)**2
                )
                
                new_x = (current_x + best_dir[0] * BLOCK_SIZE) % WIDTH
                new_y = (current_y + best_dir[1] * BLOCK_SIZE) % HEIGHT
                self.position = (new_x, new_y)
                self.last_move_time = current_time

    def create_bomb(self, current_time):
        if random.random() < 0.66 and len(self.active_bombs) < 1:
            current_age = current_time - self.creation_time
            radius = 1 + int(4 * (current_age / FOOD_MAX_AGE))
            return (self.position[0], self.position[1], current_time, radius)
        return None

    def create_slowdown(self):
        if random.random() < 0.3 and len(self.active_slowdowns) < 2:
            return (self.position[0], self.position[1], pygame.time.get_ticks())
        return None 