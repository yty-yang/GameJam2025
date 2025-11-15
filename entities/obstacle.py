import pygame
import math
from utils.settings import BALL_RADIUS


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
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.radius = 25
        self.animation_time = 0.0


    def update(self, dt):
        """更新动画"""
        self.animation_time += dt * 3.0

    def check_collision(self, ball):
        """检查碰撞并返回传送目标位置"""
        distance = math.hypot(self.x - ball.x, self.y - ball.y)
        if distance <= self.radius + BALL_RADIUS:
            return (self.target_x, self.target_y)
        return None


    # TODO: 增加箭头指示传送方向
    def draw(self, screen, camera):
        """绘制传送门"""
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        
        # 脉冲效果
        pulse_radius = self.radius + math.sin(self.animation_time) * 5
        
        # 外圈（紫色，像素风格）
        pygame.draw.circle(screen, (150, 0, 255), (int(screen_x), int(screen_y)), int(pulse_radius), 3)
        
        # 内圈（深紫色）
        pygame.draw.circle(screen, (100, 0, 150), (int(screen_x), int(screen_y)), int(self.radius))
        
        # 旋转效果（像素风格）
        for i in range(8):
            angle = self.animation_time + (i * math.pi / 4)
            start_x = screen_x + math.cos(angle) * self.radius * 0.7
            start_y = screen_y + math.sin(angle) * self.radius * 0.7
            end_x = screen_x + math.cos(angle) * self.radius
            end_y = screen_y + math.sin(angle) * self.radius
            pygame.draw.line(screen, (200, 100, 255), 
                           (int(start_x), int(start_y)), 
                           (int(end_x), int(end_y)), 2)

