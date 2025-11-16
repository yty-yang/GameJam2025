import json
import pygame
from pathlib import Path

from core.scenes.common.game_mixin import GameMixin
from core.scenes.common.menu_navigation_mixin import confirm_pressed
from core.sound import sound_manager
from entities.coin import Coin
from entities.finishLine import FinishLine
from entities.hole import Hole
from entities.obstacle import MovingPlatform, Spring, Teleporter
from utils.settings import GAME_STATE, SCREEN_WIDTH, SCREEN_HEIGHT


def load_level_data(id):
    # 获取项目根目录：core/scenes/gameplay/levelScene.py → 上四级目录
    project_root = Path(__file__).resolve().parents[3]

    level_path = project_root / "data" / "game" / "level.json"
    if not level_path.exists():
        return None

    with level_path.open("r", encoding="utf-8") as f:
        level_data = json.load(f)

    for level in level_data["levels"]:
        if level["id"] == id:
            return level

    return None


class LevelScene(GameMixin):
    def __init__(self, info):
        super().__init__()

        level, life = info.rsplit("_", 1)
        level_data = load_level_data(level)
        self.life = int(life)

        # 终点线（在小球上方一定距离）
        self.finish_line = None

        self._init_obj(level_data)

        self.level = level
        # 前置对话
        self.show_intro = False
        self.intro_image = None
        if level == "level_1":
            project_root = Path(__file__).resolve().parents[3]
            intro_path = project_root / "data" / "pictures" / "dialogs" / "before_game.png"

            self.intro_image = pygame.image.load(intro_path).convert_alpha()
            self.show_intro = True



    def _init_obj(self, level_data):
        # 初始化终点线

        self.finish_line = FinishLine(level_data["finish_line_y"])

        # 初始化洞口
        hole_positions = level_data.get("holes", [])
        for pos in hole_positions:
            hole = Hole(x=pos["x"], y=pos["y"])
            self.holes.append(hole)

        # 初始化金币
        coin_positions = level_data.get("coins", [])
        for pos in coin_positions:
            coin = Coin(x=pos["x"], y=pos["y"])
            self.coins.append(coin)

        # 初始化障碍物
        obstacles = level_data.get("obstacles", [])
        for obstacle in obstacles:
            if obstacle["type"] == "moving_platform":
                platform = MovingPlatform(obstacle["x"], obstacle["y"], obstacle["direction"])
                self.moving_platforms.append(platform)
            elif obstacle["type"] == "spring":
                spring = Spring(obstacle["x"], obstacle["y"])
                self.springs.append(spring)
            elif obstacle["type"] == "teleporterPair":
                # 创建配对传送门，使用配对ID区分不同的传送门对
                pair_id = len(self.teleporters)  # 每个传送门对使用不同的ID
                teleporter1 = Teleporter(obstacle["x1"], obstacle["y1"], obstacle["x2"], obstacle["y2"], pair_id=pair_id)
                teleporter2 = Teleporter(obstacle["x2"], obstacle["y2"], obstacle["x1"], obstacle["y1"], pair_id=pair_id)
                # 设置配对引用
                teleporter1.pair_teleporter = teleporter2
                teleporter2.pair_teleporter = teleporter1
                self.teleporters.append([teleporter1, teleporter2])

    def _obj_update(self, dt):
        self._update_game_func(dt)

    def _fall_into_hole(self):
        self._fall_into_hole_func()

    def _update_entities(self, dt):
        self.ball.update(self.platform, dt)

        # 更新障碍物和金币
        self._obj_update(dt)

        # 碰撞边缘抖动
        if self.ball.collision_side():
            self.shake_timer = 10

        # 判断是否碰撞洞口，如果碰撞则开始动画
        self._fall_into_hole()

    def _finish(self, victory):
        sound_manager.stop_sound("ball_roll")

        # 保存游戏状态
        GAME_STATE["score"] = self.score
        if self.score > GAME_STATE["highest_score"]:
            GAME_STATE["highest_score"] = self.score
        GAME_STATE["total_coins"] += self.coins_collected
        GAME_STATE["coins"] = self.coins_collected
        GAME_STATE["victory"] = victory
        self.game_over = True

        project_root = Path(__file__).resolve().parents[3]
        level_num = int(self.level.split("_")[1])
        self.show_dialog = True
        if victory:
            sound_manager.play_sound("winning")
            # 设置胜利对话显示
            dialog_path = project_root / "data" / "pictures" / "dialogs" / f"win_{level_num}.png"
            self.dialog_image = pygame.image.load(dialog_path).convert_alpha()

            if level_num == 1 or level_num == 2:
                self.next_scene_after_dialog = f"level_{level_num + 1}_{self.life}"
            else:
                self.next_scene_after_dialog = "menu"
        else:
            sound_manager.play_sound("game_over")

            dialog_path = project_root / "data" / "pictures" / "dialogs" / f"gameover_{level_num}.png"
            self.dialog_image = pygame.image.load(dialog_path).convert_alpha()
            self.next_scene_after_dialog = f"level_{level_num}_{self.life - 1}" if self.life > 1 else "menu"

    def _compute_progress(self):
        total_distance = abs(self.start_y - self.finish_line.y)
        current_distance = abs(self.ball.y - self.finish_line.y)

        return 1.0 - (current_distance / total_distance) if total_distance > 0 else 0.0

    # 获取屏幕抖动参数
    def get_shake_offset(self):
        return self._get_shake_offset_func()

    def handle_events(self, events):
        if self.show_intro:
            if confirm_pressed(events):
                self.show_intro = False  # 关闭前置对话
            return

        if getattr(self, "show_dialog", False):
            if confirm_pressed(events):
                self.show_dialog = False
                self.fade_out = True
            return

        self._handle_events_func(events)

    def update(self, dt):
        if self.show_intro or getattr(self, "show_dialog", False):
            return

        # 如果在渐变过程中
        if self.fade_out:
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                # 渐变完成，切换场景
                self.next_scene = getattr(self, "next_scene_after_dialog", None)
            return  # 渐变期间暂停游戏逻辑

        if not self.paused:
            # 更新终点线动画
            self.finish_line.update(dt)

            # 检查是否到达终点
            if self.finish_line.check_reached(self.ball):
                self._finish(True)

        self._update_common_func(dt)

    def draw(self, screen):
        if self.show_intro and self.intro_image:
            # 获取原始尺寸
            img_w, img_h = self.intro_image.get_size()

            # 计算缩放比例，使宽度等于 SCREEN_WIDTH - 50
            target_width = SCREEN_WIDTH - 50
            scale_ratio = target_width / img_w
            new_w = int(img_w * scale_ratio)
            new_h = int(img_h * scale_ratio)

            # 缩放图片
            scaled_img = pygame.transform.smoothscale(self.intro_image, (new_w, new_h))

            # 计算水平和垂直居中坐标
            x = (SCREEN_WIDTH - new_w) // 2
            y = (SCREEN_HEIGHT - new_h) // 2

            # 绘制图片
            screen.blit(scaled_img, (x, y))
        elif getattr(self, "show_dialog", False):
            # 胜利对话绘制
            img_w, img_h = self.dialog_image.get_size()
            target_width = SCREEN_WIDTH - 50
            scale_ratio = target_width / img_w
            new_w = int(img_w * scale_ratio)
            new_h = int(img_h * scale_ratio)
            scaled_img = pygame.transform.smoothscale(self.dialog_image, (new_w, new_h))
            x = (SCREEN_WIDTH - new_w) // 2
            y = (SCREEN_HEIGHT - new_h) // 2
            screen.blit(scaled_img, (x, y))
        else:
            self.draw_func(screen)

        # 如果渐变中，绘制黑色覆盖层
        if self.fade_out:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.set_alpha(int(self.fade_alpha))
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))
