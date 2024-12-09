import enum

# 游戏参数
key_fastmark = 'p'  # 快速标记按键
lock_head = 'l'  # 锁头
gun_game = 'pubg'
if 'csgo' in gun_game:
	hfov = 106.260205
	vfov = 73.739795
	dfov = 113.65618288622655
	hcomp = 1
	vcomp = 666 / 540
	screen_width = 1280
	screen_height = 960
	detect_width = 256
	detect_height = 256
elif 'pubg' in gun_game:
	hfov = 95
	vfov = 63.08828455525377
	hcomp = 890 / 960
	vcomp = 592 / 540
	screen_width = 1920
	screen_height = 1080
	detect_width = 512
	detect_height = 512
screen_size = screen_width / screen_height
screen_center_width = int(screen_width / 2)
screen_center_height = int(screen_height / 2)
screen_detect_width_half = int(detect_width / 2)
screen_detect_height_half = int(detect_height / 2)
x0 = int(screen_center_width - detect_width / 2)
y0 = int(screen_center_height - detect_height / 2)

# 阈值
score_thres = 0.40
img_score_thres = 0.1
dist_thres = 5
num_person_thres = 6

# 单发
min_shoot_gap = 0.15

# 压枪
comp_dist_first = 4
comp_dist_second = 4
comp_ctrl_sens = 1
gun_state = 0  # 一号武器
force_delay = 0.01
scope_state_first = 0
scope_state_second = 0
scope_list = [1, 2, 3, 4, 6, 8, 15]

# PID参数
Kp = 0.5
Ki = 0.06
Kd = 0.001

# 键控参数
key_ctrl_sens = 100