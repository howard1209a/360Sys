import pandas as pd

# video4能耗

# 读取 CSV 文件
csv_file = "video4/u1.csv"
df_csv = pd.read_csv(csv_file)

# 读取 TXT 文件
txt_file = "video4/u1.txt"
df_txt = pd.read_csv(txt_file, sep="\s+", header=None, names=["timeStamp", "cpuUsage"])

# 解析 timeStamp 为 datetime 格式
df_csv["timeStamp"] = pd.to_datetime(df_csv["timeStamp"])
df_txt["timeStamp"] = pd.to_datetime(df_txt["timeStamp"])

# 按时间排序（merge_asof 需要数据有序）
df_csv = df_csv.sort_values("timeStamp")
df_txt = df_txt.sort_values("timeStamp")

# 使用 merge_asof 进行时间戳的最近匹配
df_merged = pd.merge_asof(df_csv, df_txt, on="timeStamp", direction="nearest")

# 计算所需列的平均值
average_values = df_merged[["totalThroughput", "totalDownloadTime", "cpuUsage"]].mean()

# 输出结果
print(average_values)
