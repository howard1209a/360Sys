import xml.etree.ElementTree as ET
import ast
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

# 注册 MPD 命名空间
ns = {'mpd': 'urn:mpeg:dash:schema:mpd:2011'}


# 获取带宽列表
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


# 获取带宽数据
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


# === 计算每秒数据浪费 ===
def compute_waste(row):
    quality = row["listQuality"]
    visible_ids = row["visibleFaceIDs"]
    visible_percent = row["percentageVisibleFaces"]

    # 构造映射：tile_id -> coverage
    id2percentage = dict(zip(visible_ids, visible_percent))

    total_waste = 0.0
    total_throughput = 0.0
    for tile_id in range(23):
        if quality[tile_id] == 1:  # 高质量传输
            bw = float(bandwidth_list_map[chunk_now][tile_id])  # 转换为浮动类型以进行计算
            total_throughput += bw
            if tile_id not in id2percentage:
                total_waste += bw  # 完全看不到
            else:
                visible_ratio = id2percentage[tile_id]
                waste_ratio = 1 - visible_ratio
                total_waste += bw * waste_ratio
    if total_throughput == 0:
        return 0
    else:
        return total_waste / total_throughput


# 定义基础路径
base_folder_path = '/Users/howard1209a/Desktop/codes/dash_file/360Sys/monitor/result/diff-fov+diff-chunk/video4/'

# fov 与 chunk 的组合
fov_chunk_map = {
    'fov120': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    'fov80': ['chunk1', 'chunk2', 'chunk5', 'chunk8'],
    'fov40': ['chunk1', 'chunk2', 'chunk5', 'chunk8']
}

results = {}
# 存储黑边比例结果
results_black_ratio = {}

# 创建保存图像的目录
output_dir = './plots'
os.makedirs(output_dir, exist_ok=True)

# 处理每个 fov 和 chunk
for fov, chunks in fov_chunk_map.items():
    results[fov] = []
    results_black_ratio[fov] = []

    for chunk in chunks:
        chunk_now = chunk
        folder_name = f'{fov}+{chunk}'
        folder_path = os.path.join(base_folder_path, folder_name)

        # 合并 u1 到 u5 数据
        all_df = pd.DataFrame()
        for u in range(1, 6):
            file_path = os.path.join(folder_path, f'u{u}.csv')
            df = pd.read_csv(file_path)
            df["listQuality"] = df["listQuality"].apply(safe_parse_list_quality)
            df["percentageVisibleFaces"] = df["percentageVisibleFaces"].apply(safe_parse_percentage)
            df["visibleFaceIDs"] = df["visibleFaces"].apply(extract_tile_ids)
            all_df = pd.concat([all_df, df], ignore_index=True)

        # === 数据浪费率计算 ===
        all_df["dataWasteRatio"] = all_df.apply(compute_waste, axis=1)

        # === 计算每个数据浪费率区间的平均黑边比例 ===
        black_ratios = []
        for idx, row in all_df.iterrows():
            try:
                list_quality = row['listQuality']
                visible_ids = row['visibleFaceIDs']
                percentages = row['percentageVisibleFaces']

                black_area = 0
                total_area = 0

                for vid, area in zip(visible_ids, percentages):
                    if 0 <= vid <= 22:
                        total_area += area
                        if list_quality[vid] == 0:
                            black_area += area

                black_ratio = black_area / total_area if total_area > 0 else 0
                black_ratios.append(black_ratio)
            except Exception as e:
                print(f"黑边比例计算错误 - 第{idx}行: {e}")
                black_ratios.append(0)

        all_df['blackRatio'] = black_ratios

        # 过滤数据冗余率为80%到100%的区间
        all_df = all_df[all_df["dataWasteRatio"] < 0.8]

        # 分区间计算黑边比例
        bins = np.linspace(0, 0.8, 4)  # 数据冗余率区间
        bin_labels = [f"{round(bins[i], 2)}-{round(bins[i + 1], 2)}" for i in range(len(bins) - 1)]

        # 将数据冗余率映射到对应的区间
        all_df['dataWasteBin'] = pd.cut(all_df['dataWasteRatio'], bins=bins, labels=bin_labels, include_lowest=True)

        # 计算每个区间的平均黑边比例
        avg_black_ratios = all_df.groupby('dataWasteBin')['blackRatio'].mean()

        # 保存结果
        results_black_ratio[fov + '+' + chunk] = avg_black_ratios

        # === 绘图 ===
        plt.figure(figsize=(10, 6))
        avg_black_ratios.plot(kind='bar', color='skyblue')
        plt.xlabel("数据冗余率区间")
        plt.ylabel("平均黑边比例")
        plt.title(f"{fov}+{chunk} 的数据冗余率区间 vs 平均黑边比例")
        plt.xticks(rotation=45)
        plt.grid(True)

        # 保存图像
        output_path = os.path.join(output_dir, f"{fov}_{chunk}_bar.png")
        plt.savefig(output_path)
        plt.close()
        print(f"保存图像: {output_path}")
