import pygame

from core.scenes.scene import Scene


class HelpScene(Scene):
    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont(None, 50)

    def handle_events(self, events):
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (
                    event.type == pygame.JOYBUTTONDOWN and event.button == 0):
                self.next_scene = "menu"  # 按 ESC 返回菜单
                return

    def update(self, dt):
        pass

    # TODO: 完善帮助界面
    def draw(self, screen):
        screen.fill((50, 50, 50))

        lines = [
            "Help:",
            "1. Use Q to move up left end of the platform",
            "2. Use E to move up right end of the platform",
            "4. Press ESC to purse",
        ]

        line_height = self.font.get_height() + 10  # 每行间距 10 像素
        total_height = len(lines) * line_height
        start_y = (screen.get_height() - total_height) // 2  # 垂直居中

        for i, line in enumerate(lines):
            text = self.font.render(line, True, (255, 255, 255))
            rect = text.get_rect(center=(screen.get_width() // 2, start_y + i * line_height))
            screen.blit(text, rect)
