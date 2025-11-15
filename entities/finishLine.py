import pygame
import math
from utils.settings import GAME_WIDTH


class FinishLine:
    def __init__(self, y):
        self.y = y  # 终点线的世界坐标y
        self.width = GAME_WIDTH
        self.thickness = 5
        self.animation_time = 0.0


    def update(self, dt):
        """更新动画"""
        pass


    def check_reached(self, ball):
        """检查小球是否到达终点线"""
        # 小球到达终点线上方（y坐标更小，因为y向上为负）
        return ball.y <= self.y

    def draw(self, screen, camera):
        """绘制终点线（复古像素风格）"""
        screen_x1, screen_y = camera.world_to_screen(0, self.y)
        screen_x2, _ = camera.world_to_screen(GAME_WIDTH, self.y)
        
        # 只绘制在屏幕可见范围内
        if screen_y < -50 or screen_y > screen.get_height() + 50:
            return
        
        # 绘制终点线主体（闪烁效果）
        alpha = int(128 + 127 * (0.5 + 0.5 * math.sin(self.animation_time)))
        line_color = (0, 255, 0)  # 绿色
        
        # 绘制主线条
        pygame.draw.line(
            screen,
            line_color,
            (int(screen_x1), int(screen_y)),
            (int(screen_x2), int(screen_y)),
            self.thickness
        )
        
        # 绘制装饰性的虚线效果（像素风格）
        dash_length = 20
        dash_gap = 10
        current_x = screen_x1
        while current_x < screen_x2:
            pygame.draw.line(
                screen,
                (100, 255, 100),
                (int(current_x), int(screen_y - 2)),
                (int(current_x + dash_length), int(screen_y - 2)),
                2
            )
            pygame.draw.line(
                screen,
                (100, 255, 100),
                (int(current_x), int(screen_y + 2)),
                (int(current_x + dash_length), int(screen_y + 2)),
                2
            )
            current_x += dash_length + dash_gap
        
        # 绘制"FINISH"文字（像素风格）
        try:
            font = pygame.font.SysFont("Courier", 24)
            text = font.render("FINISH", True, (0, 255, 0))
            text_rect = text.get_rect(center=(int((screen_x1 + screen_x2) / 2), int(screen_y)))
            screen.blit(text, text_rect)
        except:
            pass

