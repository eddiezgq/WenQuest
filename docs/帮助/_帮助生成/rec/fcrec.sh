#!/bin/bash
# 录一段带配音的 FreeCAD（第 90 轮）：bash fcrec.sh <脚本.py> <段名> <配音目录> <录屏目录>
# 需要：Xvfb、ffmpeg、FreeCAD（FREECAD 环境变量，默认 freecad）；HOME 指向装好工作台的用户目录（FC_HOME）。
SCRIPT=$(realpath "$1"); CLIP=$2; VOICE=$(realpath "$3"); OUT=$(realpath -m "$4"); mkdir -p "$OUT"
HERE=$(dirname "$(realpath "$0")")
Xvfb :98 -screen 0 1280x720x24 -nolisten tcp >/dev/null 2>&1 &
XV=$!; sleep 2
export DISPLAY=:98 HOME=${FC_HOME:-$HOME} LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONIOENCODING=utf-8 QT_QPA_PLATFORM=xcb
export WQ_SCRIPT=$SCRIPT WQ_CLIP=$CLIP WQ_VOICE=$VOICE WQ_OUT=$OUT/$CLIP.json
export WQ_T0=$(date +%s.%N)
ffmpeg -loglevel error -y -use_wallclock_as_timestamps 1 -f x11grab -video_size 1280x720 -framerate 25 -i :98 -fps_mode cfr -r 25 -c:v libx264 -preset ultrafast -crf 18 "$OUT/$CLIP.raw.mp4" &
FF=$!
timeout 600 ${FREECAD:-freecad} "$HERE/fcvrec.py" > "$OUT/$CLIP.log" 2>&1 || true
kill -INT $FF; wait $FF 2>/dev/null || true
kill $XV 2>/dev/null || true
grep -i "STEP ERROR\|Traceback\|NO VOICE" "$OUT/$CLIP.log" | head -5
echo "$CLIP recorded"
