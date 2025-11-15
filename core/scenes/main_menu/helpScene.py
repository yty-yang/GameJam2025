import pygame
from core.scenes.scene import Scene

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
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                self.next_scene = "menu"
                return

    def update(self, dt):
        pass

    def draw(self, screen):
        # 深色背景
        screen.fill((20, 20, 35))
        
        # 故事文本 - 保持不变
        story_lines = [
            "Welcome to the Frosty Mug Tavern",
            "",
            "Tucked away in a quiet corner of the city",
            "lies a tale whispered through the ages.",
            "",
            "On the back wall stands an ancient arcade",
            "cabinet - the path to ultimate glory",
            "known as 'Ice Cold Beer'.",
            "",
            "Legend says any champion who can conquer",
            "its trials will be granted a taste of",
            "the one and only 'Glacier's Heart' beer.",
            "",
            "Will you be the one to claim the legend tonight?"
        ]

        # 控制说明 - 简化并分成多行
        control_lines = [
            "--- CONTROLS ---",
            "",
            "LEFT SIDE:",
            "W = Move Up",
            "S = Move Down",
            "",
            "RIGHT SIDE:", 
            "UP ARROW = Move Up",
            "DOWN ARROW = Move Down",
            "",
            "ESC = Pause / Return to Menu"
        ]

        current_y = 40

        # 绘制主标题 - 保持不变
        title = self.title_font.render("THE LEGEND", True, (255, 215, 0))
        title_rect = title.get_rect(center=(screen.get_width() // 2, current_y))
        screen.blit(title, title_rect)
        current_y += 50

        subtitle = self.heading_font.render("of Glacier's Heart", True, (100, 200, 255))
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, current_y))
        screen.blit(subtitle, subtitle_rect)
        current_y += 70

        # 绘制故事部分 - 保持不变
        for line in story_lines:
            if line == "":
                current_y += 10
            else:
                text = self.text_font.render(line, True, (220, 220, 220))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 30

        current_y += 20  # 故事和控制之间的间距

        # 绘制控制说明 - 修复重叠问题
        for line in control_lines:
            if line == "":
                current_y += 8  # 较小的空行间距
            elif line == "--- CONTROLS ---":
                text = self.heading_font.render("CONTROLS", True, (255, 150, 50))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 40
            elif line in ["LEFT SIDE:", "RIGHT SIDE:"]:
                text = self.text_font.render(line, True, (100, 200, 255))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 30
            else:
                text = self.text_font.render(line, True, (200, 200, 200))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 25

        # 绘制返回提示
        hint_text = self.small_font.render("Press SPACE or ESC to return", True, (150, 150, 200))
        hint_rect = hint_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(hint_text, hint_rect)
