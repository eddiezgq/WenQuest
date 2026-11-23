#!/bin/bash
# 用法：rec.sh 剧本.py 输出.mp4    环境：WQ_REC 工作目录（home、clicks、subs）；FC 解开的 FreeCAD 1.1.4 AppImage（squashfs-root）
H=$(cd "$(dirname "$0")" && pwd)
# WQ_LANG=en：英文界面（$WQ_REC/home_en 里的设置 Language=English）、英文字幕
if [ "$WQ_LANG" = en ]; then export HOME=$WQ_REC/home_en LANG=en_US.UTF-8; else export HOME=$WQ_REC/home LANG=zh_CN.UTF-8; fi
# WQ_STOCK=1：官方 FreeCAD（第 20 课对比用）——去掉问渠品牌（branding.xml 暂时移开），用单独的设置目录（没有 AI 工作台）
if [ "$WQ_STOCK" = 1 ]; then export HOME=$HOME/../home_stock${WQ_LANG:+_$WQ_LANG}; HOME=$(cd "$HOME" && pwd); mv "$FC/usr/bin/branding.xml" "$FC/usr/bin/branding.xml.off" 2>/dev/null; trap 'mv "$FC/usr/bin/branding.xml.off" "$FC/usr/bin/branding.xml" 2>/dev/null' EXIT; fi
export WQ_REC WQ_LANG DISPLAY=${DISPLAY:-:77} LC_ALL=C.UTF-8   # 界面语言看 user.cfg；这里只让 Python 用 UTF-8 认中文文件名
rm -f $WQ_REC/ready.flag $WQ_REC/end.flag $WQ_REC/clicks.txt $WQ_REC/subs.txt
pkill -f squashfs-root/usr/bin/freecad; sleep 1
cd "$WQ_REC" && "$FC/AppRun" "$1" > $WQ_REC/run.log 2>&1 &
FCPID=$!
for i in $(seq 1 300); do [ -f $WQ_REC/ready.flag ] && break; sleep 0.2; done
date +%s.%N > $WQ_REC/t0.txt
ffmpeg -loglevel error -y -f x11grab -draw_mouse 1 -framerate 25 -video_size 1600x900 -i $DISPLAY -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "${2%.mp4}_raw.mp4" &
FF=$!
for i in $(seq 1 4500); do [ -f $WQ_REC/end.flag ] && break; sleep 0.2; done
sleep 1.2; kill -INT $FF; wait $FF; kill -9 $FCPID 2>/dev/null; pkill -9 -f squashfs-root/usr/bin/freecad
cat $WQ_REC/director.log
python3 "$H/rings.py" "${2%.mp4}_raw.mp4" "$2"
