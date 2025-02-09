#!/usr/bin/env bash

# Debug output to confirm correct path parsing
echo "Input file: $1"
echo "Output directory: $2"
echo "MPD name: $3"

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

# Check if OUTPUT is an absolute path
if [[ "$OUTPUT" != /* ]]; then
  echo "Warning: $OUTPUT is not an absolute path. Converting to absolute path."
  OUTPUT="$(pwd)/$OUTPUT"  # Convert to absolute path if relative
fi

# Create output directory if not exists
mkdir -p "$OUTPUT"

# Generate MPD file with three different bitrates for adaptive streaming
exec ffmpeg -hide_banner \
  -i "$INPUT" \
  -vf "$VF" \
  -map 0:v:0 -c:v:0 $CV -profile:v:0 main -b:v:0 20k -maxrate:v:0 25k -bufsize:v:0 30k \
  -map 0:v:0 -c:v:1 $CV -profile:v:1 main -b:v:1 50k -maxrate:v:1 55k -bufsize:v:1 60k \
  -map 0:v:0 -c:v:2 $CV -profile:v:2 main -b:v:2 100k -maxrate:v:2 105k -bufsize:v:2 110k \
  -f dash \
  -segment_time 4 \  # Segment time adjusted for VOD
  -segment_format mp4 \  # Generate MP4 segments for VOD
  -use_template 1 \
  -use_timeline 1 \
  -adaptation_sets "id=0,streams=v" \
  "$OUTPUT/$MPD_NAME.mpd"
