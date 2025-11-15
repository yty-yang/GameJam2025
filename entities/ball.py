import math

import pygame

from utils.settings import BALL_RADIUS, TILT_SENSITIVITY, GRAVITY, GAME_WIDTH


class Ball:
    def __init__(self, bounce, x, y=100, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.bounce = bounce

        # 滚入动画相关属性
        self.is_falling_into_hole = False
        self.fall_animation_progress = 0.0  # 0.0 到 1.0
        self.hole_target_x = 0
        self.hole_target_y = 0
        self.original_radius = BALL_RADIUS
        
        # 传送冷却时间（防止反复传送）
        self.teleport_cooldown = 0.0  # 冷却时间（秒）

    def _get_current_radius(self):
        """获取当前显示半径（动画时会缩小）"""
        if self.is_falling_into_hole:
            # 使用缓动函数让缩小更自然
            t = self.fall_animation_progress
            eased_t = t * t * t
            # 从原始半径缩小到0
            return self.original_radius * (1.0 - eased_t)
        return self.original_radius

    def update(self, platform, dt=0.0):
        # 如果正在滚入洞口，不执行物理更新
        if self.is_falling_into_hole:
            return

        # 更新传送冷却时间
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt

        # 重力
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # 边界反弹（左右）
        if self.x - BALL_RADIUS < 0:
            self.x = BALL_RADIUS
            self.vx = -self.vx * self.bounce
        elif self.x + BALL_RADIUS > GAME_WIDTH:
            self.x = GAME_WIDTH - BALL_RADIUS
            self.vx = -self.vx * self.bounce

        # ---- 平台方程： y = kx + b ----
        x1, y1 = 0, platform.y1
        x2, y2 = GAME_WIDTH, platform.y2

        dx = x2 - x1
        dy = y2 - y1

        if dx != 0:
            k = dy / dx
            b = y1  # 因为 x1 = 0，所以 b = y1

            # 小球脚下的地面高度
            y_ground = k * self.x + b

            # 小球从上方落到平台，增加一个小的epsilon防止卡住
            epsilon = 1e-3
            if self.vy > 0 and self.y + BALL_RADIUS >= y_ground - epsilon >= self.y - BALL_RADIUS:
                # 反弹：vy 反向乘以弹性系数
                self.vy = -self.vy * self.bounce
                # 落到平台表面
                self.y = y_ground - BALL_RADIUS
                # 若反弹速度过小，视作停止（防止无限抖动）
                if abs(self.vy) < 0.2:
                    self.vy = 0

                # 沿斜面加速度：g * sin(theta)
                angle = math.atan2(dy, dx)
                # 增加倾斜影响系数，让小球对倾斜更敏感
                tilt_sensitivity = TILT_SENSITIVITY  # 可以调整这个值：越大倾斜影响越快
                self.vx += GRAVITY * math.sin(angle) * tilt_sensitivity

    def collision_side(self):
        if self.x - BALL_RADIUS <= 0 or self.x + BALL_RADIUS >= GAME_WIDTH:
            return True
        return False

    def start_fall_animation(self, hole_x, hole_y):
        """开始滚入洞口的动画"""
        self.is_falling_into_hole = True
        self.fall_animation_progress = 0.0
        self.hole_target_x = hole_x
        self.hole_target_y = hole_y
        # 记录起始位置
        self._start_x = self.x
        self._start_y = self.y
        # 停止物理运动
        self.vx = 0
        self.vy = 0

    def update_fall_animation(self, dt):
        """更新滚入动画"""
        if self.is_falling_into_hole:
            # 动画进度增加（可以根据需要调整速度）
            self.fall_animation_progress += dt * 2.0  # 约0.5秒完成动画
            if self.fall_animation_progress > 1.0:
                self.fall_animation_progress = 1.0

            # 使用缓动函数（ease-in）让动画更自然
            # ease_in_cubic: t^3
            t = self.fall_animation_progress
            eased_t = t * t * t

            # 小球逐渐移动到洞口中心（使用线性插值，但用缓动函数控制速度）
            # 根据缓动进度插值
            self.x = self._start_x + (self.hole_target_x - self._start_x) * eased_t
            self.y = self._start_y + (self.hole_target_y - self._start_y) * eased_t

    def is_animation_complete(self):
        """检查动画是否完成"""
        return self.is_falling_into_hole and self.fall_animation_progress >= 1.0

    def draw(self, screen, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        current_radius = self._get_current_radius()

        if current_radius > 0:
            # 绘制小球主体
            pygame.draw.circle(screen, (50, 200, 50), (int(screen_x), int(screen_y)), int(current_radius))

            # 如果正在滚入，添加旋转效果（通过绘制一个高光点）
            if self.is_falling_into_hole:
                # 根据进度计算高光位置（模拟旋转）
                angle = self.fall_animation_progress * 10  # 旋转角度
                highlight_x = screen_x + math.cos(angle) * current_radius * 0.6
                highlight_y = screen_y + math.sin(angle) * current_radius * 0.6
                highlight_color = (100, 255, 100)
                pygame.draw.circle(screen, highlight_color, (int(highlight_x), int(highlight_y)),
                                   int(current_radius * 0.3))
            else:
                # 正常状态的高光
                highlight_x = screen_x - current_radius * 0.4
                highlight_y = screen_y - current_radius * 0.4
                highlight_color = (100, 255, 100)
                pygame.draw.circle(screen, highlight_color, (int(highlight_x), int(highlight_y)),
                                   int(current_radius * 0.3))
