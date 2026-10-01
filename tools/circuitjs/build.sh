#!/usr/bin/env bash
# 从源码编译 CircuitJS1 嵌入版（第 7 轮第 6 步）。由 .github/workflows/circuitjs.yml 在 GitHub 上运行（需要 Maven 仓库和 Java 8）。
#   tools/circuitjs/build.sh <输出文件>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$(realpath -m "${1:-circuitjs-embed.html}")"
COMMIT="$(cat "$HERE/COMMIT")"
WORK="$(mktemp -d)"
git -C "$WORK" init -q
git -C "$WORK" remote add origin https://github.com/pfalstad/circuitjs1.git
git -C "$WORK" fetch -q --depth 1 origin "$COMMIT"
git -C "$WORK" checkout -q FETCH_HEAD
python3 "$HERE/patch.py" "$WORK"
( cd "$WORK" && ./gradlew --no-daemon --console plain compileGwt )
python3 "$HERE/bundle.py" "$WORK" "$OUT" "$COMMIT"
