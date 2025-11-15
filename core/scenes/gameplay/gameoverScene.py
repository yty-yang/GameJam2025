import pygame

from core.scenes.scene import Scene
from core.sound import sound_manager
from core.ui import UI
from utils.settings import GAME_STATE


# TODO: endless和level分开写，level要复杂一些
class GameoverScene(Scene):
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
        pass

    def draw(self, screen):
        # 复古背景
        screen.fill((20, 20, 20))

        ui = UI()
        # 应用CRT效果
        ui.apply_effects(screen)

        # 获取游戏统计数据
        score = GAME_STATE.get("score", 0)
        coins = GAME_STATE.get("coins", 0)
        victory = GAME_STATE.get("victory", False)
        endless = GAME_STATE.get("endless", False)

        if endless:
            lines = [
                "ENDLESS MODE",
                "",
                f"FINAL SCORE: {score:06d}",
                f"COINS COLLECTED: {coins}",
                "",
                f"HIGHEST SCORE: {GAME_STATE.get('highest_score', 0):06d}",
                "",
                "PRESS ESC OR ENTER",
                "TO RETURN TO MENU"
            ]
        else:
            if victory:
                lines = [
                    "VICTORY!",
                    "",
                    f"FINAL SCORE: {score:06d}",
                    f"COINS COLLECTED: {coins}",
                    "",
                    "YOU REACHED THE FINISH LINE!",
                    "",
                    "PRESS ESC OR ENTER",
                    "TO RETURN TO MENU"
                ]
            else:
                lines = [
                    "GAME OVER",
                    "",
                    f"FINAL SCORE: {score:06d}",
                    f"COINS COLLECTED: {coins}",
                    "",
                    "PRESS ESC OR ENTER",
                    "TO RETURN TO MENU"
                ]

        line_height = 50
        total_height = len(lines) * line_height
        start_y = (screen.get_height() - total_height) // 2

        for i, line in enumerate(lines):
            if line == "":
                continue
            # 使用不同字体大小
            if i == 0:  # GAME OVER 或 VICTORY
                font = self.font
                color = (0, 255, 0) if victory else (255, 0, 0)
            elif "FINAL SCORE" in line:
                font = self.small_font
                color = (255, 255, 0)
            elif "COINS" in line:
                font = self.small_font
                color = (255, 215, 0)
            else:
                font = self.small_font
                color = (200, 200, 200)

            text = font.render(line, True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, start_y + i * line_height))
            screen.blit(text, rect)
