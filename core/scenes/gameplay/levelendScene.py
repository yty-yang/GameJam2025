import pygame
import math
from pathlib import Path

from core.scenes.scene import Scene
from core.scenes.common.menu_navigation_mixin import confirm_pressed


class LevelendScene(Scene):
    def __init__(self, win):
        super().__init__()
        self.win = win
        
        # 动画相关
        self.timer = 0.0
        self.fade_in_duration = 1.2  # 淡入持续时间
        self.rise_duration = 1.5  # 升起动画持续时间
        self.alpha = 0
        self.float_offset = 0.0
        self.glow_intensity = 0.0
        self.rise_progress = 0.0  # 升起进度（0到1）
        
        # 失败场景动画相关
        self.cat_slide_progress = 0.0  # 猫滑入进度
        self.beer_tilt_angle = 0.0  # 啤酒倾斜角度
        self.beer_spill_progress = 0.0  # 啤酒洒出进度
        self.cat_slide_duration = 1.5  # 猫滑入持续时间（增加时间让动画更明显）
        self.beer_spill_duration = 0.8  # 啤酒洒出持续时间
        self.beer_spill_delay = 0.5  # 啤酒洒出延迟（猫滑入后）

    def handle_events(self, events):
        if confirm_pressed(events):
            self.next_scene = "menu"
            return

    def update(self, dt):
        self.timer += dt
        
        # 淡入动画
        if self.timer < self.fade_in_duration:
            self.alpha = int(255 * (self.timer / self.fade_in_duration))
        else:
            self.alpha = 255
        
        # 升起动画（从右下角到中心）
        if self.timer < self.rise_duration:
            # 使用缓动函数，让动画更平滑
            progress = self.timer / self.rise_duration
            # 三次缓动（ease-out）
            self.rise_progress = 1 - (1 - progress) ** 3
        else:
            self.rise_progress = 1.0
            # 升起完成后才开始浮动效果
            self.float_offset = math.sin((self.timer - self.rise_duration) * 2.0) * 8  # 上下浮动 ±8px
        
        # 闪光效果（脉冲）
        self.glow_intensity = (math.sin(self.timer * 3.0) + 1) * 0.5  # 0 到 1
        
        # 失败场景动画
        if not self.win:
            # 猫滑入动画（延迟开始，让人物和啤酒先升起）
            cat_slide_start_delay = 0.3  # 延迟0.3秒后开始滑入
            if self.timer >= cat_slide_start_delay:
                elapsed = self.timer - cat_slide_start_delay
                if elapsed < self.cat_slide_duration:
                    progress = elapsed / self.cat_slide_duration
                    # 使用缓动函数（ease-out，开始快后面慢）
                    self.cat_slide_progress = 1 - (1 - progress) ** 3  # 三次缓动，更明显
                else:
                    self.cat_slide_progress = 1.0
            else:
                self.cat_slide_progress = 0.0
            
            # 啤酒洒出动画（延迟后开始，在猫滑入完成后）
            cat_slide_start_delay = 0.3
            spill_start_time = cat_slide_start_delay + self.cat_slide_duration + self.beer_spill_delay
            if self.timer >= spill_start_time:
                spill_elapsed = self.timer - spill_start_time
                if spill_elapsed < self.beer_spill_duration:
                    self.beer_spill_progress = spill_elapsed / self.beer_spill_duration
                    # 啤酒倾斜角度（从0到-30度）
                    self.beer_tilt_angle = -30 * (1 - (1 - self.beer_spill_progress) ** 2)
                else:
                    self.beer_spill_progress = 1.0
                    self.beer_tilt_angle = -30

    def draw(self, screen):
        # 获取项目根目录
        project_root = Path(__file__).resolve().parents[3]

        # 加载背景图并铺满屏幕
        bg_path = project_root / "data/pictures/level_end_background.png"
        background = pygame.image.load(str(bg_path)).convert_alpha()
        background = pygame.transform.scale(background, screen.get_size())
        screen.blit(background, (0, 0))

        # 根据胜负加载对应 bartender 图片
        if self.win:
            bartender_path = project_root / "data/pictures/characters/bartender_win.png"
        else:
            bartender_path = project_root / "data/pictures/characters/bartender_lose.png"

        bartender_img_original = pygame.image.load(str(bartender_path)).convert_alpha()
        # 放大人物：高度为屏幕高度的1/2（更大更醒目）
        sw, sh = screen.get_size()
        target_height = int(sh / 2)
        bw, bh = bartender_img_original.get_size()
        scale_ratio = target_height / bh
        target_width = int(bw * scale_ratio)
        bartender_img = pygame.transform.scale(bartender_img_original, (target_width, target_height))

        # 计算目标位置（居中，但向右偏移一些）
        bw, bh = bartender_img.get_size()
        target_x = (sw - bw) // 2 + 100  # 向右移动100像素
        target_y = (sh - bh) // 2
        
        # 计算起始位置（屏幕外右下角，完全在屏幕外面）
        start_x = sw  # 完全在屏幕右边外面
        start_y = sh  # 完全在屏幕底部外面
        
        # 根据升起进度计算当前位置
        current_x = start_x + (target_x - start_x) * self.rise_progress
        current_y = start_y + (target_y - start_y) * self.rise_progress
        
        # 应用浮动偏移（仅在升起完成后）
        if self.rise_progress >= 1.0:
            pos_x = int(current_x)
            pos_y = int(current_y + self.float_offset)
        else:
            pos_x = int(current_x)
            pos_y = int(current_y)
        
        # 绘制光晕效果（仅在胜利时且淡入完成后）
        if self.win and self.alpha >= 200:
            glow_radius = int(30 + self.glow_intensity * 20)  # 30-50 像素
            glow_alpha = int(80 + self.glow_intensity * 40)  # 80-120
            
            # 创建光晕表面
            glow_surface = pygame.Surface((bw + glow_radius * 2, bh + glow_radius * 2), pygame.SRCALPHA)
            glow_center_x = (bw + glow_radius * 2) // 2
            glow_center_y = (bh + glow_radius * 2) // 2
            
            # 绘制多层光晕（从外到内渐变）
            for i in range(glow_radius, 0, -2):
                alpha = int(glow_alpha * (i / glow_radius))
                color = (255, 255, 200, alpha)  # 淡黄色光晕
                pygame.draw.circle(glow_surface, color, 
                                 (glow_center_x, glow_center_y), i)
            
            # 绘制光晕到屏幕
            screen.blit(glow_surface, (pos_x - glow_radius, pos_y - glow_radius))
        
        # 失败场景：绘制猫和打翻的啤酒
        if not self.win and self.alpha >= 200:
            # 加载猫和啤酒图片
            cat_path = project_root / "data/pictures/characters/failure_cat.PNG"
            beer_path = project_root / "data/pictures/characters/spilled_beer.PNG"
            
            try:
                # 加载并缩放猫
                cat_img_original = pygame.image.load(str(cat_path)).convert_alpha()
                cat_height = int(bh * 0.8)  # 猫的高度是人物高度的60%
                cw, ch = cat_img_original.get_size()
                cat_scale = cat_height / ch
                cat_width = int(cw * cat_scale)
                cat_img = pygame.transform.scale(cat_img_original, (cat_width, cat_height))
                
                # 加载并缩放啤酒
                beer_img_original = pygame.image.load(str(beer_path)).convert_alpha()
                beer_height = int(bh * 0.4)  # 啤酒的高度是人物高度的40%
                bew, beh = beer_img_original.get_size()
                beer_scale = beer_height / beh
                beer_width = int(bew * beer_scale)
                beer_img = pygame.transform.scale(beer_img_original, (beer_width, beer_height))
                
                # 计算啤酒位置（人物左上，向右移动一些）
                beer_offset_x = -beer_width + 40  # 人物左边，但更靠近（向右移动）
                beer_offset_y = -beer_height // 2  # 人物上方中间
                beer_base_x = pos_x + beer_offset_x
                beer_base_y = pos_y + beer_offset_y
                
                # 计算猫的目标位置（基于人物和啤酒的最终位置）
                # 人物和啤酒的最终位置（中心位置，向右偏移）
                target_bartender_x = (sw - bw) // 2 + 100  # 与上面保持一致，向右移动100像素
                target_bartender_y = (sh - bh) // 2
                target_beer_x = target_bartender_x + beer_offset_x
                target_beer_y = target_bartender_y + beer_offset_y
                
                # 猫的目标位置（啤酒左边）
                cat_target_x = target_beer_x - cat_width + 10
                cat_target_y = target_bartender_y + (bh - cat_height) // 2
                
                # 猫从屏幕左侧滑入（从更远的地方开始，让动画更明显）
                cat_start_x = -cat_width - 300  # 从屏幕左边外面更远的地方开始（300像素外）
                cat_current_x = cat_start_x + (cat_target_x - cat_start_x) * self.cat_slide_progress
                cat_current_y = cat_target_y
                
                # 绘制猫（带淡入效果，从左侧滑入）
                cat_alpha = int(255 * min(1.0, self.cat_slide_progress * 1.5))
                cat_display = cat_img.copy()
                cat_display.set_alpha(cat_alpha)
                screen.blit(cat_display, (int(cat_current_x), int(cat_current_y)))
                
                # 绘制啤酒（带倾斜和洒出动画）
                if self.beer_spill_progress > 0:
                    # 旋转啤酒（打翻效果）
                    beer_rotated = pygame.transform.rotate(beer_img, self.beer_tilt_angle)
                    
                    # 计算旋转后的位置（保持左上角位置）
                    beer_rotated_x = beer_base_x
                    beer_rotated_y = beer_base_y + int(self.beer_spill_progress * 10)  # 稍微下移
                    
                    # 绘制啤酒
                    beer_alpha = int(255 * min(1.0, self.beer_spill_progress * 1.2))
                    beer_display = beer_rotated.copy()
                    beer_display.set_alpha(beer_alpha)
                    screen.blit(beer_display, (beer_rotated_x, beer_rotated_y))
                    
                    # 绘制洒出的啤酒粒子效果
                    if self.beer_spill_progress > 0.3:
                        particle_count = 8
                        for i in range(particle_count):
                            angle = math.pi / 2 + (i / particle_count - 0.5) * math.pi / 3  # 向下扇形
                            distance = 30 + self.beer_spill_progress * 40
                            particle_x = beer_rotated_x + beer_width // 2 + math.cos(angle) * distance
                            particle_y = beer_rotated_y + beer_height // 2 + math.sin(angle) * distance
                            
                            # 粒子大小和透明度
                            particle_size = int(3 + (1 - self.beer_spill_progress) * 2)
                            particle_alpha = int(200 * (1 - self.beer_spill_progress))
                            
                            # 绘制粒子（小圆点）
                            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
                            pygame.draw.circle(particle_surface, (255, 200, 0, particle_alpha),
                                             (particle_size, particle_size), particle_size)
                            screen.blit(particle_surface, 
                                      (int(particle_x - particle_size), int(particle_y - particle_size)))
                else:
                    # 啤酒还未洒出，正常显示
                    beer_display = beer_img.copy()
                    beer_display.set_alpha(int(255 * 0.7))  # 稍微透明
                    screen.blit(beer_display, (beer_base_x, beer_base_y))
                    
            except Exception as e:
                print(f"无法加载失败场景图片: {e}")
        
        # 设置透明度并绘制 bartender
        bartender_display = bartender_img.copy()
        bartender_display.set_alpha(self.alpha)
        screen.blit(bartender_display, (pos_x, pos_y))
        
        # 绘制闪光效果（仅在胜利时）
        if self.win and self.alpha >= 200:
            # 在人物周围绘制闪烁的星星/光点
            star_count = 8
            for i in range(star_count):
                angle = (self.timer * 2.0 + i * (2 * math.pi / star_count)) % (2 * math.pi)
                distance = 40 + math.sin(self.timer * 4.0 + i) * 10
                star_x = pos_x + bw // 2 + math.cos(angle) * distance
                star_y = pos_y + bh // 2 + math.sin(angle) * distance
                
                # 星星大小和透明度随闪光强度变化
                star_size = int(3 + self.glow_intensity * 3)
                star_alpha = int(150 + self.glow_intensity * 105)
                
                # 绘制星星（简单的十字形状）
                star_color = (255, 255, 200, star_alpha)
                star_surface = pygame.Surface((star_size * 2 + 1, star_size * 2 + 1), pygame.SRCALPHA)
                # 横线
                pygame.draw.line(star_surface, star_color, 
                               (0, star_size), (star_size * 2, star_size), 2)
                # 竖线
                pygame.draw.line(star_surface, star_color, 
                               (star_size, 0), (star_size, star_size * 2), 2)
                
                screen.blit(star_surface, (star_x - star_size, star_y - star_size))
