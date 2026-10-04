#!/bin/bash
# 渲染第 1 章 5 段动画（1080p 30 帧），输出到 课程资料/第1章 CMOS反相器/动画/
export PATH=/home/claude/manim-venv/bin:$PATH
cd "$(dirname "$0")"
OUT="../../课程资料/第1章 CMOS反相器/动画"; mkdir -p "$OUT"

for s in ${SCENES:-SwitchPath VtcSweep Sizing Chain Power}; do
  manim -r 1920,1080 --fps 30 --disable_caching -o "$s" ch1.py $s > "log_$s.txt" 2>&1 \
    && cp "media/videos/ch1/1080p30/$s.mp4" "$OUT/$(python3 -c "print({'SwitchPath':'1.1','VtcSweep':'1.2','Sizing':'1.3','Chain':'1.4','Power':'1.5'}['$s'])")_$s.mp4" && echo "$s ok" || echo "$s FAIL"

done
