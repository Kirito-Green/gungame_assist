# env: tensorflow_gpu
# 侧键定位爆头
# 辅助压强可调节
import pyautogui
import win32api
import win32con
import time
import threading
import numpy as np
import pynput.keyboard as pk
import pynput.mouse as pm
from pynput.keyboard import Key
from pynput.mouse import Button

from config import *
from demo import get_head_pos
from screenshot import get_screenshot
from lghub import *
from cal_offset import cal_3d_distance

ctl = pk.Controller()
mouse = pm.Controller()

mouse_pos = (0, 0)


def on_move(x, y):
	global mouse_pos
	mouse_pos = (x, y)
	# print('Pointer moved to {0}'.format(mouse_pos))
	# print('mouse', mouse.position)


flag_ctrl = 0


def on_click(x, y, button, pressed):
	global flag_ctrl
	if pressed:
		if button == Button.middle:
			listener_pm.stop()
			listener_pk.stop()
		elif button == Button.left:
			# with ctl.pressed( # 快速标记
			#         key_fastmark):
			#     pass

			lock_state = win32api.GetKeyState(win32con.VK_CAPITAL)  # 0 release 1 pressed
			if lock_state:
				mouse.position = (screen_center_width, screen_center_height)
			flag_ctrl = 1
	else:
		if button == Button.left:
			flag_ctrl = 0


def on_press(key):
	global gun_state, comp_dist_first, comp_dist_second
	if hasattr(key, 'char') and key.char == lock_head:  # 侧上键锁头并开枪
		img = get_screenshot(width, height)
		person_pos = get_head_pos(img)
		if len(person_pos) > 0:  # 1 17 3
			for head_pos in person_pos[0][0:3]:  # nose eyes
				if head_pos[2] >= score_thres:  # y x
					head_x = int(x0 + head_pos[1] * width)
					head_y = int(y0 + head_pos[0] * height)
					dx_3d, dy_3d = cal_3d_distance(head_x - screen_center_width, head_y - screen_center_height)
					driver.move_R(dx_3d, dy_3d)
					time.sleep(0.008)
					driver.click_Left_down()
					driver.click_Left_up()
					break

	if hasattr(key, 'char') and key.char == open_scope_and_lock_head:  # 侧下键开镜锁头并开枪
		driver.click_Right_down()
		driver.click_Right_up()
		time.sleep(0.1)
		img = get_screenshot(width, height)
		person_pos = get_head_pos(img)
		if len(person_pos) > 0:  # 1 17 3
			for head_pos in person_pos[0][0:13]:  # above of leg
				if head_pos[2] >= score_thres:  # y x
					head_x = int(x0 + head_pos[1] * width)
					head_y = int(y0 + head_pos[0] * height)
					dx_3d, dy_3d = cal_3d_distance(head_x - screen_center_width, head_y - screen_center_height)
					driver.move_R(dx_3d, dy_3d)
					time.sleep(0.05)
					driver.click_Left_down()
					driver.click_Left_up()
					break
		time.sleep(0.1)
		# 切枪
		with ctl.pressed( # 刀
		      '3'):
		    pass
		time.sleep(0.1)
		with ctl.pressed( # 刀
		      '1'):
		    pass

	elif key == Key.left or key == Key.right:
		gun_state = not gun_state
		print('gun state is', gun_state + 1)
	elif key == Key.up:
		if gun_state == 0:
			comp_dist_first += comp_ctrl_sens
			print('comp first is', comp_dist_first)
		elif gun_state == 1:
			comp_dist_second += comp_ctrl_sens
			print('comp second is', comp_dist_second)
	elif key == Key.down:
		if gun_state == 0:
			comp_dist_first -= comp_ctrl_sens
			print('comp first is', comp_dist_first)
		elif gun_state == 1:
			comp_dist_second -= comp_ctrl_sens
			print('comp second is', comp_dist_second)


def on_release(key):
	if hasattr(key, 'char') and key.char == lock_head:  # 结束锁头
		global lock_head_flag
		lock_head_flag = 0


def force_ctrl_thread():
	global flag_ctrl, gun_state, comp_dist_first, comp_dist_second
	while True:
		# 无模型固定参数控制
		lock_state = win32api.GetKeyState(win32con.VK_CAPITAL)  # 0 release 1 pressed
		if lock_state and flag_ctrl:
			if gun_state == 0:
				driver.move_R(None, comp_dist_first)
			elif gun_state == 1:
				driver.move_R(None, comp_dist_second)
		time.sleep(force_delay)

		# 反馈控制
		# lock_state = win32api.GetKeyState(win32con.VK_CAPITAL)  # 0 release 1 pressed
		# if lock_state and flag_ctrl:
		#     global mouse_pos
		#     x, y = mouse_pos # 当前位置
		#     print(x, y)
		#     driver.move_R(screen_center_width - x, screen_center_height - y)
		#     time.sleep(force_delay)


if __name__ == "__main__":
	print('-----------pubg assist is started------------')
	t = threading.Thread(target=force_ctrl_thread)
	t.daemon = True
	t.start()

	listener_pk = pk.Listener(
	    on_press=on_press,
	    on_release=on_release
	)
	listener_pk.start()

	with pm.Listener(
	        on_move=on_move,
	        on_click=on_click
	) as listener_pm:
	    listener_pm.join()
