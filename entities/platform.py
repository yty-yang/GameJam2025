import pygame

from utils.settings import SCREEN_WIDTH, PLATFORM_MAX_SLOPE, PLATFORM_VY, BALL_RADIUS


class Platform:
    def __init__(self, y=BALL_RADIUS, speed=PLATFORM_VY):
        self.y1 = y
        self.y2 = y
        self.speed = speed
        self.base_y = y

    def move(self, left, right, up, speed_factor=1.0):
        if up:
            if left:
                self.y1 -= self.speed * speed_factor

                if self.y2 > self.y1 + PLATFORM_MAX_SLOPE:
                    self.y2 = self.y1 + PLATFORM_MAX_SLOPE
            if right:
                self.y2 -= self.speed * speed_factor

                if self.y1 > self.y2 + PLATFORM_MAX_SLOPE:
                    self.y1 = self.y2 + PLATFORM_MAX_SLOPE
        else:
            if left:
                self.y1 += self.speed * speed_factor

                if self.y1 > self.y2 + PLATFORM_MAX_SLOPE:
                    self.y2 = self.y1 - PLATFORM_MAX_SLOPE
            if right:
                self.y2 += self.speed * speed_factor

                if self.y2 > self.y1 + PLATFORM_MAX_SLOPE:
                    self.y1 = self.y2 - PLATFORM_MAX_SLOPE



    def draw(self, screen, camera):
        pygame.draw.line(
            screen,
            (200, 50, 50),
            camera.world_to_screen(0, self.y1),
            camera.world_to_screen(SCREEN_WIDTH, self.y2),
            8
        )
