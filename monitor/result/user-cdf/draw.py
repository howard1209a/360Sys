import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 定义视频文件列表：视频 2、8、5、4、9
videos = [2, 8, 5, 4, 9]

# 创建一个字典来存储每个视频的角度偏移量
video_angle_differences = {video: [] for video in videos}

# 遍历视频
for video in videos:
    for user in range(1, 11):  # u1 到 u10
        csv_file = f"/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video{video}/motion/u{user}_preprocessed.csv"
        df = pd.read_csv(csv_file)

        # 提取经纬度（经度在前，纬度在后）
        longitudes = np.radians(df.iloc[:, 1].values)  # 转换为弧度
        latitudes = np.radians(df.iloc[:, 2].values)  # 转换为弧度

        # 计算相邻点之间的角度偏移量
        for i in range(len(latitudes) - 1):
            delta_lon = longitudes[i + 1] - longitudes[i]
            angle = np.arccos(
                np.sin(latitudes[i]) * np.sin(latitudes[i + 1]) +
                np.cos(latitudes[i]) * np.cos(latitudes[i + 1]) * np.cos(delta_lon)
            )
            angle_degrees = np.degrees(angle)  # 转换回角度

            # 仅保留小于或等于 2 度的角度偏移量
            if angle_degrees <= 2:
                video_angle_differences[video].append(angle_degrees)

# 绘制每个视频的 CDF 曲线
plt.figure(figsize=(10, 6))

# 为每个视频绘制单独的曲线
for video in videos:
    sorted_angles = np.sort(video_angle_differences[video])  # 排序
    cdf = np.arange(1, len(sorted_angles) + 1) / len(sorted_angles)  # 计算累积分布
    plt.plot(sorted_angles, cdf, label=f"Video {video}", linestyle="-", alpha=0.7)  # 去掉 marker 只绘制线

# 添加图例和标签
plt.xlabel("视野偏移角度 (度)")
plt.ylabel("累积分布函数 (CDF)")
plt.title("不同视频的用户视野偏移角度 CDF 对比")
plt.legend(title="视频", loc="lower right")
plt.grid(True)

# 显示图形
plt.show()
