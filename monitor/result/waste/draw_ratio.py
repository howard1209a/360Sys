import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import xml.etree.ElementTree as ET
import ast

# 注册 MPD 命名空间
ns = {'mpd': 'urn:mpeg:dash:schema:mpd:2011'}

# 定义基础路径
base_folder_path = '/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/diff-fov+diff-chunk/video4/'

# fov 与 chunk 的组合
fov_chunk_map = {
    'fov120': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    'fov80': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    'fov40': ['chunk1', 'chunk2', 'chunk5', 'chunk8']
}

# 存储吞吐量和数据浪费的结果
throughput_results = {}
waste_results = {}


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
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import xml.etree.ElementTree as ET
import ast

# 定义基础路径
base_folder_path = '/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/diff-fov+diff-chunk/video4/'

# fov 与 chunk 的组合
fov_chunk_map = {
    'fov120': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    'fov80': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    'fov40': ['chunk1', 'chunk2', 'chunk5', 'chunk8']
}

# 存储吞吐量和数据浪费的结果
throughput_results = {}
waste_results = {}


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


# 吞吐量计算
for fov, chunks in fov_chunk_map.items():
    throughput_results[fov] = []
    for chunk in chunks:
        folder_name = f'{fov}+{chunk}'
        folder_path = os.path.join(base_folder_path, folder_name)

        all_throughputs = []

        for i in range(1, 6):
            file_path = os.path.join(folder_path, f'u{i}.csv')
            df = pd.read_csv(file_path)
            all_throughputs.extend(df['totalThroughput'].values)

        avg_throughput = sum(all_throughputs) / len(all_throughputs)
        throughput_results[fov].append(avg_throughput)


# 获取带宽数据
def get_bandwidth_list(chunk):
    base_path = "/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video4/tile/2*2/chunk" + str(
        chunk) + "/"
    bandwidth_list = []

    for folder_name in sorted(os.listdir(base_path)):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            mpd_file = os.path.join(folder_path, f'{folder_name}.mpd')
            if os.path.exists(mpd_file):
                try:
                    tree = ET.parse(mpd_file)
                    root = tree.getroot()
                    rep = root.find('.//mpd:Period/mpd:AdaptationSet/mpd:Representation', ns)
                    if rep is not None:
                        bandwidth = rep.attrib.get('bandwidth', 'N/A')
                        bandwidth_list.append(bandwidth)
                except Exception as e:
                    print(f'{folder_name}: 解析失败 - {e}')
    return bandwidth_list


bandwidth_list_map = {}
chunk_list = [1, 2, 5, 8]
for chunk in chunk_list:
    bandwidth_list_map["chunk" + str(chunk)] = get_bandwidth_list(chunk)


# 计算浪费数据量
def compute_waste(row):
    quality = row["listQuality"]
    visible_ids = row["visibleFaceIDs"]
    visible_percent = row["percentageVisibleFaces"]

    id2percentage = dict(zip(visible_ids, visible_percent))

    total_waste = 0.0
    for tile_id in range(23):
        if quality[tile_id] == 1:
            bw = float(bandwidth_list_map[chunk_now][tile_id])
            if tile_id not in id2percentage:
                total_waste += bw
            else:
                visible_ratio = id2percentage[tile_id]
                waste_ratio = 1 - visible_ratio
                total_waste += bw * waste_ratio
    return total_waste


# 浪费数据计算
for fov, chunks in fov_chunk_map.items():
    waste_results[fov] = []
    for chunk in chunks:
        chunk_now = chunk
        folder_name = f'{fov}+{chunk}'
        folder_path = os.path.join(base_folder_path, folder_name)

        all_data_waste = []

        for i in range(1, 6):
            file_path = os.path.join(folder_path, f'u{i}.csv')
            df = pd.read_csv(file_path)
            df["listQuality"] = df["listQuality"].apply(safe_parse_list_quality)
            df["percentageVisibleFaces"] = df["percentageVisibleFaces"].apply(safe_parse_percentage)
            df["visibleFaceIDs"] = df["visibleFaces"].apply(extract_tile_ids)
            df["dataWaste"] = df.apply(compute_waste, axis=1)

            avg_waste = df['dataWaste'].mean()
            all_data_waste.append(avg_waste)

        avg_data_waste = sum(all_data_waste) / len(all_data_waste)
        waste_results[fov].append(avg_data_waste)

# 计算浪费数据比例
waste_ratio_results = {}
for fov in fov_chunk_map.keys():
    waste_ratio_results[fov] = []
    for i, chunk in enumerate(fov_chunk_map[fov]):
        waste_ratio = waste_results[fov][i] / throughput_results[fov][i] if throughput_results[fov][i] != 0 else 0
        waste_ratio_results[fov].append(waste_ratio)

# 绘制浪费数据比例图
fov_labels = list(waste_ratio_results.keys())
chunk_labels = fov_chunk_map[fov_labels[0]]
x = np.arange(len(fov_labels))
width = 0.2

fig, ax = plt.subplots()

for idx, chunk in enumerate(chunk_labels):
    chunk_waste_ratios = [waste_ratio_results[fov][idx] for fov in fov_labels]
    ax.bar(x + idx * width, chunk_waste_ratios, width, label=chunk)

# 设置坐标轴
ax.set_xlabel('FOV')
ax.set_ylabel('浪费数据比例')
ax.set_title('不同FOV下不同Chunk设置的浪费数据比例')
ax.set_xticks(x + width / 2)
ax.set_xticklabels(fov_labels)
ax.legend(title='Chunk')

plt.tight_layout()
plt.show()


# 解析 visibleFaces -> 仅提取 tile ID
def extract_tile_ids(s):
    raw = s.strip("[]")
    if not raw:
        return []
    return [int(item.split("_")[2]) for item in raw.split(";") if item.strip()]


# 吞吐量计算
for fov, chunks in fov_chunk_map.items():
    throughput_results[fov] = []
    for chunk in chunks:
        folder_name = f'{fov}+{chunk}'
        folder_path = os.path.join(base_folder_path, folder_name)

        all_throughputs = []

        for i in range(1, 6):
            file_path = os.path.join(folder_path, f'u{i}.csv')
            df = pd.read_csv(file_path)
            all_throughputs.extend(df['totalThroughput'].values)

        avg_throughput = sum(all_throughputs) / len(all_throughputs)
        throughput_results[fov].append(avg_throughput)


# 获取带宽数据
def get_bandwidth_list(chunk):
    base_path = "/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/video4/tile/2*2/chunk" + str(
        chunk) + "/"
    bandwidth_list = []

    for folder_name in sorted(os.listdir(base_path)):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            mpd_file = os.path.join(folder_path, f'{folder_name}.mpd')
            if os.path.exists(mpd_file):
                try:
                    tree = ET.parse(mpd_file)
                    root = tree.getroot()
                    rep = root.find('.//mpd:Period/mpd:AdaptationSet/mpd:Representation', ns)
                    if rep is not None:
                        bandwidth = rep.attrib.get('bandwidth', 'N/A')
                        bandwidth_list.append(bandwidth)
                except Exception as e:
                    print(f'{folder_name}: 解析失败 - {e}')
    return bandwidth_list


bandwidth_list_map = {}
chunk_list = [1, 2, 5, 8]
for chunk in chunk_list:
    bandwidth_list_map["chunk" + str(chunk)] = get_bandwidth_list(chunk)


# 计算浪费数据量
def compute_waste(row):
    quality = row["listQuality"]
    visible_ids = row["visibleFaceIDs"]
    visible_percent = row["percentageVisibleFaces"]

    id2percentage = dict(zip(visible_ids, visible_percent))

    total_waste = 0.0
    for tile_id in range(23):
        if quality[tile_id] == 1:
            bw = float(bandwidth_list_map[chunk_now][tile_id])
            if tile_id not in id2percentage:
                total_waste += bw
            else:
                visible_ratio = id2percentage[tile_id]
                waste_ratio = 1 - visible_ratio
                total_waste += bw * waste_ratio
    return total_waste


# 浪费数据计算
for fov, chunks in fov_chunk_map.items():
    waste_results[fov] = []
    for chunk in chunks:
        chunk_now = chunk
        folder_name = f'{fov}+{chunk}'
        folder_path = os.path.join(base_folder_path, folder_name)

        all_data_waste = []

        for i in range(1, 6):
            file_path = os.path.join(folder_path, f'u{i}.csv')
            df = pd.read_csv(file_path)
            df["listQuality"] = df["listQuality"].apply(safe_parse_list_quality)
            df["percentageVisibleFaces"] = df["percentageVisibleFaces"].apply(safe_parse_percentage)
            df["visibleFaceIDs"] = df["visibleFaces"].apply(extract_tile_ids)
            df["dataWaste"] = df.apply(compute_waste, axis=1)

            avg_waste = df['dataWaste'].mean()
            all_data_waste.append(avg_waste)

        avg_data_waste = sum(all_data_waste) / len(all_data_waste)
        waste_results[fov].append(avg_data_waste)

# 计算浪费数据比例
waste_ratio_results = {}
for fov in fov_chunk_map.keys():
    waste_ratio_results[fov] = []
    for i, chunk in enumerate(fov_chunk_map[fov]):
        waste_ratio = waste_results[fov][i] / throughput_results[fov][i] if throughput_results[fov][i] != 0 else 0
        waste_ratio_results[fov].append(waste_ratio)

# 绘制浪费数据比例图
fov_labels = list(waste_ratio_results.keys())
chunk_labels = fov_chunk_map[fov_labels[0]]
x = np.arange(len(fov_labels))
width = 0.2

fig, ax = plt.subplots()

for idx, chunk in enumerate(chunk_labels):
    chunk_waste_ratios = [waste_ratio_results[fov][idx] for fov in fov_labels]
    ax.bar(x + idx * width, chunk_waste_ratios, width, label=chunk)

# 设置坐标轴
ax.set_xlabel('FOV')
ax.set_ylabel('浪费数据比例')
ax.set_title('不同FOV下不同Chunk设置的浪费数据比例')
ax.set_xticks(x + width / 2)
ax.set_xticklabels(fov_labels)
ax.legend(title='Chunk')

plt.tight_layout()
plt.show()
