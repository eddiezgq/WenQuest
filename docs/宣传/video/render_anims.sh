#!/bin/bash
# Render the four Manim animations used in the video at 1080p into <work>/anim/ (about a minute each).
# Usage: bash render_anims.sh <work dir>
W=${1:?work dir}/anim
R=$(cd "$(dirname "$0")/../../.." && pwd)
mkdir -p "$W"
for f in ch04/anim/a4_2_1 ch06/anim/a6_1_1 ch07/anim/a7_2_1 ch12/anim/a12_2_1; do
  n=$(basename $f); [ -f "$W/$n.mp4" ] && continue
  (cd "$R/textbook/robotics/$(dirname $f)" && PYTHONPATH="$R/services/animator" manim -r 1920,1080 --fps 30 --disable_caching \
     --progress_bar none $n.py Lesson --media_dir "$W/media_$n" -o $n > "$W/$n.log" 2>&1)
  m=$(find "$W/media_$n" -name "$n.mp4" | head -1); [ -n "$m" ] && cp "$m" "$W/$n.mp4"
  echo "$n done"
done
