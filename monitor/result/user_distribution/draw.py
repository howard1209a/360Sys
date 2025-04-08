import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 要处理的视频索引
video_indices = [2, 4, 5, 8, 9]

# 存储所有视频所有用户的角速度
all_vx = []
all_vy = []

for video_index in video_indices:
    base_dir = f"/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video{video_index}/motion"

    for i in range(1, 21):  # 用户 u1 ~ u20
        filename = f'u{i}_preprocessed.csv'
        filepath = os.path.join(base_dir, filename)

        if not os.path.exists(filepath):
            print(f'未找到文件：{filepath}，跳过')
            continue

        df = pd.read_csv(filepath)

        # 每秒一帧降采样（原数据为60Hz）
        df_downsampled = df.iloc[::60].reset_index(drop=True)

        # 计算角速度（单位：度/秒）
        vx = df_downsampled['Pose_Angle_x'].diff().abs().dropna()
        vy = df_downsampled['Pose_Angle_y'].diff().abs().dropna()

        all_vx.extend(vx.tolist())
        all_vy.extend(vy.tolist())

print(f"已读取完所有视频的用户角速度数据：vx={len(all_vx)} 条，vy={len(all_vy)} 条")

# === 绘图 ===

# 设置区间数量
num_bins = 15
max_vx = max(all_vx)
max_vy = max(all_vy)

bins_vx = np.linspace(0, max_vx, num_bins + 1)
bins_vy = np.linspace(0, max_vy, num_bins + 1)

hist_vx, _ = np.histogram(all_vx, bins=bins_vx)
hist_vy, _ = np.histogram(all_vy, bins=bins_vy)

percent_vx = hist_vx / sum(hist_vx)
percent_vy = hist_vy / sum(hist_vy)

plt.figure(figsize=(14, 6))

# 经度角速度
plt.subplot(1, 2, 1)
plt.bar(bins_vx[:-1], percent_vx, width=np.diff(bins_vx), align='edge', edgecolor='black', color='skyblue')
plt.xlabel('经度角速度（度/秒）')
plt.ylabel('占比')
plt.title('所有视频用户的经度角速度分布')
plt.grid(True)

# 纬度角速度
plt.subplot(1, 2, 2)
plt.bar(bins_vy[:-1], percent_vy, width=np.diff(bins_vy), align='edge', edgecolor='black', color='salmon')
plt.xlabel('纬度角速度（度/秒）')
plt.ylabel('占比')
plt.title('所有视频用户的纬度角速度分布')
plt.grid(True)

plt.tight_layout()
plt.show()
