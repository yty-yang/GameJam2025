import json
import math
import random
from pathlib import Path

import pygame

from core.camera import Camera
from core.scenes.scene import Scene
from core.ui import UI
from entities.ball import Ball
from entities.pauseMenu import PauseMenu
from entities.platform import Platform
from utils.settings import GAME_STATE, BALL_BOUNCE, SCREEN_WIDTH, BALL_RADIUS


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
            x=SCREEN_WIDTH // 2,
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
            for teleporter_pair in self.teleporters[:]:  # 用切片复制列表
                tele_target = False
                for teleporter in teleporter_pair:
                    teleporter.update(dt)
                    tele_target = teleporter.check_collision(self.ball)
                    if tele_target:
                        # 传送
                        self.ball.x, self.ball.y = tele_target
                        self.ball.vx *= 0.5
                        self.ball.vy *= 0.5
                        self.shake_timer = 2
                        self.teleporters.remove(teleporter_pair)
                        break

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
        if not self.paused:
            # 如果小球正在滚入洞口，更新动画
            if self.ball.is_falling_into_hole:
                self.ball.update_fall_animation(dt)
                # 动画完成后切换到游戏结束场景
                if self.ball.is_animation_complete():
                    self._finish(False)
            # TODO: 增加游戏结束条件，小球掉出屏幕
            else:
                self._update_entities(dt)

            # 游戏结束保存状态
            if self.game_over:
                save_data()

        else:
            self.pauseMenu.update(dt)

    def draw_func(self, screen):
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

        # 计算进度（距离终点的进度）
        progress = self._compute_progress() if hasattr(self, "finish_line") else 0

        # 绘制UI（带CRT效果）
        ui = UI()
        ui.game_ui(screen, self.score, self.coins_collected, progress)

        # 绘制暂停菜单
        if self.paused:
            self.pauseMenu.draw(screen)
