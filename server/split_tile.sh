#!/bin/bash

if [ -z "$1" ]; then
    echo "请提供视频编号作为参数！"
    exit 1
fi

video_num=$1

base_dir="/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/"
video_file="video${video_num}/video_${video_num}_cmp.mp4"

if [ ! -f "${base_dir}$video_file" ]; then
    echo "视频文件 $video_file 不存在，请检查路径和视频编号！"
    exit 1
fi

output_dir="${base_dir}video${video_num}/tile"
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
fi

echo "开始裁剪视频 ${video_file}..."

ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:0:0" -c:v libx264 -crf 18 -preset faster -c:a copy "${base_dir}video${video_num}/tile/video_${video_num}_tile1.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:480:0" -c:v libx264 -crf 18 -preset faster -c:a copy "${base_dir}video${video_num}/tile/video_${video_num}_tile2.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:960:0" -c:v libx264 -crf 18 -preset faster -c:a copy "${base_dir}video${video_num}/tile/video_${video_num}_tile3.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:0:480" -c:v libx264 -crf 18 -preset faster -c:a copy "${base_dir}video${video_num}/tile/video_${video_num}_tile4.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:480:480" -c:v libx264 -crf 18 -preset faster -c:a copy "${base_dir}video${video_num}/tile/video_${video_num}_tile5.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:960:480" -c:v libx264 -crf 18 -preset faster -c:a copy "${base_dir}video${video_num}/tile/video_${video_num}_tile6.mp4"

echo "裁剪完成！"
