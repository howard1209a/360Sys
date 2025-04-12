import matplotlib.pyplot as plt

import numpy as np


# labels是字符串列表，对应每个横轴点
# data是二维列表，长度和labels一致，和labels同一位置即为该横轴点所有柱子的高度
def format_draw_histogram(labels, data, x_label_name, y_label_name, y_bottom, y_top_ratio):
    plt.rcParams['font.family'] = ['Arial']
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    fig, ax = plt.subplots(1, 1, figsize=(12, 4))

    ax.set_xlabel(x_label_name, fontsize=20)
    ax.set_ylabel(..., fontsize=20)

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
    offsets = [-1.5, -0.5, 0.5, 1.5]
    offsets = [i * bar_spacing * width for i in offsets]

    # 绘制柱子
    ax.bar(x + offsets[0], [row[0] for row in data], width, label='chunk1',
           edgecolor='lightgoldenrodyellow', color='#000e4d', linewidth=.8, hatch='x')

    ax.bar(x + offsets[1], [row[1] for row in data], width, label='chunk2',
           edgecolor='#FAEBD7', color='#5c095e', linewidth=.8, hatch='o')

    ax.bar(x + offsets[2], [row[2] for row in data], width, label='chunk5',
           edgecolor='g', color='#9f055e', linewidth=.8, hatch='/')

    ax.bar(x + offsets[3], [row[3] for row in data], width, label='chunk8',
           edgecolor='k', color='#d5314f', linewidth=.8, hatch='+')

    # 设置 legend
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.05),
        ncol=4,
        fontsize=20,
        frameon=False
    )

    # 调整上下边距，防止 legend 和 xtick 被截断
    fig.subplots_adjust(top=0.85, bottom=0.2)

    # 保存图像
    plt.savefig('./info.jpg', dpi=400, bbox_inches='tight')

    plt.show()
