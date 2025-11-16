import pygame
from pathlib import Path

from core.scenes.scene import Scene
from core.scenes.common.menu_navigation_mixin import confirm_pressed


class LevelendScene(Scene):
    def __init__(self, win):
        super().__init__()
        self.win = win

    def handle_events(self, events):
        if confirm_pressed(events):
            self.next_scene = "menu"
            return

    def update(self, dt):
        pass

    # TODO: 动画，人物浮现
    def draw(self, screen):
        # 获取项目根目录
        project_root = Path(__file__).resolve().parents[3]

        # 加载背景图并铺满屏幕
        bg_path = project_root / "data/pictures/level_end_background.png"
        background = pygame.image.load(str(bg_path)).convert_alpha()
        background = pygame.transform.scale(background, screen.get_size())
        screen.blit(background, (0, 0))

        # 根据胜负加载对应 bartender 图片
        if self.win:
            bartender_path = project_root / "data/pictures/characters/bartender_win.png"
        else:
            bartender_path = project_root / "data/pictures/characters/bartender_lose.png"

        bartender_img = pygame.image.load(str(bartender_path)).convert_alpha()
        # 缩放 bartender 高度为屏幕高度的1/5，保持宽高比
        sw, sh = screen.get_size()
        target_height = sh // 5
        bw, bh = bartender_img.get_size()
        scale_ratio = target_height / bh
        target_width = int(bw * scale_ratio)
        bartender_img = pygame.transform.scale(bartender_img, (target_width, target_height))

        # 居中显示 bartender
        bw, bh = bartender_img.get_size()
        sw, sh = screen.get_size()
        pos_x = (sw - bw) // 2
        pos_y = (sh - bh) // 2
        screen.blit(bartender_img, (pos_x, pos_y))
