from pico2d import *


class Bird:
    image = None  # 모든 새가 공유하는 스프라이트 시트

    def __init__(self):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = 800, 400

    def update(self):
        pass

    def draw(self):
        pass
