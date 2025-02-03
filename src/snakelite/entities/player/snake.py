import os
import sys
import pygame
import random
from snakelite.settings import *
from snakelite.entities.food import Food
from snakelite.systems.combat import CombatSystem
from snakelite.ui.renderer import GameRenderer

# Initialize Pygame
pygame.init()

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.renderer = GameRenderer(self)
        self.clock = pygame.time.Clock()
        self.combat_system = CombatSystem()
        self.max_level = 3
        self.next_run_powerups = []
        self.coins = 0
        self.death_reason = ""
        self.reset_game()

    def reset_game(self):
        self.snake = [
            (WIDTH // 2, HEIGHT // 2),
            (WIDTH // 2 - BLOCK_SIZE, HEIGHT // 2),
            (WIDTH // 2 - 2 * BLOCK_SIZE, HEIGHT // 2),
        ]
        self.direction = RIGHT
        self.foods = []
        self.stone_blocks = []
        self.slowdown_elements = []
        self.bombs = []
        self.affected_blocks = []
        self.score = 0
        self.game_over = False
        self.current_speed = BASE_SPEED
        self.active_slowdowns = []
        self.powerups = []
        self.active_powerups = []
        self.projectiles = []
        self.current_level = 1
        self.shield_count = self.next_run_powerups.count('shield')
        self.next_run_powerups = []
        self.game_state = "start"
        self.death_reason = ""
        self.setup_level()

    def setup_level(self):
        self.snake = [
            (WIDTH // 2, HEIGHT // 2),
            (WIDTH // 2 - BLOCK_SIZE, HEIGHT // 2),
            (WIDTH // 2 - 2 * BLOCK_SIZE, HEIGHT // 2),
        ]
        self.direction = RIGHT
        self.foods = []
        self.stone_blocks = []
        self.bombs = []
        self.slowdown_elements = []
        self.active_slowdowns = []
        self.active_powerups = []
        self.projectiles = []
        self.affected_blocks = []
        self.game_over = False

        if self.current_level == 1:
            num_foods = 1
        elif self.current_level == 2:
            num_foods = 3
        elif self.current_level == 3:
            num_foods = 5
            for x in range(BLOCK_SIZE*5, WIDTH-BLOCK_SIZE*5, BLOCK_SIZE):
                self.stone_blocks.append((x, HEIGHT//3))
                self.stone_blocks.append((x, HEIGHT//3*2))

        for _ in range(num_foods):
            self.foods.append(self.generate_food())

    def generate_food(self):
        existing = [f.position for f in self.foods] + self.stone_blocks + self.snake + \
                  [bomb[:2] for bomb in self.bombs] + \
                  [slow[:2] for slow in self.slowdown_elements] + \
                  [pwr[:2] for pwr in self.powerups]
        return Food.generate(existing)

    def move_food(self):
        current_time = pygame.time.get_ticks()
        for food in self.foods:
            # Collect all blocked positions
            blocked = self.stone_blocks + \
                     [bomb[:2] for bomb in self.bombs] + \
                     [slow[:2] for slow in self.slowdown_elements] + \
                     [pwr[:2] for pwr in self.powerups] + \
                     [f.position for f in self.foods if f != food]
            
            new_food = food.move(self.snake[0], blocked)
            if new_food:
                self.foods.append(new_food)

            # Handle bomb/slowdown creation
            if random.random() < 0.3:
                if bomb := food.create_bomb(current_time):
                    food.active_bombs.append(bomb)
                    self.bombs.append(bomb)
                if slowdown := food.create_slowdown():
                    food.active_slowdowns.append(slowdown)
                    self.slowdown_elements.append(slowdown)

            # Update active effects
            food.active_bombs = [b for b in food.active_bombs if current_time - b[2] < BOMB_DURATION]
            food.active_slowdowns = [s for s in food.active_slowdowns if current_time - s[2] < 5000]

    def update_powerups(self):
        current_time = pygame.time.get_ticks()
        self.powerups = [p for p in self.powerups if current_time - p[2] < POWERUP_DURATION_ON_MAP]
        self.active_powerups = [t for t in self.active_powerups if t > current_time]

    def update_projectiles(self):
        current_time = pygame.time.get_ticks()
        new_projectiles = []
        for proj in self.projectiles:
            x, y, direction, t = proj
            if current_time - t > PROJECTILE_LIFETIME:
                continue
            dx, dy = direction
            new_x = (x + dx * BLOCK_SIZE) % WIDTH
            new_y = (y + dy * BLOCK_SIZE) % HEIGHT
            if (new_x, new_y) in self.stone_blocks:
                self.stone_blocks.remove((new_x, new_y))
                self.score += 1
                continue
            new_projectiles.append((new_x, new_y, direction, t))
        self.projectiles = new_projectiles

    def move(self):
        if self.game_over or self.game_state != "playing":
            return

        self.combat_system.check_bomb_collision(self)

        dx, dy = self.direction
        head = (
            (self.snake[0][0] + dx * BLOCK_SIZE) % WIDTH,
            (self.snake[0][1] + dy * BLOCK_SIZE) % HEIGHT
        )

        powered_up = len(self.active_powerups) > 0

        if head in self.stone_blocks:
            if powered_up:
                self.stone_blocks.remove(head)
                self.score += 1
            else:
                if self.shield_count > 0:
                    self.stone_blocks.remove(head)
                    self.shield_count -= 1
                    self.score += 1
                else:
                    self.death_reason = "You crashed into a stone block!"
                    self.game_over = True
                    self.game_state = "game_over"
                    self.coins += self.score
                    return

        if head in self.snake:
            if self.shield_count > 0:
                self.shield_count -= 1
                return
            else:
                self.death_reason = "You collided with yourself!"
                self.game_over = True
                self.game_state = "game_over"
                self.coins += self.score
                return

        self.snake.insert(0, head)

        ate_food = False
        for food in self.foods[:]:
            if head == food.position:
                self.score += 1
                food.eaten_remaining -= 1
                if food.eaten_remaining > 0:
                    # Regenerate food with reset properties
                    current_time = pygame.time.get_ticks()
                    while True:
                        new_x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
                        new_y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
                        existing = [f.position for f in self.foods if f != food] + self.stone_blocks + self.snake
                        if (new_x, new_y) not in existing:
                            food.position = (new_x, new_y)
                            food.last_move_time = current_time
                            food.creation_time = current_time  # Reset creation time
                            food.active_bombs = []  # Clear existing bombs
                            break
                else:
                    self.foods.remove(food)
                ate_food = True
                break

        if not ate_food:
            self.snake.pop()
        else:
            # Create either bomb OR slowdown when food is eaten
            current_time = pygame.time.get_ticks()
            if random.random() < 0.3:  # 30% chance for any effect
                # Randomly choose between bomb or slowdown
                if random.choice([True, False]):
                    if bomb := food.create_bomb(current_time):
                        self.bombs.append(bomb)
                else:
                    if slowdown := food.create_slowdown():
                        self.slowdown_elements.append(slowdown)
                
            if not self.foods:
                if self.current_level < self.max_level:
                    self.game_state = "level_complete"
                else:
                    self.game_state = "victory"

        current_time = pygame.time.get_ticks()
        for elem in self.slowdown_elements[:]:
            if (elem[0], elem[1]) == head:
                self.active_slowdowns.append(current_time + SLOW_DURATION)
                self.slowdown_elements.remove(elem)

        for powerup in self.powerups[:]:
            if (powerup[0], powerup[1]) == head:
                self.powerups.remove(powerup)
                self.active_powerups.append(current_time + POWERUP_EFFECT_DURATION)

    def draw(self):
        self.renderer.draw()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == "start":
                    self.setup_level()
                    self.game_state = "level_intro"
                elif self.game_state == "level_intro" and event.key == pygame.K_SPACE:
                    self.game_state = "playing"
                elif self.game_state == "level_complete" and event.key == pygame.K_SPACE:
                    self.current_level += 1
                    if self.current_level <= self.max_level:
                        self.setup_level()
                        self.game_state = "level_intro"
                    else:
                        self.game_state = "victory"
                elif self.game_state == "victory" and event.key == pygame.K_SPACE:
                    self.reset_game()
                elif self.game_state == "game_over":
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_SPACE:
                        self.game_state = "shop"
                elif self.game_state == "shop":
                    if event.key == pygame.K_1:
                        if self.coins >= 5:
                            self.coins -= 5
                            self.next_run_powerups.append('shield')
                    elif event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.game_state = "level_intro"
                
                if self.game_state == "playing":
                    if event.key == pygame.K_UP and self.direction != DOWN:
                        self.direction = UP
                    elif event.key == pygame.K_DOWN and self.direction != UP:
                        self.direction = DOWN
                    elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                        self.direction = LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                        self.direction = RIGHT
                    elif event.key == pygame.K_SPACE and self.active_powerups:
                        head_x, head_y = self.snake[0]
                        self.projectiles.append((head_x, head_y, self.direction, pygame.time.get_ticks()))

    def run(self):
        while True:
            self.handle_input()
            
            if self.game_state == "playing":
                self.move_food()
                self.combat_system.update_bombs(self)
                self.combat_system.check_explosion_collision(self)
                self.combat_system.update_explosions(self)
                self.combat_system.update_slowdowns(self)
                self.update_powerups()
                self.update_projectiles()
                self.move()
            
            self.draw()
            self.clock.tick(self.current_speed)

def main():
    game = SnakeGame()
    game.run()

if __name__ == "__main__":
    main()