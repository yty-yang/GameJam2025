import json
from pathlib import Path

import pygame

from core.scenes.gameplay.endlessScene import EndlessScene
from core.scenes.gameplay.gameoverScene import GameoverScene
from core.scenes.gameplay.levelScene import LevelScene
from core.scenes.main_menu.helpScene import HelpScene
from core.scenes.main_menu.menuScene import MenuScene
from core.scenes.main_menu.modeScene import ModeScene
from core.scenes.main_menu.settingScene import SettingScene
from core.sound import sound_manager
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_STATE

try:
    import pygame.haptic as haptic_module

    HAS_HAPTIC = True
except ImportError:
    HAS_HAPTIC = False


def game_state_load():
    # 读取数据
    # 获取项目根目录
    project_root = Path(__file__).resolve().parent

    # 确保 data 文件夹存在
    data_dir = project_root / "data" / "game"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 写入 JSON 文件
    data_path = data_dir / "data.json"

    # 如果文件不存在或为空，就创建默认数据
    if not data_path.exists() or data_path.stat().st_size == 0:
        data = {"highest_score": 0, "total_coins": 0}
        with data_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        try:
            with data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # 文件内容损坏时也用默认值重建
            data = {"highest_score": 0, "total_coins": 0}
            with data_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    GAME_STATE["highest_score"] = data.get("highest_score", 0)
    GAME_STATE["total_coins"] = data.get("total_coins", 0)


def check_haptic():
    haptic = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        if HAS_HAPTIC:
            try:
                haptic = haptic_module.Haptic(joystick)
                haptic.init()
                print("Haptic initialized!")
            except pygame.error:
                haptic = None
                print("This controller does not support haptic feedback.")
        else:
            print("Pygame haptic module not available.")

    return haptic


def shake_apply(current_scene, screen, haptic):
    # 如果 Scene 有 shake，就用 shake
    dest = current_scene.get_shake_offset() if hasattr(current_scene, "get_shake_offset") else (0, 0)
    pygame.display.get_surface().blit(screen, dest)
    if haptic:
        dx, dy = dest
        magnitude = (dx ** 2 + dy ** 2) ** 0.5  # 偏移大小
        max_magnitude = 20  # 根据你的屏幕 shake 最大偏移调整
        level = min(magnitude / max_magnitude, 1.0)  # 0~1
        length = int(100 + 400 * (magnitude / max_magnitude))  # 最短 100ms，最长 500ms

        effect_id = haptic.new_effect(haptic_module.Effect(
            type=haptic_module.Constant,
            length=length,
            level=level
        ))
        haptic.run_effect(effect_id)


def scene_switch(current_scene):
    if current_scene.next_scene == "menu":
        current_scene = MenuScene()
    elif current_scene.next_scene == "mode":
        current_scene = ModeScene()
    elif current_scene.next_scene == "ball":
        current_scene = LevelScene()
    elif current_scene.next_scene == "endless":
        current_scene = EndlessScene()
    elif current_scene.next_scene == "help":
        current_scene = HelpScene()
    elif current_scene.next_scene == "setting":
        current_scene = SettingScene()
    elif current_scene.next_scene == "gameover":
        current_scene = GameoverScene()

    return current_scene


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED
    )
    pygame.display.set_caption("GameJam Demo")
    clock = pygame.time.Clock()

    game_state_load()

    # 检查是否有手柄及震动支持
    haptic = check_haptic()

    # 初始化音乐管理器
    sound_manager.set_music_file("data/sounds/background.mp3")
    sound_manager.play_music()  # 循环播放主背景音乐

    # 初始化场景
    current_scene = MenuScene()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # 场景逻辑
        current_scene.handle_events(events)
        current_scene.update(dt)
        current_scene.draw(screen)

        # screen shake apply
        shake_apply(current_scene, screen, haptic)

        pygame.display.flip()

        # 场景切换
        current_scene = scene_switch(current_scene)

    pygame.quit()


if __name__ == "__main__":
    main()
