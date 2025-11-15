import math

import pygame

from utils.settings import BALL_RADIUS, HOLE_RADIUS


class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def check_collision(self, ball):
        distance = math.hypot(self.x - ball.x, self.y - ball.y)
        return distance <= HOLE_RADIUS + BALL_RADIUS

    def draw(self, screen, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # 简单的立体效果：外圈边框 + 内圈黑色
        # 外圈边框（深灰色，2像素宽）
        pygame.draw.circle(screen, (50, 50, 50), (int(screen_x), int(screen_y)), HOLE_RADIUS + 2, 2)

        # 主洞口（黑色）
        pygame.draw.circle(screen, (0, 0, 0), (int(screen_x), int(screen_y)), HOLE_RADIUS)
