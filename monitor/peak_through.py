import pandas as pd
import matplotlib.pyplot as plt

# 读取CSV文件，确保timeStamp列正确解析为日期时间格式
csv_data = pd.read_csv('result/static/data.csv', parse_dates=['timeStamp'])
time_data = csv_data['timeStamp'].to_numpy()
yaw_data = csv_data['yaw'].to_numpy()
pitch_data = csv_data['pitch'].to_numpy()
throughput_data = csv_data['totalThroughput'].to_numpy()

def draw_cpu():
    # 读取txt文件
    data = pd.read_csv('result/static/cpu_usage_log.txt', sep='\s+', header=None, names=['timeStamp', 'cpuUsage'], parse_dates=['timeStamp'])

    # 将 timeStamp 转换为 numpy 数组
    time_data = data['timeStamp'].to_numpy()

    # 将 cpuUsage 转换为 numpy 数组
    cpu_usage_data = data['cpuUsage'].to_numpy()

    # 绘图
    plt.figure(figsize=(10, 6))

    # 绘制 yaw 与 timeStamp 的关系
    plt.plot(time_data, cpu_usage_data, label='cpu_usage', color='blue')

    # 添加图例
    plt.legend()

    # 添加标题和标签
    plt.title('CPU Usage Over Time')
    plt.xlabel('Time')
    plt.ylabel('CPU Usage')

    # 设置x轴的日期格式
    plt.xticks(rotation=45)

    # 保存图片到文件
    plt.tight_layout()
    plt.savefig('cpu_usage.png')  # 保存为PNG文件

def draw_throughput():
    # 绘图
    plt.figure(figsize=(10, 6))

    # 绘制 yaw 与 timeStamp 的关系
    plt.plot(time_data, throughput_data, label='throughput', color='blue')

    # 添加图例
    plt.legend()

    # 添加标题和标签
    plt.title('Throughput Over Time')
    plt.xlabel('Time')
    plt.ylabel('Throughput')

    # 设置x轴的日期格式
    plt.xticks(rotation=45)

    # 保存图片到文件
    plt.tight_layout()
    plt.savefig('throughput.png')  # 保存为PNG文件


def draw_yaw_pitch():
    # 绘图
    plt.figure(figsize=(10, 6))

    # 绘制 yaw 与 timeStamp 的关系
    plt.plot(time_data, yaw_data, label='Yaw Angle', color='blue')

    # 绘制 pitch 与 timeStamp 的关系
    plt.plot(time_data, pitch_data, label='Pitch Angle', color='green')

    # 添加图例
    plt.legend()

    # 添加标题和标签
    plt.title('Yaw and Pitch Angles Over Time')
    plt.xlabel('Time')
    plt.ylabel('Angle (degrees)')

    # 设置x轴的日期格式
    plt.xticks(rotation=45)

    # 保存图片到文件
    plt.tight_layout()

    plt.savefig('yaw_pitch_angles.png')  # 保存为PNG文件

draw_cpu()
draw_throughput()
draw_yaw_pitch()
