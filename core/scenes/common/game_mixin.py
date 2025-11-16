import json

import random
import sys
from pathlib import Path

import pygame

from core.camera import Camera
from core.scenes.common.game_machine_mixin import GameMachineMixin
from core.scenes.scene import Scene
from core.sound import sound_manager
from core.ui import UI
from entities.ball import Ball
from entities.pauseMenu import PauseMenu
from entities.platform import Platform
from utils.settings import GAME_STATE, BALL_BOUNCE, SCREEN_HEIGHT, BALL_RADIUS, GAME_WIDTH, BEER_DURATION
from utils.helper import save_data


class GameMixin(Scene, GameMachineMixin):
    """
    Mixin for updating game objects like moving platforms, springs,
    teleporters, and coins. Scenes that have these objects can inherit this Mixin.
    """

    def __init__(self):
        super().__init__()

        # 初始化平台
        self.platform = Platform()

        # 初始化小球在平台上方
        self.ball = Ball(
            bounce=BALL_BOUNCE,
            x=GAME_WIDTH // 2,
            y=self.platform.y1 - BALL_RADIUS - 100
        )

        self.holes = []

        # 金币系统
        self.coins = []
        self.coins_collected = 0

        # 障碍物系统
        self.moving_platforms = []
        self.springs = []
        self.teleporters = []

        # 计分系统
        self.score = 0
        self.speed_bonus = 0
        self.start_y = self.ball.y  # 记录起始位置，用于计算进度
        self.last_distance = 0.0  # 上一次计算的距离，用于增量计算

        # 道具系统
        self.beer = False  # 是否使用啤酒道具
        self.beer_timer = 0.0  # 啤酒道具持续时间（秒）

        # 初始化摄像机
        self.camera = Camera(self.ball.x, self.ball.y)

        # 初始化暂停界面
        self.pauseMenu = PauseMenu()

        self.paused = False
        self.game_over = False
        self.shake_timer = 0

        # 渐变黑屏控制
        self.fade_out = False
        self.fade_alpha = 0
        self.fade_speed = 200

        project_root = Path(__file__).resolve().parents[3]
        # 预加载金币音效（如果存在）
        try:
            coin_sound_path = project_root / "data" / "sounds" / "eat_coins.mp3"
            if coin_sound_path.exists():
                # load_sound 接受文件路径字符串
                sound_manager.load_sound("eat_coins", str(coin_sound_path))
        except Exception as e:
            print(f"无法预加载金币音效: {e}")

        # 预加载弹簧音效
        try:
            spring_path = project_root / "data" / "sounds" / "spring.mp3"
            if spring_path.exists():
                sound_manager.load_sound("spring", str(spring_path))
        except Exception as e:
            print(f"无法预加载弹簧音效: {e}")
        
        # 预加载传送音效
        try:
            teleportation_path = project_root / "data" / "sounds" / "teleportation.mp3"
            if teleportation_path.exists():
                sound_manager.load_sound("teleportation", str(teleportation_path))
        except Exception as e:
            print(f"无法预加载传送音效: {e}")
        
        # 预加载小球滚动音效
        try:
            ball_roll_path = project_root / "data" / "sounds" / "ball_roll.mp3"
            if ball_roll_path.exists():
                sound_manager.load_sound("ball_roll", str(ball_roll_path))
        except Exception as e:
            print(f"无法预加载小球滚动音效: {e}")
        
        # 预加载游戏结束音效
        try:
            game_over_path = project_root / "data" / "sounds" / "game_over.mp3"
            if game_over_path.exists():
                sound_manager.load_sound("game_over", str(game_over_path))
        except Exception as e:
            print(f"无法预加载游戏结束音效: {e}")
        
        # 预加载胜利音效
        try:
            winning_path = project_root / "data" / "sounds" / "winning.mp3"
            if winning_path.exists():
                sound_manager.load_sound("winning", str(winning_path))
        except Exception as e:
            print(f"无法预加载胜利音效: {e}")
        
        # 预加载掉落音效
        try:
            falling_hole_path = project_root / "data" / "sounds" / "falling_hole.mp3"
            if falling_hole_path.exists():
                sound_manager.load_sound("falling_hole", str(falling_hole_path))
        except Exception as e:
            print(f"无法预加载掉落音效: {e}")
        
        # 滚动音效状态
        self.ball_rolling = False  # 小球是否正在滚动
        self.roll_sound_channel = None  # 滚动音效的播放通道
        self.last_platform_y1 = self.platform.y1
        self.last_platform_y2 = self.platform.y2
        
        # 掉落音效状态
        self.ball_falling = False  # 小球是否正在掉落
        self.falling_sound_channel = None  # 掉落音效的播放通道
        self.last_ball_y = self.ball.y  # 上一帧小球Y坐标，用于检测高度持续降低
        self.falling_sound_played = False  # 标记是否已经播放过掉落音效（避免重复播放）

        try:
            gameover_sound_path = project_root / "data" / "sounds" / "game_over.mp3"
            if gameover_sound_path.exists():
                # load_sound 接受文件路径字符串
                sound_manager.load_sound("game_over", str(gameover_sound_path))
        except Exception as e:
            print(f"无法预加载失败音效: {e}")


    def _update_game_func(self, dt):
        """更新移动平台、弹簧、传送门和金币"""
        # 实时增加分数（基于距离起点的位置）
        if not self.paused and not self.ball.is_falling_into_hole:
            # 计算向下移动的距离（游戏是向下进行的）
            # 使用Y坐标的差值：向下移动时，start_y > ball.y，所以是正数
            distance_traveled = self.start_y - self.ball.y

            # 只有当距离增加时才更新分数（避免后退时减少分数）
            if distance_traveled > self.last_distance:
                # 计算新增的距离
                distance_delta = distance_traveled - self.last_distance

                # 根据距离增加分数：每向下移动1像素 = 1分
                # 可以调整这个系数来改变分数增长速度
                score_increase = int(distance_delta / 10)

                if score_increase > 0:
                    self.score += score_increase
                    self.last_distance = distance_traveled

        """更新移动平台、弹簧、传送门和金币"""
        if hasattr(self, "moving_platforms"):
            for platform in self.moving_platforms:
                platform.update(dt)
                if platform.check_collision(self.ball):
                    # 小球撞到移动平台，轻微反弹
                    self.ball.vy = -abs(self.ball.vy) * 0.3
                    self.shake_timer = 10

        if hasattr(self, "springs"):
            for spring in self.springs:
                spring.update(dt)
                if spring.check_collision(self.ball):
                    # 播放弹簧音效
                    sound_manager.play_sound("spring")
                    
                    # 弹簧弹跳
                    self.ball.vy = -spring.bounce_power
                    self.shake_timer = 20

        if hasattr(self, "teleporters"):
            teleported = False  # 防止同一帧内多次传送
            for teleporter_pair in self.teleporters:
                if teleported:
                    break
                for teleporter in teleporter_pair:
                    teleporter.update(dt)
                    if not teleported:
                        tele_target = teleporter.check_collision(self.ball)
                        if tele_target:
                            # 播放传送音效
                            sound_manager.play_sound("teleportation")
                            
                            # 传送
                            self.ball.x, self.ball.y = tele_target
                            self.ball.vx *= 0.5
                            self.ball.vy *= 0.5
                            self.shake_timer = 30
                            # 设置传送冷却时间（0.5秒，防止立即传回）
                            self.ball.teleport_cooldown = 0.5
                            teleported = True
                            break  # 只传送一次，不删除传送门对，允许重复使用

        if hasattr(self, "coins"):
            for coin in self.coins:
                coin.update(dt)
                if coin.check_collision(self.ball) and not coin.collected:
                    coin.collect()
                    self.coins_collected += 1
                    self.score += 50
                    self.shake_timer = 10

    def _fall_into_hole_func(self):
        for hole in self.holes:
            if hole.check_collision(self.ball) and not self.ball.is_falling_into_hole:
                # 在开始动画前，确保最后一次距离计算完成
                distance_traveled = self.start_y - self.ball.y
                if distance_traveled > self.last_distance:
                    distance_delta = distance_traveled - self.last_distance
                    score_increase = int(distance_delta / 10)
                    if score_increase > 0:
                        self.score += score_increase
                        self.last_distance = distance_traveled

                self.ball.start_fall_animation(hole.x, hole.y)

                self.shake_timer = 50
                break

    def _get_shake_offset_func(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1

            # TODO: 震动太小了现在
            # 手柄震动
            if GAME_STATE.get("vibration", True) and hasattr(self, 'joystick') and self.joystick:
                # 震动强度根据剩余时间变化
                strength = min(1.0, self.shake_timer / 50.0)
                duration_ms = 100  # 每次震动持续100毫秒
                from utils.vibrate import GameController
                controller = GameController(joystick=self.joystick)
                controller.rumble(strength=strength, duration_ms=duration_ms)

            return random.randint(-2, 2), random.randint(-2, 2)
        return 0, 0
    
    def _update_roll_sound(self, dt):
        """更新滚动音效播放"""
        if "ball_roll" not in sound_manager.sounds:
            return
        
        roll_sound = sound_manager.sounds["ball_roll"]
        
        # 如果小球开始滚动且音效未播放，开始播放
        if self.ball_rolling and (self.roll_sound_channel is None or not self.roll_sound_channel.get_busy()):
            # 估算滚动持续时间（基于当前速度）
            # 如果速度很小，可能是短暂滚动，使用短循环
            # 如果速度较大，可能是长时间滚动，使用长循环
            speed = abs(self.ball.vx)
            
            # 播放音效，循环播放
            self.roll_sound_channel = roll_sound.play(loops=-1)  # -1 表示无限循环
            
        # 如果小球停止滚动，停止音效
        elif not self.ball_rolling and self.roll_sound_channel and self.roll_sound_channel.get_busy():
            # 停止音效（会有淡出效果）
            self.roll_sound_channel.fadeout(100)  # 100ms 淡出
            self.roll_sound_channel = None
    
    def _update_falling_sound(self, dt):
        """更新掉落音效播放"""
        if "falling_hole" not in sound_manager.sounds:
            return
        
        falling_sound = sound_manager.sounds["falling_hole"]
        
        # 如果小球开始掉落且音效未播放过，开始播放（只播放一次）
        if self.ball_falling and not self.falling_sound_played:
            # 播放掉落音效，只播放一次（不循环）
            self.falling_sound_channel = falling_sound.play(loops=0)
            self.falling_sound_played = True  # 标记已播放，避免重复播放
            
        # 如果小球停止掉落（回到平台或触发 game over），停止音效
        elif not self.ball_falling and self.falling_sound_channel and self.falling_sound_channel.get_busy():
            # 停止音效（会有淡出效果）
            self.falling_sound_channel.fadeout(200)  # 200ms 淡出
            self.falling_sound_channel = None

    # TODO: 弹簧音效
    def _update_spring_sound(self, dt):
        """更新弹簧音效播放"""
        if "spring" not in sound_manager.sounds:
            return


    def _handle_events_func(self, events):
        if not self.paused:
            """处理玩家输入，让平台上下移动"""
            # 记录平台移动前的状态
            keys = pygame.key.get_pressed()
            platform_moved = False
            if keys[pygame.K_w]:
                self.platform.move(True, False, True)
                platform_moved = True
            if keys[pygame.K_UP]:
                self.platform.move(False, True, True)
                platform_moved = True
            if keys[pygame.K_s]:
                self.platform.move(True, False, False)
                platform_moved = True
            if keys[pygame.K_DOWN]:
                self.platform.move(False, True, False)
                platform_moved = True
            if self.joystick:
                ly = self.joystick.get_axis(1)  # 左摇杆Y轴
                ry = self.joystick.get_axis(3)  # 右摇杆Y轴

                if ly < -0.2:  # 左摇杆上推
                    self.platform.move(True, False, True, speed_factor=min(1.0, -ly))
                    platform_moved = True
                if ry < -0.2:  # 右摇杆上推
                    self.platform.move(False, True, True, speed_factor=min(1.0, -ry))
                    platform_moved = True
                if ly > 0.2:  # 左摇杆下推
                    self.platform.move(True, False, False, speed_factor=min(1.0, ly))
                    platform_moved = True
                if ry > 0.2:  # 右摇杆下推
                    self.platform.move(False, True, False, speed_factor=min(1.0, ry))

            if platform_moved:
                self.ball.update(self.platform)

            # 处理按键功能
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    if event.key == pygame.K_SPACE:
                        if GAME_STATE["beer"] > 0 and not self.beer:
                            self.beer = True
                            self.beer_timer = BEER_DURATION
                            GAME_STATE["slow_time"] = True
                            GAME_STATE["beer"] -= 1
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.paused = not self.paused
                    if event.button == 2:  # X 键 → 使用啤酒道具
                        if GAME_STATE["beer"] > 0 and not self.beer:
                            self.beer = True
                            self.beer_timer = BEER_DURATION
                            GAME_STATE["slow_time"] = True
                            GAME_STATE["beer"] -= 1

        else:
            result = self.pauseMenu.handle_events(events)
            if result == "Resume":
                self.paused = False
            elif result == "Quit":
                self.next_scene = "menu"

    def _update_common_func(self, dt):
        # 更新游戏机背景动画帧
        self._update_game_machine_animation(dt)
        
        # 检测小球是否在滚动和掉落
        if not self.paused and not self.ball.is_falling_into_hole:
            # 检查小球是否在平台上
            x1, y1 = 0, self.platform.y1
            x2, y2 = GAME_WIDTH, self.platform.y2
            dx = x2 - x1
            dy = y2 - y1
            
            if dx != 0:
                k = dy / dx
                b = y1
                y_ground = k * self.ball.x + b
                on_platform = abs(self.ball.y + BALL_RADIUS - y_ground) < 5  # 在平台上5像素范围内
            else:
                on_platform = False
                y_ground = self.platform.y1
            
            # 小球在滚动：在平台上且有明显的水平速度
            was_rolling = self.ball_rolling
            self.ball_rolling = on_platform and abs(self.ball.vx) > 0.5
            
            # 检测小球是否在平台下方且高度持续降低
            # 小球在平台下方：小球底部在平台下方
            below_platform = (self.ball.y + BALL_RADIUS) > y_ground + 5
            # 高度持续降低：Y坐标持续增加（向下是正方向）或垂直速度向下
            height_decreasing = self.ball.y > self.last_ball_y or self.ball.vy > 0
            
            # 如果小球在平台下方且高度持续降低，开始/继续掉落
            if below_platform and height_decreasing:
                if not self.ball_falling:
                    self.ball_falling = True
                    self.falling_sound_played = False  # 重置播放标志，允许播放音效
            else:
                # 如果小球不在平台下方或高度不再降低，停止掉落
                if self.ball_falling:
                    self.ball_falling = False
                    self.falling_sound_played = False  # 重置播放标志
                    if self.falling_sound_channel and self.falling_sound_channel.get_busy():
                        self.falling_sound_channel.fadeout(200)
                        self.falling_sound_channel = None
            
            # 如果小球在掉落状态，继续检测
            if self.ball_falling:
                self.shake_timer = 40
                # 计算小球在屏幕上的Y坐标
                screen_x, screen_y = self.camera.world_to_screen(self.ball.x, self.ball.y)
                # 如果掉出屏幕下方，停止掉落音效（即将触发 game over）
                if screen_y > SCREEN_HEIGHT + 100:
                    self.ball_falling = False
                    if self.falling_sound_channel and self.falling_sound_channel.get_busy():
                        self.falling_sound_channel.stop()
                        self.falling_sound_channel = None
            
            # 更新上一帧的Y坐标
            self.last_ball_y = self.ball.y
            
            # 处理滚动音效
            self._update_roll_sound(dt)
            
            # 处理掉落音效
            self._update_falling_sound(dt)

            self._update_spring_sound(dt)
        
        if not self.paused:
            # 如果小球正在滚入洞口，更新动画
            if self.ball.is_falling_into_hole:
                # 开始播放掉落音效（如果还没播放）
                if not self.ball_falling:
                    self.ball_falling = True
                    self.falling_sound_played = False  # 重置播放标志
                    self._update_falling_sound(dt)
                
                self.ball.update_fall_animation(dt)
                # 动画完成后切换到游戏结束场景
                if self.ball.is_animation_complete():
                    # 停止掉落音效（在 game over 音效之前）
                    if self.falling_sound_channel and self.falling_sound_channel.get_busy():
                        self.falling_sound_channel.stop()
                        self.falling_sound_channel = None
                    self.ball_falling = False
                    self.falling_sound_played = False  # 重置播放标志
                    
                    # 播放 game over 音效
                    sound_manager.play_sound("game_over")
                    self._finish(False)
            else:
                self._update_entities(dt)
                
                # 检测小球是否掉出屏幕（掉到平台下方太远）
                # 计算小球在屏幕上的Y坐标
                screen_x, screen_y = self.camera.world_to_screen(self.ball.x, self.ball.y)
                
                # 如果小球掉到屏幕下方（超过屏幕高度 + 一定缓冲距离），触发 game over
                if screen_y > SCREEN_HEIGHT + 100:  # 掉出屏幕下方100像素后触发
                    # 停止掉落音效（在 game over 音效之前）
                    if self.falling_sound_channel and self.falling_sound_channel.get_busy():
                        self.falling_sound_channel.stop()
                        self.falling_sound_channel = None
                    self.ball_falling = False
                    self.falling_sound_played = False  # 重置播放标志
                    
                    # 播放 game over 音效
                    sound_manager.play_sound("game_over")
                    self._finish(False)

            if self.beer:
                GAME_STATE["slow_time"] = True
                self.beer_timer -= dt  # dt 是本帧经过的秒数
                self.shake_timer = 50
                if self.beer_timer <= 0:
                    self.beer = False
                    self.beer_timer = 0
                    GAME_STATE["slow_time"] = False

            # 游戏结束保存状态
            if self.game_over:
                GAME_STATE["slow_time"] = False
                if self.roll_sound_channel and self.roll_sound_channel.get_busy():
                    self.roll_sound_channel.fadeout(100)  # 100ms 淡出
                self.roll_sound_channel = None
                save_data()

        else:
            GAME_STATE["slow_time"] = False
            if self.roll_sound_channel and self.roll_sound_channel.get_busy():
                self.roll_sound_channel.fadeout(100)  # 100ms 淡出
            self.roll_sound_channel = None
            self.pauseMenu.update(dt)

    def _draw_surface(self, game_surface):
        # camera跟随ball
        self.camera.follow(self.ball.x, self.ball.y, target_screen_x=self.ball.x)

        # 绘制平台
        self.platform.draw(game_surface, self.camera)

        # 绘制终点线（在背景层）
        if hasattr(self, "finish_line"):
            self.finish_line.draw(game_surface, self.camera)

        # 绘制障碍物
        for platform in self.moving_platforms:
            platform.draw(game_surface, self.camera)
        for spring in self.springs:
            spring.draw(game_surface, self.camera)

        # 绘制传送门（内部已包含箭头指示）
        if hasattr(self, "teleporters"):
            for t_pair in self.teleporters:
                for teleporter in t_pair:
                    teleporter.draw(game_surface, self.camera)

        # 绘制金币
        for coin in self.coins:
            if not coin.collected:
                coin.draw(game_surface, self.camera)

        # 先绘制洞口（在底层）
        for hole in self.holes:
            hole.draw(game_surface, self.camera)
        # 再绘制小球（在上层，确保小球不会被洞口覆盖）
        self.ball.draw(game_surface, self.camera)

        # 计算进度（距离终点的进度）
        progress = self._compute_progress() if hasattr(self, "finish_line") else 0

        # 生命数绘制（右上角）
        if hasattr(self, "life"):
            heart_radius = 10  # 心形圆点半径
            spacing = 5  # 心形之间的间距
            total_width = self.life * (2 * heart_radius + spacing) - spacing
            start_x = GAME_WIDTH - 20 - total_width  # 右上角距离屏幕右边20像素
            start_y = 20  # 距离屏幕顶部20像素

            for i in range(self.life):
                pygame.draw.circle(
                    game_surface,
                    (255, 0, 0),
                    (start_x + i * (2 * heart_radius + spacing) + heart_radius, start_y + heart_radius),
                    heart_radius
                )

        if self.beer:
            beer_text = f"Beer effect: {int(self.beer_timer)}s"
            text_surface = pygame.font.SysFont(None, 26).render(beer_text, True, (255, 180, 50))
            game_surface.blit(text_surface, (20, 100))  # 左上角显示


        # 绘制UI（带CRT效果）
        ui = UI()
        ui.game_ui(game_surface, self.score, self.coins_collected, progress)

        # 绘制暂停菜单
        if self.paused:
            self.pauseMenu.draw(game_surface)

        # 获取游戏区域抖动偏移
        return self._get_shake_offset_func()

    def draw_func(self, screen):
        self._draw_with_bg(screen)
