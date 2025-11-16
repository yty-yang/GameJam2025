from pathlib import Path

import pygame

from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, GAME_HEIGHT


class GameMachineMixin:
    def __init__(self):
        super().__init__()

        # 背景色
        self.background_color = (30, 30, 30)

        # 加载游戏机背景图片（动画序列）
        project_root = Path(__file__).resolve().parents[3]
        game_machine_dir = project_root / "data" / "pictures" / "game_machine"

        self.game_machine_frames = []
        self.animation_frame = 0.0
        self.animation_speed = 0.15  # 动画速度（每帧增加的帧数）

        try:
            # 加载所有动画帧（0-8）
            for i in range(9):
                frame_path = game_machine_dir / f"game_machine-{i}.png"

                frame = pygame.image.load(str(frame_path)).convert_alpha()

                # 缩放背景到屏幕大小
                frame = pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.game_machine_frames.append(frame)

            if len(self.game_machine_frames) == 0:
                # 如果没有找到动画帧，尝试加载单个图片作为后备
                game_machine_path = project_root / "data" / "pictures" / "game_machine.png"
                if game_machine_path.exists():
                    self.game_machine_bg = pygame.image.load(str(game_machine_path)).convert_alpha()
                    self.game_machine_bg = pygame.transform.scale(self.game_machine_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.game_machine_frames = None
                else:
                    self.game_machine_bg = None
                    self.game_machine_frames = None
            else:
                self.game_machine_bg = None  # 使用动画帧时不需要单个背景
                print(f"成功加载 {len(self.game_machine_frames)} 帧游戏机背景动画")

            # 游戏区域：1:1 正方形，左右居中，上下贴顶
            # 游戏区域宽度等于高度（正方形），不被缩放
            self.game_area_width = GAME_WIDTH  # 1:1 正方形，所以宽度 = 高度
            self.game_area_height = GAME_HEIGHT

            # 水平居中
            self.game_area_x = (SCREEN_WIDTH - self.game_area_width) // 2
            # 上下贴顶
            self.game_area_y = 0

        except Exception as e:
            print(f"无法加载游戏机背景图片: {e}")
            self.game_machine_bg = None
            self.game_machine_frames = None

    def _update_game_machine_animation(self, dt):
        # 更新游戏机背景动画帧
        if hasattr(self, 'game_machine_frames') and self.game_machine_frames:
            self.animation_frame += self.animation_speed * dt * 60  # 假设60fps
            # 循环播放（0-8，共9帧）
            if self.animation_frame >= len(self.game_machine_frames):
                self.animation_frame = 0.0

    def _draw_with_bg(self, screen):
        # 如果加载了游戏机背景动画，使用游戏机屏幕效果
        if hasattr(self, 'game_machine_frames') and self.game_machine_frames:
            # 获取当前动画帧
            current_frame_index = int(self.animation_frame) % len(self.game_machine_frames)
            current_bg = self.game_machine_frames[current_frame_index]
        elif self.game_machine_bg:
            # 使用单个背景图片（后备方案）
            current_bg = self.game_machine_bg
        else:
            current_bg = None

        if current_bg:
            # 创建游戏内容surface（1:1 正方形）
            game_surface = pygame.Surface((self.game_area_width, self.game_area_height))
            game_surface.fill(self.background_color)

            self._draw_surface(game_surface)

            # 将游戏机背景绘制到主屏幕（使用当前动画帧）
            screen.blit(current_bg, (0, 0))

            # 将游戏内容surface直接绘制到游戏区域（不缩放，保持 1:1 比例)
            screen.blit(game_surface, (self.game_area_x, self.game_area_y))
        else:
            self._draw_surface(screen)