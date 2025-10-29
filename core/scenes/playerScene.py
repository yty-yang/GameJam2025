import pygame

from core.scenes.scene import Scene
from utils.settings import PLAYER_SIZE, RED, WHITE
from utils.helpers import draw_rect
from entities.player import Player

# 简单关卡矩阵 (1 = 墙, 0 = 可走)
LEVEL = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

class PlayerScene(Scene):
    def __init__(self):
        super().__init__()

        self.player = Player(1, 1)
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)

    def handle_events(self, events):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        self.player.move(dx, dy, LEVEL)

        # 按回车切换场景
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.next_scene = "ball"  # 或者你想切换到的其他场景名称
                elif event.key == pygame.K_ESCAPE:
                    self.next_scene = "menu"

    def update(self, dt):
        pass  # 后续可以加敌人、道具逻辑

    def draw(self, screen):
        screen.fill(WHITE)
        # 绘制格子
        for y, row in enumerate(LEVEL):
            for x, tile in enumerate(row):
                if tile == 0:
                    # 可走区域画蓝色
                    draw_rect(screen, (0, 0, 255), x * PLAYER_SIZE, y * PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)
                elif tile == 1:
                    # 墙画黑色
                    draw_rect(screen, (0, 0, 0), x * PLAYER_SIZE, y * PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)

        # 绘制玩家
        self.player.draw(screen)
        # 绘制分数
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))