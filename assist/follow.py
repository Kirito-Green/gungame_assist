import win32api
import win32con
import time

from screenshot import get_screenshot
from demo import get_head_pos
from lghub import *


def main():
    screen_width = 1920
    screen_height = 1080
    width = 640
    height = 480
    x0 = int(screen_width / 2 - width / 2)
    y0 = int(screen_height / 2 - height / 2)
    score_thres = 0.35

    while True:
        try:
            lock_state = win32api.GetKeyState(win32con.VK_CAPITAL)  # 0 release 1 pressed
            # print(lock_state)
            if lock_state == 1:
                img = get_screenshot(width, height)
                get_head_pos(img)
                person_pos = get_head_pos(img)
                if len(person_pos) > 0: # 1 17 3
                    head_pos = person_pos[0][0]
                    if head_pos[2] >= score_thres: # y x
                        head_x = int(x0 + head_pos[1] * width)
                        head_y = int(y0 + head_pos[0] * height)
                        driver.move_R(int(head_x - screen_width / 2), int(head_y - screen_height / 2))
                        # linear_interpolation(int(head_x-screen_width/2), int(head_y-screen_height/2), num_steps=20, delay=0.01)
                        break
            else:
                time.sleep(100 / 1000)
        except KeyboardInterrupt as e:
            print(e)


if __name__ == "__main__":
    main()
