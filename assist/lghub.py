import ctypes
import time
import pynput
from simple_pid import PID

driver = ctypes.CDLL("D:\\Software\\script\\driver\\MouseControl\\MouseControl.dll")

'''
 // 相对移动
 move_R(int x, int y);
 // 绝对移动
 move_Abs(int x, int y);

 // 左键按下
 click_Left_down();
 // 左键松开
 click_Left_up();

 // 右键按下
 click_Right_down();
 // 右键松开
 click_Right_up();
'''

def linear_interpolation(deltax, deltay, num_steps, delay):  # 绝对平滑移动
	dx = int(deltax / num_steps)
	dy = int(deltay / num_steps)

	for i in range(1, num_steps + 1):
		driver.move_R(dx, dy)
		time.sleep(delay)


def mouse_move_PID(mouse, target_x, target_y):
	while True:
		if abs(target_x - mouse.position[0]) < 3 and abs(target_y - mouse.position[1]) < 3:
			break
		pid_x = PID(0.25, 0.01, 0.01, setpoint=target_x)
		pid_y = PID(0.25, 0.01, 0.01, setpoint=target_y)
		next_x, next_y = pid_x(mouse.position[0]), pid_y(mouse.position[1])
		driver.move_R(int(round(next_x)), int(round(next_y)), False)  # 鼠标移动
		# print(mouse.position) # 打印鼠标位置


if __name__ == "__main__":
	# driver.move_R(500, None)
	# linear_interpolation(200, 200, num_steps=20, delay=0.01)
	time.sleep(3)
	# driver.move_R(890, None)
	driver.move_R(None, -592)