import pygame

from core.scenes.scene import Scene
from utils.settings import SCREEN_WIDTH

class MenuScene(Scene):
    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont(None, 48)
        self.options = ["Start Game", "Help", "Setting", "Quit"]
        self.selected_index = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()

    def select_option(self):
        if self.selected_index == 0:  # Start Game
            self.next_scene = "player"  # 切换到游戏
        elif self.selected_index == 1:
            self.next_scene = "help"
        elif self.selected_index == 2:
            self.next_scene = "setting"
        elif self.selected_index == 3:  # Quit
            pygame.quit()
            exit()

    def update(self, dt):
        pass  # 菜单没有动画的话可以空着

    def draw(self, screen):
        screen.fill((30, 30, 30))

        # 计算菜单总高度（选项高度 + 间距）
        option_height = self.font.get_height()
        line_spacing = 40  # 行间距更紧凑
        total_height = len(self.options) * option_height + (len(self.options) - 1) * line_spacing

        start_y = (SCREEN_WIDTH // 2) - (total_height // 2)

        # 绘制菜单选项，垂直居中显示
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text_surface = self.font.render(option, True, color)
            rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * (option_height + line_spacing)))
            screen.blit(text_surface, rect)

        # 绘制操作提示，使用更小字体，垂直居中显示在菜单下方
        hint_font = pygame.font.SysFont(None, 28)
        hint_text = "Use UP/DOWN arrows to navigate, ENTER to select"
        hint_surface = hint_font.render(hint_text, True, (200, 200, 200))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + total_height + 40))
        screen.blit(hint_surface, hint_rect)