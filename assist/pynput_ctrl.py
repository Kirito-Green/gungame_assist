# 测试pynput鼠标和键盘控制
import pynput.keyboard as pk
import pynput.mouse as pm
from pynput.keyboard import Key
from pynput.mouse import Button
import time
ctl = pk.Controller()
mouse = pm.Controller()


if __name__ == '__main__':
	time.sleep(3)
	while True:
		ctl.pressed(Key.ctrl)  # 急停
		# ctl.pressed('w')
		# ctl.pressed('s')
		# ctl.pressed('a')
		# ctl.pressed('d')
		time.sleep(1)
		# mouse.click(Button.left, 1)
		ctl.release(Key.ctrl)
		# ctl.release('w')
		# ctl.release('s')
		# ctl.release('a')
		# ctl.release('d')
		time.sleep(1)