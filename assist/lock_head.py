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
from util import delay_ms

ctl = pk.Controller()
mouse = pm.Controller()


def on_move(x, y):
	# print('Pointer moved to {0}'.format(mouse_pos))
	# print('mouse', mouse.position)
	# print(pyautogui.position())
	# mouse_pos = win32api.GetCursorPos()
	# print(mouse_pos)
	pass


flag_ctrl = 0
def on_click(x, y, button, pressed):
	global flag_ctrl
	if pressed:
		if button == Button.middle:
			listener_pm.stop()
			listener_pk.stop()
		elif button == Button.left:
			if 'pubg' in gun_game:
				with ctl.pressed( # 快速标记
				        key_fastmark):
				    pass

			lock_state = win32api.GetKeyState(win32con.VK_CAPITAL)  # 0 release 1 pressed
			if lock_state:
				flag_ctrl = 1
	else:
		if button == Button.left:
			flag_ctrl = 0


key_list = [Key.up, Key.down, Key.left, Key.right, Key.enter]

flag_open_scope = 0
def on_press(key):
	global gun_state, comp_dist_first, comp_dist_second, scope_state_first, scope_state_second
	if hasattr(key, 'char') and key.char == lock_head:  # 侧上键锁头并开枪
		img = get_screenshot(width, height)  # 5ms
		if img is not None:
			person_pos = get_head_pos(img)  # gpu 30ms
			if len(person_pos) > 0:  # 1 17 3
				for head_pos in person_pos[0][0:5]:  # nose eyes ears
					if head_pos[2] >= score_thres:  # y x
						head_x = int(x0 + head_pos[1] * width)
						head_y = int(y0 + head_pos[0] * height)
						dx_3d, dy_3d = cal_3d_distance(head_x - screen_center_width, head_y - screen_center_height)
						driver.move_R(dx_3d, dy_3d)
						delay_ms(10)  # TODO 优化
						# driver.click_Left_down()
						# driver.click_Left_up()
						mouse.click(Button.left, 1)
						break

	if hasattr(key, 'char') and key.char == open_scope_and_lock_head:  # 侧下键开镜锁头并开枪
		global flag_open_scope
		if not flag_open_scope: # 防多次侧键识别
			flag_open_scope = 1
			# driver.click_Right_down()
			# driver.click_Right_up()
			mouse.click(Button.right, 1)
			time.sleep(0.1)
			img = get_screenshot(width, height)
			if img is not None:
				person_pos = get_head_pos(img)
				if len(person_pos) > 0:  # 1 17 3
					for head_pos in person_pos[0][0:13]:  # above of leg
						if head_pos[2] >= score_thres:  # y x
							head_x = int(x0 + head_pos[1] * width)
							head_y = int(y0 + head_pos[0] * height)
							dx_3d, dy_3d = cal_3d_distance(head_x - screen_center_width, head_y - screen_center_height)
							driver.move_R(dx_3d, dy_3d)
							# time.sleep(0.1)
							delay_ms(20)
							# driver.click_Left_down()
							# driver.click_Left_up()
							mouse.click(Button.left, 1)
							break
			# 切枪
			time.sleep(0.1)
			with ctl.pressed(  # 刀
					'3'):
				pass
			time.sleep(0.1)
			with ctl.pressed(  # 枪
					'1'):
				pass

	elif key == Key.up:
		if gun_state == 0:
			comp_dist_first += comp_ctrl_sens
		elif gun_state == 1:
			comp_dist_second += comp_ctrl_sens
	elif key == Key.down:
		if gun_state == 0:
			comp_dist_first = max(0, comp_dist_first - 1)
		elif gun_state == 1:
			comp_dist_second = max(0, comp_dist_second - 1)
	elif key == Key.left:  # 减小倍镜
		if gun_state == 0:
			scope_state_first = (scope_state_first - 1 + len(scope_list)) % len(scope_list)
		elif gun_state == 1:
			scope_state_second = (scope_state_second - 1 + len(scope_list)) % len(scope_list)
	elif key == Key.right:  #
		if gun_state == 0:
			scope_state_first = (scope_state_first + 1) % len(scope_list)
		elif gun_state == 1:
			scope_state_second = (scope_state_second + 1) % len(scope_list)
	elif key == Key.enter: # 切换武器压枪补偿量
		gun_state = not gun_state
	elif key == Key.end:
		mouse.position = (screen_center_width, screen_center_height) # 鼠标校准

	if key in key_list:
		if gun_state == 0:
			print('comp first:', comp_dist_first,
			      'scope:', scope_list[scope_state_first],
			      'comp value:', comp_dist_first * scope_list[scope_state_first] / force_delay, '/s')
		elif gun_state == 1:
			print('comp second:', comp_dist_second,
			      'scope:', scope_list[scope_state_second],
			      'comp value:', comp_dist_second * scope_list[scope_state_second] / force_delay, '/s')



def on_release(key):
	if hasattr(key, 'char') and key.char == open_scope_and_lock_head:  # TODO 开镜锁头锁头
		global flag_open_scope
		flag_open_scope = 0


def force_ctrl_thread():
	global flag_ctrl, gun_state, comp_dist_first, comp_dist_second, scope_state_first, scope_state_second
	while True:
		# 无模型固定参数控制
		lock_state = win32api.GetKeyState(win32con.VK_CAPITAL)  # 0 release 1 pressed
		if lock_state and flag_ctrl and 'pubg' in gun_game:
			if gun_state == 0:
				driver.move_R(None, comp_dist_first * scope_list[scope_state_first])
			elif gun_state == 1:
				driver.move_R(None, comp_dist_second * scope_list[scope_state_second])
			time.sleep(force_delay)

		# 自动锁头开枪
		elif lock_state:
			img = get_screenshot(width, height)  # 100us
			if img is not None:
				person_pos = get_head_pos(img)  # gpu 空载 20ms 负载 30ms
				if len(person_pos) > 0:  # 1 17 3
					for head_pos in person_pos[0][0:5]:  # nose eyes ears
						if head_pos[2] >= score_thres:  # y x
							head_x = int(x0 + head_pos[1] * width)
							head_y = int(y0 + head_pos[0] * height)
							dx_3d, dy_3d = cal_3d_distance(head_x - screen_center_width, head_y - screen_center_height)
							driver.move_R(dx_3d, dy_3d)
							delay_ms(10)
							mouse.click(Button.left, 1)
							break

		if not lock_state:
			time.sleep(0.1) # 程序待机


if __name__ == "__main__":
	print('-----------pubg assist is started------------')
	print('comp first:', comp_dist_first,
	      'scope:', scope_list[scope_state_first],
	      'comp value:', comp_dist_first * scope_list[scope_state_first] / force_delay, '/s')

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
