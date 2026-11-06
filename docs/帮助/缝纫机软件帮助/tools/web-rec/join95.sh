#!/bin/bash
# 第 95 轮：两段带配音的录屏接成一段（都转成 1280×720、25 帧、AAC），字幕时间顺延。
#   bash join95.sh <前段.mp4> <后段.mp4> <后段取几秒，0 = 全部> <出片.mp4> [前段.vtt 后段.vtt 出片.vtt]
# web-14-video：录屏 + 第 90 轮花样机 2000 转配旁白小样的开头（docs/截图/第90轮-讲解片配音/），小样自带字幕，不另加
# fc-09-video：FreeCAD 那一段 + 浏览器那一段（wfc09.js）
set -e
A=$1; B=$2; SEC=$3; OUT=$4
TB=""; [ "$SEC" != "0" ] && TB="-t $SEC"
ffmpeg -loglevel error -y -i "$A" $TB -i "$B" -filter_complex \
  "[0:v]scale=1280:720,fps=25,setsar=1[v0];[1:v]scale=1280:720,fps=25,setsar=1[v1];[0:a]aresample=48000[a0];[1:a]aresample=48000,afade=t=out:st=$( [ "$SEC" != "0" ] && echo $((SEC-1)) || echo 99999 ):d=1[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$OUT"
if [ -n "$5" ]; then
  python3 - "$A" "$5" "$6" "$7" <<'E'
import re, subprocess, sys
a, va, vb, out = sys.argv[1:5]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a], capture_output=True, text=True).stdout)
def sh(m):
    t = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) + dur
    return "%02d:%02d:%06.3f" % (t // 3600, t % 3600 // 60, t % 60)
pa = open(va, encoding="utf-8").read().rstrip() + "\n\n"
pb = open(vb, encoding="utf-8").read().split("\n\n", 1)[1] if vb != "-" else ""
pb = re.sub(r"(\d+):(\d+):([\d.]+)", sh, pb)
open(out, "w", encoding="utf-8").write(pa + pb)
E
fi
