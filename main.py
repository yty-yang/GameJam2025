import pygame

from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from core.scenes.menuScene import MenuScene
from core.scenes.playerScene import PlayerScene
from core.scenes.ballScene import BallScene
from core.scenes.helpScene import HelpScene
from core.scenes.settingScene import SettingScene


def sceneSwitch(current_scene):
    if current_scene.next_scene == "ball":
        current_scene = BallScene()
    elif current_scene.next_scene == "player":
        current_scene = PlayerScene()
    elif current_scene.next_scene == "menu":
        current_scene = MenuScene()
    elif current_scene.next_scene == "help":
        current_scene = HelpScene()
    elif current_scene.next_scene == "setting":
        current_scene = SettingScene()

    return current_scene

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("GameJam Demo")
    clock = pygame.time.Clock()

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

        pygame.display.flip()

        # 场景切换
        current_scene = sceneSwitch(current_scene)

    pygame.quit()


if __name__ == "__main__":
    main()