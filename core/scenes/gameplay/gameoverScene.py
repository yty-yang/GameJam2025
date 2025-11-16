import pygame

from core.scenes.common.game_machine_mixin import GameMachineMixin
from core.scenes.scene import Scene
from core.sound import sound_manager
from core.ui import UI
from utils.settings import GAME_STATE


class GameoverScene(Scene, GameMachineMixin):
    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 36)

        sound_manager.stop_sound("ball_roll")




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
        self._update_game_machine_animation(dt)

    def _draw_surface(self, screen):
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
        self._draw_with_bg(screen)
