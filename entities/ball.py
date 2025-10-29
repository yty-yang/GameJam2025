import pygame, platform
from utils.settings import BALL_RADIUS, GRAVITY, SCREEN_WIDTH


class Ball:
    def __init__(self, x, y=100, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self, platform):
        # 小球物理更新
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # 碰撞检测：边界
        if self.x - BALL_RADIUS < 0 or self.x + BALL_RADIUS > SCREEN_WIDTH:
            self.vx = -self.vx
        if self.y - BALL_RADIUS < 0:
            self.vy = 0
            self.y = BALL_RADIUS

        # 计算平台直线方程 y = kx + b
        dx = platform.x2 - platform.x1
        dy = platform.y2 - platform.y1
        if dx != 0:
            k = dy / dx
            b = platform.y1 - k * platform.x1
            # 投影到平台上
            y_on_line = k * self.x + b
            # 检测碰撞（小球在平台上方并接触）
            if self.vy > 0 and y_on_line - BALL_RADIUS <= self.y <= y_on_line:
                self.y = y_on_line - BALL_RADIUS
                # 小球沿平台滑动
                self.vx += GRAVITY * k  # 简化摩擦沿斜面加速
                self.vy = 0



    def draw(self, screen):
        pygame.draw.circle(screen, (50, 200, 50), (int(self.x), int(self.y)), BALL_RADIUS)