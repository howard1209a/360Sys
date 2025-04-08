import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

# 定义基础路径
base_folder_path = '/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/diff-fov+diff-chunk/video4/'

# fov 与 chunk 的组合
fov_chunk_map = {
    'fov120': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    'fov80': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    'fov40': ['chunk1', 'chunk2', 'chunk5', 'chunk8']
}

# 存储数据
results = {}

for fov, chunks in fov_chunk_map.items():
    results[fov] = []
    for chunk in chunks:
        folder_name = f'{fov}+{chunk}'
        folder_path = os.path.join(base_folder_path, folder_name)

        all_throughputs = []

        for i in range(1, 6):
            file_path = os.path.join(folder_path, f'u{i}.csv')
            df = pd.read_csv(file_path)
            all_throughputs.extend(df['totalThroughput'].values)

        avg_throughput = sum(all_throughputs) / len(all_throughputs)
        results[fov].append(avg_throughput)

# 准备绘图数据
fov_labels = list(results.keys())
chunk_labels = fov_chunk_map[fov_labels[0]]  # 假设所有fov的chunk组合一致
x = np.arange(len(fov_labels))  # fov在x轴的位置
width = 0.2  # 每个柱子的宽度

# 绘图
fig, ax = plt.subplots()

for idx, chunk in enumerate(chunk_labels):
    chunk_throughputs = [results[fov][idx] for fov in fov_labels]
    ax.bar(x + idx * width, chunk_throughputs, width, label=chunk)

# 设置坐标轴
ax.set_xlabel('FOV')
ax.set_ylabel('平均吞吐量')
ax.set_title('不同FOV下不同Chunk设置的平均吞吐量')
ax.set_xticks(x + width / 2)
ax.set_xticklabels(fov_labels)
ax.legend(title='Chunk')

plt.tight_layout()
plt.show()
