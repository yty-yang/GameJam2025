import pygame
from utils.settings import SCREEN_HEIGHT


class Platform:
    def __init__(self, x, y, width, height, speed):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y
        self.width = width
        self.height = height
        self.speed = speed

    def move_left(self, up, down):
        if up:
            self.y1 = max(0, self.y1 - self.speed)
        if down:
            self.y1 = min(SCREEN_HEIGHT - self.height, self.y1 + self.speed)

    def move_right(self, up, down):
        if up:
            self.y2 = max(0, self.y2 - self.speed)
        if down:
            self.y2 = min(SCREEN_HEIGHT - self.height, self.y2 + self.speed)

    def draw(self, screen):
        pygame.draw.line(screen, (200, 50, 50), (self.x1, self.y1), (self.x2, self.y2), self.height)