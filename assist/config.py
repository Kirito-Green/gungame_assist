import enum

# 游戏参数
key_fastmark = 'p' # 快速标记按键
key_eaglevision = 'o' # 鹰眼锁定
game_sens = 32/50

# 屏幕参数
screen_width = 1920
screen_height = 1080
screen_center_width = int(screen_width / 2)
screen_center_height = int(screen_height / 2)
# width = 640
# height = 480
width = 800
height = 600
x0 = int(screen_center_width - width / 2)
y0 = int(screen_center_height - height / 2)

# 阈值
score_thres = 0.3

# 压枪
comp_dist_first = 50
comp_dist_second = 50
comp_ctrl_sens = 10
gun_state = 0 # 一号武器
force_delay = 0.08