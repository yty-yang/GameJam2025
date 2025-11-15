import pygame
from core.scenes.scene import Scene
from core.scenes.common.menu_navigation_mixin import confirm_pressed

class HelpScene(Scene):
    def __init__(self):
        super().__init__()
        # 使用像素风格字体
        try:
            self.title_font = pygame.font.Font("fonts/pixel.ttf", 36)
            self.heading_font = pygame.font.Font("fonts/pixel.ttf", 28)
            self.text_font = pygame.font.Font("fonts/pixel.ttf", 22)
            self.small_font = pygame.font.Font("fonts/pixel.ttf", 18)
        except:
            # 备用字体
            self.title_font = pygame.font.SysFont("Courier", 36, bold=True)
            self.heading_font = pygame.font.SysFont("Courier", 28, bold=True)
            self.text_font = pygame.font.SysFont("Courier", 22)
            self.small_font = pygame.font.SysFont("Courier", 18)

    def handle_events(self, events):
        if confirm_pressed(events):
            self.next_scene = "menu"
            return

    def update(self, dt):
        pass

    def draw(self, screen):
        # 深色背景
        screen.fill((20, 20, 35))
        
        # 故事文本
        story_lines = [
            "Welcome to the Frosty Mug Tavern",
            "",
            "A legend whispers in this quiet corner",
            "of the city...",
            "",
            "An ancient arcade cabinet holds the key",
            "to the ultimate prize: 'Ice Cold Beer'.",
            "",
            "Conquer its trials to earn a taste of",
            "the legendary 'Glacier's Heart' beer.",
            "",
            "Will you claim the legend tonight?"
        ]

        # 控制说明
        control_lines = [
            "CONTROLS",
            "",
            "LEFT SIDE:    W = Up    S = Down",
            "RIGHT SIDE:   ↑ = Up    ↓ = Down", 
        ]

        current_y = 40

        # 绘制主标题
        title = self.title_font.render("THE LEGEND", True, (255, 215, 0))
        title_rect = title.get_rect(center=(screen.get_width() // 2, current_y))
        screen.blit(title, title_rect)
        current_y += 50

        subtitle = self.heading_font.render("of Glacier's Heart", True, (100, 200, 255))
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, current_y))
        screen.blit(subtitle, subtitle_rect)
        current_y += 70

        # 绘制故事部分
        for line in story_lines:
            if line == "":
                current_y += 10  # 空行间距
            else:
                text = self.text_font.render(line, True, (220, 220, 220))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 30

        current_y += 30  # 故事和控制之间的间距

        # 绘制分隔线
        pygame.draw.line(screen, (80, 80, 120), 
                        (screen.get_width() // 2 - 150, current_y),
                        (screen.get_width() // 2 + 150, current_y), 2)
        current_y += 30

        # 绘制控制说明
        for line in control_lines:
            if line == "":
                current_y += 10  # 空行间距
            else:
                if line == "CONTROLS":
                    text = self.heading_font.render(line, True, (255, 150, 50))
                else:
                    text = self.text_font.render(line, True, (200, 200, 200))
                
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 35

        # 绘制返回提示
        hint_text = self.small_font.render("Press SPACE or ESC to return", True, (150, 150, 200))
        hint_rect = hint_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(hint_text, hint_rect)
