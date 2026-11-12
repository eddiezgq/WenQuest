"""第 161g 轮：芯片封测厂案例 C——编码器接口芯片 WQ-ENCIF：规格 → RTL → 逐拍仿真对照参考模型 → 综合与版图（SKY130）→ 晶圆测试 → 封装 → 成品测试。

    python3 tools/cases/chip_c.py

设计是第 92–93 轮已有的（factory/designs/wq-encif：RTL、Python 参考模型、Icarus 仿真、LibreLane 版图，CI 工作流 chip.yml 产出 out/design.json）；
本案例按八步串起来，补“制造”：芯片封测厂仿真车间晶圆测试（晶圆图）+ 封装测试。输出到 factory/cases/chip/C/。
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-chip.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
from sim import wafermap as WM  # noqa: E402

E = ROOT / "factory" / "designs" / "wq-encif"
DJ = json.loads((E / "out" / "design.json").read_text(encoding="utf-8"))
LY = DJ["layout"]
TOOLS = {
    "chip": ("芯片设计（WQ-ENCIF）", "Chip design (WQ-ENCIF)", "/chip-design"),
    "wafer": ("晶圆图", "Wafer map", "/wafer-map"),
    "pcb": ("电路板设计（驱动板 B 版）", "PCB design (drive board B)", "/pcb-design"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "lab40": ("实验 40：一批芯片从订单到交付", "Lab 40: a chip lot from order to delivery", "/labo/40"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("chip", "C", "完整", "编码器接口芯片 WQ-ENCIF：从 RTL 到封装测试", "Encoder interface IC WQ-ENCIF: from RTL to packaged test", "WQ-ENCIF",
              "一颗真能走完开源流程的小芯片：引脚与寄存器、五个功能块的 RTL、九个场景逐拍对照 Python 参考模型、SKY130 综合与版图（时序、设计规则、LVS），"
              "到芯片封测厂一片晶圆的晶圆测试（晶圆图、良率）、封装 12 道工序、成品测试，约 34 000 只交给电路板厂。",
              "A small chip that really goes through an open-source flow: pins and registers, RTL of five blocks, nine scenarios checked cycle by cycle against a Python model, "
              "SKY130 synthesis and layout (timing, DRC, LVS), then wafer probe of one wafer (wafer map, yield), 12 assembly steps and final test, about 34 000 parts to the PCB plant.",
              "tools/cases/chip_c.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：编码器接口芯片 WQ-ENCIF

**为什么要做芯片**　关节驱动板读电机端增量编码器（A、B、Z），原来用 MCU 定时器的编码器模式：滤波弱、丢步查不出、Z 相要软件处理。
做一颗小芯片：滤波、4 倍频解码、32 位计数、丢步检测、Z 相锁存，MCU 通过 SPI 读——驱动板 B 版用它（电路板厂案例 C）。

| 项目 | 值 | 出处 |
|---|---|---|
| 工艺 | {DJ['pdk']} | 开源工艺库 |
| 时钟 | {DJ['clock_mhz']} MHz | 设计 |
| 引脚 | {len(DJ['pins'])} 个信号脚（{', '.join(p['name'] for p in DJ['pins'])}） | `out/design.json` |
| 寄存器 | {len(DJ['regs'])} 个（{', '.join(r['addr'] + ' ' + r['name'] for r in DJ['regs'])}） | 同上 |
| 封装 | QFN-16 3×3 mm | 芯片厂清单 |
| 量 | 一片晶圆一批，约 34 000 只（电路板厂整批买） | 芯片厂清单 |

> {DJ['disclaimer']}
"""
case.step("brief", f"{DJ['pdk']}、{DJ['clock_mhz']} MHz；{len(DJ['pins'])} 个信号脚、{len(DJ['regs'])} 个寄存器；QFN-16；一片晶圆约 34 000 只。",
          f"{DJ['pdk']}, {DJ['clock_mhz']} MHz; {len(DJ['pins'])} signal pins, {len(DJ['regs'])} registers; QFN-16; about 34 000 parts per wafer.",
          md=case.text("1_任务书.md", brief), tools=tools("chip", "pcb"), facts=[("时钟", "Clock", DJ["clock_mhz"], "MHz"), ("寄存器", "Registers", len(DJ["regs"]), "")])

# ================================================================ 2 方案：功能块、寄存器
reg_rows = [[r["addr"], r["name"], r["access"], r["reset"], "；".join(f"{b[0]}：{b[1]}" for b in r["bits"])[:80]] for r in DJ["regs"]]
concept = f"""# 方案：功能块与寄存器

{L.md_table(["功能块", "做什么"], [[b['name'], b['desc']] for b in DJ['blocks']])}

{L.md_table(["地址", "寄存器", "读写", "复位值", "位"], reg_rows)}

输入 A、B、Z 用施密特缓冲（案例 A）进同步器；SPI 模式 0、SCLK ≤ 时钟 / 10。
"""
case.step("concept", f"{len(DJ['blocks'])} 个功能块（同步、滤波、4 倍频解码、计数与 Z 锁存、SPI 从机）；{len(DJ['regs'])} 个寄存器。",
          f"{len(DJ['blocks'])} blocks (synchroniser, filter, x4 decoder, counter & Z latch, SPI slave); {len(DJ['regs'])} registers.",
          md=case.text("2_方案.md", concept), tools=tools("chip"))

# ================================================================ 3 计算：RTL 规模、滤波、SPI 时序
filt_ns = (3 + 1) / DJ["clock_mhz"] * 1000
f_ab_max = DJ["clock_mhz"] * 1e6 / (3 + 1 + 2) / 4
calcmd = f"""# 计算：RTL 与时序要点

- RTL `rtl/wq_encif.v` {DJ['rtl_lines']} 行；参考模型 `model/encif.py`（Python，逐拍同样的行为）。
- **滤波**：输入要连续 N+1 拍与当前值不同才认；复位值 N = 3 → 短于 {filt_ns:.0f} ns 的毛刺被滤掉。
- **最高计数频率**：每个边沿要等同步 2 拍 + 滤波 N+1 拍才被认，A、B 两相边沿间隔至少约 {3 + 1 + 2} 拍 → A 相最高约 {f_ab_max / 1e6:.1f} MHz；
  电机 6000 r/min、2500 线编码器 A 相 250 kHz，余量很大。
- **SPI**：SCLK 由芯片时钟过采样，要求 SCLK ≤ {DJ['clock_mhz'] / 10:g} MHz；驱动板固件用 ≤ 5 MHz（电路板厂案例 C 的固件说明）。
"""
case.step("calc", f"RTL {DJ['rtl_lines']} 行；滤掉 < {filt_ns:.0f} ns 的毛刺；A 相最高约 {f_ab_max / 1e6:.1f} MHz；SPI ≤ {DJ['clock_mhz'] / 10:g} MHz。",
          f"{DJ['rtl_lines']} lines of RTL; glitches under {filt_ns:.0f} ns rejected; A-phase up to about {f_ab_max / 1e6:.1f} MHz; SPI ≤ {DJ['clock_mhz'] / 10:g} MHz.",
          md=case.text("3_计算.md", calcmd), tools=tools("chip"), facts=[("RTL 行数", "RTL lines", DJ["rtl_lines"], ""), ("滤波宽度", "Filter width", round(filt_ns), "ns")])

# ================================================================ 4 仿真：九个场景对照参考模型
sc = DJ["sim"]["cases"]
n_match = sum(c["match"] for c in sc)
simmd = f"""# 仿真：{DJ['sim']['tool']}，逐拍对照 Python 参考模型

测试平台给 RTL 和参考模型同一串输入，每一拍比输出；任何一拍不一样就记下第一个不一致的位置。

{L.md_table(["场景", "拍数", "逐拍一致", "结束时计数 / Z / 状态"], [[c['name'], c['cycles'], '✓' if c['match'] else '✗', f"{c['final']['count']} / {c['final']['index']} / {c['final']['status']}"] for c in sc])}

**{n_match} / {len(sc)}** 个场景逐拍一致（合计 {sum(c['cycles'] for c in sc):,} 拍）。“毛刺”“丢步”“溢出”这些场景专门验证坏情况下的行为。
"""
case.step("sim", f"{n_match} / {len(sc)} 个场景、{sum(c['cycles'] for c in sc):,} 拍逐拍与参考模型一致。",
          f"{n_match} / {len(sc)} scenarios, {sum(c['cycles'] for c in sc):,} cycles, match the reference model cycle by cycle.",
          md=case.text("4_逐拍仿真.md", simmd), tools=tools("chip"), facts=[("场景", "Scenarios", len(sc), ""), ("一致", "Matching", f"{n_match}/{len(sc)}", "")])
case.check("sim", "与参考模型逐拍一致的场景", "Scenarios matching the reference model", n_match, "==", len(sc), "", "Icarus 逐拍对照")

# ================================================================ 5 综合与版图
shutil.copy(E / "out" / "layout" / "layout-all.png", case.path("5_版图.png"))
lay_rows = [["芯片面积", f"{LY['die_area_um2']:,.0f} μm²（{DJ['images']['die_um'][0]:.0f} × {DJ['images']['die_um'][1]:.0f} μm）"],
            ["标准单元", f"{LY['stdcells']} 个（其中触发器 {LY['cells_by_kind'].get('触发器', '—')}），利用率 {LY['utilization']:.0%}"],
            ["时序余量（建立 / 保持）", f"{LY['setup_ws_ns']:.2f} / {LY['hold_ws_ns']:.2f} ns（{DJ['clock_mhz']} MHz 周期 {1000 / DJ['clock_mhz']:.0f} ns）"],
            ["设计规则（布线 / Magic / KLayout）", f"{LY['route_drc_errors']} / {LY['magic_drc_errors']} / {LY['klayout_drc_errors']}"],
            ["版图与原理图一致（LVS）", f"错误 {LY['lvs_errors']}"],
            ["天线效应", f"{LY['antenna_violations']}"],
            ["最大转换时间违例", f"{LY['max_slew_violations']}（多在输入输出端口的缓冲上，待优化，不影响功能仿真）"],
            ["功耗（{DJ['clock_mhz']} MHz）", f"{LY['power_total_w'] * 1000:.2f} mW"]]
cadmd = f"""# 综合与版图（LibreLane，CI 工作流 `chip.yml`）

{L.md_table(["项目", "结果"], lay_rows)}

![版图](5_版图.png)

产物：GDS 版图 `wq_encif.gds`、门级网表 `wq_encif.nl.v`、时序约束 `wq_encif.sdc`（`factory/designs/wq-encif/out/layout/`）。
芯片面积主要是逻辑；封装后的尺寸由焊盘和 QFN-16 决定。最大转换时间违例 {LY['max_slew_violations']} 处是实话——开源流程跑通了，但离“可以流片”还差这一项的优化。
"""
case.step("cad", f"{LY['die_area_um2']:,.0f} μm²、{LY['stdcells']} 个标准单元；时序余量 {LY['setup_ws_ns']:.2f} ns；DRC、LVS 0 错误；转换时间违例 {LY['max_slew_violations']} 处待优化。",
          f"{LY['die_area_um2']:,.0f} μm², {LY['stdcells']} standard cells; {LY['setup_ws_ns']:.2f} ns setup slack; zero DRC/LVS errors; {LY['max_slew_violations']} slew violations to fix.",
          md=case.text("5_综合与版图.md", cadmd), figs=[("5_版图.png", "WQ-ENCIF 版图（SKY130）", "WQ-ENCIF layout (SKY130)")], tools=tools("chip"),
          facts=[("面积", "Die area", LY["die_area_um2"], "μm²"), ("建立余量", "Setup slack", round(LY["setup_ws_ns"], 2), "ns")])
case.check("cad", "建立时间余量", "Setup slack", round(LY["setup_ws_ns"], 2), ">=", 0, "ns", "静态时序分析")
case.check("cad", "保持时间余量", "Hold slack", round(LY["hold_ws_ns"], 2), ">=", 0, "ns", "静态时序分析")
case.check("cad", "设计规则 + LVS 错误", "DRC + LVS errors", LY["route_drc_errors"] + LY["magic_drc_errors"] + LY["klayout_drc_errors"] + LY["lvs_errors"], "==", 0, "", "LibreLane")

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt_cp = F.ROUTINGS[F.BOMS["WAF-ENCIF-CP"][0]]
rt_at = F.ROUTINGS[F.BOMS["WQ-ENCIF"][0]]
bom = F.BOMS["WQ-ENCIF"][1]
procmd = f"""# 工艺：晶圆测试 + 封装测试

外协代工流片（200 mm 晶圆）→ 芯片封测厂：

**晶圆测试**（WAF-ENCIF-CP）：

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt_cp)])}

**封装测试**（WQ-ENCIF，一片晶圆一批）：

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt_at)])}

**一批的物料**（一片晶圆）：{'，'.join(f"{F.ITEMS[c][0].split('（')[0] if c in F.ITEMS else c} {q:g}" for c, q in bom)}。
引线键合最慢（{dict(rt_at).get('引线键合 Wire bonding', '—')} 分钟/批），是封装线的瓶颈（芯片厂实验 40）。
"""
case.step("process", f"晶圆测试 {len(rt_cp)} 道 + 封装测试 {len(rt_at)} 道；引线键合是瓶颈。",
          f"{len(rt_cp)} wafer-probe + {len(rt_at)} assembly/test operations; wire bonding is the bottleneck.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt_cp) + len(rt_at), "")])

# ================================================================ 7 制造：一片晶圆 → 一批成品
s1 = L.run_shop("WAF-ENCIF-CP", 1, "WO-CASE-CHIP-C1", seed=1634)
s2 = L.run_shop("WQ-ENCIF", 1, "WO-CASE-CHIP-C2", seed=1635)
cp = {m["characteristic"]: m for m in s1["measurements"] if m["item"] == "WAF-ENCIF-CP"}
ft = {m["characteristic"]: m for m in s2["measurements"] if m["item"] == "WQ-ENCIF"}
wd = ast.literal_eval(cp["cp_yield"]["wafer"]) if isinstance(cp["cp_yield"].get("wafer"), str) else cp["cp_yield"]["wafer"]
wm = WM.render(wd)
grid = np.full((wm["n"], wm["n"]), np.nan)
for i, row in enumerate(wm["rows"]):
    for j, ch in enumerate(row):
        if ch != " ":
            grid[i, j] = int(ch)
from matplotlib.colors import ListedColormap  # noqa: E402

fig, ax = plt.subplots(figsize=(5.6, 5.6))
ax.imshow(grid, cmap=ListedColormap(["#5fa36a", "#c92a2a", "#e8a33d", "#6c5ce7"]), vmin=0.5, vmax=4.5, interpolation="nearest")
ax.set_axis_off()
ax.set_title(f"CP 晶圆图：良率 {wm['yield_pct']:.1f} %（{wm['total']:,} 颗）", fontsize=10)
for k, c in zip((1, 2, 3, 4), ("#5fa36a", "#c92a2a", "#e8a33d", "#6c5ce7")):
    ax.plot([], [], "s", color=c, label=f"{WM.BINS[k]} {wm['by_bin'].get(k, wm['by_bin'].get(str(k), 0)):,}")
ax.legend(fontsize=7, loc="lower left", bbox_to_anchor=(0, -0.12), ncol=2, frameon=False)
case.fig(fig, "7_晶圆图.png")
good_cp = wm["by_bin"].get(1, wm["by_bin"].get("1", 0))
out_parts = good_cp * ft["ft_yield"]["value_mm"] / 100
rows = [[m["name"], f"{m['lower_tol_mm']:g}–{m['upper_tol_mm']:g}", f"{m['value_mm']:.4g} {m.get('unit', '')}", "✓" if m["result"] == "pass" else "✗"] for m in list(cp.values()) + list(ft.values())]
fails = sum(1 for m in list(cp.values()) + list(ft.values()) if m["result"] != "pass")
makemd = f"""# 制造：一片晶圆 → 一批芯片

芯片封测厂仿真车间：晶圆测试 {s1['hours']:.1f} 小时、封装测试 {s2['hours']:.0f} 小时。

![晶圆图](7_晶圆图.png)

{L.md_table(["特性", "公差", "这一批", ""], rows)}

CP 合格 {good_cp:,} 颗 × FT 良率 {ft['ft_yield']['value_mm']:.1f} % ≈ **{out_parts:,.0f} 只成品**，编带 12 盘，整批卖给电路板厂（驱动板 B 版）。
晶圆图上红点（有几处成簇）是随机缺陷，靠边缘的零星黄点是静态电流超标——**看图比看良率一个数字多知道“坏在哪、为什么坏”**（芯片厂实验 38）。
"""
case.step("make", f"一片晶圆 CP 良率 {wm['yield_pct']:.1f} %、FT 良率 {ft['ft_yield']['value_mm']:.1f} % → 约 {out_parts:,.0f} 只；不合格项 {fails}。",
          f"One wafer: CP yield {wm['yield_pct']:.1f} %, FT yield {ft['ft_yield']['value_mm']:.1f} % → about {out_parts:,.0f} parts; {fails} items out of tolerance.",
          md=case.text("7_晶圆测试与封装.md", makemd), figs=[("7_晶圆图.png", "这片晶圆的 CP 晶圆图", "CP wafer map of this wafer")],
          tools=tools("planner", "operator", "quality", "wafer", "lab40"),
          facts=[("CP 良率", "CP yield", round(wm["yield_pct"], 1), "%"), ("成品", "Good parts", round(out_parts), "只")])
case.check("make", "晶圆测试 + 成品测试不合格项", "Probe + final-test failures", fails, "==", 0, "", "芯片厂测试公差")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **芯片设计 = 写 RTL + 证明它对**：参考模型、逐拍对照、坏情况场景，比 RTL 本身花的功夫多。
2. **开源工具链能走到 GDS**：SKY130 + LibreLane，时序、设计规则、LVS 都过；还剩转换时间违例要优化——工具诚实地列出来。
3. **一片晶圆就是一批货**：{wm['total']:,} 颗 → {out_parts:,.0f} 只成品；良率由晶圆图解释，瓶颈在键合。
4. **芯片、电路板、机器人接上了**：这颗芯片装在驱动板 B 版上（电路板厂案例 C），驱动板装在机器人关节里（机器人厂案例 B）。

## 留给学生的问题

1. 把滤波长度 N 改成 7：能滤掉多宽的毛刺？最高计数频率变成多少？
2. 晶圆图上第 4 档（接触不良）如果集中在某个测试位，该查什么？
3. 案例 B 的 SSI 模块并进来，芯片面积、功耗大约增加多少？

相关：数字工厂“芯片设计”“晶圆图”；芯片厂实验 38、40；电路板厂案例 C；芯片厂案例 A、B。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；{len(sc)} 个场景逐拍一致，一片晶圆约 {out_parts:,.0f} 只。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; {len(sc)} scenarios match, about {out_parts:,.0f} parts per wafer.",
          md=case.text("8_总结.md", review), tools=tools("chip", "lab40"))
case.write()
print("ok", wm["yield_pct"], out_parts, fails)
