import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 要处理的视频索引
video_indices = [2, 4, 5, 8, 9]

# 存储所有视频所有用户的角速度
all_vx_1s = []
all_vy_1s = []
all_vx_2s = []
all_vy_2s = []
all_vx_5s = []
all_vy_5s = []
all_vx_8s = []
all_vy_8s = []

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

        # 计算不同时间窗口（1s, 2s, 5s, 8s）的角速度（单位：度/秒）

        # 1秒角速度
        vx_1s = df_downsampled['Pose_Angle_x'].diff().abs().dropna()
        vy_1s = df_downsampled['Pose_Angle_y'].diff().abs().dropna()

        # 2秒角速度（每2秒为一个窗口计算一次角速度）
        vx_2s = df_downsampled['Pose_Angle_x'].diff(2).abs().dropna()
        vy_2s = df_downsampled['Pose_Angle_y'].diff(2).abs().dropna()

        # 5秒角速度（每5秒为一个窗口计算一次角速度）
        vx_5s = df_downsampled['Pose_Angle_x'].diff(5).abs().dropna()
        vy_5s = df_downsampled['Pose_Angle_y'].diff(5).abs().dropna()

        # 8秒角速度（每8秒为一个窗口计算一次角速度）
        vx_8s = df_downsampled['Pose_Angle_x'].diff(8).abs().dropna()
        vy_8s = df_downsampled['Pose_Angle_y'].diff(8).abs().dropna()

        # 将角速度数据存储
        all_vx_1s.extend(vx_1s.tolist())
        all_vy_1s.extend(vy_1s.tolist())
        all_vx_2s.extend(vx_2s.tolist())
        all_vy_2s.extend(vy_2s.tolist())
        all_vx_5s.extend(vx_5s.tolist())
        all_vy_5s.extend(vy_5s.tolist())
        all_vx_8s.extend(vx_8s.tolist())
        all_vy_8s.extend(vy_8s.tolist())

print(f"已读取完所有视频的用户角速度数据：")
print(f"vx_1s={len(all_vx_1s)} 条，vy_1s={len(all_vy_1s)} 条")
print(f"vx_2s={len(all_vx_2s)} 条，vy_2s={len(all_vy_2s)} 条")
print(f"vx_5s={len(all_vx_5s)} 条，vy_5s={len(all_vy_5s)} 条")
print(f"vx_8s={len(all_vx_8s)} 条，vy_8s={len(all_vy_8s)} 条")

# === 绘图 ===

# 设置区间数量
num_bins = 15
max_vx_1s = max(all_vx_1s)
max_vy_1s = max(all_vy_1s)
max_vx_2s = max(all_vx_2s)
max_vy_2s = max(all_vy_2s)
max_vx_5s = max(all_vx_5s)
max_vy_5s = max(all_vy_5s)
max_vx_8s = max(all_vx_8s)
max_vy_8s = max(all_vy_8s)

# 设置所有角速度的最大值，避免显示不完全
max_vx = max(max_vx_1s, max_vx_2s, max_vx_5s, max_vx_8s)
max_vy = max(max_vy_1s, max_vy_2s, max_vy_5s, max_vy_8s)

bins_vx_1s = np.linspace(0, max_vx, num_bins + 1)
bins_vy_1s = np.linspace(0, max_vy, num_bins + 1)

bins_vx_2s = np.linspace(0, max_vx, num_bins + 1)
bins_vy_2s = np.linspace(0, max_vy, num_bins + 1)

bins_vx_5s = np.linspace(0, max_vx, num_bins + 1)
bins_vy_5s = np.linspace(0, max_vy, num_bins + 1)

bins_vx_8s = np.linspace(0, max_vx, num_bins + 1)
bins_vy_8s = np.linspace(0, max_vy, num_bins + 1)

# 计算直方图和CDF
hist_vx_1s, _ = np.histogram(all_vx_1s, bins=bins_vx_1s)
hist_vy_1s, _ = np.histogram(all_vy_1s, bins=bins_vy_1s)

hist_vx_2s, _ = np.histogram(all_vx_2s, bins=bins_vx_2s)
hist_vy_2s, _ = np.histogram(all_vy_2s, bins=bins_vy_2s)

hist_vx_5s, _ = np.histogram(all_vx_5s, bins=bins_vx_5s)
hist_vy_5s, _ = np.histogram(all_vy_5s, bins=bins_vy_5s)

hist_vx_8s, _ = np.histogram(all_vx_8s, bins=bins_vx_8s)
hist_vy_8s, _ = np.histogram(all_vy_8s, bins=bins_vy_8s)

percent_vx_1s = hist_vx_1s / sum(hist_vx_1s)
percent_vy_1s = hist_vy_1s / sum(hist_vy_1s)

percent_vx_2s = hist_vx_2s / sum(hist_vx_2s)
percent_vy_2s = hist_vy_2s / sum(hist_vy_2s)

percent_vx_5s = hist_vx_5s / sum(hist_vx_5s)
percent_vy_5s = hist_vy_5s / sum(hist_vy_5s)

percent_vx_8s = hist_vx_8s / sum(hist_vx_8s)
percent_vy_8s = hist_vy_8s / sum(hist_vy_8s)

# 计算CDF
cdf_vx_1s = np.cumsum(percent_vx_1s)
cdf_vy_1s = np.cumsum(percent_vy_1s)

cdf_vx_2s = np.cumsum(percent_vx_2s)
cdf_vy_2s = np.cumsum(percent_vy_2s)

cdf_vx_5s = np.cumsum(percent_vx_5s)
cdf_vy_5s = np.cumsum(percent_vy_5s)

cdf_vx_8s = np.cumsum(percent_vx_8s)
cdf_vy_8s = np.cumsum(percent_vy_8s)

# 设置字体为 Arial，字号为 14
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.size'] = 14

plt.figure(figsize=(14, 6))

# 经度角速度的CDF
plt.subplot(1, 2, 1)
plt.plot(bins_vx_1s[:-1], cdf_vx_1s, marker='o', label='1s', color='#B24475')
plt.plot(bins_vx_2s[:-1], cdf_vx_2s, marker='s', label='2s', color='#864CBC')
plt.plot(bins_vx_5s[:-1], cdf_vx_5s, marker='^', label='5s', color='#386688')
plt.plot(bins_vx_8s[:-1], cdf_vx_8s, marker='x', label='8s', color='#845D1C')
plt.xlabel('水平方向角速度(°/s)')
plt.ylabel('CDF')
plt.grid(True)
plt.legend()

# 纬度角速度的CDF
plt.subplot(1, 2, 2)
plt.plot(bins_vy_1s[:-1], cdf_vy_1s, marker='o', label='1s', color='#B24475')
plt.plot(bins_vy_2s[:-1], cdf_vy_2s, marker='s', label='2s', color='#864CBC')
plt.plot(bins_vy_5s[:-1], cdf_vy_5s, marker='^', label='5s', color='#386688')
plt.plot(bins_vy_8s[:-1], cdf_vy_8s, marker='x', label='8s', color='#845D1C')
plt.xlabel('竖直方向角速度(°/s)')
plt.ylabel('CDF')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
