import pandas as pd
import ast
import os
import matplotlib.pyplot as plt
import numpy as np

from monitor.result.format_draw import format_draw_histogram


def format_draw_histogram_local(labels, data, x_label_name, y_label_name, y_bottom, y_top_ratio):
    plt.rcParams['font.family'] = ['Arial']
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    fig, ax = plt.subplots(1, 1, figsize=(12, 4))

    ax.set_xlabel(x_label_name, fontsize=14, labelpad=25)  # 默认可能是5，增加这个值让标签下移
    ax.set_ylabel(..., fontsize=14)

    x = np.arange(len(labels))
    width = 0.2

    ax.tick_params(which='major', direction='in', length=5, width=1.5, labelsize=18, bottom=False)
    ax.tick_params(axis='x', labelsize=18, bottom=False, labelrotation=0)

    ax.set_xticks(x)

    ax.set_ylabel(y_label_name)  # Energy Consumption(Wh) Bitrate(Mbps) Delay(s)

    max_value = max(max(row) for row in data)
    ax.set_ylim(bottom=y_bottom, top=max_value * y_top_ratio)

    ax.set_xticklabels(labels)

    linewidth = 1.5
    for spine in ['top', 'bottom', 'left', 'right']:
        ax.spines[spine].set_linewidth(linewidth)

    bar_spacing = 1.1  # 柱子之间的间距倍数（1.0 为紧挨着，越大越松散）

    # 偏移值计算方式（中心对称）
    offsets = [-1.5, -0.5, 0.5, 1.5, 2.5]
    offsets = [i * bar_spacing * width for i in offsets]

    # 绘制柱子
    ax.bar(x + offsets[0], [row[0] for row in data], width, label='0-20',
           edgecolor='lightgoldenrodyellow', color='#B24475', linewidth=.8, hatch='x')

    ax.bar(x + offsets[1], [row[1] for row in data], width, label='20-40',
           edgecolor='lightgoldenrodyellow', color='#864CBC', linewidth=.8, hatch='o')

    ax.bar(x + offsets[2], [row[2] for row in data], width, label='40-60',
           edgecolor='lightgoldenrodyellow', color='#386688', linewidth=.8, hatch='/')

    ax.bar(x + offsets[3], [row[3] for row in data], width, label='60-80',
           edgecolor='lightgoldenrodyellow', color='#845D1C', linewidth=.8, hatch='+')

    ax.bar(x + offsets[4], [row[4] for row in data], width, label='80-100',
           edgecolor='lightgoldenrodyellow', color='#8A543C', linewidth=.8, hatch='\\')

    ranges = ['0°/s-20°/s', '20°/s-40°/s', '40°/s-60°/s', '60°/s-80°/s', '80°/s-100°/s']

    for i in range(len(x)):  # 遍历每个x位置（也就是每组柱子）
        for j in range(5):  # 每组里的6个柱子
            ax.text(
                x[i] + offsets[j],
                y_bottom - (max_value * 0.05),  # 让文字在柱子下方一点点
                ranges[j],
                ha='center',
                va='top',
                fontsize=12,
                rotation=0
            )

    # 调整上下边距，防止 legend 和 xtick 被截断
    fig.subplots_adjust(top=0.85, bottom=0.2)

    save_name = f"{output_dir}/fov{fov}_chunk{chunk}_{motion_type}_blackratio.png"

    # 保存图像
    plt.savefig(save_name, dpi=400, bbox_inches='tight')


# 基础路径
base_path = "/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/diff-fov+diff-chunk/video4"

fovs = [40, 80, 120]
chunks = [1, 2, 5, 8]

# 构建结构：{fov: {chunk: [black_ratio列表, pitch_speed列表, yaw_speed列表]}}
data = {fov: {} for fov in fovs}

for fov in fovs:
    for chunk in chunks:
        file_path = os.path.join(base_path, f"fov{fov}+chunk{chunk}", "u1.csv")

        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
            data[fov][chunk] = None
            continue

        black_ratios = []
        pitch_speeds = []
        yaw_speeds = []

        prev_pitch = None
        prev_yaw = None

        for idx, row in df.iterrows():
            try:
                # 提取并解析listQuality
                list_quality_str = row['listQuality'].replace(';', ',')
                list_quality = ast.literal_eval(list_quality_str)

                visible_faces_str = row['visibleFaces'].strip("[]")
                percentage_str = row['percentageVisibleFaces'].strip("[]")

                if not visible_faces_str or not percentage_str:
                    black_ratios.append(None)
                    pitch_speeds.append(None)
                    yaw_speeds.append(None)
                    continue

                visible_faces = visible_faces_str.split(';')
                percentages = list(map(float, percentage_str.split(';')))
                visible_ids = [int(face.split('_')[2]) for face in visible_faces]

                black_area = 0
                total_area = 0
                for vid, area in zip(visible_ids, percentages):
                    if 0 <= vid <= 22:
                        total_area += area
                        if vid < len(list_quality) and list_quality[vid] == 0:
                            black_area += area

                black_ratio = black_area / total_area if total_area > 0 else 0
                black_ratios.append(black_ratio)

                # ------------------- 计算角速度 -------------------
                pitch = np.degrees(float(row['pitch']))
                yaw = np.degrees(float(row['yaw']))

                if prev_pitch is not None and prev_yaw is not None:
                    pitch_speed = abs(pitch - prev_pitch)
                    yaw_speed = abs(yaw - prev_yaw)
                else:
                    pitch_speed = 0.0
                    yaw_speed = 0.0

                pitch_speeds.append(pitch_speed)
                yaw_speeds.append(yaw_speed)

                prev_pitch = pitch
                prev_yaw = yaw

            except Exception as e:
                print(f"第{idx}行解析错误：{e}")
                black_ratios.append(None)
                pitch_speeds.append(None)
                yaw_speeds.append(None)

        # 保存结果
        data[fov][chunk] = {
            "black_ratios": black_ratios,
            "pitch_speeds": pitch_speeds,
            "yaw_speeds": yaw_speeds
        }

# ------------------- 可视化：角速度区间 vs 平均黑边比例 -------------------

# 设置角速度区间
pitch_bins = np.linspace(0, 30, 6)  # [0, 6, 12, 18, 24, 30]
yaw_bins = np.linspace(0, 100, 6)  # [0, 20, 40, 60, 80, 100]

output_dir = "./angle_speed_analysis"
os.makedirs(output_dir, exist_ok=True)

for fov in fovs:
    for chunk in chunks:
        result = data[fov][chunk]
        if result is None:
            continue

        for motion_type, bins in zip(['pitch', 'yaw'], [pitch_bins, yaw_bins]):
            speeds = result[f"{motion_type}_speeds"]
            blacks = result["black_ratios"]

            bin_avg_black = []
            bin_labels = []

            for i in range(len(bins) - 1):
                low = bins[i]
                high = bins[i + 1]

                bin_labels.append(f"{int(low)}-{int(high)}")
                # 获取当前区间的黑边比例
                bin_blacks = [
                    b for s, b in zip(speeds, blacks)
                    if s is not None and b is not None and low <= s < high
                ]

                # 计算平均黑边比例
                avg_black = np.mean(bin_blacks) if bin_blacks else 0
                bin_avg_black.append(avg_black)

            format_draw_histogram_local([""], [bin_avg_black], "Horizontal Speed", "Black Ratio", 0, 1.1)
