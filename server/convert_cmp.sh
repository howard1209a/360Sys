#!/bin/bash

if [ -z "$1" ]; then
    echo "请提供视频编号作为参数！"
    exit 1
fi

video_num=$1

base_dir="/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/"
video_file="video${video_num}/video_${video_num}.mp4"

if [ ! -f "${base_dir}$video_file" ]; then
    echo "视频文件 $video_file 不存在，请检查路径和视频编号！"
    exit 1
fi

output_dir="${base_dir}video${video_num}"
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
fi

ffmpeg -i "${base_dir}$video_file" \
       -vf "scale=3840:1920:flags=lanczos+accurate_rnd+full_chroma_int+full_chroma_inp,setsar=1,format=yuv420p,v360=equirect:c3x2" \
       -c:v libx264 \
       -preset slower \
       -crf 14 \
       -profile:v high \
       -level 5.1 \
       -x264-params "aq-mode=3:aq-strength=1.0:psy-rd=1.0:psy-rdoq=1.0" \
       -c:a copy \
       -movflags +faststart \
       -pix_fmt yuv420p \
       "${base_dir}video${video_num}/video_${video_num}_cmp.mp4"

if [ $? -eq 0 ]; then
    echo "转换完成！输出文件: video${video_num}/video_${video_num}_cmp.mp4"
else
    echo "转换失败，请检查错误信息！"
    exit 1
fi