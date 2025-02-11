#!/bin/bash

# 启动 FFmpeg 进程，并设置输出到 "output.mpd" 文件
ffmpeg -i /Users/howard1209a/Desktop/codes/dash_file/video/school/tile_1_480p_186kbps_30fps.mp4 -c:v libx264 -preset ultrafast -tune zerolatency \
  -g 10 -keyint_min 10 \
  -f dash -segment_time 4 -use_template 1 -use_timeline 1 \
  -window_size 5 -extra_window_size 5 -remove_at_exit 1 \
  output.mpd &

# 获取 FFmpeg 进程的 PID
ffmpeg_pid=$!

# 启动一个命名管道，用于动态控制 FFmpeg
mkfifo ffmpeg_control

# 监听 angular_speed 的输入
while read angular_speed; do
  # 根据 angular_speed 设置 segment_duration
  if [ "$angular_speed" -gt 120 ]; then
    seg_duration=1
  elif [ "$angular_speed" -gt 69 ]; then
    seg_duration=2
  else
    seg_duration=4
  fi

  # 输出当前的 segment_duration
  echo "Setting segment duration to $seg_duration seconds"

  # 通过管道向 FFmpeg 传递新的参数
  echo "segment_duration $seg_duration" > ffmpeg_control

done

# 等待 FFmpeg 进程结束
wait $ffmpeg_pid
