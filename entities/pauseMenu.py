import pygame


class PauseMenu:
    def __init__(self, options=None, font_size=40, screen_width=800, screen_height=600):
        """
        options: 菜单选项列表
        font_size: 字体大小
        """
        self.options = options or ["Resume", "Quit"]
        self.selected_index = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont(None, font_size)
        self.title_font = pygame.font.SysFont(None, font_size + 20)
        self.title_text = self.title_font.render("Paused", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(screen_width // 2, screen_height // 4))

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def handle_events(self, events):
        if self.joystick:
            ly = self.joystick.get_axis(1)
            # 上推
            if ly < -0.5 and not hasattr(self, "_joystick_up_pressed"):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                self._joystick_up_pressed = True
            elif ly > 0.5 and not hasattr(self, "_joystick_down_pressed"):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                self._joystick_down_pressed = True
            elif -0.3 < ly < 0.3:
                # 归位，允许下一次输入
                if hasattr(self, "_joystick_up_pressed"):
                    delattr(self, "_joystick_up_pressed")
                if hasattr(self, "_joystick_down_pressed"):
                    delattr(self, "_joystick_down_pressed")

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected_index]
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                return self.options[self.selected_index]
        return None

    def update(self, dt):
        # TODO: 可以在这里加光标闪烁或动画
        pass

    def draw(self, screen):
        # 半透明遮罩
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 标题
        screen.blit(self.title_text, self.title_rect)

        # 菜单选项
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + i * 60))
            screen.blit(text, rect)
