#!/bin/bash
# 第 1、3、4 课样课录屏：中文界面一套、英文界面一套（WQ_LANG=en，成片名加 -en），按顺序录（后一段用前一段存的文件）。
# 环境同 rec.sh；成片放到 $OUT（默认学习平台帮助的 media 目录）。只录一种语言：LANGS=en ./make_all.sh
set -e
H=$(cd "$(dirname "$0")" && pwd)
fccmd() { if [ -x "$FC/usr/bin/freecadcmd" ]; then "$FC/usr/bin/freecadcmd" "$@"; else LD_LIBRARY_PATH="$FC/lib" PYTHONHOME="$FC" "$FC/bin/FreeCADCmd" "$@"; fi; }   # 官方 AppImage 或问渠 CAD 的 Linux 环境
OUT=${OUT:-$H/../../../apps/web/src/static/help/wqcad/media}
mkdir -p "$OUT" "$WQ_REC/model" "$WQ_REC/model_en"
LC_ALL=C.UTF-8 fccmd "$H/prep_slider.py"            # 第 15、16 课的零件
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
  for c in l12a l12b l12c l13a l13b l13c l14a; do "$H/rec.sh" "$H/$c.py" "$WQ_REC/$c$sfx.mp4"; done     # 依次接着上一段存的“机头曲面”
  rm -f "$M/slider/曲柄滑块.FCStd" "$M/slider/SliderCrank.FCStd"
  for c in l15a l15b l16a l16b; do "$H/rec.sh" "$H/$c.py" "$WQ_REC/$c$sfx.mp4"; done
  cp "$FC"/usr/share/Mod/TechDraw/Templates/ISO/localized/zh-CN/landscape/A4_Landscape_CN_CLIP.svg "$WQ_REC/" 2>/dev/null
  cp "$FC"/usr/share/Mod/TechDraw/Templates/ISO/A4_Landscape_ISO5457_minimal.svg "$WQ_REC/" 2>/dev/null
  LC_ALL=C.UTF-8 fccmd "$H/prep_needle_drawing.py"   # 第 17 课的针杆（两种语言的文件都重做）
  for c in l17a l17b; do "$H/rec.sh" "$H/$c.py" "$WQ_REC/$c$sfx.mp4"; done
  cp "$FC"/usr/share/Mod/TechDraw/Templates/ISO/localized/zh-CN/landscape/A3_Landscape_CN_CLIP.svg "$WQ_REC/" 2>/dev/null
  cp "$FC"/usr/share/Mod/TechDraw/Templates/ISO/A3_Landscape_ISO5457_minimal.svg "$WQ_REC/" 2>/dev/null
  for c in l18a l18b; do "$H/rec.sh" "$H/$c.py" "$WQ_REC/$c$sfx.mp4"; done     # 18a 接 17b 存的针杆图；18b 接第 16 课存的曲柄滑块
  WQ_CRANK="$WQ_REC/crank_r178.step" LC_ALL=C.UTF-8 fccmd "$H/prep_crank_fea.py"   # 第 19 课的针杆曲柄 + 两条辅助线（第 178 轮的曲柄）
  for c in l19a l19b; do "$H/rec.sh" "$H/$c.py" "$WQ_REC/$c$sfx.mp4"; done     # 19b 接 19a 存的分析
  FAPR=${FAP_REPO:-/home/claude/freecad-ai-parts}                               # 19c：问渠有限元入门例子 02 的零件和 AI 回复录制（回放）
  mkdir -p "$WQ_REC/rj201"; cp "$FAPR/examples/wenquest-fea/02-rj201-shaft-sentence/RJ-201.step" "$WQ_REC/rj201/"
  rm -rf "$WQ_REC/fea_draft_rec"; cp -r "$FAPR/tests/recordings/fea_draft" "$WQ_REC/fea_draft_rec"
  FAP_LLM_REPLAY="$WQ_REC/fea_draft_rec" FAP_AI_PROVIDER=claude "$H/rec.sh" "$H/l19c.py" "$WQ_REC/l19c$sfx.mp4"
  # 第 21 课 AI 工作台（AI 工作台 59aa749 = 问渠 CAD 0.3.4：四个面板有英文，11-23）
  if true; then
    if [ $WQ_LANG = en ]; then export WQ_ENT=/srv/wq/demo-sewing-company; else export WQ_ENT="/srv/wq/示范缝纫机企业库"; fi
    rm -rf "$WQ_ENT"; mkdir -p "$(dirname "$WQ_ENT")"
    cp -r "$FAPR/examples/enterprise-lockstitch/library" "$WQ_ENT"            # 示范缝纫机企业（虚构）的企业库
    HS="$WQ_REC/home${sfx/-/_}/.freecad-ai-parts/settings.json"; mkdir -p "$(dirname "$HS")"
    echo '{"first_run_done": true}' > "$HS"                                   # 21b 第一段在界面里选企业库
    "$H/rec.sh" "$H/l21a.py" "$WQ_REC/l21a$sfx.mp4"
    WQ_PART=1 "$H/rec.sh" "$H/l21b.py" "$WQ_REC/l21b1$sfx.mp4"
    WQ_PART=2 "$H/rec.sh" "$H/l21b.py" "$WQ_REC/l21b2$sfx.mp4"                 # 重启后企业库生效
    python3 "$H/cat_rec.py" "$WQ_REC/l21b$sfx.mp4" "$WQ_REC/l21b1$sfx.mp4" "$WQ_REC/l21b2$sfx.mp4"
    "$H/rec.sh" "$H/l21c.py" "$WQ_REC/l21c$sfx.mp4"
  fi
  for c in l01a l01b l01c l02a l02b l02c l03a l03b l04a l04b l04c l05a l05b l06a l06b l07a l07b l08a l08b l09a l09b l09c l10a l10b l11a l12a l12b l12c l13a l13b l13c l14a l15a l15b l16a l16b l17a l17b l18a l18b l19a l19b l19c l21a l21b l21c; do
    ffmpeg -loglevel error -y -i "$WQ_REC/$c$sfx.mp4" -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart -an "$OUT/wqcad-$c$sfx.mp4"
    ffmpeg -loglevel error -y -sseof -2 -i "$WQ_REC/$c$sfx.mp4" -frames:v 1 -vf scale=960:-1 -q:v 4 "$OUT/wqcad-$c$sfx.jpg"
    cp "$WQ_REC/$c$sfx.vtt" "$OUT/wqcad-$c$sfx.vtt"
  done
done
