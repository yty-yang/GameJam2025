import pygame
from core.scenes.scene import Scene
from core.scenes.common.menu_navigation_mixin import confirm_pressed

class CreditsScene(Scene):
    def __init__(self):
        super().__init__()
        # 使用和Help界面相同的字体
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
        # 深色背景 - 与Help界面一致
        screen.fill((20, 20, 35))
        
        # 制作人员内容
        credits_lines = [
            "CREDITS",
            "",
            "Special Thanks to:",
            "University of Bristol",
            "Computer Science Society",
            "for hosting this Game Jam",
            "",
            "--- TEAM SATURDAY 19 ---",
            "",
            "Team Members:",
            "Stephen Yang",
            "Siyue Teng", 
            "Xiaoting Huang",
            "Xinlan Shi",
            "Kehao Zhou",
            "Haoran Liu"
        ]

        current_y = 50

        # 绘制主标题
        title = self.title_font.render("ICE COLD BEER", True, (255, 215, 0))
        title_rect = title.get_rect(center=(screen.get_width() // 2, current_y))
        screen.blit(title, title_rect)
        current_y += 60

        # 绘制制作人员内容
        for line in credits_lines:
            if line == "":
                current_y += 15  # 空行间距
            elif line == "CREDITS":
                text = self.heading_font.render(line, True, (100, 200, 255))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 50
            elif line == "--- TEAM SATURDAY 19 ---":
                text = self.heading_font.render("TEAM SATURDAY 19", True, (255, 150, 50))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 40
            elif line in ["Special Thanks to:", "Team Members:"]:
                text = self.text_font.render(line, True, (100, 200, 255))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 35
            else:
                text = self.text_font.render(line, True, (220, 220, 220))
                text_rect = text.get_rect(center=(screen.get_width() // 2, current_y))
                screen.blit(text, text_rect)
                current_y += 30

        # 绘制返回提示
        hint_text = self.small_font.render("Press ENTER to return", True, (150, 150, 200))
        hint_rect = hint_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(hint_text, hint_rect)


