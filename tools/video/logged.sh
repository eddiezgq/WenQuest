#!/bin/sh
# 在 GitHub Actions 里运行一条命令：输出照常显示；失败时把最后 60 行写成 ::error:: 注释，运行摘要里就能看到原因。
log="${RUNNER_TEMP:-/tmp}/logged.$$.txt"
{ "$@"; echo $? > "$log.code"; } 2>&1 | tee "$log"
code=$(cat "$log.code" 2>/dev/null || echo 1)
if [ "$code" != "0" ]; then
    msg=$(tail -n 60 "$log" | cut -c1-400 | sed -e 's/%/%25/g' | awk '{printf "%s%%0A", $0}')
    echo "::error title=$1 $2 failed::$msg"
fi
rm -f "$log" "$log.code"
exit "$code"
