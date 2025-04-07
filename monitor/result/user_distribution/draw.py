import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 数据根目录（替换成你自己的）
base_dir = '/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video4/motion'

# 存储所有用户的角速度
all_vx = []
all_vy = []

# 遍历 u1 到 u20
for i in range(1, 21):
    filename = f'u{i}_preprocessed.csv'
    filepath = os.path.join(base_dir, filename)

    if not os.path.exists(filepath):
        print(f'未找到文件：{filepath}，跳过')
        continue

    df = pd.read_csv(filepath)

    # 降采样，每秒一条
    df_downsampled = df.iloc[::60].reset_index(drop=True)

    # 计算角速度（单位：度/秒）
    vx = df_downsampled['Pose_Angle_x'].diff().abs()
    vy = df_downsampled['Pose_Angle_y'].diff().abs()

    # 去掉 NaN（第一条）
    vx = vx.dropna()
    vy = vy.dropna()

    # 累加
    all_vx.extend(vx.tolist())
    all_vy.extend(vy.tolist())

print("所有用户的角速度数据读取完毕，共计：")
print(f"vx：{len(all_vx)} 条，vy：{len(all_vy)} 条")

# === 统计并绘图 ===

# 设置区间数量
num_bins = 15

# 计算最大角速度，用于设置 bins
max_vx = max(all_vx)
max_vy = max(all_vy)

bins_vx = np.linspace(0, max_vx, num_bins + 1)
bins_vy = np.linspace(0, max_vy, num_bins + 1)

# 计算直方图
hist_vx, _ = np.histogram(all_vx, bins=bins_vx)
hist_vy, _ = np.histogram(all_vy, bins=bins_vy)

# 占比归一化
percent_vx = hist_vx / sum(hist_vx)
percent_vy = hist_vy / sum(hist_vy)

# 绘图
plt.figure(figsize=(14, 6))

# 经度角速度
plt.subplot(1, 2, 1)
plt.bar(bins_vx[:-1], percent_vx, width=np.diff(bins_vx), align='edge', edgecolor='black', color='skyblue')
plt.xlabel('经度角速度（度/秒）')
plt.ylabel('占比')
plt.title('所有用户的经度角速度分布')
plt.grid(True)

# 纬度角速度
plt.subplot(1, 2, 2)
plt.bar(bins_vy[:-1], percent_vy, width=np.diff(bins_vy), align='edge', edgecolor='black', color='salmon')
plt.xlabel('纬度角速度（度/秒）')
plt.ylabel('占比')
plt.title('所有用户的纬度角速度分布')
plt.grid(True)

plt.tight_layout()
plt.show()
