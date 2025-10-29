import pygame
from core.scenes.scene import Scene
from entities.ball import Ball
from entities.platform import Platform
from utils.settings import BALL_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT, PLATFORM_WIDTH, PLATFORM_HEIGHT, PLATFORM_VY


class BallScene(Scene):
    def __init__(self):
        super().__init__()

        # 初始化平台在屏幕中下方
        self.platform = Platform(
            x=(SCREEN_WIDTH - PLATFORM_WIDTH) // 2,
            y=SCREEN_HEIGHT - 100,
            width=PLATFORM_WIDTH,
            height=PLATFORM_HEIGHT,
            speed=PLATFORM_VY
        )

        # 初始化小球在平台上方
        self.ball = Ball(
            x=SCREEN_WIDTH // 2,
            y=self.platform.y1 - BALL_RADIUS - 100,
            vx=0,
            vy=0
        )

        # 背景色
        self.background_color = (30, 30, 30)

    def handle_events(self, events):
        """处理玩家输入，让平台上下移动"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.platform.move_right(True, False)
        if keys[pygame.K_DOWN]:
            self.platform.move_right(False, True)
        if keys[pygame.K_w]:
            self.platform.move_left(True, False)
        if keys[pygame.K_s]:
            self.platform.move_left(False, True)

        # 按回车切换场景
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.next_scene = "player"  # 或者你想切换到的其他场景名称
                elif event.key == pygame.K_ESCAPE:
                    self.next_scene = "menu"

    def update(self, dt):
        """更新小球物理和平台碰撞"""
        self.ball.update(self.platform)

    def draw(self, screen):
        """绘制平台和小球"""
        screen.fill(self.background_color)
        # 绘制平台
        self.platform.draw(screen)
        # 绘制小球
        self.ball.draw(screen)