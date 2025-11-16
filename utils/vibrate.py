import sys
import random

import pygame

# Windows 平台尝试导入 XInput
if sys.platform.startswith("win"):
    try:
        import XInput  # XInput-Python
        XINPUT_AVAILABLE = True
    except ImportError:
        XINPUT_AVAILABLE = False
else:
    XINPUT_AVAILABLE = False


class GameController:
    def __init__(self, joystick=None, player_index=0):
        """
        joystick: pygame.joystick.Joystick 对象
        player_index: XInput 玩家索引 0~3
        """
        self.joystick = joystick
        self.player_index = player_index
        self.platform = sys.platform

    def rumble(self, strength=1.0, duration_ms=500):
        """
        strength: 0.0~1.0
        duration_ms: 震动持续时间（毫秒）
        """
        # Windows + XInput
        if self.platform.startswith("win") and XINPUT_AVAILABLE:
            try:
                # XInput 强震动/弱震动取值 0~65535
                force = int(strength * 65535)
                XInput.set_vibration(self.player_index, force, force)
                pygame.time.set_timer(pygame.USEREVENT + 1, duration_ms)
            except Exception as e:
                print("XInput 震动失败:", e)

        # 其他平台，用 pygame 震动
        elif self.joystick and hasattr(self.joystick, "rumble"):
            try:
                self.joystick.rumble(strength, strength, duration_ms)
            except Exception as e:
                print("pygame 震动失败:", e)

    def stop_rumble(self):
        if self.platform.startswith("win") and XINPUT_AVAILABLE:
            try:
                XInput.set_vibration(self.player_index, 0, 0)
            except:
                pass
        elif self.joystick and hasattr(self.joystick, "rumble"):
            try:
                self.joystick.rumble(0, 0, 0)
            except:
                pass

    def get_shake_offset(self, shake_timer):
        """
        返回随机抖动偏移，同时触发震动
        shake_timer: int
        """
        if shake_timer > 0:
            # 震动强度随时间递减
            strength = min(shake_timer / 20.0, 1.0)
            self.rumble(strength, 200)  # 震动 200ms
            return random.randint(-2, 2), random.randint(-2, 2)
        return 0, 0