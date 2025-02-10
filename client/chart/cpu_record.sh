#!/bin/bash

# 提示用户输入进程PID
read -p "请输入要监控的进程PID: " PROCESS_PID

# 输出文件
OUTPUT_FILE="cpu_usage_log.txt"

# 检查进程是否存在
check_process() {
  # 检查进程是否存在
  if ! ps -p "$PROCESS_PID" > /dev/null; then
    echo "进程 $PROCESS_PID 未找到"
    exit 1
  fi
}

# 获取进程的CPU占用率
get_cpu_usage() {
  cpu_usage=$(ps -p "$PROCESS_PID" -r -o %cpu | tail -n 1)  # 获取CPU占用率
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "$timestamp $cpu_usage" >> "$OUTPUT_FILE"
}

# 主程序，每秒记录一次
check_process
echo "监控开始，记录保存到 $OUTPUT_FILE"
while true; do
  get_cpu_usage
  sleep 1  # 每秒记录一次
done
