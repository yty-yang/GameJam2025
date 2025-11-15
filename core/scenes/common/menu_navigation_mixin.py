import pygame


def confirm_pressed(events):
    """检查回车/手柄按钮是否按下"""
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:

            return True
        if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
            return True
    return False


class MenuNavigationMixin:
    """
    给有 options 和 selected_index 的 Scene 提供通用的菜单导航功能。
    没有 options 的 Scene 调用不会报错，自动跳过。
    """

    def _handle_common_navigation(self, events):
        # 如果这个 Scene 没有选项，不处理
        if not hasattr(self, "options") or not hasattr(self, "selected_index"):
            return

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

