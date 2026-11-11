import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 리소스 상대 경로 기준을 이 폴더로

from pico2d import open_canvas, delay, close_canvas
import game_framework

import play_mode as start_mode

open_canvas(1600, 600)
game_framework.run(start_mode)
close_canvas()

