import cv2
import numpy as np


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


if __name__ == "__main__":
    img1 = cv2.imread("../imgs/img1.png")
    img2 = cv2.imread("../imgs/img2.png")
    distance = get_distance(img1, img2)
    print(distance)