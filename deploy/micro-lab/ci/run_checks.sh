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

step "第 5 步 贯通项目参考解：器件 → 与非门 → RTL 测试 → Tiny Tapeout 格式 GDS"
CAP=$WQ_HOME/capstone
export WQ_CAP_REF=$REPO/deploy/micro-lab/wenquest/capstone/ref      # 参考解不在镜像里，从仓库读
test ! -e "$CAP/ref" || { echo "::error::参考解进了学生镜像（capstone/ref）"; fail=1; }
mkdir -p "$OUT/capstone"
cmp -s "$CAP/ch1_params.json" "$REPO/labs/micro/kit/models/params.json" || { echo "::error::capstone/ch1_params.json 与 labs/micro/kit/models/params.json 不一致（运行 regen_ch1.sh）"; fail=1; }
wqlab device --out "$OUT/capstone/step1" > "$OUT/capstone/step1.log" 2>&1 || { fail=1; tail -20 "$OUT/capstone/step1.log"; }
wqlab nand2 --out "$OUT/capstone/step2" > "$OUT/capstone/step2.log" 2>&1 || { fail=1; tail -20 "$OUT/capstone/step2.log"; }
cp -r "$WQ_CAP_REF/step3_rtl" "$OUT/capstone/step3"
wqlab test "$OUT/capstone/step3" > "$OUT/capstone/step3.log" 2>&1 || { fail=1; tail -40 "$OUT/capstone/step3.log"; }
wqlab tt "$OUT/capstone/step3" --out "$OUT/capstone/step4" > "$OUT/capstone/step4.log" 2>&1 || { fail=1; tail -40 "$OUT/capstone/step4.log"; tail -30 "$OUT/capstone/step4/librelane.log" 2>/dev/null; }
# 第 5 步试点：AI 测试学生只看指导书和起始文件做出的作品，在镜像里用学生命令检查，步骤四在这里跑
PILOT=$REPO/samples/微电子贯通项目/试点/第1次
if [ -d "$PILOT" ]; then
  P=$OUT/pilot; rm -rf "$P"; cp -r "$PILOT" "$P"
  wqlab device --script "$P/step1_device/device_curves.py" --out "$P/step1_device/out" > "$P/step1.log" 2>&1 || { fail=1; tail -20 "$P/step1.log"; }
  wqlab nand2 --check "$P/step2_nand2" --schematic "$P/step2_nand2/nand2_schematic.spice" > "$P/step2.log" 2>&1 || { fail=1; tail -20 "$P/step2.log"; }
  wqlab test "$P/step3_rtl" > "$P/step3.log" 2>&1 || { fail=1; tail -30 "$P/step3.log"; }
  cp "$P/step3_rtl/result.json" "$P/step3_own.json" 2>/dev/null || true
  wqlab test "$P/step3_rtl" --ref > "$P/step3ref.log" 2>&1 || { fail=1; tail -30 "$P/step3ref.log"; }
  wqlab tt "$P/step3_rtl" --config "$CAP/start/step4_chip/config.json" --out "$P/step4" > "$P/step4.log" 2>&1 || { fail=1; tail -30 "$P/step4.log"; }
fi
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
cs = {k: j(f"capstone/{k}/result.json") or {} for k in ("step1", "step2", "step3", "step4")}
s["capstone"] = cs
json.dump(s, open(os.path.join(o, "summary.json"), "w"), indent=1, ensure_ascii=False)
c1, c2, c3, c4 = (cs[k] for k in ("step1", "step2", "step3", "step4"))
print(f"::notice title=贯通 1 器件::VTn {c1.get('vtn_v')} V，VTp {c1.get('vtp_v')} V，IDSAT n/p {c1.get('idsat_n_ua_um')}/{c1.get('idsat_p_ua_um')} μA/μm，S {c1.get('swing_n_mv_dec')} mV/dec，迁移率比 {c1.get('mobility_ratio')}")
sc = c2.get("stdcell") or {}
print(f"::notice title=贯通 2 与非门::DRC {c2.get('drc_errors')}，LVS {c2.get('lvs_match')}，面积 {c2.get('area_um2')} μm²；标准单元 {sc.get('area_um2')} μm²（{sc.get('width_um')}×{sc.get('height_um')}），管宽 n {sc.get('nmos_w_um')} p {sc.get('pmos_w_um')}；面积比 {c2.get('area_ratio_vs_stdcell')}")
print(f"::notice title=贯通 3 测试::{c3.get('passed')}/{c3.get('tests')} 通过，{c3.get('seconds')} s")
pl = {"step1": j("pilot/step1_device/out/result.json"), "step2": j("pilot/step2_nand2/result.json"), "step3_own": j("pilot/step3_own.json"),
      "step3_ref": j("pilot/step3_rtl/result.json"), "step4": j("pilot/step4/result.json")}
if any(pl.values()):
    p4, p2 = pl["step4"] or {}, pl["step2"] or {}
    print(f"::notice title=试点学生::器件 VTn {(pl['step1'] or {}).get('vtn_v')}；与非门 DRC {p2.get('drc_errors')} LVS {p2.get('lvs_match')} 面积 {p2.get('area_um2')}；"
          f"自己的测试 {(pl['step3_own'] or {}).get('passed')}/{(pl['step3_own'] or {}).get('tests')}，参考测试 {(pl['step3_ref'] or {}).get('passed')}/{(pl['step3_ref'] or {}).get('tests')}；"
          f"芯片 TT 就绪 {p4.get('tt_ready')}，setup {p4.get('setup_ws_ns')} ns，hold {p4.get('hold_ws_ns')} ns，DRC {p4.get('magic_drc_errors')}，LVS {p4.get('lvs_errors')}，天线 {p4.get('antenna_violations')}")
s["pilot"] = pl
json.dump(s, open(os.path.join(o, "summary.json"), "w"), indent=1, ensure_ascii=False)
import base64, gzip
print("::notice title=贯通结果 summary::" + base64.b64encode(gzip.compress(json.dumps({"capstone": cs, "pilot": pl}, separators=(",", ":")).encode())).decode())
print(f"::notice title=贯通 4 芯片::TT 就绪 {c4.get('tt_ready')}（流片就绪 {c4.get('tapeout_ready')}，接口 {c4.get('ports_ok')}，1 块 {c4.get('fits_one_tile')}）；setup {c4.get('setup_ws_ns')} ns，hold {c4.get('hold_ws_ns')} ns，DRC {c4.get('magic_drc_errors')}，LVS {c4.get('lvs_errors')}，天线 {c4.get('antenna_violations')}，单元 {c4.get('cells')}，{c4.get('seconds')} s，{c4.get('peak_mem_mb')} MB")
# 镜像里的完整校准结果（gzip + base64），供仓库采用：python -c "import sys,gzip,base64;print(gzip.decompress(base64.b64decode(sys.argv[1])).decode())" <注释内容>
import base64, gzip
for name in ("result", "params.sky130"):
    f = os.path.join(o, "calib", name + ".json")
    if os.path.exists(f):
        raw = json.dumps(json.load(open(f)), separators=(",", ":")).encode()
        print(f"::notice title=校准结果 {name}.json::" + base64.b64encode(gzip.compress(raw)).decode())
PY
exit $fail
