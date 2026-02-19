#!/bin/bash

if [ -z "$1" ]; then
    echo "请提供视频编号作为参数！"
    exit 1
fi

video_num=$1
base_dir="/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/"
tile_dir="${base_dir}video${video_num}/tile/1*1/tile"

for i in {1..6}
do
  output_tile_dir="${tile_dir}${i}"
  if [ ! -d "${output_tile_dir}" ]; then
    mkdir -p "${output_tile_dir}"
  fi

  input_tile_video="${base_dir}video${video_num}/tile/1*1/video_${video_num}_tile${i}.mp4"
  ffmpeg -hide_banner -loglevel error \
  -i "${input_tile_video}" \
  -map 0:v:0 -c:v:0 libx264 -profile:v:0 main -crf:v:0 14 -g 25 \
  -map 0:v:0 -c:v:1 libx264 -profile:v:1 main -crf:v:1 28 -g 25 \
  -map 0:v:0 -c:v:2 libx264 -profile:v:2 main -crf:v:2 51 -g 25 \
  -f dash \
  -segment_time 1 \
  -segment_list "$OUTPUT/stream.m3u8" \
  -segment_format mp4 \
  -use_timeline 1 \
  -adaptation_sets "id=0,streams=v" \
  "${output_tile_dir}/tile${i}.mpd"
done