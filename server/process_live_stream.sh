#!/bin/bash

# 直播流处理脚本 - 处理单个瓦片的RTMP流并生成动态MPD

# 配置参数
RTMP_BASE="rtmp://localhost:1935/rtmplive/tile"
OUTPUT_BASE="/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/live/tile"

# 检查是否有输入参数
if [ -z "$1" ]; then
    echo "请提供瓦片编号作为参数！"
    echo "用法: $0 <瓦片编号1-6>"
    exit 1
fi

tile_num=$1

# 验证瓦片编号是否在1-6范围内
if [ $tile_num -lt 1 ] || [ $tile_num -gt 6 ]; then
    echo "错误：瓦片编号必须在1-6之间！"
    exit 1
fi

# 创建输出目录
output_dir="${OUTPUT_BASE}${tile_num}"
if [ ! -d "${output_dir}" ]; then
    mkdir -p "${output_dir}"
fi

echo "开始处理瓦片 ${tile_num} 的直播流..."
echo "RTMP源地址: ${RTMP_BASE}${tile_num}"
echo "输出目录: ${output_dir}"

# 清理函数
cleanup() {
    echo "正在停止ffmpeg进程..."
    pkill -f "ffmpeg.*tile${tile_num}.*live"
    exit 0
}

# 设置中断处理
trap cleanup SIGINT SIGTERM

# 启动ffmpeg进程处理指定瓦片
input_rtmp="${RTMP_BASE}${tile_num}"
    
echo "启动瓦片 ${tile_num} 的处理进程..."
    
ffmpeg -i "${input_rtmp}" \
    -map 0:v:0 -c:v:0 libx264 -profile:v:0 main -crf:v:0 45 -preset faster -g 25 \
    -map 0:v:0 -c:v:1 libx264 -profile:v:1 main -crf:v:1 51 -preset faster -g 25 \
    -f dash \
    -segment_time 2 \
    -segment_list "$OUTPUT/stream.m3u8" \
    -segment_list_flags +live \
    -segment_format mp4 \
    -use_template 1 \
    -use_timeline 1 \
    -window_size 0 \
    -adaptation_sets "id=0,streams=v" \
    "${output_dir}/tile${tile_num}.mpd"

# 等待ffmpeg进程结束
wait