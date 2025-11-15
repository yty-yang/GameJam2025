from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    def __init__(self, target_x, target_y, target_screen_x=None, target_screen_y=None, smooth=0.1):
        self.smooth = 1
        self.x = 0
        self.y = 0

        self.follow(target_x, target_y, target_screen_x, target_screen_y)
        self.smooth = smooth

    def follow(self, target_x, target_y, target_screen_x=None, target_screen_y=None):
        """
        target_x/y: 世界坐标
        target_screen_x/y: 小球在屏幕上的目标位置
        """
        if target_screen_x is None:
            target_screen_x = SCREEN_WIDTH / 2
        if target_screen_y is None:
            target_screen_y = SCREEN_HEIGHT * 0.6

        # 平滑跟随
        self.x += (target_x - target_screen_x - self.x) * self.smooth
        self.y += (target_y - target_screen_y - self.y) * self.smooth

    def world_to_screen(self, world_x, world_y):
        """把世界坐标转换成屏幕坐标"""
        return world_x - self.x, world_y - self.y
