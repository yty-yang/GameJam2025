from pathlib import Path
import math

import pygame

from core.scenes.common.menu_navigation_mixin import confirm_pressed
from core.scenes.scene import Scene
from core.sound import sound_manager
from utils.helper import save_data
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_STATE

class ShopScene(Scene):
    def __init__(self):
        super().__init__()
        
        self.show_beer_prompt = True     # 一进入 Shop 就显示提示
        self.beer_choice_index = 0       # 0 = Yes, 1 = No
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)  # 标题字体
        self.hud_font = pygame.font.Font(None, 32)  # HUD 字体

        # 加载背景图
        project_root = Path(__file__).resolve().parents[3]
        path = project_root / "data/pictures/level_end_background.png"
        img = pygame.image.load(path).convert()
        self.background = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # 啤酒淡入淡出动画
        beer_path = project_root / "data/pictures/characters/beer_with_ice.png"
        self.beer_img_original = pygame.image.load(beer_path).convert_alpha()
        w, h = self.beer_img_original.get_size()
        self.beer_base_size = (int(w * 0.3), int(h * 0.3))
        self.beer_img = pygame.transform.scale(self.beer_img_original, self.beer_base_size)
        self.beer_alpha = 0
        self.beer_state = None  # None / fadein / hold / fadeout
        self.beer_timer = 0
        self.beer_scale = 0.5  # 初始缩放（从0.5倍放大到1.0倍）
        self.beer_rotation = 0  # 旋转角度
        
        # 预加载购买音效
        try:
            eat_coins_path = project_root / "data" / "sounds" / "eat_coins.mp3"
            if eat_coins_path.exists():
                sound_manager.load_sound("eat_coins", str(eat_coins_path))
        except Exception as e:
            print(f"无法预加载购买音效: {e}")

    def handle_events(self, events):
        if self.show_beer_prompt:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.beer_choice_index = max(0, self.beer_choice_index - 1)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.beer_choice_index = min(1, self.beer_choice_index + 1)


            if hasattr(self, "joystick") and self.joystick:
                lx = self.joystick.get_axis(0)
                if lx < -0.5 and not hasattr(self, "_joy_left"):
                    self.beer_choice_index = max(0, self.beer_choice_index - 1)
                    self._joy_left = True

                elif lx > 0.5 and not hasattr(self, "_joy_right"):
                    self.beer_choice_index = min(1, self.beer_choice_index + 1)
                    self._joy_right = True


                elif -0.3 < lx < 0.3:
                    # 松开时允许再次触发
                    if hasattr(self, "_joy_left"):
                        delattr(self, "_joy_left")

                    if hasattr(self, "_joy_right"):
                        delattr(self, "_joy_right")

            if confirm_pressed(events):
                if self.beer_choice_index == 0:
                    # 玩家选择了 "Yes"
                    if GAME_STATE["total_coins"] >= 5:
                        GAME_STATE["total_coins"] -= 5
                        GAME_STATE["beer"] += 1
                        save_data()

                        # 播放购买音效
                        try:
                            sound_manager.play_sound("eat_coins")
                        except Exception:
                            pass  # 如果音效加载失败，不影响功能

                        # 启动啤酒动画
                        self.beer_state = "fadein"
                        self.beer_alpha = 0
                        self.beer_timer = 0
                        self.beer_scale = 0.5  # 从0.5倍开始
                        self.beer_rotation = 0

                self.show_beer_prompt = False
                # 等动画结束再跳
                if self.beer_state is None:
                    self.next_scene = "menu"  # 返回主菜单
        else:
            # 可以在这里处理其他 ShopScene 的事件
            pass

    def update(self, dt):
        # 啤酒动画（摇晃 + 闪光 + 缩放 + 旋转）
        if self.beer_state in ("fadein", "hold", "fadeout"):
            self.beer_timer += dt

            # 上下浮动: sin 波动
            self.beer_float_offset = math.sin(self.beer_timer * 6) * 8  # 上下 ±8px

            # 左右轻微摇晃
            self.beer_shake_offset = math.sin(self.beer_timer * 12) * 4  # 左右 ±4px

            if self.beer_state == "fadein":
                # 淡入阶段：缩放从0.5到1.0，旋转360度，闪光效果
                fadein_duration = 0.8  # 淡入持续时间
                progress = min(1.0, self.beer_timer / fadein_duration)
                
                # 缩放动画（弹性效果）
                if progress < 1.0:
                    # 使用缓动函数实现弹性效果
                    ease_progress = 1 - (1 - progress) ** 3  # 三次缓动
                    self.beer_scale = 0.5 + ease_progress * 0.5
                else:
                    self.beer_scale = 1.0
                
                # 旋转动画（360度旋转）
                self.beer_rotation = progress * 360
                
                # 闪光效果
                flash = (math.sin(self.beer_timer * 20) + 1) * 0.1  # 0 ~ 0.2
                self.beer_alpha = min(255, int(255 * progress) + int(flash * 50))
                
                # 淡入完成后进入保持阶段
                if progress >= 1.0:
                    self.beer_state = "hold"
                    self.beer_timer = 0  # 重置计时器用于保持阶段

            elif self.beer_state == "hold":
                # 保持阶段：轻微摇晃和浮动，持续1.5秒
                hold_duration = 1.5
                self.beer_alpha = 255
                self.beer_scale = 1.0
                self.beer_rotation = 0
                
                if self.beer_timer >= hold_duration:
                    self.beer_state = "fadeout"
                    self.beer_timer = 0  # 重置计时器用于淡出阶段

            elif self.beer_state == "fadeout":
                # 淡出阶段：缩小并淡出
                fadeout_duration = 0.5
                progress = min(1.0, self.beer_timer / fadeout_duration)
                
                self.beer_scale = 1.0 - progress * 0.3  # 缩小到0.7倍
                self.beer_alpha = int(255 * (1 - progress))
                
                if progress >= 1.0:
                    self.beer_alpha = 0
                    self.beer_state = None
                    self.next_scene = "menu"

    def draw(self, screen):
        # 先绘制背景
        screen.blit(self.background, (0, 0))
        
        # 顶部 HUD 条（在背景之上）- 优化设计
        hud_height = 50
        # 半透明灰色背景
        hud_bg = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
        for i in range(hud_height):
            alpha = int(150 + (i / hud_height) * 50)  # 从150到200的透明度
            gray_value = 85 + int((i / hud_height) * 20)  # 灰色值从80到100
            pygame.draw.line(hud_bg, (gray_value, gray_value, gray_value, alpha), 
                            (0, i), (SCREEN_WIDTH, i))
        screen.blit(hud_bg, (0, 0))
        
        # 底部边框（亮色）
        pygame.draw.line(screen, (100, 100, 100), (0, hud_height - 1), (SCREEN_WIDTH, hud_height - 1), 2)
        # 顶部高光
        pygame.draw.line(screen, (150, 150, 150), (0, 0), (SCREEN_WIDTH, 0), 1)
        
        # HUD 文字（带阴影效果）
        coins_text = f"Coins: {GAME_STATE['total_coins']}"
        beer_text = f"Beer: {GAME_STATE['beer']}"
        
        # 金币文字（金色，带阴影）
        coins_shadow = self.hud_font.render(coins_text, True, (0, 0, 0))
        coins_surface = self.hud_font.render(coins_text, True, (255, 215, 0))  # 金色
        screen.blit(coins_shadow, (22, 12))
        screen.blit(coins_surface, (20, 10))
        
        # 啤酒文字（青色，带阴影）
        beer_shadow = self.hud_font.render(beer_text, True, (0, 0, 0))
        beer_surface = self.hud_font.render(beer_text, True, (100, 200, 255))  # 青色
        beer_x = SCREEN_WIDTH - beer_surface.get_width() - 20
        screen.blit(beer_shadow, (beer_x + 2, 12))
        screen.blit(beer_surface, (beer_x, 10))

        if self.show_beer_prompt:
            # 对话框 - 轻量设计，不覆盖背景
            box_w, box_h = SCREEN_WIDTH - 200, 160
            box_x = 100
            box_y = SCREEN_HEIGHT - box_h - 60
            
            # 只给对话框区域添加半透明背景（更透明）
            dialog_bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            for i in range(box_h):
                alpha = int(80 + (i / box_h) * 40)  # 从80到120的渐变，更透明
                color_value = 20 + int((i / box_h) * 10)
                pygame.draw.line(dialog_bg, (color_value, color_value, color_value, alpha), 
                                (0, i), (box_w, i))
            screen.blit(dialog_bg, (box_x, box_y))
            
            # 外阴影（更轻）
            shadow_surface = pygame.Surface((box_w + 6, box_h + 6), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 60))  # 更透明的阴影
            screen.blit(shadow_surface, (box_x - 3, box_y - 3))
            
            # 边框（更细，更精致）
            # 外边框（亮色，细线）
            pygame.draw.rect(screen, (220, 220, 220), (box_x, box_y, box_w, box_h), 2)
            # 内边框（暗色，细线）
            pygame.draw.rect(screen, (100, 100, 100), (box_x + 2, box_y + 2, box_w - 4, box_h - 4), 1)

            # 标题文本（带更明显的阴影，确保在背景上可读）
            title_text = "Do you want a beer?"
            # 多层阴影效果，增强可读性
            for offset_x, offset_y in [(3, 3), (2, 2), (1, 1)]:
                title_shadow = self.title_font.render(title_text, True, (0, 0, 0))
                screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + offset_x, 
                                          box_y + 40 - title_shadow.get_height() // 2 + offset_y))
            title_surface = self.title_font.render(title_text, True, (255, 255, 255))  # 白色，更清晰
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 40))
            screen.blit(title_surface, title_rect)
            
            # 价格文本（带阴影）
            price_text = "( 5 coins )"
            price_shadow = self.font.render(price_text, True, (0, 0, 0))
            price_surface = self.font.render(price_text, True, (255, 215, 0))  # 金色
            price_rect = price_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 75))
            screen.blit(price_shadow, (price_rect.x + 1, price_rect.y + 1))
            screen.blit(price_surface, price_rect)

            # Yes / No 按钮 - 优化设计
            options = ["Yes", "No"]
            button_spacing = 200
            button_start_x = SCREEN_WIDTH // 2 - (button_spacing * (len(options) - 1)) // 2
            
            for i, option in enumerate(options):
                button_x = button_start_x + i * button_spacing
                button_y = box_y + 120  # 向下移动20像素
                is_selected = (i == self.beer_choice_index)
                
                # 按钮背景
                button_w, button_h = 100, 45
                button_rect = pygame.Rect(button_x - button_w // 2, button_y - button_h // 2, 
                                         button_w, button_h)
                
                if is_selected:
                    # 选中状态：亮色背景
                    # 渐变背景
                    for j in range(button_h):
                        color_value = 200 + int((j / button_h) * 55)
                        pygame.draw.line(screen, (color_value, color_value, 100), 
                                        (button_rect.x, button_rect.y + j), 
                                        (button_rect.x + button_w, button_rect.y + j))
                    # 边框（亮黄色）
                    pygame.draw.rect(screen, (255, 255, 100), button_rect, 3)
                    # 高光
                    pygame.draw.line(screen, (255, 255, 200), 
                                   (button_rect.x + 2, button_rect.y + 2), 
                                   (button_rect.x + button_w - 2, button_rect.y + 2), 1)
                    text_color = (50, 50, 0)  # 深色文字
                else:
                    # 未选中状态：暗色背景
                    pygame.draw.rect(screen, (60, 60, 60), button_rect)
                    pygame.draw.rect(screen, (120, 120, 120), button_rect, 2)
                    text_color = (200, 200, 200)  # 浅色文字
                
                # 按钮文字（带阴影）
                text_surface = self.font.render(option, True, text_color)
                text_rect = text_surface.get_rect(center=(button_x, button_y))
                if is_selected:
                    # 选中时添加阴影
                    text_shadow = self.font.render(option, True, (0, 0, 0))
                    screen.blit(text_shadow, (text_rect.x + 1, text_rect.y + 1))
                screen.blit(text_surface, text_rect)
        else:
            # 可以绘制 Shop 主界面内容
            info_surface = self.font.render("Welcome to the Shop!", True, (200, 200, 255))
            screen.blit(info_surface, (SCREEN_WIDTH // 2 - info_surface.get_width() // 2, SCREEN_HEIGHT // 2))

        # 啤酒淡入淡出 + 摇晃动画 + 缩放 + 旋转
        if self.beer_state is not None:
            # 计算缩放后的尺寸
            scaled_size = (int(self.beer_base_size[0] * self.beer_scale), 
                          int(self.beer_base_size[1] * self.beer_scale))
            
            # 缩放图片
            scaled_img = pygame.transform.scale(self.beer_img_original, scaled_size)
            
            # 旋转图片（仅在淡入阶段旋转）
            if self.beer_state == "fadein" and self.beer_rotation != 0:
                rotated_img = pygame.transform.rotate(scaled_img, -self.beer_rotation)
            else:
                rotated_img = scaled_img
            
            # 设置透明度
            rotated_img.set_alpha(int(self.beer_alpha))

            # 计算位置（考虑摇晃和浮动）
            cx = SCREEN_WIDTH // 2 + getattr(self, "beer_shake_offset", 0)
            cy = SCREEN_HEIGHT // 2 + getattr(self, "beer_float_offset", 0)

            # 绘制（居中）
            rect = rotated_img.get_rect(center=(cx, cy))
            screen.blit(rotated_img, rect)
