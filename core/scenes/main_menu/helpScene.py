import pygame
from core.scenes.scene import Scene

class HelpScene(Scene):
    def __init__(self):
        super().__init__()
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.heading_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)

    def handle_events(self, events):
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or (
                    event.type == pygame.JOYBUTTONDOWN and event.button == 0):
                self.next_scene = "menu"
                return

    def update(self, dt):
        pass

    def draw(self, screen):
        # 干净的深色背景
        screen.fill((25, 25, 40))  # 深蓝色背景
        
        # 故事文本 - 重新组织为更适合阅读的段落
        story_sections = [
            [
                "Welcome to the Frosty Mug Tavern",
                "Tucked away in a quiet corner of the city lies a tale",
                "whispered through the ages."
            ],
            [
                "On the back wall stands an ancient arcade cabinet -",
                "the path to ultimate glory known as 'Ice Cold Beer'."
            ],
            [
                "Legend says any champion who can conquer its trials",
                "will be granted a taste of the one and only",
                "'Glacier's Heart' beer."
            ],
            [
                "Will you be the one to claim the legend tonight?"
            ]
        ]

        # 控制说明
        control_lines = [
            "CONTROLS",
            "Q - Move left side up",
            "E - Move right side up", 
            "ESC - Pause/Return to menu"
        ]

        # 绘制主标题
        title = self.title_font.render("THE LEGEND", True, (255, 215, 0))  # 金色
        title_rect = title.get_rect(center=(screen.get_width() // 2, 60))
        screen.blit(title, title_rect)

        subtitle = self.heading_font.render("of Glacier's Heart", True, (100, 200, 255))  # 冰蓝色
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(subtitle, subtitle_rect)

        # 绘制故事部分
        y_pos = 150
        for section in story_sections:
            for line in section:
                text = self.text_font.render(line, True, (220, 220, 220))
                text_rect = text.get_rect(center=(screen.get_width() // 2, y_pos))
                screen.blit(text, text_rect)
                y_pos += 30
            y_pos += 15  # 段间距

        # 绘制分隔线
        pygame.draw.line(screen, (80, 80, 120), 
                        (screen.get_width() // 2 - 200, y_pos + 10),
                        (screen.get_width() // 2 + 200, y_pos + 10), 2)

        # 绘制控制说明
        control_y = y_pos + 40
        for i, line in enumerate(control_lines):
            if i == 0:  # 标题
                text = self.heading_font.render(line, True, (255, 150, 50))  # 橙色
            else:
                text = self.text_font.render(line, True, (200, 200, 200))
            
            text_rect = text.get_rect(center=(screen.get_width() // 2, control_y))
            screen.blit(text, text_rect)
            control_y += 35

        # 绘制返回提示
        hint_text = self.small_font.render("Press SPACE or ESC to return to menu", True, (150, 150, 200))
        hint_rect = hint_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40))
        screen.blit(hint_text, hint_rect)

        # 简单的装饰：四个角的标记
        corner_size = 4
        color = (100, 100, 150)
        # 左上角
        pygame.draw.rect(screen, color, (30, 30, corner_size, 20))
        pygame.draw.rect(screen, color, (30, 30, 20, corner_size))
        # 右上角
        pygame.draw.rect(screen, color, (screen.get_width()-50, 30, corner_size, 20))
        pygame.draw.rect(screen, color, (screen.get_width()-50, 30, 20, corner_size))
        # 左下角
        pygame.draw.rect(screen, color, (30, screen.get_height()-50, corner_size, 20))
        pygame.draw.rect(screen, color, (30, screen.get_height()-50, 20, corner_size))
        # 右下角
        pygame.draw.rect(screen, color, (screen.get_width()-50, screen.get_height()-50, corner_size, 20))
        pygame.draw.rect(screen, color, (screen.get_width()-50, screen.get_height()-50, 20, corner_size))
