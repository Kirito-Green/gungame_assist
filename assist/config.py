import enum

# 游戏参数
key_fastmark = 'p'  # 快速标记按键
lock_head = '-'  # 锁头
open_scope_and_lock_head = '=' # 开镜并锁头
gun_game = 'csgo_online'
if 'csgo' in gun_game:
	hfov = 106.260205
	vfov = 73.739795
	hcomp = 1
	vcomp = 666 / 540
elif 'pubg' in gun_game:
	hfov = 95
	vfov = 63.08828455525377
	hcomp = 890 / 960
	vcomp = 592 / 540

# 屏幕参数
screen_width = 1920
screen_height = 1080
screen_size = screen_width / screen_height
screen_center_width = int(screen_width / 2)
screen_center_height = int(screen_height / 2)
width = 640
height = 480
# width = 800
# height = 600
x0 = int(screen_center_width - width / 2)
y0 = int(screen_center_height - height / 2)

# 阈值
score_thres = 0.3

# 压枪
comp_dist_first = 4
comp_dist_second = 4
comp_ctrl_sens = 1
gun_state = 0  # 一号武器
force_delay = 0.01
scope_state_first = 0
scope_state_second = 0
scope_list = [1, 2, 3, 4, 6, 8, 15]
