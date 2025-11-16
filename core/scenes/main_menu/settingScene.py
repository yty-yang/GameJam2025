import pygame

from core.scenes.scene import Scene
import core.scenes.common.menu_navigation_mixin as menu_nav
from core.sound import sound_manager
from core.ui import UI
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_STATE
from utils.helper import save_data


class SettingScene(Scene, menu_nav.MenuNavigationMixin):
    def __init__(self):
        super().__init__()

        self.title_font = pygame.font.SysFont(None, 56)
        self.option_font = pygame.font.SysFont(None, 42)
        self.value_font = pygame.font.SysFont(None, 36)
        self.hint_font = pygame.font.SysFont(None, 24)

        self.options = ["Volume", "Vibration", "Return"]
        self.selected_index = 0

        self.volume = GAME_STATE["volume"]
        self.vibration = GAME_STATE["vibration"]

    def handle_events(self, events):
        self._handle_common_navigation(events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.options[self.selected_index] == "Volume":
                    if event.key == pygame.K_LEFT:
                        self.volume = max(0, self.volume - 1)
                        sound_manager.set_volume(self.volume / 10)
                        GAME_STATE["volume"] = self.volume
                        save_data()
                    if event.key == pygame.K_RIGHT:
                        self.volume = min(10, self.volume + 1)
                        sound_manager.set_volume(self.volume / 10)
                        GAME_STATE["volume"] = self.volume
                        save_data()

            # Joystick left/right to adjust volume
            if event.type == pygame.JOYAXISMOTION and self.options[self.selected_index] == "Volume":
                if event.axis == 0:  # horizontal axis
                    if event.value < -0.5:
                        self.volume = max(0, self.volume - 1)
                        sound_manager.set_volume(self.volume / 10)
                        GAME_STATE["volume"] = self.volume
                        save_data()
                    elif event.value > 0.5:
                        self.volume = min(10, self.volume + 1)
                        sound_manager.set_volume(self.volume / 10)
                        GAME_STATE["volume"] = self.volume
                        save_data()

        if menu_nav.confirm_pressed(events):
            self._select_option()

    def _select_option(self):
        option = self.options[self.selected_index]
        if self.options[self.selected_index] == "Vibration":
            self.vibration = not self.vibration
            GAME_STATE["vibration"] = self.vibration
            save_data()
        elif option == "Return":
            self.next_scene = "menu"

    def update(self, dt):
        pass

    def draw(self, screen):
        # 背景
        screen.fill((20, 20, 20))
        
        # 应用CRT效果
        ui = UI()
        ui.apply_effects(screen)

        center_x = SCREEN_WIDTH // 2
        
        # 绘制标题
        title_y = 80
        title = self.title_font.render("SETTINGS", True, (255, 255, 0))
        title_rect = title.get_rect(center=(center_x, title_y))
        screen.blit(title, title_rect)
        
        # 绘制分隔线
        line_y = title_y + 50
        pygame.draw.line(screen, (100, 100, 100), (center_x - 200, line_y), (center_x + 200, line_y), 2)
        
        # 选项起始位置
        option_start_y = 200
        option_spacing = 120  # 选项之间的间距
        
        for i, option in enumerate(self.options):
            option_y = option_start_y + i * option_spacing
            is_selected = i == self.selected_index
            
            # 选项名称颜色
            option_color = (255, 255, 0) if is_selected else (255, 255, 255)
            
            # 绘制选项名称（更靠左，避免与内容重叠）
            option_text = self.option_font.render(option, True, option_color)
            option_x = 150  # 左侧固定位置，给右侧内容留出空间
            screen.blit(option_text, (option_x, option_y))
            
            # 绘制选项内容（右侧区域）
            content_x = center_x + 50  # 内容区域从中心偏右开始
            if option == "Volume":
                self._draw_volume_setting(screen, content_x, option_y, is_selected)
            elif option == "Vibration":
                self._draw_vibration_setting(screen, content_x, option_y, is_selected)
            elif option == "Return":
                # Return选项不需要额外内容
                pass
        
        # 绘制操作提示
        hint_y = SCREEN_HEIGHT - 60
        if self.selected_index == 0:  # Volume
            hint_text = "Use LEFT/RIGHT arrows to adjust volume"
        elif self.selected_index == 1:  # Vibration
            hint_text = "Press ENTER to toggle vibration"
        else:  # Return
            hint_text = "Press ENTER to return to menu"
        
        hint_surface = self.hint_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(center_x, hint_y))
        screen.blit(hint_surface, hint_rect)

    def _draw_volume_setting(self, screen, content_x, y, is_selected):
        """绘制音量设置（像素风格）"""
        # 音量条参数
        bar_width = 300
        bar_height = 28
        bar_x = content_x - bar_width // 2
        bar_y = y + 8
        
        # 绘制背景框（像素风格 - 使用像素块）
        border_thickness = 3
        # 外框阴影
        pygame.draw.rect(screen, (20, 20, 20), 
                        (bar_x - border_thickness - 2, bar_y - border_thickness - 2, 
                         bar_width + (border_thickness + 2) * 2, bar_height + (border_thickness + 2) * 2))
        # 外框
        pygame.draw.rect(screen, (80, 80, 80), 
                        (bar_x - border_thickness, bar_y - border_thickness, 
                         bar_width + border_thickness * 2, bar_height + border_thickness * 2))
        # 内框高光
        pygame.draw.rect(screen, (120, 120, 120), 
                        (bar_x - border_thickness + 1, bar_y - border_thickness + 1, 
                         bar_width + (border_thickness - 1) * 2, bar_height + (border_thickness - 1) * 2), 1)
        
        # 绘制音量条背景（像素风格 - 使用深色块）
        pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
        # 背景纹理（像素点）
        for px in range(bar_x, bar_x + bar_width, 4):
            for py in range(bar_y, bar_y + bar_height, 4):
                if (px + py) % 8 == 0:
                    pygame.draw.rect(screen, (20, 20, 20), (px, py, 2, 2))
        
        # 绘制音量填充（像素风格 - 使用蓝青色，不那么绿）
        fill_width = int((self.volume / 10) * bar_width)
        if fill_width > 0:
            # 像素块填充（每4像素一个块）
            pixel_size = 4
            for x in range(bar_x, bar_x + fill_width, pixel_size):
                block_width = min(pixel_size, bar_x + fill_width - x)
                progress = (x - bar_x) / bar_width
                
                # 使用蓝青色渐变（从深蓝绿到亮蓝绿）
                # R: 0-100, G: 150-255, B: 150-255
                r = int(0 + progress * 50)
                g = int(150 + progress * 105)
                b = int(150 + progress * 105)
                color = (r, g, b)
                
                pygame.draw.rect(screen, color, (x, bar_y, block_width, bar_height))
            
            # 像素风格高光（顶部）
            highlight_height = 8
            for x in range(bar_x, bar_x + fill_width, 2):
                if x % 4 == 0:  # 每隔一个像素点绘制高光
                    pygame.draw.rect(screen, (100, 220, 220), (x, bar_y, 2, highlight_height))
        
        # 绘制刻度线（像素风格）
        for i in range(11):  # 0-10
            tick_x = bar_x + int((i / 10) * bar_width)
            tick_length = 10 if i % 5 == 0 else 6  # 每5个单位一个长刻度
            # 像素风格的刻度（使用矩形块）
            pygame.draw.rect(screen, (100, 100, 100), 
                           (tick_x - 1, bar_y + bar_height, 3, tick_length))
        
        # 绘制当前音量数值（像素风格）
        volume_text = self.value_font.render(f"{self.volume}/10", True, (200, 220, 255))
        volume_rect = volume_text.get_rect(center=(content_x, bar_y + bar_height + 22))
        # 文字阴影效果
        shadow_text = self.value_font.render(f"{self.volume}/10", True, (0, 0, 0))
        screen.blit(shadow_text, (volume_rect.x + 2, volume_rect.y + 2))
        screen.blit(volume_text, volume_rect)

    def _draw_vibration_setting(self, screen, content_x, y, is_selected):
        """绘制振动设置（像素风格）"""
        # 开关按钮参数
        switch_width = 100
        switch_height = 45
        switch_x = content_x - switch_width // 2
        switch_y = y + 8
        
        # 绘制开关背景（像素风格 - 使用像素块边框）
        border_thickness = 3
        # 外框阴影
        pygame.draw.rect(screen, (20, 20, 20), 
                        (switch_x - border_thickness - 2, switch_y - border_thickness - 2, 
                         switch_width + (border_thickness + 2) * 2, switch_height + (border_thickness + 2) * 2))
        # 外框
        bg_color = (80, 180, 100) if self.vibration else (70, 70, 70)
        pygame.draw.rect(screen, (80, 80, 80), 
                        (switch_x - border_thickness, switch_y - border_thickness, 
                         switch_width + border_thickness * 2, switch_height + border_thickness * 2))
        # 背景
        pygame.draw.rect(screen, bg_color, (switch_x, switch_y, switch_width, switch_height))
        # 内框高光
        pygame.draw.rect(screen, (120, 120, 120), 
                        (switch_x + 1, switch_y + 1, switch_width - 2, switch_height - 2), 1)
        
        # 背景纹理（像素点）
        pixel_spacing = 4
        for px in range(switch_x, switch_x + switch_width, pixel_spacing):
            for py in range(switch_y, switch_y + switch_height, pixel_spacing):
                if (px + py) % 8 == 0:
                    pixel_color = (60, 160, 80) if self.vibration else (50, 50, 50)
                    pygame.draw.rect(screen, pixel_color, (px, py, 2, 2))
        
        # 绘制开关滑块（像素风格）
        slider_width = switch_width // 2 - 4
        slider_height = switch_height - 6
        if self.vibration:
            slider_x = switch_x + switch_width - slider_width - 3
            slider_color = (150, 240, 170)
        else:
            slider_x = switch_x + 3
            slider_color = (120, 120, 120)
        
        # 滑块主体
        pygame.draw.rect(screen, slider_color, (slider_x, switch_y + 3, slider_width, slider_height))
        # 滑块边框
        pygame.draw.rect(screen, (200, 200, 200), (slider_x, switch_y + 3, slider_width, slider_height), 2)
        # 滑块高光（像素风格）
        pygame.draw.rect(screen, (220, 255, 220) if self.vibration else (180, 180, 180), 
                        (slider_x + 1, switch_y + 4, slider_width - 2, 4))
        
        # 绘制ON/OFF文字（像素风格）
        status_text = "ON" if self.vibration else "OFF"
        status_color = (100, 255, 120) if self.vibration else (150, 150, 150)
        status_surface = self.value_font.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(content_x, switch_y + switch_height // 2))
        # 文字阴影
        shadow_surface = self.value_font.render(status_text, True, (0, 0, 0))
        screen.blit(shadow_surface, (status_rect.x + 2, status_rect.y + 2))
        screen.blit(status_surface, status_rect)
