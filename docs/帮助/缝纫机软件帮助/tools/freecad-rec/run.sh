#!/bin/bash
# 录一段 FreeCAD：bash run.sh <段名>

CLIP=$1; OUT=/home/claude/fc/rec/out; mkdir -p $OUT
[ -f /tmp/xvfb99.pid ] && kill $(cat /tmp/xvfb99.pid) 2>/dev/null; sleep 1
Xvfb :99 -screen 0 1280x720x24 -nolisten tcp >/dev/null 2>&1 &
XV=$!; echo $XV > /tmp/xvfb99.pid; sleep 2
export DISPLAY=:99 HOME=/home/claude/fc/home LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONIOENCODING=utf-8 QT_QPA_PLATFORM=xcb
export WQ_CLIP=$CLIP WQ_CUES=$OUT/$CLIP.cues.json WQ_KEYFILE=/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/ui/key.txt
export WQ_PARAMS=/home/claude/fc/rec/web-6000.wqsew.json
T0=$(date +%s.%N)
ffmpeg -loglevel error -y -f x11grab -video_size 1280x720 -framerate 25 -i :99 -c:v libx264 -preset ultrafast -crf 18 $OUT/$CLIP.raw.mp4 &
FF=$!
timeout 300 /home/claude/fc/squashfs-root/usr/bin/freecad /home/claude/fc/rec/drive.py > $OUT/$CLIP.log 2>&1 || true
kill -INT $FF; wait $FF 2>/dev/null || true
kill $XV 2>/dev/null || true
echo "{\"t0\": $T0}" > $OUT/$CLIP.t0.json
grep -i "STEP ERROR\|Traceback" $OUT/$CLIP.log | head -5
echo "$CLIP recorded"
