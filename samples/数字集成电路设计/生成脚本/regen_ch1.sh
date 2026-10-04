#!/bin/bash
# 参数（labs/micro/kit/models/params.json）变化后，一键重新生成第 1 章全部资料并自检（第 17 轮 RM2）。
# 实验台（含模型比对）→ 实验自动测试 → 指导书与报告模板 → 量规 → 课件用图 → 课件 → 动画（ANIM=0 可跳过）。
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../.." && pwd)
cd "$ROOT"
node labs/micro/tools/build.js
python3 labs/micro/tools/test_dic_ch1.py
cd "$HERE"
python3 build_guides.py
python3 build_rubric.py
python3 deck_assets.py
node build_ch1_deck_bi.js
if [ "${ANIM:-1}" = 1 ]; then bash anim/render.sh; fi
echo "第 1 章资料已重新生成"
