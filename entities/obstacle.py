import pygame
import math
from utils.settings import BALL_RADIUS, HOLE_RADIUS


class MovingPlatform:
    """移动平台障碍物"""
    def __init__(self, x, y, width=100, height=10, speed=50, direction=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed  # 移动速度
        self.direction = direction  # 1 向右，-1 向左
        self.start_x = x
        self.range = 200  # 移动范围


    def update(self, dt):
        """更新移动平台位置"""
        self.x += self.speed * self.direction * dt
        
        # 到达边界时反转方向
        if self.x > self.start_x + self.range:
            self.direction = -1
        elif self.x < self.start_x:
            self.direction = 1


    def check_collision(self, ball):
        """检查与小球碰撞"""
        # 简单的矩形碰撞检测
        ball_left = ball.x - BALL_RADIUS
        ball_right = ball.x + BALL_RADIUS
        ball_top = ball.y - BALL_RADIUS
        ball_bottom = ball.y + BALL_RADIUS
        
        platform_left = self.x - self.width / 2
        platform_right = self.x + self.width / 2
        platform_top = self.y - self.height / 2
        platform_bottom = self.y + self.height / 2
        
        return (ball_right > platform_left and 
                ball_left < platform_right and
                ball_bottom > platform_top and
                ball_top < platform_bottom)


    def draw(self, screen, camera):
        """绘制移动平台"""
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        
        # 绘制平台主体（复古像素风格）
        rect = pygame.Rect(
            int(screen_x - self.width / 2),
            int(screen_y - self.height / 2),
            int(self.width),
            int(self.height)
        )
        pygame.draw.rect(screen, (150, 150, 150), rect)
        pygame.draw.rect(screen, (100, 100, 100), rect, 2)
        
        # 添加像素风格的细节
        for i in range(0, int(self.width), 10):
            pygame.draw.line(
                screen,
                (120, 120, 120),
                (int(screen_x - self.width / 2 + i), int(screen_y - self.height / 2)),
                (int(screen_x - self.width / 2 + i), int(screen_y + self.height / 2)),
                1
            )


class Spring:
    """弹簧障碍物（弹跳板）"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 15
        self.compressed = False
        self.compression_time = 0.0
        self.bounce_power = 15.0  # 弹跳力度


    def update(self, dt):
        """更新弹簧状态"""
        if self.compressed:
            self.compression_time += dt
            if self.compression_time > 0.1:  # 压缩后释放
                self.compressed = False
                self.compression_time = 0.0


    def check_collision(self, ball):
        """检查碰撞并返回是否应该弹跳"""
        ball_left = ball.x - BALL_RADIUS
        ball_right = ball.x + BALL_RADIUS
        ball_top = ball.y - BALL_RADIUS
        ball_bottom = ball.y + BALL_RADIUS
        
        spring_left = self.x - self.width / 2
        spring_right = self.x + self.width / 2
        spring_top = self.y - self.height / 2
        spring_bottom = self.y + self.height / 2
        
        if (ball_right > spring_left and 
            ball_left < spring_right and
            ball_bottom > spring_top and
            ball_top < spring_bottom):
            if not self.compressed:
                self.compressed = True
                return True
        return False


    def draw(self, screen, camera):
        """绘制弹簧"""
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        
        # 根据压缩状态调整高度
        draw_height = self.height * (0.5 if self.compressed else 1.0)
        
        # 绘制弹簧主体（像素风格）
        rect = pygame.Rect(
            int(screen_x - self.width / 2),
            int(screen_y - draw_height / 2),
            int(self.width),
            int(draw_height)
        )
        pygame.draw.rect(screen, (200, 100, 50), rect)
        pygame.draw.rect(screen, (150, 75, 25), rect, 2)
        
        # 绘制弹簧线圈（像素风格）
        coil_count = 5
        for i in range(coil_count):
            coil_x = screen_x - self.width / 2 + (self.width / coil_count) * i
            pygame.draw.line(
                screen,
                (100, 50, 25),
                (int(coil_x), int(screen_y - draw_height / 2)),
                (int(coil_x), int(screen_y + draw_height / 2)),
                2
            )


class Teleporter:
    """传送门"""
    # 不同传送门对的颜色列表（用于视觉区分）
    PAIR_COLORS = [
        ((150, 0, 255), (100, 0, 150), (200, 100, 255)),  # 紫色系
        ((0, 255, 150), (0, 150, 100), (100, 255, 200)),  # 绿色系
        ((255, 150, 0), (200, 100, 0), (255, 200, 100)),  # 橙色系
        ((0, 150, 255), (0, 100, 200), (100, 200, 255)),  # 蓝色系
    ]
    
    def __init__(self, x, y, target_x, target_y, pair_id=0, pair_teleporter=None):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.radius = HOLE_RADIUS
        self.animation_time = 0.0
        self.pair_id = pair_id  # 配对ID，用于颜色区分
        self.pair_teleporter = pair_teleporter  # 配对传送门的引用


    def update(self, dt):
        """更新动画"""
        self.animation_time += dt * 3.0

    def check_collision(self, ball):
        """检查碰撞并返回传送目标位置"""
        # 如果小球还在传送冷却时间内，不触发传送
        if hasattr(ball, 'teleport_cooldown') and ball.teleport_cooldown > 0:
            return None
        
        distance = math.hypot(self.x - ball.x, self.y - ball.y)
        if distance <= self.radius + BALL_RADIUS:
            return (self.target_x, self.target_y)
        return None


    def draw(self, screen, camera):
        """绘制传送门"""
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        
        # 根据配对ID选择颜色
        color_index = self.pair_id % len(self.PAIR_COLORS)
        outer_color, inner_color, accent_color = self.PAIR_COLORS[color_index]
        
        # 脉冲效果
        pulse_radius = self.radius + math.sin(self.animation_time) * 5
        
        # 外圈（根据配对ID选择颜色）
        pygame.draw.circle(screen, outer_color, (int(screen_x), int(screen_y)), int(pulse_radius), 3)
        
        # 内圈
        pygame.draw.circle(screen, inner_color, (int(screen_x), int(screen_y)), int(self.radius))
        
        # 旋转效果（像素风格）
        for i in range(8):
            angle = self.animation_time + (i * math.pi / 4)
            start_x = screen_x + math.cos(angle) * self.radius * 0.7
            start_y = screen_y + math.sin(angle) * self.radius * 0.7
            end_x = screen_x + math.cos(angle) * self.radius
            end_y = screen_y + math.sin(angle) * self.radius
            pygame.draw.line(screen, accent_color, 
                           (int(start_x), int(start_y)), 
                           (int(end_x), int(end_y)), 2)
        
        # 绘制内部箭头指示传送方向（复古像素风格）
        target_screen_x, target_screen_y = camera.world_to_screen(self.target_x, self.target_y)
        
        # 计算方向角度
        dx = target_screen_x - screen_x
        dy = target_screen_y - screen_y
        if dx != 0 or dy != 0:
            direction_angle = math.atan2(dy, dx)
            
            # 箭头动画：脉冲效果（大小变化）
            arrow_pulse = 1.0 + math.sin(self.animation_time * 2.0) * 0.3
            arrow_size = 8 * arrow_pulse  # 基础大小8像素，带脉冲
            
            # 箭头位置：稍微偏离中心，指向目标方向
            arrow_offset = self.radius * 0.3  # 箭头距离中心的距离
            arrow_center_x = screen_x + math.cos(direction_angle) * arrow_offset
            arrow_center_y = screen_y + math.sin(direction_angle) * arrow_offset
            
            # 箭头动画：轻微前后移动（模拟流动效果）
            flow_offset = math.sin(self.animation_time * 3.0) * 2.0
            arrow_tip_x = arrow_center_x + math.cos(direction_angle) * (arrow_size + flow_offset)
            arrow_tip_y = arrow_center_y + math.sin(direction_angle) * (arrow_size + flow_offset)
            
            # 箭头两翼的位置（复古像素风格，使用较小的角度）
            wing_angle = math.pi / 5  # 约36度，复古风格
            wing_length = arrow_size * 0.7
            
            arrow_left_x = arrow_tip_x - wing_length * math.cos(direction_angle - wing_angle)
            arrow_left_y = arrow_tip_y - wing_length * math.sin(direction_angle - wing_angle)
            arrow_right_x = arrow_tip_x - wing_length * math.cos(direction_angle + wing_angle)
            arrow_right_y = arrow_tip_y - wing_length * math.sin(direction_angle + wing_angle)
            
            # 箭头尾部中心点
            tail_x = arrow_center_x - math.cos(direction_angle) * arrow_size * 0.3
            tail_y = arrow_center_y - math.sin(direction_angle) * arrow_size * 0.3
            
            # 绘制箭头（像素风格，使用较亮的颜色）
            arrow_color = (min(255, accent_color[0] + 50), 
                          min(255, accent_color[1] + 50), 
                          min(255, accent_color[2] + 50))
            
            # 绘制箭头主体（三角形）
            pygame.draw.polygon(screen, arrow_color, [
                (int(arrow_tip_x), int(arrow_tip_y)),
                (int(arrow_left_x), int(arrow_left_y)),
                (int(tail_x), int(tail_y)),
                (int(arrow_right_x), int(arrow_right_y))
            ])
            
            # 绘制箭头边框（像素风格，更粗的边框）
            pygame.draw.polygon(screen, (255, 255, 255), [
                (int(arrow_tip_x), int(arrow_tip_y)),
                (int(arrow_left_x), int(arrow_left_y)),
                (int(tail_x), int(tail_y)),
                (int(arrow_right_x), int(arrow_right_y))
            ], 1)
            
            # 添加像素风格的内部高光
            highlight_x = arrow_tip_x - math.cos(direction_angle) * arrow_size * 0.3
            highlight_y = arrow_tip_y - math.sin(direction_angle) * arrow_size * 0.3
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(highlight_x), int(highlight_y)), 2)

