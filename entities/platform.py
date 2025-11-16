import pygame

from utils.settings import GAME_WIDTH, PLATFORM_MAX_SLOPE, PLATFORM_VY, BALL_RADIUS


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

    def _draw_metal_line(self,screen, start, end, width):
        # 金属的三层颜色
        colors = [(220, 220, 220), (180, 180, 180), (120, 120, 120)]
        offsets = [-width // 4, 0, width // 4]

        for c, o in zip(colors, offsets):
            pygame.draw.line(
                screen,
                c,
                (start[0], start[1] + o),
                (end[0], end[1] + o),
                width // 3
            )

    def draw(self, screen, camera):
        self._draw_metal_line(
            screen,
            camera.world_to_screen(0, self.y1),
            camera.world_to_screen(GAME_WIDTH, self.y2),
            12
        )
