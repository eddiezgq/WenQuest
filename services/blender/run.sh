#!/usr/bin/env bash
# 租来的 Lambda 机器上出一段三维视频（第 38 轮第 2 步）。网关通过 JupyterLab 把这些文件放进 ~/wq3d/：
#   bundle.tgz（渲染器，来自 blender 容器 GET /bundle）、run.sh（本文件）、job/scene.yaml、job/job.json {"quality": "draft"|"hd"}
# 然后在后台运行本文件。进度写在 status.json（网关每隔一会儿读一次）：
#   {"stage": "setup"|"render"|"encode"|"done"|"error", "done": 帧, "total": 帧, "msg": "...", "files": [...]}
# 机器上第一次运行要装环境（Python 3.11、bpy、Chromium、中文字体），约 3–5 分钟。
set -u
cd "$(dirname "$0")"
HERE=$(pwd)
status() { printf '{"stage": "%s", "done": %s, "total": %s, "msg": %s, "files": %s}\n' "$1" "$2" "$3" "$4" "${5:-[]}" > status.tmp && mv status.tmp status.json; }
fail() { msg=$(tail -c 1500 "$1" 2>/dev/null | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))'); status error 0 0 "$msg"; exit 1; }

status setup 0 0 '"unpack"'
rm -rf wq && mkdir -p wq && tar xzf bundle.tgz -C wq || fail /dev/null
if [ ! -x env/bin/python ]; then
  status setup 0 0 '"install"'
  {
    sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq fonts-noto-cjk ffmpeg libegl1 libxkbcommon0 libsm6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1
    curl -LsSf https://astral.sh/uv/install.sh | sh
    "$HOME/.local/bin/uv" venv -q -p 3.11 env
    "$HOME/.local/bin/uv" pip install -q -p env/bin/python -r wq/tools/blender/requirements.txt
    PLAYWRIGHT_BROWSERS_PATH="$HERE/pw" env/bin/python -m playwright install --with-deps chromium
  } > setup.log 2>&1 || fail setup.log
fi
export PLAYWRIGHT_BROWSERS_PATH="$HERE/pw"

Q=$(python3 -c 'import json;print(json.load(open("job/job.json")).get("quality","draft"))')
FLAG=""; [ "$Q" = "draft" ] && FLAG="--draft"
S=wq/video3d/_job
rm -rf "$S" && mkdir -p "$S" && cp job/* "$S"/
TOTAL=$(env/bin/python -c "
import yaml;s=yaml.safe_load(open('$S/scene.yaml'));d='$Q'=='draft'
print(int(float(s['duration'])*(15 if d else int(s.get('fps',30)))))")
CPU=$(nproc)
N=$(( CPU / 3 )); [ "$N" -lt 1 ] && N=1; [ "$N" -gt 12 ] && N=12      # 每份渲染自己也开多线程，份数取核数的三分之一
status render 0 "$TOTAL" '""'
pids=()
for k in $(seq 0 $((N - 1))); do
  env/bin/python wq/tools/blender/render.py "$S" $FLAG --shard "$k/$N" > "render_$k.log" 2>&1 &
  pids+=($!)
done
while :; do
  n=$(ls "$S"/_frames/f*.png 2>/dev/null | wc -l)
  status render "$n" "$TOTAL" '""'
  alive=0; for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ "$alive" = 0 ] && break
  sleep 10
done
for i in "${!pids[@]}"; do wait "${pids[$i]}" || fail "render_$i.log"; done
status encode "$TOTAL" "$TOTAL" '""'
env/bin/python wq/tools/blender/render.py "$S" $FLAG --encode > encode.log 2>&1 || fail encode.log
rm -rf out && mkdir out
for f in "$S"/*.mp4 "$S"/*.webm; do [ -f "$f" ] && cp "$f" out/; done
files=$(cd out && python3 -c 'import json,os;print(json.dumps(sorted(os.listdir("."))))')
[ "$files" = "[]" ] && fail encode.log
status done "$TOTAL" "$TOTAL" '""' "$files"
