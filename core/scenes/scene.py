import pygame

from core.sound import sound_manager


def get_joystick():
    """返回已初始化的手柄对象（如果存在），否则返回 None"""
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        return joystick
    return None


class Scene:
    def __init__(self):
        self.next_scene = ""
        self.joystick = get_joystick()
        self.sound_manager = sound_manager

        super().__init__()

    def handle_events(self, events):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError
