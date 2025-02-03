import pygame
from snakelite.settings import *

class CombatSystem:
    def update_bombs(self, game):
        current_time = pygame.time.get_ticks()
        new_bombs = []
        for bomb in game.bombs:
            x, y, t, radius = bomb
            if current_time - t < BOMB_DURATION:
                new_bombs.append(bomb)
            else:
                if (x, y) not in game.stone_blocks:
                    game.stone_blocks.append((x, y))
                explosion_positions = [(x, y)]
                for i in range(1, radius + 1):
                    positions = [
                        ((x + i*BLOCK_SIZE) % WIDTH, y),
                        ((x - i*BLOCK_SIZE) % WIDTH, y),
                        (x, (y + i*BLOCK_SIZE) % HEIGHT),
                        (x, (y - i*BLOCK_SIZE) % HEIGHT)
                    ]
                    explosion_positions.extend(positions)
                for pos in explosion_positions:
                    game.affected_blocks.append((pos[0], pos[1], current_time + EXPLOSION_DURATION))
        game.bombs = new_bombs

    def check_explosion_collision(self, game):
        current_time = pygame.time.get_ticks()
        for (x, y, end_time) in game.affected_blocks:
            if current_time < end_time and (x, y) == game.snake[0]:
                if game.shield_count == 0 and not game.active_powerups:
                    game.death_reason = "You were caught in an explosion!"
                    game.game_over = True
                    game.game_state = "shop"
                    game.coins += game.score

    def update_explosions(self, game):
        current_time = pygame.time.get_ticks()
        game.affected_blocks = [b for b in game.affected_blocks if current_time < b[2]]

    def check_bomb_collision(self, game):
        current_time = pygame.time.get_ticks()
        head = game.snake[0]
        for i, bomb in enumerate(game.bombs):
            x, y, t, radius = bomb
            if (x, y) == head:
                game.bombs.pop(i)
                game.score += 5

    def update_slowdowns(self, game):
        current_time = pygame.time.get_ticks()
        game.slowdown_elements = [s for s in game.slowdown_elements if current_time - s[2] < 5000]
        game.active_slowdowns = [t for t in game.active_slowdowns if t > current_time]
        game.current_speed = BASE_SPEED // (1 + 2 * min(len(game.active_slowdowns), 3))
