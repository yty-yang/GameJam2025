import pygame
from core.scenes.scene import Scene

class HelpScene(Scene):
    def __init__(self):
        super().__init__()
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.heading_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.story_font = pygame.font.SysFont("Arial", 22)
        self.control_font = pygame.font.SysFont("Arial", 24)
        self.continue_font = pygame.font.SysFont("Arial", 20, italic=True)
        
        # 创建渐变色背景
        self.background = self.create_gradient_background(800, 600)

    def create_gradient_background(self, width, height):
        """创建深色渐变背景"""
        background = pygame.Surface((width, height))
        for y in range(height):
            # 从深蓝色渐变到深紫色
            color = (30, 30, 60 + y//10, 255)
            pygame.draw.line(background, color, (0, y), (width, y))
        return background

    def handle_events(self, events):
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (
                    event.type == pygame.JOYBUTTONDOWN and event.button == 0):
                self.next_scene = "menu"  # 按 ESC 返回菜单
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.next_scene = "menu"  # 按空格键也可以返回

    def update(self, dt):
        pass

    def draw(self, screen):
        # 绘制渐变背景
        screen.blit(self.background, (0, 0))
        
        # 故事文本
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

        # 控制说明
        control_lines = [
            "CONTROLS:",
            "Q - Move left side up",
            "E - Move right side up", 
            "ESC - Pause/Return to menu",
            "SPACE - Continue"
        ]

        # 绘制标题
        title = self.title_font.render("THE LEGEND", True, (255, 215, 0))  # 金色
        title_rect = title.get_rect(center=(screen.get_width() // 2, 40))
        screen.blit(title, title_rect)

        subtitle = self.heading_font.render("of Glacier's Heart", True, (173, 216, 230))  # 淡蓝色
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 85))
        screen.blit(subtitle, subtitle_rect)

        # 绘制故事文本（左侧）
        story_y = 140
        for i, line in enumerate(story_lines):
            if line == "":
                story_y += 10  # 空行间距
            else:
                if i == 0:  # 第一行是子标题
                    text = self.heading_font.render(line, True, (255, 255, 255))
                else:
                    text = self.story_font.render(line, True, (200, 200, 200))
                
                text_rect = text.get_rect(midleft=(50, story_y))
                screen.blit(text, text_rect)
                story_y += 35

        # 绘制分隔线
        pygame.draw.line(screen, (100, 100, 150), 
                        (screen.get_width() // 2 - 20, 140),
                        (screen.get_width() // 2 - 20, 500), 2)

        # 绘制控制说明（右侧）
        control_y = 140
        for i, line in enumerate(control_lines):
            if i == 0:  # 标题行
                text = self.heading_font.render(line, True, (255, 165, 0))  # 橙色
            else:
                text = self.control_font.render(line, True, (200, 200, 200))
            
            text_rect = text.get_rect(midleft=(screen.get_width() // 2 + 20, control_y))
            screen.blit(text, text_rect)
            control_y += 40

        # 绘制装饰边框
        pygame.draw.rect(screen, (100, 100, 150), (20, 20, screen.get_width()-40, screen.get_height()-40), 3, border_radius=10)
        
        # 绘制底部提示
        continue_text = self.continue_font.render("Press SPACE or ESC to return to menu", True, (150, 150, 200))
        continue_rect = continue_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(continue_text, continue_rect)

        # 绘制装饰性图标
        self.draw_decorations(screen)

    def draw_decorations(self, screen):
        """绘制一些装饰性元素"""
        # 左上角啤酒杯图标
        beer_icon = [
            "  ***  ",
            " *   * ",
            " *   * ",
            " ***** ",
            "  ***  ",
            "  * *  "
        ]
        
        # 绘制简单的ASCII风格啤酒杯
        for y, line in enumerate(beer_icon):
            for x, char in enumerate(line):
                if char == '*':
                    pos_x = 100 + x * 6
                    pos_y = 120 + y * 6
                    pygame.draw.rect(screen, (255, 215, 0), (pos_x, pos_y, 4, 4))
