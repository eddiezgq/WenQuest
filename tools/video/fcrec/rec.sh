#!/bin/bash
# 用法：rec.sh 剧本.py 输出.mp4
# WQ_REC：工作目录（home、model、clicks）；FC：解开的 FreeCAD 1.1.4 AppImage（squashfs-root）
F=$FC
export WQ_REC
export HOME=$WQ_REC/home LANG=zh_CN.UTF-8 DISPLAY=:77
rm -f $WQ_REC/ready.flag $WQ_REC/end.flag $WQ_REC/clicks.txt
pkill -f squashfs-root/usr/bin/freecad; sleep 1
$F/AppRun "$1" > $WQ_REC/run.log 2>&1 &
FCPID=$!
until [ -f $WQ_REC/ready.flag ]; do sleep 0.2; done
date +%s.%N > $WQ_REC/t0.txt
ffmpeg -loglevel error -y -f x11grab -draw_mouse 1 -framerate 25 -video_size 1600x900 -i :77 -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "${2%.mp4}_raw.mp4" &
FF=$!
for i in $(seq 1 600); do [ -f $WQ_REC/end.flag ] && break; sleep 0.2; done
sleep 1.5; kill -INT $FF; wait $FF; kill -9 $FCPID 2>/dev/null; pkill -9 -f squashfs-root/usr/bin/freecad
grep -E "Traceback|Error" -A3 $WQ_REC/run.log | grep -v defects | head -20
python3 $(dirname "$0")/rings.py "${2%.mp4}_raw.mp4" "$2"
