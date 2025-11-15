import pygame

from core.scenes.scene import Scene
import core.scenes.common.menu_navigation_mixin as menu_nav
from core.sound import sound_manager


class SettingScene(Scene, menu_nav.MenuNavigationMixin):
    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)

        self.options = ["Volume", "Vibration", "Return"]
        self.selected_index = 0

        self.volume = 5  # 0–10
        self.vibration = True

    def handle_events(self, events):
        self._handle_common_navigation(events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.options[self.selected_index] == "Volume":
                    if event.key == pygame.K_LEFT:
                        self.volume = max(0, self.volume - 1)
                        sound_manager.set_volume(self.volume / 10)
                    elif event.key == pygame.K_RIGHT:
                        self.volume = min(10, self.volume + 1)
                        sound_manager.set_volume(self.volume / 10)

        if menu_nav.confirm_pressed(events):
            self._select_option()

    def _select_option(self):
        option = self.options[self.selected_index]
        if self.options[self.selected_index] == "Vibration":
            self.vibration = not self.vibration
        elif option == "Return":
            self.next_scene = "menu"

    def update(self, dt):
        sound_manager.set_volume(self.volume / 10)

    def draw(self, screen):
        screen.fill((50, 50, 50))

        center_x = screen.get_width() // 2
        y = 120

        title = self.font.render("Setting", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(center_x, y)))
        y += 80

        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text = self.font.render(option, True, color)
            screen.blit(text, text.get_rect(center=(center_x, y)))

            if option == "Volume":
                bar_width = 300
                bar_height = 18
                bar_x = center_x - bar_width // 2
                bar_y = y + 40

                pygame.draw.rect(screen, (180, 180, 180), (bar_x, bar_y, bar_width, bar_height), 2)

                fill_width = int((self.volume / 10) * bar_width)
                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, fill_width, bar_height))

                y += 70

            elif option == "Vibration":
                vib_text = self.small_font.render(
                    "On" if self.vibration else "Off",
                    True,
                    (200, 200, 200)
                )
                screen.blit(vib_text, vib_text.get_rect(center=(center_x, y + 40)))

                y += 70

            else:
                y += 60
