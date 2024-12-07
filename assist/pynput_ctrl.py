# 测试pynput鼠标和键盘控制
import pynput.keyboard as pk
import pynput.mouse as pm
from pynput.keyboard import Key
from pynput.mouse import Button
import time
from config import *


ctl = pk.Controller()
mouse = pm.Controller()

def on_press(key):
	# print('press', key)
	if (hasattr(key, 'char') and key.char == lock_head) or str(key) == r"'\x10'":  # 和ctrl同时按下
		print('start')

def on_release(key):
	print('release', key)

if __name__ == '__main__':
	listener_pk = pk.Listener(
		on_press=on_press,
		on_release=on_release
	)
	listener_pk.start()
	listener_pk.join()

	# with pm.Listener(
	# 		on_move=on_move,
	# 		on_click=on_click
	# ) as listener_pm:
	# 	listener_pm.join()
