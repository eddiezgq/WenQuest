#!/bin/bash
# 第 1、3、4 课样课录屏，按顺序录（后一段用前一段存的文件）。环境同 rec.sh；成片放到 $OUT（默认学习平台帮助的 media 目录）
set -e
H=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-$H/../../../apps/web/src/static/help/wqcad/media}
mkdir -p "$OUT" "$WQ_REC/model"
for c in l01a l01b l01c l03a l03b; do "$H/rec.sh" "$H/$c.py" "$WQ_REC/$c.mp4"; done
cp "$WQ_REC/model/针夹草图.FCStd" "$WQ_REC/model/针夹草图_L3.FCStd"
"$H/rec.sh" "$H/l04a.py" "$WQ_REC/l04a.mp4"
cp "$WQ_REC/model/针夹草图_L3.FCStd" "$WQ_REC/model/针夹草图.FCStd"
"$H/rec.sh" "$H/l04b.py" "$WQ_REC/l04b.mp4"
"$H/rec.sh" "$H/l04c.py" "$WQ_REC/l04c.mp4"
for c in l01a l01b l01c l03a l03b l04a l04b l04c; do
  ffmpeg -loglevel error -y -i "$WQ_REC/$c.mp4" -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart -an "$OUT/wqcad-$c.mp4"
  ffmpeg -loglevel error -y -sseof -2 -i "$WQ_REC/$c.mp4" -frames:v 1 -vf scale=960:-1 -q:v 4 "$OUT/wqcad-$c.jpg"
  cp "$WQ_REC/$c.vtt" "$OUT/wqcad-$c.vtt"
done
