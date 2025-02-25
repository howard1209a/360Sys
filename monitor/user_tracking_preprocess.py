import pandas as pd
import numpy as np

video_index = 4

for user_index in range(1, 11):
    # 读取 CSV 文件
    df = pd.read_csv(
        "/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video" + str(
            video_index) + "/motion/u" + str(user_index) + ".csv")

    # 将 AdjustedTime 列转换为 datetime 类型
    df['AdjustedTime'] = pd.to_datetime(df['AdjustedTime'], unit='s')

    # 设置采样时间戳为索引，且索引为 DatetimeIndex
    df.set_index('AdjustedTime', inplace=True)

    # 计算每个采样点对应的视野角度
    # 假设视频的宽度是1920，高度是1080
    video_width = 1920
    video_height = 1080

    # 每个像素对应的角度
    angle_x_per_pixel = 360 / video_width
    angle_y_per_pixel = 180 / video_height

    # 计算视野角度
    df['Pose_Angle_x'] = df['Pose_Point_x'] * angle_x_per_pixel
    df['Pose_Angle_y'] = df['Pose_Point_y'] * angle_y_per_pixel

    # 降低采样率：每秒 60 个样本
    # 假设每行的时间戳单位是秒
    df_resampled = df.resample('16.67L').mean()  # 16.67 ms ≈ 每秒 60 个采样点

    # 重置索引，使其从0开始
    df_resampled.reset_index(inplace=True)
    df_resampled.index = np.arange(len(df_resampled))  # 设置索引从 0 开始

    # 保存处理后的 CSV 文件
    df_resampled[['Pose_Angle_x', 'Pose_Angle_y']].to_csv(
        "/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video" + str(
            video_index) + "/motion/u" + str(user_index) + "_preprocessed.csv",
        index=True)

    print("处理完成，生成的文件为 'processed_file.csv'")
