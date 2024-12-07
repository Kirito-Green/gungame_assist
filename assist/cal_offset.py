import cv2
import numpy as np
import math
from config import *


def get_coordinates_from_matches(matches: list, kp1: list, kp2: list):
	'''
	Created on Wed Aug 17 21:00:36 2022

	Input :
			matches : [type=DMatch, ...]
			kp1     : KeyPoints from query image, [type=KeyPoint, ...]
			kp2     : KeyPoints from train image, [type=KeyPoint, ...]

	Return:
			list1   : stores the matching keypoints for query image
			list2   : stores the matching keypoints for train image

	len(matches) == len(kp1) == len(kp2)
	@author: zqfeng
	'''
	# Initialize lists
	list_kp1 = []
	list_kp2 = []

	# For each match...
	for mat in matches:
		# Get the matching keypoints for each of the images
		img1_idx = mat.queryIdx
		img2_idx = mat.trainIdx
		# x - columns
		# y - rows
		# Get the coordinates
		(x1, y1) = kp1[img1_idx].pt
		(x2, y2) = kp2[img2_idx].pt
		# Append to each list
		list_kp1.append((x1, y1))
		list_kp2.append((x2, y2))

	return list_kp1, list_kp2


def get_distance(img1, img2):
	# 初始化ORB
	orb = cv2.ORB_create()

	# 寻找关键点
	kp1 = orb.detect(img1)
	kp2 = orb.detect(img2)

	# 计算描述符
	kp1, des1 = orb.compute(img1, kp1)
	kp2, des2 = orb.compute(img2, kp2)

	# 画出关键点
	outimg1 = cv2.drawKeypoints(img1, keypoints=kp1, outImage=None)
	outimg2 = cv2.drawKeypoints(img2, keypoints=kp2, outImage=None)

	# 显示关键点
	# import numpy as np
	# outimg3 = np.hstack([outimg1, outimg2])
	# cv2.imshow("Key Points", outimg3)
	# cv2.waitKey(0)

	# 初始化 BFMatcher
	bf = cv2.BFMatcher(cv2.NORM_HAMMING)

	# 对描述子进行匹配
	matches = bf.match(des1, des2)

	# 计算最大距离和最小距离
	min_distance = matches[0].distance
	max_distance = matches[0].distance
	for x in matches:
		if x.distance < min_distance:
			min_distance = x.distance
		if x.distance > max_distance:
			max_distance = x.distance

	# 筛选匹配点
	'''
			当描述子之间的距离大于两倍的最小距离时，认为匹配有误。
			但有时候最小距离会非常小，所以设置一个经验值30作为下限。
	'''
	good_match = []
	for x in matches:
		if x.distance <= max(2 * min_distance, 30):
			good_match.append(x)

	# 绘制匹配结果
	draw_match(img1, img2, kp1, kp2, good_match)

	list_kp1, list_kp2 = get_coordinates_from_matches(good_match, kp1, kp2)
	num_points = len(list_kp1)
	distance = np.array(list_kp1) - np.array(list_kp2) / 0.817
	print(distance)

	return np.mean(np.array(list_kp1) - np.array(list_kp2), axis=0) / 0.817


def draw_match(img1, img2, kp1, kp2, match):
	outimage = cv2.drawMatches(img1, kp1, img2, kp2, match, outImg=None)
	cv2.imshow("Match Result", outimage)
	cv2.waitKey(0)


def angle2radian(angle):
	return angle / 180.0 * math.pi


def radian2angle(radian):
	return radian / math.pi * 180.0


def cal_2d_dist(p1, p2):
	return math.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]))


def cal_3d_dist_special(dx, dy):
	def cal_mouse_dist(dx, length, fov, comp):
		theta = angle2radian(fov / 2)  # 弧度
		d = length / math.tan(theta)
		return math.atan(dx / d) / theta * length * comp

	dx_3d = cal_mouse_dist(dx, screen_center_width, hfov, hcomp)
	dy_3d = vcomp * cal_mouse_dist(dy, screen_center_height, vfov, vcomp)
	return int(dx_3d), int(dy_3d)


def cal_3d_dist(mouse_pos, dx, dy):  # 考虑视角偏差
	vfov_half = angle2radian(vfov / 2)  # 弧度
	d = screen_center_height / math.tan(vfov_half)
	alpha = mouse_pos[1] / (vcomp * screen_center_height) * vfov / 2 # 下正上负
	alpha_radian = angle2radian(alpha)
	x, y, z = d, dx, -dy
	x_, y_, z_ = d * math.cos(alpha_radian) - dy * math.sin(alpha_radian), dx, -d * math.sin(alpha_radian) - dy * math.cos(alpha_radian)
	r = d / math.cos(angle2radian(dfov / 2))
	phi = radian2angle(math.asin(-z_ / r))
	theta = radian2angle(math.atan(y_ / x_))
	dx_3d = theta / (hfov / 2) * screen_center_width * hcomp
	dy_3d = (phi - alpha) / (vfov / 2) * screen_center_height * vcomp
	print(dx_3d, dy_3d)
	return int(dx_3d), int(dy_3d)


def cal_hvfov(dfov): # return radian
	dfov_radian = angle2radian(dfov)
	theta = math.atan(1 / screen_size)
	hfov = 2 * math.atan(math.tan(dfov_radian / 2) * math.cos(theta))
	vfov = 2 * math.atan(math.tan(dfov_radian / 2) * math.sin(theta))
	print(radian2angle(hfov), radian2angle(vfov))


def cal_dfov(hfov, vfov): # in angle
	hfov_radian = angle2radian(hfov)
	vfov_radian = angle2radian(vfov)
	return radian2angle(2 * math.atan(math.sqrt(math.pow(math.tan(hfov_radian / 2.0), 2.0) + math.pow(math.tan(vfov_radian / 2.0), 2.0))))


def cal_vfov_from_hfov(hfov): # in angle
	return radian2angle(2 * math.atan(1 / screen_size * math.tan(angle2radian(hfov) / 2)))


def is_at_head(keypoints):
  nose = keypoints[0][0:2]
  nose = np.array([nose[1] * width, nose[0] * height])
  left_ear = keypoints[3][0:2]
  left_ear = np.array([left_ear[1] * width, left_ear[0] * height])
  right_ear = keypoints[4][0:2]
  right_ear = np.array([right_ear[1] * width, right_ear[0] * height])
  center = (left_ear + right_ear) / 2
  # radius = min(cal_2d_dist(nose, left_ear), cal_2d_dist(nose, right_ear))
  radius = max(cal_2d_dist(left_ear, right_ear) / 2, (cal_2d_dist(left_ear, nose) + cal_2d_dist(right_ear, nose)) / 2)
  # print('pos', nose, left_ear, right_ear, center)
  return cal_2d_dist(center, (width / 2, height / 2)) < radius


if __name__ == "__main__":
	# img1 = cv2.imread("../imgs/img1.png")
	# img2 = cv2.imread("../imgs/img2.png")
	# distance = get_distance(img1, img2)
	# print(distance)
	cal_3d_dist([0, 0], 540, 0)
	# print(cal_hvfov(90))
	# print(cal_dfov(hfov, vfov))
	# print(cal_vfov_from_hfov(95))
	# print(cal_dfov(hfov, vfov))