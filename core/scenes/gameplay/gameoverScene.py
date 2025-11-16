from pathlib import Path

import pygame

from core.scenes.scene import Scene
from core.sound import sound_manager
from core.ui import UI
from utils.settings import GAME_STATE, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, GAME_HEIGHT


class GameoverScene(Scene):
    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 36)

        sound_manager.stop_sound("ball_roll")

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
                # 尝试两种文件名格式：game_machine-0.png 和 game_machine_0.png
                frame_path1 = game_machine_dir / f"game_machine-{i}.png"
                frame_path2 = game_machine_dir / f"game_machine_{i}.png"

                if frame_path1.exists():
                    frame = pygame.image.load(str(frame_path1)).convert_alpha()
                elif frame_path2.exists():
                    frame = pygame.image.load(str(frame_path2)).convert_alpha()
                else:
                    print(f"警告：找不到游戏机背景帧 {i}")
                    continue

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


    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    # 播放按回车音效
                    from core.sound import sound_manager
                    try:
                        if "press_enter" not in sound_manager.sounds:
                            from pathlib import Path
                            project_root = Path(__file__).resolve().parents[3]
                            press_enter_path = project_root / "data" / "sounds" / "press_enter.mp3"
                            if press_enter_path.exists():
                                sound_manager.load_sound("press_enter", str(press_enter_path))
                        
                        if "press_enter" in sound_manager.sounds:
                            sound_manager.play_sound("press_enter")
                    except Exception:
                        pass
                    self.next_scene = "menu"  # 按 ESC 或 ENTER 返回菜单
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                # 播放按回车音效
                from core.sound import sound_manager
                try:
                    if "press_enter" not in sound_manager.sounds:
                        from pathlib import Path
                        project_root = Path(__file__).resolve().parents[3]
                        press_enter_path = project_root / "data" / "sounds" / "press_enter.mp3"
                        if press_enter_path.exists():
                            sound_manager.load_sound("press_enter", str(press_enter_path))
                    
                    if "press_enter" in sound_manager.sounds:
                        sound_manager.play_sound("press_enter")
                except Exception:
                    pass
                self.next_scene = "menu"  # 按 ESC 或 ENTER 返回菜单

    def update(self, dt):
        pass

    def _draw_text(self, screen):
        # 复古背景
        screen.fill((20, 20, 20))

        ui = UI()
        ui.apply_effects(screen)

        # 获取游戏统计数据
        score = GAME_STATE.get("score", 0)
        coins = GAME_STATE.get("coins", 0)
        highest_score = GAME_STATE.get("highest_score", 0)

        lines = [
            "ENDLESS MODE",
            f"FINAL SCORE: {score:06d}",
            f"COINS COLLECTED: {coins}",
            f"HIGHEST SCORE: {highest_score:06d}",
        ]

        # 动态字体大小和间距，使内容放得下
        max_height = screen.get_height() * 0.8  # 占屏幕高度80%
        line_count = len(lines)
        line_height = min(50, max_height // line_count)  # 最大50，自动调整
        total_height = line_height * line_count
        start_y = (screen.get_height() - total_height) // 2

        for i, line in enumerate(lines):
            # 使用不同字体和颜色
            if i == 0:
                font = pygame.font.SysFont(None, int(line_height * 0.8))
                color = (255, 0, 0)
            elif "SCORE" in line:
                font = pygame.font.SysFont(None, int(line_height * 0.7))
                color = (255, 255, 0)
            elif "COINS" in line:
                font = pygame.font.SysFont(None, int(line_height * 0.7))
                color = (255, 215, 0)
            else:
                font = pygame.font.SysFont(None, int(line_height * 0.6))
                color = (200, 200, 200)

            text = font.render(line, True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, start_y + i * line_height))
            screen.blit(text, rect)

            hint_text = self.small_font.render("PRESS ESC OR ENTER TO RETURN", True, (150, 150, 200))
            hint_rect = hint_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
            screen.blit(hint_text, hint_rect)

    def draw(self, screen):
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

            self._draw_text(game_surface)

            # 将游戏机背景绘制到主屏幕（使用当前动画帧）
            screen.blit(current_bg, (0, 0))

            # 将游戏内容surface直接绘制到游戏区域（不缩放，保持 1:1 比例)
            screen.blit(game_surface, (self.game_area_x, self.game_area_y))
        else:
            self._draw_text(screen)
