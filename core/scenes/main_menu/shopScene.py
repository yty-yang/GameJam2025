from pathlib import Path
import math

import pygame

from core.scenes.common.menu_navigation_mixin import confirm_pressed
from core.scenes.scene import Scene
from utils.helper import save_data
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_STATE

class ShopScene(Scene):
    def __init__(self):
        super().__init__()
        
        self.show_beer_prompt = True     # 一进入 Shop 就显示提示
        self.beer_choice_index = 0       # 0 = Yes, 1 = No
        self.font = pygame.font.Font(None, 36)

        # 加载背景图
        project_root = Path(__file__).resolve().parents[3]
        path = project_root / "data/pictures/level_end_background.png"
        img = pygame.image.load(path).convert()
        self.background = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # 啤酒淡入淡出动画
        beer_path = project_root / "data/pictures/characters/beer_with_ice.png"
        self.beer_img = pygame.image.load(beer_path).convert_alpha()
        w, h = self.beer_img.get_size()
        self.beer_img = pygame.transform.scale(self.beer_img, (int(w * 0.3), int(h * 0.3)))
        self.beer_alpha = 0
        self.beer_state = None  # None / fadein / hold / fadeout
        self.beer_timer = 0

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

                        # 启动啤酒动画
                        self.beer_state = "fadein"
                        self.beer_alpha = 0
                        self.beer_timer = 0

                self.show_beer_prompt = False
                # 等动画结束再跳
                if self.beer_state is None:
                    self.next_scene = "menu"  # 返回主菜单
        else:
            # 可以在这里处理其他 ShopScene 的事件
            pass

    def update(self, dt):
        # 啤酒动画（摇晃 + 闪光）
        if self.beer_state in ("fadein", "hold", "fadeout"):
            self.beer_timer += dt

            # 上下浮动: sin 波动
            self.beer_float_offset = math.sin(self.beer_timer * 6) * 8  # 上下 ±8px

            # 左右轻微摇晃
            self.beer_shake_offset = math.sin(self.beer_timer * 12) * 4  # 左右 ±4px

            # 闪光：淡入阶段轻微闪烁（不是很闪眼）
            if self.beer_state == "fadein":
                flash = (math.sin(self.beer_timer * 20) + 1) * 0.1  # 0 ~ 0.2
                self.beer_alpha = min(255, self.beer_alpha + (200 * dt) + flash * 255)

            elif self.beer_state == "hold":
                self.beer_alpha = 255

            elif self.beer_state == "fadeout":
                self.beer_alpha -= 200 * dt
                if self.beer_alpha <= 0:
                    self.beer_alpha = 0
                    self.beer_state = None
                    self.next_scene = "menu"

    def draw(self, screen):
        # 顶部 HUD 条
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, SCREEN_WIDTH, 40))
        pygame.draw.rect(screen, (200, 200, 200), (0, 0, SCREEN_WIDTH, 40), 3)

        hud_text = f"Coins: {GAME_STATE['total_coins']}    Beer: {GAME_STATE['beer']}"
        hud_surface = self.font.render(hud_text, True, (255, 255, 0))
        screen.blit(hud_surface, (20, 6))

        screen.blit(self.background, (0, 0))

        if self.show_beer_prompt:
            # 半透明背景
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))

            # 对话框
            box_w, box_h = SCREEN_WIDTH, 120
            box_x = 0
            box_y = SCREEN_HEIGHT - box_h
            # 像素底框 (深灰)
            pygame.draw.rect(screen, (30, 30, 30), (box_x, box_y, box_w, box_h))

            # 内框 (稍亮灰)
            pygame.draw.rect(screen, (80, 80, 80), (box_x + 4, box_y + 4, box_w - 8, box_h - 8), 3)

            # 外框 (亮色)
            pygame.draw.rect(screen, (220, 220, 220), (box_x, box_y, box_w, box_h), 4)

            # 文本
            prompt_surface = self.font.render("Do you want a beer ( 5 coins )", True, (255, 255, 255))
            prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 35))
            screen.blit(prompt_surface, prompt_rect)

            # Yes / No
            options = ["Yes", "No"]
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == self.beer_choice_index else (255, 255, 255)
                text_surface = self.font.render(option, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2 - 60 + i * 120, box_y + 80))

                # 选中的用像素框框住
                if i == self.beer_choice_index:
                    pygame.draw.rect(screen, (255, 255, 0), text_rect.inflate(20, 10), 2)

                screen.blit(text_surface, text_rect)
        else:
            # 可以绘制 Shop 主界面内容
            info_surface = self.font.render("Welcome to the Shop!", True, (200, 200, 255))
            screen.blit(info_surface, (SCREEN_WIDTH // 2 - info_surface.get_width() // 2, SCREEN_HEIGHT // 2))

        # 啤酒淡入淡出 + 摇晃动画
        if self.beer_state is not None:
            temp = self.beer_img.copy()
            temp.set_alpha(int(self.beer_alpha))

            cx = SCREEN_WIDTH // 2 + getattr(self, "beer_shake_offset", 0)
            cy = SCREEN_HEIGHT // 2 + getattr(self, "beer_float_offset", 0)

            rect = temp.get_rect(center=(cx, cy))
            screen.blit(temp, rect)
