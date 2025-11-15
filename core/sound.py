import pygame
from pathlib import Path

class SoundManager:
    def __init__(self, music_file: str = "data/sounds/background.mp3", volume: float = 0.5):
        pygame.mixer.init()
        self.music_file = Path(music_file)
        self.volume = volume
        self.is_playing = False

        # 背景音乐加载
        if not self.music_file.exists():
            print(f"音乐文件 {self.music_file} 未找到！")
        else:
            pygame.mixer.music.load(str(self.music_file))
            pygame.mixer.music.set_volume(self.volume)

        # 音效字典，用于存储不同事件的音效
        self.sounds = {}

    # 背景音乐控制
    def play_music(self, loop: bool = True):
        if self.music_file.exists():
            pygame.mixer.music.play(-1 if loop else 0)
            self.is_playing = True

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def pause_music(self):
        pygame.mixer.music.pause()
        self.is_playing = False

    def unpause_music(self):
        pygame.mixer.music.unpause()
        self.is_playing = True

    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))  # 限制在 0~1
        pygame.mixer.music.set_volume(self.volume)

    # 音效管理
    def load_sound(self, name: str, filepath: str):
        """加载一个音效并以名字存储"""
        path = Path(filepath)
        if not path.exists():
            print(f"音效文件 {filepath} 未找到！")
            return
        self.sounds[name] = pygame.mixer.Sound(str(path))

    def play_sound(self, name: str):
        """播放指定名字的音效"""
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"音效 {name} 尚未加载！")

sound_manager = SoundManager()