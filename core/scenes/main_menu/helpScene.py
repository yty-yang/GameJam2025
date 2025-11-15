import pygame
from core.scenes.scene import Scene

class HelpScene(Scene):
    def __init__(self):
        super().__init__()
        # 尝试加载像素字体，如果失败则使用默认字体
        try:
            self.title_font = pygame.font.Font("fonts/pixel.ttf", 48)
            self.heading_font = pygame.font.Font("fonts/pixel.ttf", 32)
            self.text_font = pygame.font.Font("fonts/pixel.ttf", 24)
            self.small_font = pygame.font.Font("fonts/pixel.ttf", 18)
        except:
            # 如果像素字体不存在，使用系统默认字体但模拟像素风格
            self.title_font = pygame.font.SysFont("Courier", 48, bold=True)
            self.heading_font = pygame.font.SysFont("Courier", 32, bold=True)
            self.text_font = pygame.font.SysFont("Courier", 24)
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
        
        # 故事文本 - 重新组织为更合理的段落
        story_sections = [
            ["Welcome to the Frosty Mug Tavern"],
            ["Tucked away in a quiet corner of the city", "lies a tale whispered through the ages."],
            ["On the back wall stands an ancient arcade", "cabinet - the path to ultimate glory", "known as 'Ice Cold Beer'."],
            ["Legend says any champion who can conquer", "its trials will be granted a taste of", "the one and only 'Glacier's Heart' beer."],
            ["Will you be the one to claim", "the legend tonight?"]
        ]

        # 控制说明 - 修正后的控制方案
        control_sections = [
            ["CONTROLS"],
            ["LEFT SIDE", "W - Move Up", "S - Move Down"],
            ["RIGHT SIDE", "UP - Move Up", "DOWN - Move Down"],
            ["ESC - Pause/Return to Menu"]
        ]

        # 绘制主标题
        title = self.title_font.render("THE LEGEND", True, (255, 215, 0))  # 金色
        title_rect = title.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title, title_rect)

        subtitle = self.heading_font.render("of Glacier's Heart", True, (100, 200, 255))  # 冰蓝色
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 90))
        screen.blit(subtitle, subtitle_rect)

        # 绘制故事部分（左侧）
        story_y = 150
        for section in story_sections:
            for line in section:
                text = self.text_font.render(line, True, (220, 220, 220))
                text_rect = text.get_rect(midleft=(50, story_y))
                screen.blit(text, text_rect)
                story_y += 30
            story_y += 15  # 段间距

        # 绘制分隔线
        pygame.draw.line(screen, (80, 80, 120), 
                        (screen.get_width() // 2 + 10, 140),
                        (screen.get_width() // 2 + 10, 400), 2)

        # 绘制控制说明（右侧）
        control_y = 150
        for section in control_sections:
            for i, line in enumerate(section):
                if i == 0:  # 标题行
                    color = (255, 150, 50) if line == "CONTROLS" else (100, 200, 255)
                    font = self.heading_font if line == "CONTROLS" else self.text_font
                else:
                    color = (200, 200, 200)
                    font = self.text_font
                
                text = font.render(line, True, color)
                text_rect = text.get_rect(midleft=(screen.get_width() // 2 + 40, control_y))
                screen.blit(text, text_rect)
                control_y += 30
            control_y += 10  # 段间距

        # 绘制返回提示
        hint_text = self.small_font.render("Press SPACE or ESC to return", True, (150, 150, 200))
        hint_rect = hint_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(hint_text, hint_rect)

        # 简单的像素风格装饰
        self.draw_pixel_decoration(screen)

    def draw_pixel_decoration(self, screen):
        """绘制像素风格的装饰"""
        # 四个角的像素风格装饰
        pixel_size = 4
        color = (100, 150, 200)
        
        # 左上角
        for i in range(5):
            pygame.draw.rect(screen, color, (20, 20 + i*pixel_size*2, pixel_size, pixel_size))
            pygame.draw.rect(screen, color, (20 + i*pixel_size*2, 20, pixel_size, pixel_size))
        
        # 右上角
        for i in range(5):
            pygame.draw.rect(screen, color, (screen.get_width()-40, 20 + i*pixel_size*2, pixel_size, pixel_size))
            pygame.draw.rect(screen, color, (screen.get_width()-40 - i*pixel_size*2, 20, pixel_size, pixel_size))
        
        # 左下角
        for i in range(5):
            pygame.draw.rect(screen, color, (20, screen.get_height()-40 - i*pixel_size*2, pixel_size, pixel_size))
            pygame.draw.rect(screen, color, (20 + i*pixel_size*2, screen.get_height()-40, pixel_size, pixel_size))
        
        # 右下角
        for i in range(5):
            pygame.draw.rect(screen, color, (screen.get_width()-40, screen.get_height()-40 - i*pixel_size*2, pixel_size, pixel_size))
            pygame.draw.rect(screen, color, (screen.get_width()-40 - i*pixel_size*2, screen.get_height()-40, pixel_size, pixel_size))
