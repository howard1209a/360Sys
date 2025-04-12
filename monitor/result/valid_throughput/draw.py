import xml.etree.ElementTree as ET
import ast
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

from monitor.result.format_draw import format_draw_histogram

# 注册 MPD 命名空间
ns = {'mpd': 'urn:mpeg:dash:schema:mpd:2011'}


def get_bandwidth_list(chunk):
    base_path = "/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video4/tile/2*2/chunk" + str(
        chunk) + "/"
    bandwidth_list = []

    for folder_name in sorted(os.listdir(base_path)):
        folder_path = os.path.join(base_path, folder_name)

        # 检查是否为目录
        if os.path.isdir(folder_path):
            mpd_file = os.path.join(folder_path, f'{folder_name}.mpd')

            # 检查 mpd 文件是否存在
            if os.path.exists(mpd_file):
                try:
                    tree = ET.parse(mpd_file)
                    root = tree.getroot()

                    # 获取第一个 Representation 的 bandwidth
                    rep = root.find('.//mpd:Period/mpd:AdaptationSet/mpd:Representation', ns)
                    if rep is not None:
                        bandwidth = rep.attrib.get('bandwidth', 'N/A')
                        bandwidth_list.append(bandwidth)
                    else:
                        print(f'{folder_name}: 没有找到 Representation')
                except Exception as e:
                    print(f'{folder_name}: 解析失败 - {e}')
            else:
                print(f'{folder_name}: MPD 文件不存在')

    return bandwidth_list


chunk_list = [1, 2, 5, 8]
bandwidth_list_map = {}
for chunk in chunk_list:
    bandwidth_list_map["chunk" + str(chunk)] = get_bandwidth_list(chunk)


# 处理 listQuality 和 percentageVisibleFaces 列的非法格式
def safe_parse_list_quality(s):
    try:
        return ast.literal_eval(s.replace(";", ","))
    except:
        print(f"解析 listQuality 出错：{s}")
        return [0] * 24  # 或者返回 None，看你想怎么处理异常


def safe_parse_percentage(s):
    try:
        return ast.literal_eval(s.replace(";", ","))
    except:
        print(f"解析 percentageVisibleFaces 出错：{s}")
        return []


# 解析 visibleFaces -> 仅提取 tile ID
def extract_tile_ids(s):
    raw = s.strip("[]")
    if not raw:
        return []
    return [int(item.split("_")[2]) for item in raw.split(";") if item.strip()]


chunk_now = 0


# === 计算每秒数据浪费 ===
def compute_valid_throughput(row):
    quality = row["listQuality"]
    visible_ids = row["visibleFaceIDs"]
    visible_percent = row["percentageVisibleFaces"]

    # 构造映射：tile_id -> coverage
    id2percentage = dict(zip(visible_ids, visible_percent))

    total_valid_throughput = 0.0
    for tile_id in range(23):
        if quality[tile_id] == 1 and tile_id in id2percentage:  # 高质量传输
            bw = float(bandwidth_list_map[chunk_now][tile_id])  # 转换为浮动类型以进行计算
            visible_ratio = id2percentage[tile_id]
            total_valid_throughput += bw * visible_ratio

    return total_valid_throughput


# 定义基础路径
base_folder_path = '/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/diff-fov+diff-chunk/video4/'

# fov 与 chunk 的组合
fov_chunk_map = {
    '40': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    '80': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    '120': ['chunk1', 'chunk2', 'chunk5', 'chunk8']
}

# 存储数据
results = {}

for fov, chunks in fov_chunk_map.items():
    results[fov] = []
    for chunk in chunks:
        chunk_now = chunk
        folder_name = f'fov{fov}+{chunk}'
        folder_path = os.path.join(base_folder_path, folder_name)

        all_data_valid_throughput = []

        for i in range(1, 6):
            file_path = os.path.join(folder_path, f'u{i}.csv')
            # === 读取数据 ===
            df = pd.read_csv(file_path)
            df["listQuality"] = df["listQuality"].apply(safe_parse_list_quality)
            df["percentageVisibleFaces"] = df["percentageVisibleFaces"].apply(safe_parse_percentage)
            df["visibleFaceIDs"] = df["visibleFaces"].apply(extract_tile_ids)
            df["validThroughput"] = df.apply(compute_valid_throughput, axis=1)

            # 计算每个文件的平均数据浪费
            avg_valid_throughput = df['validThroughput'].mean()
            all_data_valid_throughput.append(avg_valid_throughput)

        avg_data_valid_throughput = sum(all_data_valid_throughput) / len(all_data_valid_throughput)
        results[fov].append(avg_data_valid_throughput)

# 准备绘图数据
labels = list(results.keys())
data = []
for label in labels:
    for index, value in enumerate(results[label]):
        results[label][index] = value / 8388608.0
    data.append(results[label])
format_draw_histogram(["40°×40°", "80°×80°", "120°×120°"], data, "Transmitted Area", "Throughput/MB", 0.09)
