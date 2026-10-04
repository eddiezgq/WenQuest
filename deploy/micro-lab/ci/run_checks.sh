#!/bin/bash
# 第 17 轮附 4a–4d 验收：在 wenquest/micro-lab 镜像里运行（由 .github/workflows/micro-lab.yml 调用）。
# /repo = 仓库（只读），/out = 结果目录。每一步的结论写进 /out/summary.json；任何一步不过，脚本以非零退出。
set -u
OUT=/out; mkdir -p "$OUT"
REPO=/repo
CH1=$WQ_HOME/ch1
fail=0
step() { echo "::group::$1"; }
endstep() { echo "::endgroup::"; }

step "工具版本"
wqlab tools > "$OUT/tools.json" 2> "$OUT/tools.err" || fail=1
cat "$OUT/tools.json"
endstep

step "4b 反相器：Xschem 网表 → Magic 版图 → DRC → LVS"
mkdir -p "$OUT/inv"
cp "$CH1/inv.sch" "$OUT/inv/inv.sch"
wqlab netlist "$OUT/inv/inv.sch" -o "$OUT/inv" > "$OUT/inv/netlist.log" 2>&1 || { fail=1; cat "$OUT/inv/netlist.log"; }
if [ -f "$OUT/inv/inv.spice" ]; then
  wqlab inv --schematic "$OUT/inv/inv.spice" --out "$OUT/inv/build" || fail=1
else
  wqlab inv --out "$OUT/inv/build" || fail=1
fi
endstep

step "4d SKY130 校准（完整 PDK 模型）"
LIB=$(ls "$PDKPATH"/libs.tech/combined/sky130.lib.spice "$PDKPATH"/libs.tech/ngspice/sky130.lib.spice 2>/dev/null | head -1)
echo "model library: $LIB"
CALIB_OUT="$OUT/calib" SKY130_LIB="$LIB" python3 "$REPO/samples/数字集成电路设计/生成脚本/calib/calib.py" > "$OUT/calib.log" 2>&1 || { fail=1; tail -40 "$OUT/calib.log"; }
cat "$OUT/calib.log" | tail -12
python3 - "$REPO/samples/数字集成电路设计/生成脚本/calib/result.json" "$OUT/calib/result.json" > "$OUT/calib_compare.json" <<'PY' || fail=1
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
rows = {"idsat_n": (a["device"]["idsat_n"], b["device"]["idsat_n"]), "idsat_p": (a["device"]["idsat_p"], b["device"]["idsat_p"]),
        "fo4_2.25": (sum(a["delay"]["2.25"]["4"]) / 2, sum(b["delay"]["2.25"]["4"]) / 2),
        "VM_1": (a["vtc"][0]["VM"], b["vtc"][0]["VM"]), "cin_2.25": (a["cin"]["2.25"], b["cin"]["2.25"])}
out = {k: {"repo": x, "image": y, "diff_pct": round(100 * (y - x) / x, 2)} for k, (x, y) in rows.items()}
print(json.dumps(out, indent=1))
sys.exit(0 if all(abs(v["diff_pct"]) <= 3 for v in out.values()) else 1)
PY
cat "$OUT/calib_compare.json"
endstep

step "4c 8 位计数器 RTL→GDS（LibreLane）"
mkdir -p "$OUT/counter8"
wqlab flow "$CH1/counter8/config.json" --out "$OUT/counter8" || fail=1
tail -30 "$OUT/counter8/librelane.log"
endstep

python3 - <<'PY'
import json, os
o = "/out"
def j(p):
    try: return json.load(open(os.path.join(o, p)))
    except Exception: return None
s = {"tools": j("tools.json"), "inv": j("inv/build/result.json"), "calib_compare": j("calib_compare.json"),
     "calib_fit": (j("calib/result.json") or {}).get("fit"), "counter8": j("counter8/result.json")}
json.dump(s, open(os.path.join(o, "summary.json"), "w"), indent=1, ensure_ascii=False)
inv, c8 = s["inv"] or {}, s["counter8"] or {}
print(f"::notice title=反相器::DRC {inv.get('drc_errors')}，LVS {inv.get('lvs_match')}，面积 {inv.get('area_um2')} μm²")
print(f"::notice title=计数器 GDS::流片就绪 {c8.get('tapeout_ready')}，setup {c8.get('setup_ws_ns')} ns，hold {c8.get('hold_ws_ns')} ns，DRC {c8.get('magic_drc_errors')}，LVS {c8.get('lvs_errors')}，{c8.get('seconds')} s，内存峰值 {c8.get('peak_mem_mb')} MB")
cc = s["calib_compare"] or {}
print("::notice title=校准对照::" + "；".join(f"{k} {v['diff_pct']}%" for k, v in cc.items()))
PY
exit $fail
