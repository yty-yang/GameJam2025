from pathlib import Path

import pygame

from core.scenes.scene import Scene
import core.scenes.common.menu_navigation_mixin as menu_nav

from core.ui import UI
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MenuScene(Scene, menu_nav.MenuNavigationMixin):
    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont(None, 48)
        self.options = ["Start Game", "Help", "Setting", "Credits", "Quit"]
        self.selected_index = 0

        # 加载背景图
        project_root = Path(__file__).resolve().parents[3]   # 到 root/
        bg_path = project_root / "data" / "pictures" / "menu_picture.jpg"
        self.background = pygame.image.load(bg_path).convert()

        # 如果需要拉伸到全屏：
        self.background = pygame.transform.scale(
            self.background,
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

    def _select_option(self):
        if self.selected_index == 0:  # Start Game
            self.next_scene = "mode"  # 切换到模式选择场景
        elif self.selected_index == 1:
            self.next_scene = "help"
        elif self.selected_index == 2:
            self.next_scene = "setting"
        elif self.selected_index == 3:
            self.next_scene = "credits"
        elif self.selected_index == 4:  # Quit
            pygame.quit()
            exit()

        # 等待按键松开，防止多次触发
        if self.joystick:
            while self.joystick.get_button(0):
                pygame.event.pump()  # 等待按键松开

    def handle_events(self, events):
        self._handle_common_navigation(events)

        if menu_nav.confirm_pressed(events):
            self._select_option()

    def update(self, dt):
        pass  # 菜单没有动画的话可以空着

    def draw(self, screen):
        # 绘制背景
        screen.blit(self.background, (0, 0))

        ui = UI()
        ui.menu_ui(screen)

        # 计算菜单总高度（选项高度 + 间距）
        option_height = self.font.get_height()
        line_spacing = 40
        total_height = len(self.options) * option_height + (len(self.options) - 1) * line_spacing

        start_y = (SCREEN_WIDTH // 2) - (total_height // 2)

        # 绘制菜单选项
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text_surface = self.font.render(option, True, color)
            rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * (option_height + line_spacing)))
            screen.blit(text_surface, rect)

        # 绘制操作提示
        hint_font = pygame.font.SysFont(None, 28)
        hint_text = "Use UP/DOWN arrows to navigate, ENTER to select"
        hint_surface = hint_font.render(hint_text, True, (200, 200, 200))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + total_height + 40))
        screen.blit(hint_surface, hint_rect)
