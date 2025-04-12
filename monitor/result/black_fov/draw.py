import pandas as pd
import ast
import os
import matplotlib.pyplot as plt
import numpy as np

from monitor.result.format_draw import format_draw_histogram

# 基础路径
base_path = "/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/diff-fov+diff-chunk/video4"

fovs = [40, 80, 120]
chunks = [1, 2, 5, 8]

# 构建一个结构：{fov: {chunk: avg_black_ratio}}
results = []

for fov in fovs:
    inner_list = []
    for chunk in chunks:
        file_path = os.path.join(base_path, f"fov{fov}+chunk{chunk}", "u1.csv")

        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
            inner_list.append(None)
            continue

        black_area_ratios = []

        for idx, row in df.iterrows():
            try:
                list_quality_str = row['listQuality'].replace(';', ',')
                list_quality = ast.literal_eval(list_quality_str)

                visible_faces_str = row['visibleFaces'].strip("[]")
                percentage_str = row['percentageVisibleFaces'].strip("[]")

                if not visible_faces_str or not percentage_str:
                    black_area_ratios.append(None)
                    continue

                visible_faces = visible_faces_str.split(';')
                percentages = list(map(float, percentage_str.split(';')))

                visible_ids = [int(face.split('_')[2]) for face in visible_faces]

                black_area = 0
                total_area = 0

                for vid, area in zip(visible_ids, percentages):
                    if 0 <= vid <= 22:
                        total_area += area
                        if list_quality[vid] == 0:
                            black_area += area

                black_ratio = black_area / total_area if total_area > 0 else 0
                black_area_ratios.append(black_ratio)
            except Exception as e:
                print(f"第{idx}行解析错误：{e}")
                black_area_ratios.append(None)

        avg_black_ratio = pd.Series(black_area_ratios).mean()
        inner_list.append(avg_black_ratio)

    results.append(inner_list)

# 准备绘图数据
data = []
for inner_list in results:
    data.append(inner_list)
format_draw_histogram(["40°×40°", "80°×80°", "120°×120°"], data, "Transmitted Area", "Black Ratio", 0, 1.25)
