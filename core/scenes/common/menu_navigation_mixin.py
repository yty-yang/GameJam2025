import pygame
from pathlib import Path
from core.sound import sound_manager


def confirm_pressed(events):
    """检查回车/手柄按钮是否按下"""
    for event in events:
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (
                event.type == pygame.JOYBUTTONDOWN and event.button == 0):


            return True
    return False


class MenuNavigationMixin:
    """
    给有 options 和 selected_index 的 Scene 提供通用的菜单导航功能。
    没有 options 的 Scene 调用不会报错，自动跳过。
    """

    OPTION_SOUND_KEY = "option_voice"

    def _ensure_option_sound_loaded(self):
        """懒加载选项切换音效（如果存在则通过 sound_manager 加载）。"""
        # 如果已经加载或正在加载，直接返回
        if self.OPTION_SOUND_KEY in sound_manager.sounds:
            return
        try:
            project_root = Path(__file__).resolve().parents[3]
            option_path = project_root / "data" / "sounds" / "option_voice.mp3"
            if option_path.exists():
                sound_manager.load_sound(self.OPTION_SOUND_KEY, str(option_path))
        except Exception:
            # 安全失败：不阻塞菜单逻辑
            pass

    def _play_option_sound(self):
        try:
            self._ensure_option_sound_loaded()
            sound_manager.play_sound(self.OPTION_SOUND_KEY)
        except Exception:
            pass

    def _handle_common_navigation(self, events):
        # 如果这个 Scene 没有选项，不处理
        if not hasattr(self, "options") or not hasattr(self, "selected_index"):
            return

        # 记录变化前的索引，用于判断是否播放音效
        old_index = self.selected_index

        # === 摇杆 ===
        if hasattr(self, "joystick") and self.joystick:
            ly = self.joystick.get_axis(1)

            if ly < -0.5 and not hasattr(self, "_joy_up"):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                self._joy_up = True

            elif ly > 0.5 and not hasattr(self, "_joy_down"):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                self._joy_down = True

            elif -0.3 < ly < 0.3:
                # 松开时允许再次触发
                if hasattr(self, "_joy_up"):
                    delattr(self, "_joy_up")
                if hasattr(self, "_joy_down"):
                    delattr(self, "_joy_down")

        # === 键盘上下 ===
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)

        # 如果索引变化，播放选项切换音效
        if self.selected_index != old_index:
            self._play_option_sound()
