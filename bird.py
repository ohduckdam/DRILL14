import random

from pico2d import *

import game_framework

# 스프라이트 시트(918 x 506) 구성 정보
# 5열 x 3행 격자에 총 14개의 프레임이 들어있다. (마지막 행은 4개)
SHEET_HEIGHT = 506  # (가로 918px)
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

# 행 간 위치 보정 (프레임이 바뀔 때 새가 위아래로 튀는 현상 방지)
# 각 프레임의 눈동자(파란 픽셀) 중심 y 좌표(위쪽 기준)를 측정한 결과:
#   0행: 94 93 91 88 85,  1행: 255 253 254 254 256,  2행: 429 432 433 434
# 행 간격이 168, 172 로 서로 달라서 단순히 잘라 그리면 행이 바뀌는 순간 새가 튄다.
# 각 행의 기준선을 0, 168, 340 으로 두면 눈 높이가 94 -> 85 -> 88 -> 94 로
# 부드럽게 오르내리는 원래의 몸통 움직임만 남는다.
ROW_BASES = [0, 168, 340]
ANCHOR_Y = 85   # 기준선으로부터 화면상의 self.y 에 맞출 지점

# 행별 세로 보정량(원본 픽셀)을 미리 계산해 둔다.
# 잘라낸 영역의 중심이 기준점(ROW_BASES[row] + ANCHOR_Y)보다 아래에 있으면
# 그만큼 화면에서도 아래로 내려 그려야 기준점이 항상 self.y 에 놓인다.
ROW_OFFSETS = [(top + height / 2) - (base + ANCHOR_Y)
               for (top, height), base in zip(ROW_RECTS, ROW_BASES)]

# 좌우 반전 시 위치 보정
# 새 몸통 중심은 프레임 칸의 정중앙(91)이 아니라 x = 103 부근에 치우쳐 있다.
# 반전하면 몸통이 칸 중앙을 기준으로 반대편으로 넘어가 방향 전환 순간 새가 순간이동한다.
# 따라서 몸통 중심(ANCHOR_X)이 항상 self.x 에 오도록 방향에 따라 그리기 위치를 보정한다.
ANCHOR_X = 103

# 화면에 그릴 크기 배율
# 원본 프레임(182px)은 1600px 화면에 10마리를 띄우기에 너무 크므로 축소하여 그린다.
BIRD_SCALE = 0.5

# 새 비행 속도 (boy.py 와 같은 단위계: 10 pixel = 30 cm)
PIXEL_PER_METER = (10.0 / 0.3)
FLY_SPEED_KMPH = 20.0                                  # 새의 비행 속도 (km/h)
FLY_SPEED_MPM = (FLY_SPEED_KMPH * 1000.0 / 60.0)       # m/min
FLY_SPEED_MPS = (FLY_SPEED_MPM / 60.0)                 # m/s
FLY_SPEED_PPS = (FLY_SPEED_MPS * PIXEL_PER_METER)      # pixel/s

# 날갯짓 애니메이션 속도
# 14개 프레임이 날갯짓 1회(위 -> 아래 -> 위)를 이룬다.
TIME_PER_ACTION = 0.7                      # 날갯짓 1회에 걸리는 시간(초)
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION    # 초당 날갯짓 횟수
FRAMES_PER_ACTION = FRAME_COUNT            # 날갯짓 1회당 프레임 수


class Bird:
    """좌우로 반복 비행하는 새 한 마리.

    - 14프레임 날갯짓 애니메이션을 frame_time 기반으로 재생
    - 행별 클리핑/기준점 보정으로 프레임 전환 시 흔들림 없음
    - 화면 끝에서 방향 전환 및 좌우 반전 (몸통 중심 기준 보정)
    """
    image = None  # 모든 새가 공유하는 스프라이트 시트

    def __init__(self, x=800, y=400, dir=1):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = x, y
        # 모든 새가 같은 프레임에서 시작하면 10마리가 똑같이 날갯짓하여 부자연스러움
        # -> 시작 프레임을 무작위로 정해 날갯짓 타이밍을 서로 어긋나게 함
        self.frame = random.uniform(0, FRAME_COUNT)
        self.dir = dir  # 1: 오른쪽, -1: 왼쪽

        # 새마다 비행 속도를 기준 속도의 ±25% 범위에서 다르게 지정
        speed_ratio = random.uniform(0.75, 1.25)
        self.speed_pps = FLY_SPEED_PPS * speed_ratio
        # 빨리 나는 새는 날갯짓도 빠르게: 날갯짓 빈도를 속도에 비례시킴
        self.action_per_time = ACTION_PER_TIME * speed_ratio

    def update(self):
        # 컴퓨터 성능(프레임 레이트)과 무관하게 일정한 속도로 날갯짓하도록 frame_time 기반으로 진행
        self.frame = (self.frame + FRAMES_PER_ACTION * self.action_per_time * game_framework.frame_time) % FRAME_COUNT
        self.x += self.dir * self.speed_pps * game_framework.frame_time

        # 화면 가장자리에 닿으면 방향을 바꾸어 좌우로 반복 비행
        # 프레임 시간이 길어(창 드래그 등) 한 번에 경계를 크게 넘어간 경우에도
        # 경계 안쪽으로 되돌려 놓아 화면 밖에 머무르거나 떨리는 현상을 방지
        half_w = FRAME_WIDTH * BIRD_SCALE / 2
        right_limit = get_canvas_width() - half_w
        if self.x > right_limit:
            self.x = right_limit
            self.dir = -1
        elif self.x < half_w:
            self.x = half_w
            self.dir = 1

    def draw(self):
        index = int(self.frame)
        col = index % FRAME_COLS
        row = index // FRAME_COLS
        top, height = ROW_RECTS[row]
        # pico2d 는 이미지 좌표의 원점이 왼쪽 아래이므로 위쪽 기준 top 을 bottom 으로 변환
        bottom = SHEET_HEIGHT - top - height
        # 보정량은 원본 픽셀 단위이므로 그리는 배율을 곱해 화면 픽셀로 변환
        offset = ROW_OFFSETS[row] * BIRD_SCALE
        # 원본 그림은 오른쪽을 바라보므로, 왼쪽으로 날 때는 좌우 반전('h')하여 그림
        flip = '' if self.dir == 1 else 'h'
        offset_x = (ANCHOR_X - FRAME_WIDTH / 2) * BIRD_SCALE * self.dir
        Bird.image.clip_composite_draw(col * FRAME_WIDTH, bottom, FRAME_WIDTH, height,
                                       0, flip, self.x - offset_x, self.y - offset,
                                       FRAME_WIDTH * BIRD_SCALE, height * BIRD_SCALE)
