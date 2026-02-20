import pandas as pd
import os

ALGORITHMS = ['PW', 'VAAC-E', 'VAAC', 'SPB-360', 'Vaser']
FILE_COUNT = 3
START_ROW = 4
END_ROW = 60
DATA_DIR = 'raw_data'


def analyze_algorithms():
    results = []

    for algo in ALGORITHMS:
        all_data = pd.DataFrame()

        for i in range(1, FILE_COUNT + 1):
            file_path = f"{DATA_DIR}/{algo}_{i}.csv"
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df = df.iloc[START_ROW:END_ROW + 1]
                all_data = pd.concat([all_data, df], ignore_index=True)

        if len(all_data) > 0:
            results.append({
                'algorithm': algo,
                'low_quality_ratio_mean': all_data['lowQualityRatio'].mean(),
                'bitrate_in_view_mean': all_data['bitrateInView'].mean(),
                'rebuffer_count': all_data['isReBuffer'].sum(),
                'total_rows': len(all_data)
            })

    # 输出结果
    results_df = pd.DataFrame(results)
    pd.set_option('display.float_format', '{:.4f}'.format)
    print("\n各项指标统计：")
    print(results_df.to_string(index=False))

    print("\n最佳算法（按不同指标）：")
    print(f"最低低质量区域比例: {min(results, key=lambda x: x['low_quality_ratio_mean'])['algorithm']}")
    print(f"最高平均质量: {max(results, key=lambda x: x['bitrate_in_view_mean'])['algorithm']}")
    print(f"最少卡顿时长: {min(results, key=lambda x: x['rebuffer_count'])['algorithm']}")


if __name__ == "__main__":
    analyze_algorithms()