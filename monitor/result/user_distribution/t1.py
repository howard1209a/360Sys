import pandas as pd
import numpy as np
import os

# 要处理的视频索引
video_indices = [2, 4, 5, 8, 9]

# 存储所有视频所有用户的角速度（8个列表对应8条线）
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

        # 将角速度数据存储为数值列表
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

# 转换为numpy数组
all_vx_1s = np.array(all_vx_1s)
all_vy_1s = np.array(all_vy_1s)
all_vx_2s = np.array(all_vx_2s)
all_vy_2s = np.array(all_vy_2s)
all_vx_5s = np.array(all_vx_5s)
all_vy_5s = np.array(all_vy_5s)
all_vx_8s = np.array(all_vx_8s)
all_vy_8s = np.array(all_vy_8s)

# === 保存为8个npy文件 ===

# 保存水平方向角速度的4个数值列表
np.save('vx_1s.npy', all_vx_1s)
np.save('vx_2s.npy', all_vx_2s)
np.save('vx_5s.npy', all_vx_5s)
np.save('vx_8s.npy', all_vx_8s)

# 保存竖直方向角速度的4个数值列表
np.save('vy_1s.npy', all_vy_1s)
np.save('vy_2s.npy', all_vy_2s)
np.save('vy_5s.npy', all_vy_5s)
np.save('vy_8s.npy', all_vy_8s)

print("\n已保存8个数值列表文件：")
print("水平方向角速度：vx_1s.npy, vx_2s.npy, vx_5s.npy, vx_8s.npy")
print("竖直方向角速度：vy_1s.npy, vy_2s.npy, vy_5s.npy, vy_8s.npy")

# === 验证保存的数据 ===
print("\n验证保存的数据：")
print(f"vx_1s.npy: {all_vx_1s.shape}个值，范围[{all_vx_1s.min():.2f}, {all_vx_1s.max():.2f}]，均值{all_vx_1s.mean():.2f}")
print(f"vx_2s.npy: {all_vx_2s.shape}个值，范围[{all_vx_2s.min():.2f}, {all_vx_2s.max():.2f}]，均值{all_vx_2s.mean():.2f}")
print(f"vx_5s.npy: {all_vx_5s.shape}个值，范围[{all_vx_5s.min():.2f}, {all_vx_5s.max():.2f}]，均值{all_vx_5s.mean():.2f}")
print(f"vx_8s.npy: {all_vx_8s.shape}个值，范围[{all_vx_8s.min():.2f}, {all_vx_8s.max():.2f}]，均值{all_vx_8s.mean():.2f}")
print(f"vy_1s.npy: {all_vy_1s.shape}个值，范围[{all_vy_1s.min():.2f}, {all_vy_1s.max():.2f}]，均值{all_vy_1s.mean():.2f}")
print(f"vy_2s.npy: {all_vy_2s.shape}个值，范围[{all_vy_2s.min():.2f}, {all_vy_2s.max():.2f}]，均值{all_vy_2s.mean():.2f}")
print(f"vy_5s.npy: {all_vy_5s.shape}个值，范围[{all_vy_5s.min():.2f}, {all_vy_5s.max():.2f}]，均值{all_vy_5s.mean():.2f}")
print(f"vy_8s.npy: {all_vy_8s.shape}个值，范围[{all_vy_8s.min():.2f}, {all_vy_8s.max():.2f}]，均值{all_vy_8s.mean():.2f}")

# 示例：如何加载和使用这些数据
print("\n示例 - 加载数据：")
loaded_vx_1s = np.load('vx_1s.npy')
print(f"加载 vx_1s.npy: {loaded_vx_1s.shape}个值，前5个值: {loaded_vx_1s[:5]}")


# 如果需要计算CDF，可以使用以下函数
def calculate_cdf(data, num_bins=15):
    """计算数据的CDF"""
    # 创建直方图
    hist, bin_edges = np.histogram(data, bins=num_bins)

    # 计算PDF
    pdf = hist / hist.sum()

    # 计算CDF
    cdf = np.cumsum(pdf)

    # 返回bin中心点和CDF值
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    return bin_centers, cdf


# 示例：计算某个数据集的CDF
print("\n示例 - 计算vx_1s的CDF：")
bin_centers, cdf = calculate_cdf(all_vx_1s, num_bins=15)
print(f"bin中心点: {bin_centers[:5]}")
print(f"CDF值: {cdf[:5]}")