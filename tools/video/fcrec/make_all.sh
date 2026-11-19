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
  "$H/rec.sh" "$H/l05a.py" "$WQ_REC/l05a$sfx.mp4"
  "$H/rec.sh" "$H/l05b.py" "$WQ_REC/l05b$sfx.mp4"
  "$H/rec.sh" "$H/l06a.py" "$WQ_REC/l06a$sfx.mp4"
  "$H/rec.sh" "$H/l06b.py" "$WQ_REC/l06b$sfx.mp4"
  if [ $WQ_LANG = en ]; then B=NeedleBar; else B=针杆; fi
  cp "$M/$B.FCStd" "$M/${B}_L6.FCStd"            # 第 7 课 A 段在上面加第二圈槽、倒角并存盘；录完还原，重录不叠加
  "$H/rec.sh" "$H/l07a.py" "$WQ_REC/l07a$sfx.mp4"
  cp "$M/${B}_L6.FCStd" "$M/$B.FCStd"
  "$H/rec.sh" "$H/l07b.py" "$WQ_REC/l07b$sfx.mp4"
  "$H/rec.sh" "$H/l08a.py" "$WQ_REC/l08a$sfx.mp4"
  "$H/rec.sh" "$H/l08b.py" "$WQ_REC/l08b$sfx.mp4"
  "$H/rec.sh" "$H/l09a.py" "$WQ_REC/l09a$sfx.mp4"
  "$H/rec.sh" "$H/l09b.py" "$WQ_REC/l09b$sfx.mp4"
  "$H/rec.sh" "$H/l09c.py" "$WQ_REC/l09c$sfx.mp4"      # 用第 7 课存的 ${B}_L6（只有一圈槽）
  "$H/rec.sh" "$H/l10a.py" "$WQ_REC/l10a$sfx.mp4"
  "$H/rec.sh" "$H/l10b.py" "$WQ_REC/l10b$sfx.mp4"      # 改了 10a 存的文件（高 22）；重录要先重录 10a
  "$H/rec.sh" "$H/l11a.py" "$WQ_REC/l11a$sfx.mp4"
  cp "$WQLS_TE/head.stl" "$WQ_REC/head.stl"; cp "$WQLS_TE/head.stl" "$WQ_REC/机头.stl"    # 第 12 课导入的网格
  for c in l12a l12b l12c; do "$H/rec.sh" "$H/$c.py" "$WQ_REC/$c$sfx.mp4"; done     # 依次接着上一段存的“机头曲面”
  for c in l01a l01b l01c l02a l02b l02c l03a l03b l04a l04b l04c l05a l05b l06a l06b l07a l07b l08a l08b l09a l09b l09c l10a l10b l11a l12a l12b l12c; do
    ffmpeg -loglevel error -y -i "$WQ_REC/$c$sfx.mp4" -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart -an "$OUT/wqcad-$c$sfx.mp4"
    ffmpeg -loglevel error -y -sseof -2 -i "$WQ_REC/$c$sfx.mp4" -frames:v 1 -vf scale=960:-1 -q:v 4 "$OUT/wqcad-$c$sfx.jpg"
    cp "$WQ_REC/$c$sfx.vtt" "$OUT/wqcad-$c$sfx.vtt"
  done
done
