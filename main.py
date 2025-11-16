import json
from pathlib import Path

import pygame

from core.scenes.gameplay.endlessScene import EndlessScene
from core.scenes.gameplay.gameoverScene import GameoverScene
from core.scenes.gameplay.levelScene import LevelScene
from core.scenes.main_menu.creditsScene import CreditsScene
from core.scenes.main_menu.helpScene import HelpScene
from core.scenes.main_menu.menuScene import MenuScene
from core.scenes.main_menu.modeScene import ModeScene
from core.scenes.main_menu.selectScene import SelectScene
from core.scenes.main_menu.settingScene import SettingScene
from core.sound import sound_manager
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_STATE


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
        data = {"highest_score": 0, "total_coins": 0, "volume": 5, "vibration": True}
        with data_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        try:
            with data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # 文件内容损坏时也用默认值重建
            data = {"highest_score": 0, "total_coins": 0, "volume": 5, "vibration": True}
            with data_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    GAME_STATE["highest_score"] = data.get("highest_score", 0)
    GAME_STATE["total_coins"] = data.get("total_coins", 0)
    GAME_STATE["volume"] = data.get("volume", 5)
    GAME_STATE["vibration"] = data.get("vibration", True)

def scene_switch(current_scene):
    if current_scene.next_scene == "menu":
        current_scene = MenuScene()
    elif current_scene.next_scene == "mode":
        current_scene = ModeScene()
    elif current_scene.next_scene == "help":
        current_scene = HelpScene()
    elif current_scene.next_scene == "credits":
        current_scene = CreditsScene()
    elif current_scene.next_scene == "setting":
        current_scene = SettingScene()
    elif current_scene.next_scene == "select":
        current_scene = SelectScene()
    elif current_scene.next_scene == "level_1":
        current_scene = LevelScene("level_1")
    elif current_scene.next_scene == "level_2":
        current_scene = LevelScene("level_2")
    elif current_scene.next_scene == "level_3":
        current_scene = LevelScene("level_3")
    elif current_scene.next_scene == "endless":
        current_scene = EndlessScene()
    elif current_scene.next_scene == "gameover":
        current_scene = GameoverScene()

    return current_scene


# TODO: 没有淡出
class IntroScene:
    def __init__(self, screen, music_file=None, duration=2.0, fade_time=2.0):
        """
        screen: pygame 屏幕
        music_file: 背景音乐路径（可选）
        duration: 图片完全显示的时间（秒）
        fade_time: 淡入/淡出时间（秒）
        """
        self.screen = screen
        self.duration = duration
        self.fade_time = fade_time
        self.timer = 0.0
        self.done = False

        # 加载图片
        project_root = Path(__file__).resolve().parent
        img_path = project_root / "data/pictures/beginning.png"
        self.image = pygame.image.load(str(img_path)).convert_alpha()
        self.image = pygame.transform.scale(self.image, screen.get_size())

        # 背景音乐
        self.music_file = music_file
        if self.music_file:
            sound_manager.set_music_file(self.music_file)
            sound_manager.play_music(loop=-1)  # 循环播放
            self.max_volume = sound_manager.volume
            sound_manager.set_volume(0)  # 初始静音

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.done = True

    def update(self, dt):
        self.timer += dt

        # 音乐渐入
        if self.music_file and self.timer < self.fade_time:
            volume = (self.timer / self.fade_time) * self.max_volume
            sound_manager.set_volume(volume)

        # 完成淡出后停止
        if self.timer >= self.fade_time * 2 + self.duration:
            self.done = True
            if self.music_file:
                sound_manager.set_volume(self.max_volume)  # 保持最终音量

    def draw(self):
        # 淡入 -> 全显示 -> 淡出
        if self.timer < self.fade_time:
            alpha = int(255 * (self.timer / self.fade_time))
        elif self.timer < self.fade_time + self.duration:
            alpha = 255
        else:
            alpha = int(255 * (1 - (self.timer - self.fade_time - self.duration) / self.fade_time))

        alpha = max(0, min(255, alpha))
        img = self.image.copy()
        img.set_alpha(alpha)
        self.screen.blit(img, (0, 0))


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED
    )
    pygame.display.set_caption("Cold Ice Beer")
    clock = pygame.time.Clock()

    game_state_load()
    sound_manager.set_music_file("data/sounds/background.mp3")
    sound_manager.play_music()

    # ======== 开场淡入 + 音乐渐入 + 显示 + 淡出 ========
    # intro_scene = IntroScene(
    #     screen,
    #     music_file="data/sounds/background.mp3",
    #     duration=2.0,
    #     fade_time=3.0  # 可以加长淡入淡出时间让效果更明显
    # )
    # intro_running = True
    # while intro_running:
    #     dt = clock.tick(FPS) / 1000
    #     events = pygame.event.get()
    #     intro_scene.handle_events(events)
    #     intro_scene.update(dt)
    #     intro_scene.draw()
    #     pygame.display.flip()
    #     if intro_scene.done:
    #         intro_running = False

    # ======== 正常游戏菜单 ========
    current_scene = MenuScene()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        current_scene.handle_events(events)
        current_scene.update(dt)
        current_scene.draw(screen)
        pygame.display.flip()
        current_scene = scene_switch(current_scene)

    pygame.quit()


if __name__ == "__main__":
    main()
