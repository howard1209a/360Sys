import pandas as pd
import os
import matplotlib.pyplot as plt

# 文件路径和CSV文件列表
folder_path = 'result/siti/'
csv_files = [f'video{i}.csv' for i in range(1, 10)]
averages = {}

# 计算每个视频的si和ti平均值
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path)
    si_avg = df['si'].mean()
    ti_avg = df['ti'].mean()
    averages[file_name] = {'si_avg': si_avg, 'ti_avg': ti_avg}

for file_name, avg_values in averages.items():
    print(f"File: {file_name}")
    print(f"  si_avg: {avg_values['si_avg']:.3f}")
    print(f"  ti_avg: {avg_values['ti_avg']:.3f}")

# 准备绘制散点图的数据
si_values = [avg['si_avg'] for avg in averages.values()]
ti_values = [avg['ti_avg'] for avg in averages.values()]
video_labels = [file_name for file_name in csv_files]

# 绘制散点图
plt.figure(figsize=(8, 6))
plt.scatter(si_values, ti_values)

# 设置图表标签和标题
plt.xlabel('si (Average)')
plt.ylabel('ti (Average)')
plt.title('Scatter Plot of si vs ti for each video')

# 标注每个点
for i, label in enumerate(video_labels):
    plt.annotate(label, (si_values[i], ti_values[i]), textcoords="offset points", xytext=(0,5), ha='center')

# 显示网格
plt.grid(True)

# 保存图表为文件
output_path = 'result/siti/siti.png'  # 你可以修改文件名和路径
plt.savefig(output_path)

# 显示图表
plt.show()
