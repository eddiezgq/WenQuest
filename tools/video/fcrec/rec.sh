#!/bin/bash
# 用法：rec.sh 剧本.py 输出.mp4    环境：WQ_REC 工作目录（home、clicks、subs）；FC 解开的 FreeCAD 1.1.4 AppImage（squashfs-root）
# WQ_LANG=en：英文界面（$WQ_REC/home_en 里的设置 Language=English）、英文字幕
if [ "$WQ_LANG" = en ]; then export HOME=$WQ_REC/home_en LANG=en_US.UTF-8; else export HOME=$WQ_REC/home LANG=zh_CN.UTF-8; fi
export WQ_REC WQ_LANG DISPLAY=${DISPLAY:-:77}
rm -f $WQ_REC/ready.flag $WQ_REC/end.flag $WQ_REC/clicks.txt $WQ_REC/subs.txt
pkill -f squashfs-root/usr/bin/freecad; sleep 1
"$FC/AppRun" "$1" > $WQ_REC/run.log 2>&1 &
FCPID=$!
for i in $(seq 1 300); do [ -f $WQ_REC/ready.flag ] && break; sleep 0.2; done
date +%s.%N > $WQ_REC/t0.txt
ffmpeg -loglevel error -y -f x11grab -draw_mouse 1 -framerate 25 -video_size 1600x900 -i $DISPLAY -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "${2%.mp4}_raw.mp4" &
FF=$!
for i in $(seq 1 1500); do [ -f $WQ_REC/end.flag ] && break; sleep 0.2; done
sleep 1.2; kill -INT $FF; wait $FF; kill -9 $FCPID 2>/dev/null; pkill -9 -f squashfs-root/usr/bin/freecad
cat $WQ_REC/director.log
python3 "$(dirname "$0")/rings.py" "${2%.mp4}_raw.mp4" "$2"
