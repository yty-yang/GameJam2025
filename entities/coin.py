import math

import pygame

from utils.settings import BALL_RADIUS, COIN_RADIUS
from core.sound import sound_manager


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.rotation = 0.0  # 旋转角度
        self.pulse = 0.0  # 脉冲动画

    def update(self, dt):
        """更新金币动画"""
        if not self.collected:
            self.rotation += dt * 3.0  # 旋转速度
            self.pulse += dt * 5.0  # 脉冲速度

    def check_collision(self, ball):
        """检查是否与小球碰撞"""
        if self.collected:
            return False
        distance = math.hypot(self.x - ball.x, self.y - ball.y)
        return distance <= COIN_RADIUS + BALL_RADIUS

    def collect(self):
        """收集金币并播放音效（幂等）。"""
        if self.collected:
            return
        self.collected = True
        try:
            sound_manager.play_sound("eat_coins")
        except Exception:
            pass

    def draw(self, screen, camera):
        """绘制金币（复古像素风格）"""
        if self.collected:
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # 只绘制在屏幕可见范围内的金币
        if screen_x < -COIN_RADIUS or screen_x > screen.get_width() + COIN_RADIUS:
            return
        if screen_y < -COIN_RADIUS or screen_y > screen.get_height() + COIN_RADIUS:
            return

        # 脉冲效果（大小变化）
        pulse_scale = 1.0 + math.sin(self.pulse) * 0.2

        # 绘制金币（8-bit风格）
        # 外圈（金色）
        pygame.draw.circle(
            screen,
            (255, 215, 0),
            (int(screen_x), int(screen_y)),
            int(COIN_RADIUS * pulse_scale)
        )

        # 内圈（深金色） 
        pygame.draw.circle(
            screen,
            (200, 150, 0),
            (int(screen_x), int(screen_y)),
            int(COIN_RADIUS * pulse_scale * 0.7)
        )

        # 高光（模拟旋转）
        highlight_x = screen_x + math.cos(self.rotation) * COIN_RADIUS * 0.5
        highlight_y = screen_y + math.sin(self.rotation) * COIN_RADIUS * 0.5
        pygame.draw.circle(
            screen,
            (255, 255, 200),
            (int(highlight_x), int(highlight_y)),
            int(COIN_RADIUS * pulse_scale * 0.3)
        )

        # 像素风格的"$"符号
        try:
            font = pygame.font.SysFont("Courier", max(8, int(COIN_RADIUS * pulse_scale)))
            text = font.render("$", True, (255, 255, 255))
            text_rect = text.get_rect(center=(int(screen_x), int(screen_y)))
            screen.blit(text, text_rect)
        except:
            # 如果字体渲染失败，就只绘制圆圈
            pass
