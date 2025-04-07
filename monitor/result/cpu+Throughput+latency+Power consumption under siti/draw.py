import pandas as pd
import matplotlib.pyplot as plt

# 视频编号（按照指定顺序）
video_ids = [9, 2, 8, 5, 4]

# 存储每个视频的平均值
results = []

# 遍历所有视频文件
for video_id in video_ids:
    base_path = f"/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/cpu+Throughput+latency+Power consumption under siti/data/video{video_id}/u1"

    # 读取 CSV 文件
    csv_file = f"{base_path}/data.csv"
    df_csv = pd.read_csv(csv_file)

    # 读取 TXT 文件（CPU 使用率）
    txt_file = f"{base_path}/cpu_usage_log.txt"
    df_txt = pd.read_csv(txt_file, sep="\s+", header=None, names=["timeStamp", "cpuUsage"])

    # 读取能耗文件（energy.txt）
    energy_file = f"{base_path}/energy.txt"
    with open(energy_file, 'r') as f:
        energy_value = float(f.read().strip())

    # 解析 timeStamp 为 datetime 格式
    df_csv["timeStamp"] = pd.to_datetime(df_csv["timeStamp"])
    df_txt["timeStamp"] = pd.to_datetime(df_txt["timeStamp"])

    # 按时间排序（merge_asof 需要数据有序）
    df_csv = df_csv.sort_values("timeStamp")
    df_txt = df_txt.sort_values("timeStamp")

    # 使用 merge_asof 进行时间戳的最近匹配
    df_merged = pd.merge_asof(df_csv, df_txt, on="timeStamp", direction="nearest")

    # 计算所需列的平均值
    avg_values = df_merged[["totalThroughput", "totalDownloadTime", "cpuUsage"]].mean()
    results.append([
        video_id,
        avg_values["totalThroughput"],
        avg_values["totalDownloadTime"],
        avg_values["cpuUsage"],
        energy_value
    ])

# 转换为 DataFrame，并按指定顺序排序
df_results = pd.DataFrame(results, columns=["VideoID", "TotalThroughput", "TotalDownloadTime", "CPUUsage", "Energy"])
df_results["VideoID"] = pd.Categorical(df_results["VideoID"], categories=video_ids, ordered=True)
df_results = df_results.sort_values("VideoID")

# 绘制柱状图（4个子图）
fig, axes = plt.subplots(1, 4, figsize=(20, 5))

# 颜色映射
colors = ['r', 'b', 'g', 'y', 'c']

# 绘制 TotalThroughput 柱状图
axes[0].bar(df_results["VideoID"].astype(str), df_results["TotalThroughput"], color=colors, alpha=0.7)
axes[0].set_title("Total Throughput")
axes[0].set_xlabel("Video ID")
axes[0].set_ylabel("Mbps")

# 绘制 TotalDownloadTime 柱状图
axes[1].bar(df_results["VideoID"].astype(str), df_results["TotalDownloadTime"], color=colors, alpha=0.7)
axes[1].set_title("Total Download Time")
axes[1].set_xlabel("Video ID")
axes[1].set_ylabel("Seconds")

# 绘制 CPUUsage 柱状图
axes[2].bar(df_results["VideoID"].astype(str), df_results["CPUUsage"], color=colors, alpha=0.7)
axes[2].set_title("CPU Usage")
axes[2].set_xlabel("Video ID")
axes[2].set_ylabel("Percentage")

# 绘制 Energy 柱状图
axes[3].bar(df_results["VideoID"].astype(str), df_results["Energy"], color=colors, alpha=0.7)
axes[3].set_title("Energy Consumption")
axes[3].set_xlabel("Video ID")
axes[3].set_ylabel("Energy (Joule or unit)")

# 调整布局
plt.tight_layout()

# 显示图表
plt.show()
