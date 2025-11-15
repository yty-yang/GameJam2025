import json
from pathlib import Path

from core.scenes.common.game_mixin import GameMixin
from entities.coin import Coin
from entities.finishLine import FinishLine
from entities.hole import Hole
from entities.obstacle import MovingPlatform, Spring, Teleporter
from utils.settings import GAME_STATE


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
    def __init__(self):
        super().__init__()

        level_data = load_level_data("level_1")

        # 终点线（在小球上方一定距离）
        self.finish_line = None

        self._init_obj(level_data)

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
        # 保存游戏状态
        GAME_STATE["score"] = self.score
        if self.score > GAME_STATE["highest_score"]:
            GAME_STATE["highest_score"] = self.score
        GAME_STATE["total_coins"] += self.coins_collected
        GAME_STATE["coins"] = self.coins_collected
        GAME_STATE["victory"] = victory
        self.game_over = True
        self.next_scene = "gameover"

    def _compute_progress(self):
        total_distance = abs(self.start_y - self.finish_line.y)
        current_distance = abs(self.ball.y - self.finish_line.y)

        return 1.0 - (current_distance / total_distance) if total_distance > 0 else 0.0

    # main调用该方法获取屏幕抖动参数
    def get_shake_offset(self):
        return self._get_shake_offset_func()

    def handle_events(self, events):
        self._handle_events_func(events)

    def update(self, dt):
        if not self.paused:
            # 更新终点线动画
            self.finish_line.update(dt)

            # 检查是否到达终点
            if self.finish_line.check_reached(self.ball):
                self._finish(True)

        self._update_common_func(dt)

    def draw(self, screen):
        self.draw_func(screen)
