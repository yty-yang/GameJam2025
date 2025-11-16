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
        self.options = ["Start Game", "Help", "Shop", "Setting", "Credits", "Quit"]
        self.selected_index = 0

        # 加载背景图
        project_root = Path(__file__).resolve().parents[3]   # 到 root/
        bg_path = project_root / "data" / "pictures" / "menu_background.png"
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
            self.next_scene = "shop"
        elif self.selected_index == 3:
            self.next_scene = "setting"
        elif self.selected_index == 4:
            self.next_scene = "credits"
        elif self.selected_index == 5:  # Quit
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

        option_height = self.font.get_height()
        line_spacing = 30
        start_y = int(SCREEN_HEIGHT * 0.4)

        # ----------- 中间菜单选项 -----------
        menu_index = 0  # 用于计算中间菜单位置
        for i, option in enumerate(self.options):
            if option == "Shop":
                continue  # 跳过 Shop
            # 高亮逻辑
            if i == self.selected_index and option != "Shop":
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)

            text_surface = self.font.render(option, True, color)
            rect = text_surface.get_rect(
                center=(SCREEN_WIDTH // 2, start_y + menu_index * (option_height + line_spacing)))
            screen.blit(text_surface, rect)
            menu_index += 1  # 只有绘制了才增加计数

        # ----------- 右侧商城按钮 -----------
        shop_font = pygame.font.SysFont(None, 40)
        color = (255, 255, 0) if 2 == self.selected_index else (255, 255, 255)
        shop_text = shop_font.render("Shop", True, color)

        # 固定在右侧位置（你可以调整）
        shop_x = SCREEN_WIDTH - 120
        shop_y = int(SCREEN_HEIGHT * 0.55)
        shop_rect = shop_text.get_rect(center=(shop_x, shop_y))

        screen.blit(shop_text, shop_rect)

        # ----------- 操作提示 -----------
        hint_font = pygame.font.SysFont(None, 28)
        hint_text = "Use UP/DOWN arrows to navigate, ENTER to select"
        hint_surface = hint_font.render(hint_text, True, (200, 200, 200))
        hint_y = int(SCREEN_HEIGHT * 0.9)
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, hint_y))

        screen.blit(hint_surface, hint_rect)
