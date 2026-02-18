import matplotlib.pyplot as plt
import numpy as np

# 原始数据（单位 bit）
arr = [[1.8e6, 3.4e6, 3.5e6, 3.4e6, 1.5e6, 8.8e5],
       [4.2e6, 1.1e6, 1.5e6, 5.9e6, 10e6, 0],
       [5.2e6, 3.7e6, 3.4e6, 2.1e6, 3.5e6, 6.1e6],
       [3.7e6, 2.5e6, 2.7e6, 7.6e6, 1.3e6, 5.4e6],
       [4.3e6, 3.9e6, 2.1e6, 9.3e6, 4.7e6, 11e6]]

# 将 arr 转为 numpy 数组并转换为 Mbps 单位（便于阅读）
data = np.array(arr) / 1e6  # 转换成 Mbps

# 设置横纵坐标标签
x_labels = ["0-0.07", "0.07-0.15", "0.15-0.22", "0.22-0.3", "0.3-0.37", "0.37-0.45"]

# 将每个区间乘以60并格式化
x_labels = [
    f"{float(start) * 60:.0f}-{float(end) * 60:.0f}"
    for label in x_labels
    for start, end in [label.split("-")]
]
y_labels = ["Video 9", "Video 2", "Video 8", "Video 5", "Video 4"]

# 倒序排列纵轴
data = data[[3, 0, 2, 1, 4], :]

plt.figure(figsize=(10, 6))
plt.imshow(data, cmap="YlGnBu", aspect="auto")  # 热力图核心

# 添加颜色条
plt.colorbar(label="Average Throughput (Mbps)")

# 添加坐标轴标签
plt.xticks(ticks=np.arange(len(x_labels)), labels=x_labels)
plt.yticks(ticks=np.arange(len(y_labels)), labels=y_labels)

# 添加数值标注
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        plt.text(j, i, f"{data[i, j]:.1f}", ha='center', va='center', color='black')

plt.title("")
plt.xlabel("Angular Velocity Range(°/s)")
plt.ylabel("")
plt.tight_layout()
plt.show()
