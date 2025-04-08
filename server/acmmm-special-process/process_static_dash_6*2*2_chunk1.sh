#!/bin/bash

if [ -z "$1" ]; then
    echo "请提供视频编号作为参数！"
    exit 1
fi

video_num=$1
base_dir="/Users/howard1209a/Desktop/codes/dash_file/data/formal-testing/dataset/"
tile_dir="${base_dir}video${video_num}/tile/2*2/chunk1/tile"

for i in {1..6}
do
  for j in {1..4}
  do
    output_tile_dir="${tile_dir}${i}_${j}"
    if [ ! -d "${output_tile_dir}" ]; then
      mkdir -p "${output_tile_dir}"
    fi

    input_tile_video="${base_dir}video${video_num}/tile/2*2/video_${video_num}_tile${i}_${j}.mp4"

    ffmpeg -hide_banner -loglevel error \
      -i "${input_tile_video}" \
      -map 0:v:0 -c:v:0 libx264 -profile:v:0 main -crf:v:0 18 -g 25 -keyint_min 25 -sc_threshold 0 \
      -map 0:v:0 -c:v:1 libx264 -profile:v:1 main -crf:v:1 51 -g 25 -keyint_min 25 -sc_threshold 0 \
      -f dash \
      -use_timeline 1 \
      -use_template 1 \
      -seg_duration 1 \
      -min_seg_duration 1000000 \
      -adaptation_sets "id=0,streams=v" \
      "${output_tile_dir}/tile${i}_${j}.mpd"
  done
done
