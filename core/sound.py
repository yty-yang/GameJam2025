import pygame
from pathlib import Path


class SoundManager:
    def __init__(self, music_file: str = None, volume: float = 0.5):
        self.volume = volume
        self.is_playing = False
        self.music_file = None
        self.sounds = {}  # 音效字典，用于存储不同事件的音效

        # 如果提供了音乐文件路径，则加载
        if music_file:
            self.set_music_file(music_file)

    def set_music_file(self, music_file: str):
        """设置并加载音乐文件（使用绝对路径）"""
        # 获取项目根目录：core/sound.py → 上两级目录
        project_root = Path(__file__).resolve().parents[1]
        music_path = project_root / music_file

        self.music_file = music_path

        # 确保 pygame.mixer 已初始化
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # 背景音乐加载
        if not self.music_file.exists():
            print(f"音乐文件 {self.music_file} 未找到！")
        else:
            try:
                pygame.mixer.music.load(str(self.music_file))
                pygame.mixer.music.set_volume(self.volume)
                print(f"音乐文件加载成功: {self.music_file}")
            except pygame.error as e:
                print(f"加载音乐文件失败: {e}")

    # 背景音乐控制
    def play_music(self, loop: bool = True):
        if self.music_file and self.music_file.exists():
            # 确保 pygame.mixer 已初始化
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            try:
                pygame.mixer.music.play(-1 if loop else 0)
                self.is_playing = True
                print(f"开始播放音乐: {self.music_file}")
            except pygame.error as e:
                print(f"播放音乐失败: {e}")
        else:
            print(f"无法播放音乐：音乐文件未设置或不存在")

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
        """加载一个音效并以名字存储；确保 mixer 初始化并捕获加载错误。"""
        try:
            # Ensure mixer initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"初始化 pygame.mixer 失败: {e}")
            return

        path = Path(filepath)
        if not path.exists():
            print(f"音效文件 {filepath} 未找到！")
            return
        try:
            self.sounds[name] = pygame.mixer.Sound(str(path))
        except pygame.error as e:
            print(f"加载音效失败 ({filepath}): {e}")

    def play_sound(self, name: str):
        """播放指定名字的音效，带存在性检查和异常处理。"""
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"播放音效 {name} 失败: {e}")
        else:
            print(f"音效 {name} 尚未加载！")

    def stop_sound(self, name: str):
        """停止指定名字的音效，带存在性检查和异常处理。"""
        if name in self.sounds:
            try:
                self.sounds[name].stop()
            except Exception as e:
                print(f"停止音效 {name} 失败: {e}")
        else:
            print(f"音效 {name} 尚未加载！")


sound_manager = SoundManager()