import cv2
import numpy as np
import time
import pyautogui
import mss
import dxcam
from config import *

camera = dxcam.create(output_color="RGB")

def get_screenshot(width, height):
    # region = [int(screen_width/2-width/2), int(screen_height/2-height/2),
    #           width, height]
    # img = pyautogui.screenshot(region=region) # 33.3ms
    # return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    # with mss.mss() as sct:
    #     # The screen part to capture
    #     region = {'top': int(screen_width/2-width/2), 'left': int(screen_height/2-height/2), 'width': width, 'height': height}
    #     # Grab the data
    #     img = np.asarray(sct.grab(region)) # 16.7ms
    # return img

    region = [int(screen_width / 2 - width / 2), int(screen_height / 2 - height / 2),
              int(screen_width / 2 + width / 2), int(screen_height / 2 + height / 2)]
    return camera.grab(region=region) # 70us


if __name__ == "__main__":
    start = time.time()
    img = get_screenshot(640, 480)
    end = time.time()
    print("screenshot time:", end - start)
    cv2.imshow("screenshot", np.asarray(img))
    # cv2.imwrite("../imgs/test.png", img)
    cv2.waitKey(0)