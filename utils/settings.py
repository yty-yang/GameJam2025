SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

GAME_WIDTH = SCREEN_WIDTH * 0.55
GAME_HEIGHT = SCREEN_WIDTH * 0.55

# 小球参数
BALL_RADIUS = 20
BALL_BOUNCE = 0.7
TILT_SENSITIVITY = 6.0
GRAVITY = 0.5

# 平台参数
PLATFORM_MAX_SLOPE = 50
PLATFORM_VY = 5

# 洞参数
HOLE_RADIUS = BALL_RADIUS + 5

# 金币参数
COIN_RADIUS = 12

# 游戏状态（用于场景间传递数据）
GAME_STATE = {
    "highest_score": 0,
    "total_coins": 0,
    "coins": 0,
    "score": 0,
    "victory": False,
    "endless": False
}
