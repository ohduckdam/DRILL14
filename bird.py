from pico2d import *

# 스프라이트 시트(918 x 506) 구성 정보
# 5열 x 3행 격자에 총 14개의 프레임이 들어있다. (마지막 행은 4개)
SHEET_WIDTH, SHEET_HEIGHT = 918, 506
FRAME_COLS = 5
FRAME_COUNT = 14
FRAME_WIDTH = 182   # 각 프레임의 새 몸통이 정확히 182px 간격으로 배치되어 있음
FRAME_HEIGHT = 168


class Bird:
    image = None  # 모든 새가 공유하는 스프라이트 시트

    def __init__(self):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = 800, 400
        self.frame = 0

    def update(self):
        pass

    def draw(self):
        col = self.frame % FRAME_COLS
        row = self.frame // FRAME_COLS
        # pico2d 는 이미지 좌표의 원점이 왼쪽 아래이므로 위쪽 행부터 세려면 뒤집어야 함
        bottom = SHEET_HEIGHT - (row + 1) * FRAME_HEIGHT
        Bird.image.clip_draw(col * FRAME_WIDTH, bottom, FRAME_WIDTH, FRAME_HEIGHT,
                             self.x, self.y)
