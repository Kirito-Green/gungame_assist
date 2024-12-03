import pyautogui
import cv2
import numpy as np


def get_screenshot(width, height):
    width_max = 1920
    height_max = 1080
    region = [int(width_max/2-width/2), int(height_max/2-height/2),
              width, height]
    img = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


if __name__ == "__main__":
    img = get_screenshot(640, 480)
    cv2.imshow("screenshot", np.asarray(img))
    cv2.imwrite("../imgs/test.png", img)
    cv2.waitKey(0)