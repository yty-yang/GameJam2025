import random

from core.scenes.common.game_mixin import GameMixin
from entities.coin import Coin
from entities.hole import Hole
from entities.obstacle import MovingPlatform, Spring, Teleporter
from utils.settings import GAME_WIDTH, GAME_HEIGHT, GAME_STATE, HOLE_RADIUS, COIN_RADIUS


class EndlessScene(GameMixin):
    def __init__(self):
        super().__init__()

    # TODO: 优化生成逻辑，避免重叠，太少了
    def _generate_hole_coin(self, obj, count=3):
        # obj生成在屏幕上方
        for _ in range(count):
            obj_x = random.randint(0, int(GAME_WIDTH))
            obj_y = random.randint(-200, -10) + self.camera.y  # 基于摄像机位置生成在屏幕上方

            if obj == "hole":
                self.holes.append(Hole(x=obj_x, y=obj_y))
            elif obj == "coin":
                self.coins.append(Coin(obj_x, obj_y))

    def _hole_coin_init(self):
        if len(self.holes) == 0:
            self._generate_hole_coin("hole", 5)

        if len(self.coins) == 0:
            self._generate_hole_coin("coin", 5)

    # TODO: 调试时概率设置为1
    def _generate_obstacles(self):
        """生成障碍物"""
        # 偶尔生成移动平台
        if random.random() < 1 and len(self.moving_platforms) < 2:
            platform_x = random.randint(100, int(GAME_WIDTH) - 100)
            platform_y = self.camera.y - GAME_HEIGHT * 0.4 - random.randint(50, 200)
            direction = random.choice([-1, 1])
            self.moving_platforms.append(
                MovingPlatform(platform_x, platform_y, width=120, speed=80, direction=direction)
            )

        # 偶尔生成弹簧
        if random.random() < 1 and len(self.springs) < 3:
            spring_x = random.randint(50, int(GAME_WIDTH) - 50)
            spring_y = self.camera.y - GAME_HEIGHT * 0.5 - random.randint(100, 250)
            self.springs.append(Spring(spring_x, spring_y))

        # 偶尔生成传送门对
        if random.random() < 1 and len(self.teleporters) < 2:
            tele1_x = random.randint(100, int(GAME_WIDTH) - 100)
            tele1_y = self.camera.y - GAME_HEIGHT * 0.5 - random.randint(150, 300)
            tele2_x = random.randint(100, int(GAME_WIDTH) - 100)
            tele2_y = tele1_y - random.randint(200, 400)
            # 创建配对传送门，使用配对ID区分不同的传送门对
            pair_id = len(self.teleporters)  # 每个传送门对使用不同的ID
            teleporter1 = Teleporter(tele1_x, tele1_y, tele2_x, tele2_y, pair_id=pair_id)
            teleporter2 = Teleporter(tele2_x, tele2_y, tele1_x, tele1_y, pair_id=pair_id)
            # 设置配对引用
            teleporter1.pair_teleporter = teleporter2
            teleporter2.pair_teleporter = teleporter1
            self.teleporters.append([teleporter1, teleporter2])

    def _obj_update(self, dt):
        self._update_game_func(dt)

    # 清理在平台下方一定距离的物体
    # TODO: 弃用
    def _remove_offscreen_obj(self):
        lower_bound = (self.camera.world_to_screen(0, min(self.platform.y1, self.platform.y2))[1]
                       + GAME_HEIGHT * 0.4 + 100)

        self.holes = [hole for hole in self.holes
                      if self.camera.world_to_screen(hole.x, hole.y)[1] - HOLE_RADIUS < lower_bound]
        self.coins = [coin for coin in self.coins
                      if not coin.collected and
                      self.camera.world_to_screen(coin.x, coin.y)[1] - COIN_RADIUS < lower_bound]
        self.moving_platforms = [p for p in self.moving_platforms
                                 if self.camera.world_to_screen(p.x, p.y)[1] - p.height < lower_bound]
        self.springs = [s for s in self.springs
                        if self.camera.world_to_screen(s.x, s.y)[1] - s.height < lower_bound]
        self.teleporters = [t_pair for t_pair in self.teleporters
                            if
                            self.camera.world_to_screen(t_pair[0].x, t_pair[0].y)[1] - t_pair[0].radius < lower_bound or
                            self.camera.world_to_screen(t_pair[1].x, t_pair[1].y)[1] - t_pair[1].radius < lower_bound]

    def _fall_into_hole(self):
        self._fall_into_hole_func()

    def _update_entities(self, dt):
        self.ball.update(self.platform, dt)

        # 首次初始化生成洞和金币
        self._hole_coin_init()

        # 更新障碍物和金币
        self._obj_update(dt)

        # 清理离开屏幕的障碍物和金币
        self._remove_offscreen_obj()

        # 生成洞和金币
        # 如果洞口数量少于5，补充洞口
        desired_hole_num = 5
        if len(self.holes) < desired_hole_num:
            self._generate_hole_coin("hole", desired_hole_num - len(self.holes) + random.randint(0, 2))
        # 生成金币
        if len(self.coins) < 3:
            self._generate_hole_coin("coin", random.randint(2, 3))

        # 生成障碍物
        self._generate_obstacles()

        # 碰撞边缘抖动
        if self.ball.collision_side():
            self.shake_timer = 10

        # 判断是否碰撞洞口，如果碰撞则开始动画
        self._fall_into_hole()

    # victory参数无意义，保持接口一致
    def _finish(self, victory):
        # 播放游戏结束音效（无尽模式总是失败）
        from core.sound import sound_manager
        sound_manager.play_sound("game_over")
        
        # 保存游戏状态
        GAME_STATE["score"] = self.score
        if self.score > GAME_STATE["highest_score"]:
            GAME_STATE["highest_score"] = self.score
        GAME_STATE["total_coins"] += self.coins_collected
        GAME_STATE["coins"] = self.coins_collected

        GAME_STATE["endless"] = True

        self.game_over = True
        self.next_scene = "gameover"

    # main调用该方法获取屏幕抖动参数
    def get_shake_offset(self):
        return self._get_shake_offset_func()

    def handle_events(self, events):
        self._handle_events_func(events)

    def update(self, dt):
        self._update_common_func(dt)

    def draw(self, screen):
        self.draw_func(screen)
