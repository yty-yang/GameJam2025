import random

import pygame

from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_STATE


class UI:
    def __init__(self, font_size=26):
        pygame.font.init()
        # 使用像素风格字体（如果系统有的话）
        try:
            self.font = pygame.font.Font(None, font_size)
        except:
            self.font = pygame.font.SysFont("Courier", font_size)

        self.crt_time = 0.0
        self.scanline_offset = 0

    def _draw_text(self, screen, text, x, y, color=(255, 255, 255)):
        surface = self.font.render(text, True, color)
        screen.blit(surface, (x, y))

    # 增强的扫描线效果（带轻微移动）
    def _scanlines(self, screen, spacing=3, intensity=0.15):
        self.scanline_offset += 0.5
        if self.scanline_offset >= spacing:
            self.scanline_offset = 0

        for y in range(0, SCREEN_HEIGHT, spacing):
            # 创建半透明黑色扫描线
            scanline_y = int(y + self.scanline_offset)
            if 0 <= scanline_y < SCREEN_HEIGHT:
                alpha = int(255 * intensity)
                scanline_surface = pygame.Surface((SCREEN_WIDTH, 1))
                scanline_surface.set_alpha(alpha)
                scanline_surface.fill((0, 0, 0))
                screen.blit(scanline_surface, (0, scanline_y))

    # CRT边缘弯曲效果（优化版）
    def _crt_curvature(self, screen):
        # 创建边缘渐暗效果（使用更高效的方法）
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # 只在边缘区域绘制渐暗效果
        fade_width = int(SCREEN_WIDTH * 0.3)
        for x in range(fade_width):
            fade = 1 - (x / fade_width)
            alpha = int(fade * 30)
            pygame.draw.line(overlay, (0, 0, 0, alpha), (x, 0), (x, SCREEN_HEIGHT))
            pygame.draw.line(overlay, (0, 0, 0, alpha), (SCREEN_WIDTH - x - 1, 0),
                             (SCREEN_WIDTH - x - 1, SCREEN_HEIGHT))

        screen.blit(overlay, (0, 0))

    # CRT色差效果（RGB分离）
    # TODO: 加了这个就非常卡
    def _chromatic_aberration(self, screen, intensity=1):
        if intensity <= 0:
            return screen

        # 创建RGB分离效果
        r_channel = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        g_channel = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        b_channel = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # 提取RGB通道
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                color = screen.get_at((x, y))
                r_channel.set_at((x, y), (color[0], 0, 0))
                g_channel.set_at((x, y), (0, color[1], 0))
                b_channel.set_at((x, y), (0, 0, color[2]))

        # 创建最终表面
        result = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        result.fill((0, 0, 0))

        # 轻微偏移RGB通道
        offset = int(intensity)
        result.blit(r_channel, (-offset, 0))
        result.blit(g_channel, (0, 0))
        result.blit(b_channel, (offset, 0))

        return result

    # 坏死横线 glitch（增强版）
    def _glitch_lines(self, screen, chance=0.01):
        if random.random() < chance:
            y = random.randint(0, SCREEN_HEIGHT)
            height = random.randint(2, 8)
            # 随机颜色（模拟CRT故障）
            glitch_color = random.choice([
                (0, 0, 0),
                (255, 0, 0),
                (0, 255, 0),
                (255, 255, 0)
            ])
            pygame.draw.rect(screen, glitch_color, (0, y, SCREEN_WIDTH, height))

            # 偶尔添加水平偏移（模拟信号干扰）
            if random.random() < 0.3:
                offset = random.randint(-5, 5)
                if offset != 0:
                    # 使用copy而不是subsurface来避免锁定问题
                    try:
                        glitch_rect = pygame.Rect(0, y, SCREEN_WIDTH, height)
                        glitch_surface = screen.subsurface(glitch_rect).copy()
                        screen.blit(glitch_surface, (offset, y))
                    except:
                        # 如果subsurface失败，就跳过这个效果
                        pass

    # 像素化效果（可选）
    # TODO: 效果不是很明显，但是不一定要非常明显也
    def _pixelation(self, screen, pixel_size=2):
        if pixel_size <= 1:
            return screen

        small_screen = pygame.transform.scale(
            screen,
            (SCREEN_WIDTH // pixel_size, SCREEN_HEIGHT // pixel_size)
        )
        return pygame.transform.scale(small_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def apply_effects(self, screen):
        self._scanlines(screen)
        self._crt_curvature(screen)
        self._glitch_lines(screen)
        # TODO: 像素化效果可选
        self._pixelation(screen)

    def game_ui(self, screen, score, coins=0, progress=0.0):
        self.apply_effects(screen)

        # 更新CRT时间
        self.crt_time += 0.016  # 假设60fps

        # 左上角显示分数（像素风格）
        self._draw_text(screen, f"SCORE: {score:06d}", 20, 20, (255, 255, 0))

        # 显示金币数
        if coins > 0:
            self._draw_text(screen, f"COINS: {coins}", 20, 50, (255, 215, 0))

        # 绘制进度条
        if progress > 0:
            self.draw_progress_bar(screen, progress)

    def draw_progress_bar(self, screen, progress):
        """绘制进度条（复古像素风格）"""
        # 进度条位置和大小
        bar_x = SCREEN_WIDTH // 2 - 150
        bar_y = SCREEN_HEIGHT - 40
        bar_width = 300
        bar_height = 20

        # 限制进度在0-1之间
        progress = max(0.0, min(1.0, progress))

        # 绘制背景框
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)

        # 绘制进度条（绿色渐变）
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            # 主进度条（绿色）
            pygame.draw.rect(screen, (0, 255, 0), (bar_x + 2, bar_y + 2, progress_width - 4, bar_height - 4))

            # 高光效果（像素风格）
            highlight_height = (bar_height - 4) // 2
            pygame.draw.rect(screen, (100, 255, 100),
                             (bar_x + 2, bar_y + 2, progress_width - 4, highlight_height))

        # 绘制百分比文字
        percent_text = f"{int(progress * 100)}%"
        try:
            font = pygame.font.SysFont("Courier", 16)
            text = font.render(percent_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
            screen.blit(text, text_rect)
        except:
            pass

    def menu_ui(self, screen):
        self.apply_effects(screen)

        # 绘制 GAME_STATE 信息
        state_color = (100, 255, 100)  # 柔和一点的绿色，不要太刺眼

        state_texts = [
            f"PASS COUNT: {GAME_STATE['pass_count']}",
            f"PLAY COUNT: {GAME_STATE['play_count']}",
            f"HIGHEST SCORE: {GAME_STATE['highest_score']}",
            f"COINS: {GAME_STATE['coins']}"
        ]

        # 行间距更紧凑
        base_x = 40
        base_y = 40
        line_height = 28

        for i, text in enumerate(state_texts):
            text_surface = self.font.render(text, True, state_color)
            screen.blit(text_surface, (base_x, base_y + i * line_height))

        # ----------- 右上角显示 Beer 数量 -----------
        beer_text = f"BEER: {GAME_STATE['beer']}"
        text_surface = self.font.render(beer_text, True, (255, 180, 50))  # 金黄色
        text_rect = text_surface.get_rect(topright=(SCREEN_WIDTH - 40, 40))  # 右上角
        screen.blit(text_surface, text_rect)
