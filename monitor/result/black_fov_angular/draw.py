import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 要处理的视频索引
video_indices = [2, 4, 5, 8, 9]

# 存储所有视频所有用户的角速度和黑边比例
all_vx = []
all_vy = []
all_black_edge_ratios = []

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

        # 假设黑边比例是 'BlackEdgeRatio' 列
        black_edge_ratio = df_downsampled['BlackEdgeRatio'].dropna()  # 使用实际列名替换这里

        # 对角速度和黑边比例数据进行扩展
        all_vx.extend(vx.tolist())
        all_vy.extend(vy.tolist())
        all_black_edge_ratios.extend(black_edge_ratio.tolist())

# === 计算黑边比例的角速度区间 ===
num_bins = 15  # 设定角速度的区间数
max_vx = max(all_vx)
max_vy = max(all_vy)

# 定义角速度区间
bins_vx = np.linspace(0, max_vx, num_bins + 1)
bins_vy = np.linspace(0, max_vy, num_bins + 1)

# 对每个角速度区间内的黑边比例求平均
mean_black_edge_ratios_vx = []
mean_black_edge_ratios_vy = []

for i in range(len(bins_vx) - 1):
    # 获取当前区间的角速度范围
    mask = (all_vx >= bins_vx[i]) & (all_vx < bins_vx[i + 1])
    mean_black_edge_ratios_vx.append(np.mean(np.array(all_black_edge_ratios)[mask]))

for i in range(len(bins_vy) - 1):
    # 获取当前区间的角速度范围
    mask = (all_vy >= bins_vy[i]) & (all_vy < bins_vy[i + 1])
    mean_black_edge_ratios_vy.append(np.mean(np.array(all_black_edge_ratios)[mask]))

# === 绘图 ===
plt.figure(figsize=(14, 6))

# 经度角速度与黑边比例
plt.subplot(1, 2, 1)
plt.bar(bins_vx[:-1], mean_black_edge_ratios_vx, width=np.diff(bins_vx), align='edge', edgecolor='black', color='skyblue')
plt.xlabel('经度角速度（度/秒）')
plt.ylabel('平均黑边比例')
plt.title('经度角速度与黑边比例')
plt.grid(True)

# 纬度角速度与黑边比例
plt.subplot(1, 2, 2)
plt.bar(bins_vy[:-1], mean_black_edge_ratios_vy, width=np.diff(bins_vy), align='edge', edgecolor='black', color='salmon')
plt.xlabel('纬度角速度（度/秒）')
plt.ylabel('平均黑边比例')
plt.title('纬度角速度与黑边比例')
plt.grid(True)

plt.tight_layout()
plt.show()
