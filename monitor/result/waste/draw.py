import xml.etree.ElementTree as ET
import ast
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

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


chunk_list = [2, 5, 8]
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
def compute_waste(row):
    quality = row["listQuality"]
    visible_ids = row["visibleFaceIDs"]
    visible_percent = row["percentageVisibleFaces"]

    # 构造映射：tile_id -> coverage
    id2percentage = dict(zip(visible_ids, visible_percent))

    total_waste = 0.0
    for tile_id in range(23):
        if quality[tile_id] == 1:  # 高质量传输
            bw = float(bandwidth_list_map[chunk_now][tile_id])  # 转换为浮动类型以进行计算
            if tile_id not in id2percentage:
                total_waste += bw  # 完全看不到
            else:
                visible_ratio = id2percentage[tile_id]
                waste_ratio = 1 - visible_ratio
                total_waste += bw * waste_ratio
    return total_waste


# 定义基础路径
base_folder_path = '/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/diff-fov+diff-chunk/video4/'

# fov 与 chunk 的组合
fov_chunk_map = {
    'fov120': ['chunk2', 'chunk5', 'chunk8'],
    'fov80': ['chunk2', 'chunk5', 'chunk8'],
    'fov40': ['chunk2', 'chunk5', 'chunk8']
}

# 存储数据
results = {}

for fov, chunks in fov_chunk_map.items():
    results[fov] = []
    for chunk in chunks:
        chunk_now = chunk
        folder_name = f'{fov}+{chunk}'
        folder_path = os.path.join(base_folder_path, folder_name)

        all_data_waste = []

        for i in range(1, 6):
            file_path = os.path.join(folder_path, f'u{i}.csv')
            # === 读取数据 ===
            df = pd.read_csv(file_path)
            df["listQuality"] = df["listQuality"].apply(safe_parse_list_quality)
            df["percentageVisibleFaces"] = df["percentageVisibleFaces"].apply(safe_parse_percentage)
            df["visibleFaceIDs"] = df["visibleFaces"].apply(extract_tile_ids)
            df["dataWaste"] = df.apply(compute_waste, axis=1)

            # 计算每个文件的平均数据浪费
            avg_waste = df['dataWaste'].mean()  # 假设 dataWaste 列已在之前计算
            all_data_waste.append(avg_waste)

        avg_data_waste = sum(all_data_waste) / len(all_data_waste)
        results[fov].append(avg_data_waste)

# 准备绘图数据
fov_labels = list(results.keys())
chunk_labels = fov_chunk_map[fov_labels[0]]  # 假设所有fov的chunk组合一致
x = np.arange(len(fov_labels))  # fov在x轴的位置
width = 0.2  # 每个柱子的宽度

# 绘图
fig, ax = plt.subplots()

for idx, chunk in enumerate(chunk_labels):
    chunk_data_waste = [results[fov][idx] for fov in fov_labels]
    ax.bar(x + idx * width, chunk_data_waste, width, label=chunk)

# 设置坐标轴
ax.set_xlabel('FOV')
ax.set_ylabel('平均数据浪费 (MB)')
ax.set_title('不同FOV下不同Chunk设置的平均数据浪费')
ax.set_xticks(x + width / 2)
ax.set_xticklabels(fov_labels)
ax.legend(title='Chunk')

plt.tight_layout()
plt.show()
