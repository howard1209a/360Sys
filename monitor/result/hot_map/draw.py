import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 视频与用户范围
videos = [2, 8, 5, 4, 9]
user = 1

# 保存所有视频每秒的最终数据
all_data = []

for video in videos:
    # === 1. 读取 motion 数据 ===
    motion_path = f"/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video{video}/motion/u{user}_preprocessed.csv"
    df_motion = pd.read_csv(motion_path)

    # 添加时间戳（每60个点为1秒）
    df_motion["second"] = df_motion.index // 60

    # 计算每一帧转动角度
    longitudes = np.radians(df_motion.iloc[:, 1].values)
    latitudes = np.radians(df_motion.iloc[:, 2].values)

    angles = []
    for i in range(len(latitudes) - 1):
        delta_lon = longitudes[i + 1] - longitudes[i]
        angle = np.arccos(
            np.sin(latitudes[i]) * np.sin(latitudes[i + 1]) +
            np.cos(latitudes[i]) * np.cos(latitudes[i + 1]) * np.cos(delta_lon)
        )
        angle_deg = np.degrees(angle)
        if angle_deg <= 2:
            angles.append(angle_deg)
        else:
            angles.append(np.nan)  # 超过2度的视为缺失值

    angles.append(np.nan)  # 补尾部对齐

    df_motion["angle"] = angles
    df_motion.dropna(subset=["angle"], inplace=True)

    # 每秒求平均角度
    df_avg_angle = df_motion.groupby("second")["angle"].mean().reset_index()
    df_avg_angle.rename(columns={"angle": "avgRotationAngle"}, inplace=True)

    # === 2. 读取指标数据 ===
    base_path = f"/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/cpu+Throughput+latency+Power consumption under siti/data/video{video}/u{user}"

    # 读取吞吐量、下载时间
    df_metrics = pd.read_csv(os.path.join(base_path, "data.csv"))
    df_metrics["timeStamp"] = pd.to_datetime(df_metrics["timeStamp"])
    df_metrics["second"] = df_metrics["timeStamp"].dt.floor("S")

    # 每秒求平均
    df_metric_avg = df_metrics.groupby("second")[["totalThroughput", "totalDownloadTime"]].mean().reset_index()

    # 读取 CPU
    df_cpu = pd.read_csv(os.path.join(base_path, "cpu_usage_log.txt"), sep="\s+", header=None,
                         names=["timeStamp", "cpuUsage"])
    df_cpu["timeStamp"] = pd.to_datetime(df_cpu["timeStamp"])
    df_cpu["second"] = df_cpu["timeStamp"].dt.floor("S")

    # 使用 merge_asof 进行时间戳最近匹配
    df_cpu_sorted = df_cpu.sort_values("timeStamp")
    df_metrics_sorted = df_metric_avg.sort_values("second")

    df_cpu_merged = pd.merge_asof(df_metrics_sorted, df_cpu_sorted, left_on="second", right_on="timeStamp",
                                  direction="nearest", suffixes=("_metrics", "_cpu"))

    df_cpu_merged = df_cpu_merged.drop('second_metrics', axis=1)
    df_cpu_merged = df_cpu_merged.drop('second_cpu', axis=1)
    # 将 timeStamp 列转换为 datetime 类型
    df_cpu_merged['timeStamp'] = pd.to_datetime(df_cpu_merged['timeStamp'])

    # 将 df_avg_angle 的 second 列与 df_cpu_merged 按顺序对应
    df_avg_angle['timeStamp'] = df_cpu_merged['timeStamp']

    # 合并两个 DataFrame
    df_final = pd.merge(df_cpu_merged, df_avg_angle, on='timeStamp', how='inner')

    df_final["video"] = video
    df_final["user"] = user

    all_data.append(df_final)

df_final_all = pd.concat(all_data, ignore_index=True)
df_final_all.rename(columns={"second": "timeStamp"}, inplace=True)





# 1. 获取每个视频的最大转动角度
video_max_angles = df_final_all.groupby("video")["avgRotationAngle"].max()

# 2. 为每个视频划分6个区间
bins = 6
video_angle_bins = {}

for video in videos:
    max_angle = video_max_angles[video]
    angle_bins = np.linspace(0, max_angle, bins + 1)  # 生成6个区间
    video_angle_bins[video] = angle_bins

# 3. 为每个视频统计每个区间的平均值（吞吐量、下载时间、CPU使用率）
heatmap_data_throughput = []
heatmap_data_download_time = []
heatmap_data_cpu_usage = []

for video in videos:
    # 获取当前视频的数据
    df_video = df_final_all[df_final_all["video"] == video]

    # 获取当前视频的角度区间
    angle_bins = video_angle_bins[video]

    # 统计每个区间的记录数和计算平均值
    throughput_values = []
    download_time_values = []
    cpu_usage_values = []

    for i in range(len(angle_bins) - 1):
        # 找到转动角度在该区间内的记录
        mask = (df_video["avgRotationAngle"] >= angle_bins[i]) & (df_video["avgRotationAngle"] < angle_bins[i + 1])
        df_in_bin = df_video[mask]

        # 计算该区间内的平均值
        throughput_avg = df_in_bin["totalThroughput"].mean() if not df_in_bin.empty else 0
        download_time_avg = df_in_bin["totalDownloadTime"].mean() if not df_in_bin.empty else 0
        cpu_usage_avg = df_in_bin["cpuUsage"].mean() if not df_in_bin.empty else 0

        throughput_values.append(throughput_avg)
        download_time_values.append(download_time_avg)
        cpu_usage_values.append(cpu_usage_avg)

    # 保存每个视频的热力图数据
    heatmap_data_throughput.append(throughput_values)
    heatmap_data_download_time.append(download_time_values)
    heatmap_data_cpu_usage.append(cpu_usage_values)


# 设置视频的顺序
video_order = [9, 2, 8, 5, 4]

# 4. 将数据转换为 DataFrame 方便绘图
heatmap_df_throughput = pd.DataFrame(heatmap_data_throughput,
                                     columns=[f"{round(angle_bins[i], 2)}-{round(angle_bins[i+1], 2)}" for i in range(len(angle_bins)-1)])
heatmap_df_download_time = pd.DataFrame(heatmap_data_download_time,
                                        columns=[f"{round(angle_bins[i], 2)}-{round(angle_bins[i+1], 2)}" for i in range(len(angle_bins)-1)])
heatmap_df_cpu_usage = pd.DataFrame(heatmap_data_cpu_usage,
                                    columns=[f"{round(angle_bins[i], 2)}-{round(angle_bins[i+1], 2)}" for i in range(len(angle_bins)-1)])

# 赋予视频编号列
heatmap_df_throughput["video"] = videos
heatmap_df_download_time["video"] = videos
heatmap_df_cpu_usage["video"] = videos

# 按照指定的视频顺序重新排列
heatmap_df_throughput = heatmap_df_throughput.set_index("video").loc[video_order]
heatmap_df_download_time = heatmap_df_download_time.set_index("video").loc[video_order]
heatmap_df_cpu_usage = heatmap_df_cpu_usage.set_index("video").loc[video_order]

# 5. 绘制热力图

# 吞吐量热力图
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_df_throughput, annot=True, cmap='YlGnBu', cbar_kws={'label': 'Average Throughput'})
plt.title('Heatmap of Average Throughput by Rotation Angle and Video')
plt.xlabel('Rotation Angle Bins')
plt.ylabel('Video')
plt.show()

# 下载时间热力图
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_df_download_time, annot=True, cmap='YlGnBu', cbar_kws={'label': 'Average Download Time'})
plt.title('Heatmap of Average Download Time by Rotation Angle and Video')
plt.xlabel('Rotation Angle Bins')
plt.ylabel('Video')
plt.show()

# CPU使用率热力图
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_df_cpu_usage, annot=True, cmap='YlGnBu', cbar_kws={'label': 'Average CPU Usage'})
plt.title('Heatmap of Average CPU Usage by Rotation Angle and Video')
plt.xlabel('Rotation Angle Bins')
plt.ylabel('Video')
plt.show()



