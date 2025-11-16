import pygame

from core.scenes.common.game_machine_mixin import GameMachineMixin
from core.scenes.scene import Scene
import core.scenes.common.menu_navigation_mixin as menu_nav


class SelectScene(Scene, menu_nav.MenuNavigationMixin, GameMachineMixin):
    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont(None, 48)
        self.options = ["Level 1", "Level 2", "Level 3","Return"]
        self.selected_index = 0

    def _select_option(self):
        if self.selected_index == 0:
            self.next_scene = "level_1"
        elif self.selected_index == 1:
            self.next_scene = "level_2"
        elif self.selected_index == 2:
            self.next_scene = "level_3"
        elif self.selected_index == 3:
            self.next_scene = "mode"

    def handle_events(self, events):
        self._handle_common_navigation(events)

        if menu_nav.confirm_pressed(events):
            self._select_option()

    def update(self, dt):
        self._update_game_machine_animation(dt)

    def _draw_surface(self, screen):
        lines = self.options

        line_height = self.font.get_height() + 10  # 每行间距 10 像素
        total_height = len(lines) * line_height
        start_y = (screen.get_height() - total_height) // 2  # 垂直居中

        for i, line in enumerate(lines):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text = self.font.render(line, True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, start_y + i * line_height))
            screen.blit(text, rect)

    def draw(self, screen):
        self._draw_with_bg(screen)

