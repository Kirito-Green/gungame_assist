import time


def delay_ms(ms): # 1-15ms
	# 毫秒延时
	delay_mark = time.time()
	delay_time = ms * 0.001
	while True:
		offset = time.time() - delay_mark
		if offset > delay_time:
			break
