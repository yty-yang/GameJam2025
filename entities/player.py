import pygame
from utils.settings import PLAYER_SIZE, PLAYER_SPEED, RED, SCREEN_WIDTH, SCREEN_HEIGHT


class Player:
    def __init__(self, grid_x, grid_y):
        self.x = grid_x * PLAYER_SIZE
        self.y = grid_y * PLAYER_SIZE
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE

    def move(self, dx, dy, level):
        # 预测下一步位置
        next_x = self.x + dx * PLAYER_SPEED
        next_y = self.y + dy * PLAYER_SPEED

        # 格子坐标
        grid_x = next_x // PLAYER_SIZE
        grid_y = next_y // PLAYER_SIZE

        # 边界 & 碰撞检测
        if 0 <= grid_x < len(level[0]) and 0 <= grid_y < len(level):
            if level[grid_y][grid_x] == 0:
                self.x = next_x
                self.y = next_y

        # 限制屏幕边界
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))