from pico2d import *

import game_framework

# 스프라이트 시트(918 x 506) 구성 정보
# 5열 x 3행 격자에 총 14개의 프레임이 들어있다. (마지막 행은 4개)
SHEET_WIDTH, SHEET_HEIGHT = 918, 506
FRAME_COLS = 5
FRAME_COUNT = 14
FRAME_WIDTH = 182   # 각 프레임의 새 몸통이 정확히 182px 간격으로 배치되어 있음

# 행별 잘라낼 영역 (시트 위쪽 기준 top, 높이)
# 시트 높이 506 은 3으로 나누어 떨어지지 않고, 각 행의 그림 위치도 균일하지 않다.
# 실제 픽셀 분석 결과 그림이 존재하는 y 범위(위쪽 기준):
#   0행: 1 ~ 143,  1행: 216 ~ 339,  2행: 370 ~ 499
# 균일하게 168px 씩 자르면 1행 날개 끝(337~339)이 잘려 나가므로 행마다 영역을 따로 지정
ROW_RECTS = [
    (0, 170),
    (170, 170),
    (340, 166),
]

# 날갯짓 애니메이션 속도
# 14개 프레임이 날갯짓 1회(위 -> 아래 -> 위)를 이룬다.
TIME_PER_ACTION = 0.7                      # 날갯짓 1회에 걸리는 시간(초)
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION    # 초당 날갯짓 횟수
FRAMES_PER_ACTION = FRAME_COUNT            # 날갯짓 1회당 프레임 수


class Bird:
    image = None  # 모든 새가 공유하는 스프라이트 시트

    def __init__(self):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = 800, 400
        self.frame = 0.0

    def update(self):
        # 컴퓨터 성능(프레임 레이트)과 무관하게 일정한 속도로 날갯짓하도록 frame_time 기반으로 진행
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAME_COUNT

    def draw(self):
        index = int(self.frame)
        col = index % FRAME_COLS
        row = index // FRAME_COLS
        top, height = ROW_RECTS[row]
        # pico2d 는 이미지 좌표의 원점이 왼쪽 아래이므로 위쪽 기준 top 을 bottom 으로 변환
        bottom = SHEET_HEIGHT - top - height
        Bird.image.clip_draw(col * FRAME_WIDTH, bottom, FRAME_WIDTH, height,
                             self.x, self.y)
