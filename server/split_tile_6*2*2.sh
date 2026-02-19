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

output_dir="${base_dir}video${video_num}/tile/2*2"
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
fi

echo "开始裁剪视频 ${video_file}..."

ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:0:0" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile1_1.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:480:0" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile1_2.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:0:480" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile1_3.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:480:480" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile1_4.mp4"


ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:960:0" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile2_1.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:1440:0" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile2_2.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:960:480" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile2_3.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:1440:480" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile2_4.mp4"

ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:1920:0" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile3_1.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:2400:0" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile3_2.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:1920:480" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile3_3.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:2400:480" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile3_4.mp4"

ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:0:960" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile4_1.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:480:960" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile4_2.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:0:1440" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile4_3.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:480:1440" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile4_4.mp4"

ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:960:960" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile5_1.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:1440:960" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile5_2.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:960:1440" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile5_3.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:1440:1440" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile5_4.mp4"

ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:1920:960" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile6_1.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:2400:960" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile6_2.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:1920:1440" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile6_3.mp4"
ffmpeg -i "${base_dir}$video_file" -vf "crop=480:480:2400:1440" -c:v libx264 -crf 14 -preset slower -c:a copy "${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile6_4.mp4"

echo "裁剪完成！"
