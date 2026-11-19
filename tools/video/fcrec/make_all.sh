#!/bin/bash
# 第 1、3、4 课样课录屏：中文界面一套、英文界面一套（WQ_LANG=en，成片名加 -en），按顺序录（后一段用前一段存的文件）。
# 环境同 rec.sh；成片放到 $OUT（默认学习平台帮助的 media 目录）。只录一种语言：LANGS=en ./make_all.sh
set -e
H=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-$H/../../../apps/web/src/static/help/wqcad/media}
mkdir -p "$OUT" "$WQ_REC/model" "$WQ_REC/model_en"
for WQ_LANG in ${LANGS:-zh en}; do
  export WQ_LANG
  if [ $WQ_LANG = en ]; then sfx=-en; M=$WQ_REC/model_en; F=NeedleClampSketch; else sfx=; M=$WQ_REC/model; F=针夹草图; fi
  rm -f "$WQ_REC"/练习.FCStd "$WQ_REC"/practice.FCStd
  for c in l01a l01b l01c l02a l02b l02c l03a l03b; do "$H/rec.sh" "$H/$c.py" "$WQ_REC/$c$sfx.mp4"; done
  cp "$M/$F.FCStd" "$M/${F}_L3.FCStd"
  "$H/rec.sh" "$H/l04a.py" "$WQ_REC/l04a$sfx.mp4"
  cp "$M/${F}_L3.FCStd" "$M/$F.FCStd"
  "$H/rec.sh" "$H/l04b.py" "$WQ_REC/l04b$sfx.mp4"
  "$H/rec.sh" "$H/l04c.py" "$WQ_REC/l04c$sfx.mp4"
  for c in l01a l01b l01c l02a l02b l02c l03a l03b l04a l04b l04c; do
    ffmpeg -loglevel error -y -i "$WQ_REC/$c$sfx.mp4" -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart -an "$OUT/wqcad-$c$sfx.mp4"
    ffmpeg -loglevel error -y -sseof -2 -i "$WQ_REC/$c$sfx.mp4" -frames:v 1 -vf scale=960:-1 -q:v 4 "$OUT/wqcad-$c$sfx.jpg"
    cp "$WQ_REC/$c$sfx.vtt" "$OUT/wqcad-$c$sfx.vtt"
  done
done
