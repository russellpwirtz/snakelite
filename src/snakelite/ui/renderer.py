import pygame
import math
from snakelite.settings import *

class GameRenderer:
    def __init__(self, game):
        self.game = game
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.font = pygame.font.Font(None, 36)

    def draw(self):
        if self.game.game_state == "start":
            self._draw_start()
        elif self.game.game_state == "playing":
            self._draw_playing()
        elif self.game.game_state == "level_complete":
            self._draw_level_complete()
        elif self.game.game_state == "victory":
            self._draw_victory()
        elif self.game.game_state == "shop":
            self._draw_shop()
        elif self.game.game_state == "game_over":
            self._draw_game_over()
        pygame.display.flip()

    def _draw_start(self):
        self.window.fill(BLACK)
        self._draw_text("SNAKELITE", 64, WHITE, HEIGHT//4)
        self._draw_text("Press any key to begin", 32, WHITE, HEIGHT//2)
        
    def _draw_playing(self):
        self.window.fill(ICE_BLUE if self.game.active_slowdowns else BLACK)
        self._draw_environment()
        self._draw_snake()
        self._draw_ui()

    def _draw_environment(self):
        current_time = pygame.time.get_ticks()
        # Draw stone blocks
        for block in self.game.stone_blocks:
            pygame.draw.rect(self.window, DARK_GREY, (*block, BLOCK_SIZE, BLOCK_SIZE))

        # Draw food with bombs and slowdowns
        for food in self.game.foods:
            # Calculate age-based color (bright orange-red to dark red)
            age = current_time - food.creation_time
            ratio = min(age / FOOD_MAX_AGE, 1.0)
            # Start with bright orange-red (255, 69, 0) -> dark red (139, 0, 0)
            r = int(255 - (116 * ratio))  # 255 -> 139
            g = int(69 - (69 * ratio))    # 69 -> 0
            food_color = (r, g, 0)
            pygame.draw.rect(self.window, food_color, (*food.position, BLOCK_SIZE, BLOCK_SIZE))
            
            for bomb in food.active_bombs:
                # Unpack all 4 values from bomb tuple (x, y, creation_time, radius)
                x, y, creation_time, radius = bomb
                end_time = creation_time + BOMB_DURATION
                remaining = max(0, end_time - current_time)
                ratio = remaining / BOMB_DURATION
                bomb_color = (255, 165 + int(90 * ratio), 0)
                pygame.draw.rect(self.window, bomb_color, (int(x), int(y), BLOCK_SIZE, BLOCK_SIZE))
            
            for slowdown in food.active_slowdowns:
                pygame.draw.rect(self.window, BLUE, (int(slowdown[0]), int(slowdown[1]), BLOCK_SIZE, BLOCK_SIZE))

        # Draw powerups and projectiles
        for powerup in self.game.powerups:
            # Main powerup body
            pygame.draw.rect(self.window, YELLOW, (powerup[0], powerup[1], BLOCK_SIZE, BLOCK_SIZE))
            # Pulsating border effect
            pulse_thickness = int(3 + math.sin(pygame.time.get_ticks() / 500) * 1.5)
            pygame.draw.rect(self.window, ORANGE, (powerup[0], powerup[1], BLOCK_SIZE, BLOCK_SIZE), pulse_thickness)
            
        for proj in self.game.projectiles:
            pygame.draw.rect(self.window, WHITE, (proj[0], proj[1], BLOCK_SIZE//2, BLOCK_SIZE//2))

        # Draw explosion effects
        for (x, y, end_time) in self.game.affected_blocks:
            if current_time < end_time:
                alpha = 255 * (end_time - current_time) / EXPLOSION_DURATION
                surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                surf.set_alpha(alpha)
                surf.fill(ORANGE)
                self.window.blit(surf, (x, y))

    def _draw_snake(self):
        powered_up = len(self.game.active_powerups) > 0
        for i, segment in enumerate(self.game.snake):
            if powered_up:
                head_color = (255, 0, 0)  # Heroic red
                body_color = (0, 0, 255)  # Heroic blue
                border_color = (255, 255, 0)  # Bright yellow border
                color = head_color if i == 0 else body_color
            else:
                active_slows = min(len(self.game.active_slowdowns), 3)
                head_color = (int(255 * (active_slows/3 * 0.7)), int(255 - 255 * (active_slows/3 * 0.7)), 0)
                body_color = (int(255 * (active_slows/3)), 255 - int(255 * (active_slows/3)), 0)
                color = head_color if i == 0 else body_color
                border_color = DARK_GREEN
                
            # Draw segment with border
            pygame.draw.rect(self.window, color, (*segment, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.window, border_color, (*segment, BLOCK_SIZE, BLOCK_SIZE), 2 if powered_up else 1)

    def _draw_ui(self):
        # Score and level
        self._draw_text(f"Score: {self.game.score}", 28, WHITE, 10, pos_x=10)
        self._draw_text(f"Level: {self.game.current_level}", 28, WHITE, 10, pos_x=WIDTH-150)
        
        # Shields display
        shield_text = f"Shields: {self.game.shield_count}"
        text_surf = self.font.render(shield_text, True, CYAN)
        self.window.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, 10))
        
        # Slowdown/powerup indicators
        if self.game.active_slowdowns:
            self._draw_text("SLOWED!", 32, ICE_BLUE, HEIGHT-40)
        if self.game.active_powerups:
            self._draw_text("POWERED UP!", 32, YELLOW, HEIGHT-80)

    def _draw_shop(self):
        self.window.fill(BLACK)
        self._draw_text("SHOP", 64, CYAN, HEIGHT//4)
        self._draw_text(f"Coins: {self.game.coins}", 36, WHITE, HEIGHT//3)
        self._draw_text("1. Buy Shield (5 coins)", 32, CYAN, HEIGHT//2)
        self._draw_text("SPACE to exit shop", 28, WHITE, HEIGHT-100)

    def _draw_level_complete(self):
        self.window.fill(BLACK)
        self._draw_text("LEVEL COMPLETE!", 48, GREEN, HEIGHT//3)
        self._draw_text("Press SPACE to continue", 32, WHITE, HEIGHT//2)

    def _draw_victory(self):
        self.window.fill(BLACK)
        self._draw_text("VICTORY!", 64, GOLD, HEIGHT//3)
        self._draw_text(f"Final Score: {self.game.score}", 48, WHITE, HEIGHT//2)
        self._draw_text("Press SPACE to restart", 32, WHITE, HEIGHT-100)

    def _draw_game_over(self):
        self.window.fill(BLACK)
        self._draw_text("GAME OVER", 64, RED, HEIGHT//4)
        self._draw_text(self.game.death_reason, 48, WHITE, HEIGHT//3 + 50)
        self._draw_text(f"Score: {self.game.score}", 36, WHITE, HEIGHT//2)
        self._draw_text("Press SPACE to continue", 28, WHITE, HEIGHT-100)

    def _draw_text(self, text, size, color, y, pos_x=None):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if pos_x is None:  # Center text
            text_rect.center = (WIDTH // 2, y)
        else:  # Left-align
            text_rect.topleft = (pos_x, y)
        self.window.blit(text_surface, text_rect) 