import tensorflow as tf
import tensorflow_hub as hub
import cv2
import numpy as np

# 加载 MoveNet 模型
model = hub.load('https://tfhub.dev/google/movenet/singlepose/lightning/4')
model = hub.load('https://tfhub.dev/google/movenet/singlepose/lightning/4')
movenet = model.signatures['serving_default']

# 定义关键点
KEYPOINTS = {
    0: 'nose', 1: 'left_eye', 2: 'right_eye', 3: 'left_ear', 4: 'right_ear',
    5: 'left_shoulder', 6: 'right_shoulder', 7: 'left_elbow', 8: 'right_elbow',
    9: 'left_wrist', 10: 'right_wrist', 11: 'left_hip', 12: 'right_hip',
    13: 'left_knee', 14: 'right_knee', 15: 'left_ankle', 16: 'right_ankle'
}

# 定义骨架连接
EDGES = {
    (0, 1): 'm', (0, 2): 'm', (1, 3): 'm', (2, 4): 'm', (0, 5): 'm', (0, 6): 'm',
    (5, 7): 'm', (7, 9): 'm', (6, 8): 'm', (8, 10): 'm', (5, 6): 'y', (5, 11): 'm',
    (6, 12): 'm', (11, 12): 'y', (11, 13): 'm', (13, 15): 'm', (12, 14): 'm', (14, 16): 'm'
}

def draw_connections(frame, keypoints, edges, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))
    
    for edge, color in edges.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]
        
        if (c1 > confidence_threshold) & (c2 > confidence_threshold):      
            cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

def draw_keypoints(frame, keypoints, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))
    
    for kp in shaped:
        ky, kx, kp_conf = kp
        if kp_conf > confidence_threshold:
            cv2.circle(frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)

def loop_through_people(frame, keypoints_with_scores, edges, confidence_threshold):
    for person in keypoints_with_scores:
        draw_connections(frame, person, edges, confidence_threshold)
        draw_keypoints(frame, person, confidence_threshold)
    pass


def process_image(input_img, output_img):
    pass

def process_video(input_video, output_video):
    # 打开输入视频文件
    cap = cv2.VideoCapture(input_video)
    
    # 获取视频的属性（宽度、高度、帧率）
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 设置输出视频的编码器和创建VideoWriter对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    while cap.isOpened():
        # 读取一帧
        ret, frame = cap.read()
        if not ret:
            break  # 如果无法读取帧（视频结束），则退出循环

        # 预处理帧
        # 调整图像大小为MoveNet模型的输入尺寸(192x192)
        input_image = cv2.resize(frame, (192, 192))
        # 将颜色空间从BGR转换为RGB
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        # 将图像转换为TensorFlow张量，并设置数据类型为int32
        input_image = tf.cast(input_image, dtype=tf.int32)
        # 添加批次维度
        input_image = tf.expand_dims(input_image, axis=0)

        # 运行MoveNet模型
        results = movenet(input_image)
        # 获取关键点预测结果
        keypoints_with_scores = results['output_0'].numpy()

        # 在帧上绘制关键点和连接
        # EDGES是预定义的关键点连接关系
        # 0.3是置信度阈值
        loop_through_people(frame, keypoints_with_scores, EDGES, 0.3)

        # 将处理后的帧写入输出视频
        out.write(frame)

        # 显示处理后的帧（可选）
        cv2.imshow('MoveNet Pose Estimation', frame)
        # 如果用户按'q'键，则退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    out.release()
    cv2.destroyAllWindows()


# 如果你想处理摄像头实时视频，可以使用以下函数
def process_webcam():
    cap = cv2.VideoCapture(0)  # 0 表示默认摄像头

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 预处理帧
        input_image = cv2.resize(frame, (192, 192))
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        input_image = tf.cast(input_image, dtype=tf.int32)
        input_image = tf.expand_dims(input_image, axis=0)

        # 运行模型
        results = movenet(input_image)
        keypoints_with_scores = results['output_0'].numpy()

        # 绘制关键点和连接
        loop_through_people(frame, keypoints_with_scores, EDGES, 0.3)

        # 显示处理后的帧
        cv2.imshow('MoveNet Pose Estimation (Webcam)', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def get_head_pos(img):
    # 预处理帧
    # 调整图像大小为MoveNet模型的输入尺寸(192x192)
    input_image = cv2.resize(img, (192, 192))
    # 将颜色空间从BGR转换为RGB
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    # 将图像转换为TensorFlow张量，并设置数据类型为int32
    input_image = tf.cast(input_image, dtype=tf.int32)
    # 添加批次维度
    input_image = tf.expand_dims(input_image, axis=0)

    # 运行MoveNet模型
    results = movenet(input_image)
    # 获取关键点预测结果
    keypoints_with_scores = results['output_0'].numpy()

    # 在帧上绘制关键点和连接
    # EDGES是预定义的关键点连接关系
    # 0.3是置信度阈值
    loop_through_people(img, keypoints_with_scores, EDGES, 0.3)
    # 显示处理后的帧（可选）
    cv2.imshow('MoveNet Pose Estimation', img)
    cv2.waitKey(1)

    return keypoints_with_scores[0]


# 主程序
if __name__ == "__main__":
    #使用时替换文件地址
    input_video = r"D:\learn_more_from_life\computer\Python\Deep_learning\opensource\Vision\data\video\pubg1.mp4"
    output_video = "../output/output.mp4"
    img = cv2.imread("../imgs/test.png")
    get_head_pos(img)
    # process_video(input_video, output_video)
    # print(f"处理完成。输出视频保存在: {output_video}")
    #使用摄像头，取消下面这行的注释
    # process_webcam()
