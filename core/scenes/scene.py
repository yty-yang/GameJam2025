class Scene:
    def __init__(self):
        self.next_scene = ""

    def handle_events(self, events):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError