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
from demo import get_person_pos, is_person
from screenshot import get_screenshot
from lghub import driver, mouse_move_PID
from cal_offset import cal_2d_dist, cal_3d_dist, is_at_head
from util import delay_ms

ctl = pk.Controller()
mouse = pm.Controller()

mouse_pos = [0, 0]


flag_ctrl = 0


def on_click(x, y, button, pressed):
	global flag_ctrl
	if pressed:
		if button == Button.middle:
			listener_pm.stop()
			listener_pk.stop()
		elif button == Button.left:
			if 'pubg' in gun_game:
				with ctl.pressed(key_fastmark):  # 快速标记
					pass

			lock_state = win32api.GetKeyState(win32con.VK_CAPITAL)  # 0 release 1 pressed
			if lock_state:
				flag_ctrl = 1
	else:
		if button == Button.left:
			flag_ctrl = 0


key_list = [Key.up, Key.down, Key.left, Key.right, Key.home]

shoot_scope_start = 0

def on_press(key):
	global gun_state, comp_dist_first, comp_dist_second, scope_state_first, scope_state_second, mouse_pos
	if key == Key.end:  # 侧上键锁头并开枪
		img = get_screenshot(width, height)  # 5ms
		if img is not None:
			keypoints = get_person_pos(img)  # gpu 30ms
			keypoints = keypoints[0]  # one person
			if is_person(keypoints):
				target_pos = keypoints[0]  # head
				target_detect_x = target_pos[1] * width
				target_detect_y = target_pos[0] * height
				print('lock target [{}, {}]'.format(int(target_detect_x), int(target_detect_y)))
				# 模型计算
				dx_3d, dy_3d = cal_3d_dist(mouse_pos,
				                           target_detect_x - screen_detect_width_half,
				                           target_detect_y - screen_detect_height_half)  # 模型计算值
				driver.move_R(dx_3d, dy_3d)
				# mouse.click(Button.left, 1)
				mouse_pos[0] += dx_3d
				mouse_pos[1] += dy_3d

	if hasattr(key, 'char') and key.char == open_scope_and_lock_head:  # 侧下键开镜锁头并开枪
		if not shoot_scope_start:
			mouse.click(Button.right, 1)
			time.sleep(0.1)
		img = get_screenshot(width, height)
		if img is not None:
			keypoints = get_person_pos(img)  # gpu 30ms
			keypoints = keypoints[0]  # one person
			if is_person(keypoints):
				target_pos = keypoints[0]  # 0 head 5 6 shoulder
				target_detect_x = target_pos[1] * width
				target_detect_y = target_pos[0] * height
				print('lock target [{}, {}]'.format(int(target_detect_x), int(target_detect_y)))
				# 模型计算
				dx_3d, dy_3d = cal_3d_dist(target_detect_x - screen_detect_width_half,
				                           target_detect_y - screen_detect_height_half)  # 模型计算值
				driver.move_R(dx_3d, dy_3d)
				mouse.click(Button.left, 1)

	if 'csgo' in gun_game: # 键控鼠标移动
		if key == Key.up:
			driver.move_R(None, -key_ctrl_sens)
			mouse_pos[1] += -key_ctrl_sens
		elif key == Key.down:
			driver.move_R(None, key_ctrl_sens)
			mouse_pos[1] += key_ctrl_sens
		elif key == Key.left:
			driver.move_R(-key_ctrl_sens, None)
			mouse_pos[0] += -key_ctrl_sens
		elif key == Key.right:
			driver.move_R(key_ctrl_sens, None)
			mouse_pos[0] += key_ctrl_sens
		elif key == Key.home:
			# mouse_pos = (screen_center_width, screen_center_height)  # 鼠标校准
			mouse_pos = [0, 0]

		if key in key_list:
			print('mouse pos', mouse_pos)

	elif 'pubg' in gun_game:
		if key == Key.up:
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
		elif key == Key.enter:  # 切换武器压枪补偿量
			gun_state = not gun_state

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
	global shoot_start, shoot_scope_start
	if hasattr(key, 'char') and key.char == lock_head:
		shoot_start = 0
	elif hasattr(key, 'char') and key.char == open_scope_and_lock_head:  # TODO 开镜锁头锁头
		shoot_scope_start = 0
		# 切枪
		time.sleep(0.1)
		with ctl.pressed('3'):  # 刀
			pass
		time.sleep(0.1)
		with ctl.pressed('1'):  # 枪
			pass


def force_ctrl_thread():
	global flag_ctrl, gun_state, comp_dist_first, comp_dist_second, scope_state_first, scope_state_second
	while True:
		# 无模型固定参数控制
		lock_state = win32api.GetKeyState(win32con.VK_CAPITAL)  # 0 release 1 pressed
		if 'pubg' in gun_game:
			if lock_state and flag_ctrl and 'pubg' in gun_game:
				if gun_state == 0:
					driver.move_R(None, comp_dist_first * scope_list[scope_state_first])
				elif gun_state == 1:
					driver.move_R(None, comp_dist_second * scope_list[scope_state_second])
				time.sleep(force_delay)

		# 自动锁头
		elif lock_state:
			img = get_screenshot(width, height)  # 100us
			if img is not None:
				person_pos = get_person_pos(img)  # gpu 空载 20ms 负载 30ms
				for target_pos in person_pos[0][0:5]:  # nose eyes ears
					if target_pos[2] >= score_thres:  # y x
						target_x = int(x0 + target_pos[1] * width)
						target_y = int(y0 + target_pos[0] * height)
						dx_3d, dy_3d = cal_3d_dist(target_x - screen_detect_width_half, target_y - screen_detect_height_half)
						driver.move_R(dx_3d, dy_3d)
						break

		if not lock_state:
			time.sleep(0.1)  # 程序待机


if __name__ == "__main__":
	print('-----------gungame assist is started------------')
	if 'pubg' in gun_game:
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
			on_click=on_click
	) as listener_pm:
		listener_pm.join()
