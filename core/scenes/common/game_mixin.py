import json

import random
from pathlib import Path

import pygame

from core.camera import Camera
from core.scenes.scene import Scene
from core.sound import sound_manager
from core.ui import UI
from entities.ball import Ball
from entities.pauseMenu import PauseMenu
from entities.platform import Platform
from utils.settings import GAME_STATE, BALL_BOUNCE, SCREEN_WIDTH, SCREEN_HEIGHT, BALL_RADIUS, GAME_HEIGHT, GAME_WIDTH


def save_data():
    data_to_save = {
        "highest_score": GAME_STATE.get("highest_score", 0),
        "total_coins": GAME_STATE.get("total_coins", 0)
    }

    # 获取项目根目录：core/scenes/common/game_mixin.py → 上三级目录
    project_root = Path(__file__).resolve().parents[3]

    # 确保 data 文件夹存在
    data_dir = project_root / "data" / "game"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 写入 JSON 文件
    data_path = data_dir / "data.json"
    with data_path.open("w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)


class GameMixin(Scene):
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

        # 背景色
        self.background_color = (30, 30, 30)

        # 初始化摄像机
        self.camera = Camera(self.ball.x, self.ball.y)

        # 初始化暂停界面
        self.pauseMenu = PauseMenu()

        self.paused = False
        self.game_over = False
        self.shake_timer = 0
        
        # 加载游戏机背景图片（动画序列）
        project_root = Path(__file__).resolve().parents[3]
        game_machine_dir = project_root / "data" / "pictures" / "game_machine"
        
        self.game_machine_frames = []
        self.animation_frame = 0.0
        self.animation_speed = 0.15  # 动画速度（每帧增加的帧数）
        
        try:
            # 加载所有动画帧（0-8）
            for i in range(9):
                # 尝试两种文件名格式：game_machine-0.png 和 game_machine_0.png
                frame_path1 = game_machine_dir / f"game_machine-{i}.png"
                frame_path2 = game_machine_dir / f"game_machine_{i}.png"
                
                if frame_path1.exists():
                    frame = pygame.image.load(str(frame_path1)).convert_alpha()
                elif frame_path2.exists():
                    frame = pygame.image.load(str(frame_path2)).convert_alpha()
                else:
                    print(f"警告：找不到游戏机背景帧 {i}")
                    continue
                
                # 缩放背景到屏幕大小
                frame = pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.game_machine_frames.append(frame)
            
            if len(self.game_machine_frames) == 0:
                # 如果没有找到动画帧，尝试加载单个图片作为后备
                game_machine_path = project_root / "data" / "pictures" / "game_machine.png"
                if game_machine_path.exists():
                    self.game_machine_bg = pygame.image.load(str(game_machine_path)).convert_alpha()
                    self.game_machine_bg = pygame.transform.scale(self.game_machine_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.game_machine_frames = None
                else:
                    self.game_machine_bg = None
                    self.game_machine_frames = None
            else:
                self.game_machine_bg = None  # 使用动画帧时不需要单个背景
                print(f"成功加载 {len(self.game_machine_frames)} 帧游戏机背景动画")

            # 游戏区域：1:1 正方形，左右居中，上下贴顶
            # 游戏区域宽度等于高度（正方形），不被缩放
            self.game_area_width = GAME_WIDTH  # 1:1 正方形，所以宽度 = 高度
            self.game_area_height = GAME_HEIGHT

            # 水平居中
            self.game_area_x = (SCREEN_WIDTH - self.game_area_width) // 2
            # 上下贴顶
            self.game_area_y = 0

        except Exception as e:
            print(f"无法加载游戏机背景图片: {e}")
            self.game_machine_bg = None
            self.game_machine_frames = None

        # 预加载金币音效（如果存在）
        try:
            coin_sound_path = project_root / "data" / "sounds" / "eat_coins.mp3"
            if coin_sound_path.exists():
                # load_sound 接受文件路径字符串
                sound_manager.load_sound("eat_coins", str(coin_sound_path))
        except Exception as e:
            print(f"无法预加载金币音效: {e}")


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
                    self.shake_timer = 3

        if hasattr(self, "springs"):
            for spring in self.springs:
                spring.update(dt)
                if spring.check_collision(self.ball):
                    # 弹簧弹跳
                    self.ball.vy = -spring.bounce_power
                    self.shake_timer = 5

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
                            # 传送
                            self.ball.x, self.ball.y = tele_target
                            self.ball.vx *= 0.5
                            self.ball.vy *= 0.5
                            self.shake_timer = 2
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
                    self.shake_timer = 2

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
            return random.randint(-2, 2), random.randint(-2, 2)
        return 0, 0

    def _handle_events_func(self, events):
        if not self.paused:
            """处理玩家输入，让平台上下移动"""
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.platform.move(True, False, True)
            if keys[pygame.K_UP]:
                self.platform.move(False, True, True)
            if keys[pygame.K_s]:
                self.platform.move(True, False, False)
            if keys[pygame.K_DOWN]:
                self.platform.move(False, True, False)
            if self.joystick:
                ly = self.joystick.get_axis(1)  # 左摇杆Y轴
                ry = self.joystick.get_axis(3)  # 右摇杆Y轴

                if ly < -0.2:  # 左摇杆上推
                    self.platform.move(True, False, True, speed_factor=min(1.0, -ly))
                if ry < -0.2:  # 右摇杆上推
                    self.platform.move(False, True, True, speed_factor=min(1.0, -ry))
                if ly > 0.2:  # 左摇杆下推
                    self.platform.move(True, False, False, speed_factor=min(1.0, ly))
                if ry > 0.2:  # 右摇杆下推
                    self.platform.move(False, True, False, speed_factor=min(1.0, ry))

            # 处理按键功能
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    self.paused = not self.paused
        else:
            result = self.pauseMenu.handle_events(events)
            if result == "Resume":
                self.paused = False
            elif result == "Quit":
                self.next_scene = "menu"

    def _update_common_func(self, dt):
        # 更新游戏机背景动画帧
        if hasattr(self, 'game_machine_frames') and self.game_machine_frames:
            self.animation_frame += self.animation_speed * dt * 60  # 假设60fps
            # 循环播放（0-8，共9帧）
            if self.animation_frame >= len(self.game_machine_frames):
                self.animation_frame = 0.0
        
        if not self.paused:
            # 如果小球正在滚入洞口，更新动画
            if self.ball.is_falling_into_hole:
                self.ball.update_fall_animation(dt)
                # 动画完成后切换到游戏结束场景
                if self.ball.is_animation_complete():
                    self._finish(False)
            else:
                self._update_entities(dt)
                
                # 检测小球是否掉出屏幕（掉到平台下方太远）
                # 计算小球在屏幕上的Y坐标
                screen_x, screen_y = self.camera.world_to_screen(self.ball.x, self.ball.y)
                
                # 如果小球掉到屏幕下方（超过屏幕高度 + 一定缓冲距离），触发 game over
                if screen_y > SCREEN_HEIGHT + 100:  # 掉出屏幕下方100像素后触发
                    self._finish(False)

            # 游戏结束保存状态
            if self.game_over:
                save_data()

        else:
            self.pauseMenu.update(dt)

    def draw_func(self, screen):
        # 如果加载了游戏机背景动画，使用游戏机屏幕效果
        if hasattr(self, 'game_machine_frames') and self.game_machine_frames:
            # 获取当前动画帧
            current_frame_index = int(self.animation_frame) % len(self.game_machine_frames)
            current_bg = self.game_machine_frames[current_frame_index]
        elif self.game_machine_bg:
            # 使用单个背景图片（后备方案）
            current_bg = self.game_machine_bg
        else:
            current_bg = None
        
        if current_bg:
            # 创建游戏内容surface（1:1 正方形）
            game_surface = pygame.Surface((self.game_area_width, self.game_area_height))
            game_surface.fill(self.background_color)
            
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

            # 绘制UI（带CRT效果）
            ui = UI()
            ui.game_ui(game_surface, self.score, self.coins_collected, progress)

            # 绘制暂停菜单
            if self.paused:
                self.pauseMenu.draw(game_surface)
            
            # 将游戏机背景绘制到主屏幕（使用当前动画帧）
            screen.blit(current_bg, (0, 0))
            
            # 将游戏内容surface直接绘制到游戏区域（不缩放，保持 1:1 比例)
            screen.blit(game_surface, (self.game_area_x, self.game_area_y))
        else:
            # 如果没有游戏机背景，使用原来的绘制方式
            screen.fill(self.background_color)

            # camera跟随ball
            self.camera.follow(self.ball.x, self.ball.y, target_screen_x=self.ball.x)

            # 绘制平台
            self.platform.draw(screen, self.camera)

            # 绘制终点线（在背景层）
            if hasattr(self, "finish_line"):
                self.finish_line.draw(screen, self.camera)

            # 绘制障碍物
            for platform in self.moving_platforms:
                platform.draw(screen, self.camera)
            for spring in self.springs:
                spring.draw(screen, self.camera)
            
            # 绘制传送门（内部已包含箭头指示）
            if hasattr(self, "teleporters"):
                for t_pair in self.teleporters:
                    for teleporter in t_pair:
                        teleporter.draw(screen, self.camera)

            # 绘制金币
            for coin in self.coins:
                if not coin.collected:
                    coin.draw(screen, self.camera)

            # 先绘制洞口（在底层）
            for hole in self.holes:
                hole.draw(screen, self.camera)
            # 再绘制小球（在上层，确保小球不会被洞口覆盖）
            self.ball.draw(screen, self.camera)

            # 计算进度（距离终点的进度)
            progress = self._compute_progress() if hasattr(self, "finish_line") else 0

            # 绘制UI（带CRT效果)
            ui = UI()
            ui.game_ui(screen, self.score, self.coins_collected, progress)

            # 绘制暂停菜单
            if self.paused:
                self.pauseMenu.draw(screen)
