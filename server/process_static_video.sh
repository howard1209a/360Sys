#!/usr/bin/env bash

export VW="640"
export VH="360"
export ABANDWIDTH="96k"
export VBANDWIDTH="800k"
export VMAXRATE="856k"
export VBUFSIZE="1200k"
export INPUT="$1"
export OUTPUT="$2"
export MPD_NAME="$3"

# Validate required variables
for var in VW VH ABANDWIDTH VBANDWIDTH VMAXRATE VBUFSIZE; do
  if [[ -z "${!var}" ]]; then
    echo "Missing \$$var"
    exit 1
  fi
done

if [ -z "$CV" ] || [ -z "$VF" ]; then
  echo "Using CPU encoding."
  VF="scale=w=$VW:h=$VH:force_original_aspect_ratio=decrease"
  CV="libx264"
fi

# Create output directory if not exists
mkdir -p "$OUTPUT"

# Generate live MPD file with three different bitrates for adaptive streaming
exec ffmpeg -hide_banner -loglevel debug \
  -i "$INPUT" \
  -vf "$VF" \
  -map 0:v:0 -c:v:0 libx264 -profile:v:0 main -b:v:0 20k -maxrate:v:0 25k -bufsize:v:0 30k \
  -map 0:v:0 -c:v:1 libx264 -profile:v:1 main -b:v:1 50k -maxrate:v:1 55k -bufsize:v:1 60k \
  -map 0:v:0 -c:v:2 libx264 -profile:v:2 main -b:v:2 100k -maxrate:v:2 105k -bufsize:v:2 110k \
  -f dash \
  -segment_time 12 \
  -segment_list "$OUTPUT/stream.m3u8" \
  -segment_format mp4 \
  -use_template 1 \
  -use_timeline 1 \
  -adaptation_sets "id=0,streams=v" \
  "$OUTPUT/$MPD_NAME.mpd"

