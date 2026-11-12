"""第 161f 轮：电路板厂案例 C——关节伺服驱动板 DRV-JOINT-B 整板：规格 → 功能块计算 → 电路与固件仿真 → KiCad 原理图与 PCB → 可制造性 → 贴片与后段 → 测试。

    python3 tools/cases/pcb_c.py

这块板已有全套设计（第 88–118 轮：factory/designs/drv-joint、drv-joint-b，设计描述 → KiCad → 自动布线 → 导出与检查；固件在 Renode 里跑）。
本案例把它们按八步串起来、补上“制造”一步（电路板厂仿真车间贴片线 + 后段）。输出到 factory/cases/pcb/C/。
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-pcb.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import yaml  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402

DES = ROOT / "factory" / "designs"
A, B = DES / "drv-joint", DES / "drv-joint-b"
TOOLS = {
    "pcb": ("电路板设计（驱动板 A/B）", "PCB design (drive board A/B)", "/pcb-design"),
    "circuit": ("电路分析", "Circuit analysis", "/circuit"),
    "chip": ("芯片设计（WQ-ENCIF）", "Chip design (WQ-ENCIF)", "/chip-design"),
    "fct": ("功能测试台", "Functional test bench", "/fct"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "lab39": ("实验 39：一块驱动板从订单到交付", "Lab 39: a drive board from order to delivery", "/labo/39"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("pcb", "C", "完整", "关节伺服驱动板 DRV-JOINT-B 整板", "Joint servo drive board DRV-JOINT-B", "DRV-JOINT-B",
              "一块 48 V、400 W 关节伺服驱动板的全过程：规格、九个功能块的计算与判定、电路分析例题核对、固件在虚拟硬件里跑十七个场景、"
              "KiCad 原理图与四层板（自动布线、电气规则、可制造性检查），到电路板厂贴片线 + 后段做一批 50 块、在线测试与功能测试。",
              "The whole path of a 48 V, 400 W joint servo drive board: specification, calculations and verdicts for nine function blocks, circuit-analysis cross-checks, "
              "firmware running seventeen scenarios on virtual hardware, KiCad schematic and four-layer board (autorouted, DRC, DFM), then a batch of 50 boards through SMT and back end with ICT and FCT.",
              "tools/cases/pcb_c.py")

spec = yaml.safe_load((A / "design.yaml").read_text(encoding="utf-8"))
var = yaml.safe_load((B / "variant.yaml").read_text(encoding="utf-8"))
dj = json.loads((B / "out" / "design.json").read_text(encoding="utf-8"))
S = spec["spec"]

# ================================================================ 1 任务书
brief = f"""# 设计任务书：关节伺服驱动板 DRV-JOINT（B 版）

**用在哪**　机器人厂关节模组 WQJ-L/M/S 的电机驱动（第 118 轮起用 B 版），电路板厂做、卖给机器人厂（{165} 美元/块，清单）。

| 项目 | 值 | 出处 |
|---|---|---|
| 母线 | {S['bus_voltage_v']:g} V | 设计描述 `spec` |
| 电机 | {S['motor_power_w']:g} W 伺服，额定 / 峰值相电流 {S['phase_current_a']} / {S['phase_current_peak_a']} A | {S['current_source']} |
| 降额规则 | 电容 {S['derating']['capacitor']}、二极管 {S['derating']['diode']}、MOSFET {S['derating']['mosfet']}、采样余量 {S['derating']['sense_headroom']} | 示例值 |
| 接口 | CAN（多关节主站）、关节输出端绝对值编码器（SSI）、电机端增量编码器（经 WQ-ENCIF 芯片）、抱闸 24 V | B 版改动 |
| 板子 | {dj['board_mm'][0]:g} × {dj['board_mm'][1]:g} mm，{dj['layers']} 层 | 设计描述 `board` |

> {spec['notice']}
"""
case.step("brief", f"{S['bus_voltage_v']:g} V、{S['motor_power_w']:g} W，相电流 {S['phase_current_a']} / {S['phase_current_peak_a']} A；CAN、双编码器、抱闸；{dj['board_mm'][0]:g}×{dj['board_mm'][1]:g} mm 四层。",
          f"{S['bus_voltage_v']:g} V, {S['motor_power_w']:g} W, phase current {S['phase_current_a']} / {S['phase_current_peak_a']} A; CAN, two encoders, brake; {dj['board_mm'][0]:g}×{dj['board_mm'][1]:g} mm, four layers.",
          md=case.text("1_任务书.md", brief), tools=tools("pcb"), facts=[("母线", "DC bus", S["bus_voltage_v"], "V"), ("功率", "Power", S["motor_power_w"], "W")])

# ================================================================ 2 方案：功能块
blk = [[b["name"], b.get("name_en", ""), "；".join(str(x) for x in (b.get("notes") or []))[:90]] for b in spec["blocks"]]
chg = dj["changes"]
concept = f"""# 方案：功能块

设计描述（`factory/designs/drv-joint/design.yaml`）按功能块写：每块一组参数，生成器算出元件值、画原理图、出判定。A 版 {len(spec['blocks'])} 块：

{L.md_table(["功能块", "English", "要点"], blk)}

**B 版**（`variant.yaml`，在 A 版上的改动清单，{len(chg)} 处）：放上问渠芯片厂的编码器接口芯片 WQ-ENCIF（芯片厂案例）、加抱闸驱动和线圈电流检测、
关节输出端绝对值编码器走 SSI。改动由工具自动列出（“电路板设计”页 A/B 切换）：

{L.md_table(["位号", "改了什么"], [[c['ref'], c['what']] for c in chg[:14]])}
{"（共 " + str(len(chg)) + " 处，只列前 14 处）" if len(chg) > 14 else ""}
"""
case.step("concept", f"A 版 {len(spec['blocks'])} 个功能块；B 版在其上 {len(chg)} 处改动（WQ-ENCIF、抱闸、SSI）。",
          f"{len(spec['blocks'])} function blocks in rev A; rev B adds {len(chg)} changes (WQ-ENCIF, brake, SSI).",
          md=case.text("2_方案.md", concept), tools=tools("pcb", "chip"), facts=[("功能块", "Function blocks", len(spec["blocks"]), ""), ("B 版改动", "Rev-B changes", len(chg), "")])

# ================================================================ 3 计算：计算书的判定汇总
calc = (A / "calc" / "calc.md").read_text(encoding="utf-8")
secs = re.split(r"^## ", calc, flags=re.M)
rows, tot = [], {"通过": 0, "不通过": 0, "待核对": 0, "未知": 0}
for s_ in secs[1:]:
    title = s_.splitlines()[0].strip()
    if title in ("规格", "结论") or title.startswith("用到的器件"):
        continue
    cnt = {k: len(re.findall(r"\| \*\*" + k + r"\*\* \|", s_)) for k in tot}
    if not any(cnt.values()):
        continue
    for k in tot:
        tot[k] += cnt[k]
    rows.append([title.split("（")[0], cnt["通过"], cnt["不通过"], cnt["待核对"], cnt["未知"]])
concl = re.search(r"## 结论\s+(.+)", calc).group(1).strip()
calcmd = f"""# 计算：功能块计算器的判定

每个功能块由问渠电子的功能块计算器算元件值、按降额规则判定（第 104 轮；完整计算书 `factory/designs/drv-joint/calc/calc.md`，“电路板设计”页“计算书”）。
判定四种：通过 / 不通过 / **待核对**（用到的器件数据还没人对照规格书核对，不算通过）/ **未知**（缺数据）。

{L.md_table(["功能块", "通过", "不通过", "待核对", "未知"], rows)}

计算书结论：**{concl}**

“待核对”“未知”不是小事：比如采样放大器能承受的共模电压、固定增益，都写着规格书的出处，但还没人翻规格书核对——**这块板“未经硬件验证、不能直接投产”就是这个意思**。
"""
case.step("calc", f"{len(rows)} 个功能块的判定：通过 {tot['通过']}、不通过 {tot['不通过']}、待核对 {tot['待核对']}、未知 {tot['未知']}。",
          f"Verdicts over {len(rows)} blocks: {tot['通过']} pass, {tot['不通过']} fail, {tot['待核对']} to verify, {tot['未知']} unknown.",
          md=case.text("3_计算书汇总.md", calcmd), tools=tools("pcb", "circuit"),
          facts=[("通过", "Pass", tot["通过"], "项"), ("不通过", "Fail", tot["不通过"], "项"), ("待核对", "To verify", tot["待核对"], "项")])
case.check("calc", "计算书“不通过”项", "Calculation 'fail' verdicts", tot["不通过"], "==", 0, "", "功能块计算器")

# ================================================================ 4 仿真：电路分析核对 + 固件在虚拟硬件里跑
sims = re.findall(r"\| 仿真：[^|]+\|[^|]+\|[^|]+\|[^|]+\| \*\*(\S+)\*\* \|", calc)
mot = json.loads((B / "fw" / "out" / "sim_motor.json").read_text(encoding="utf-8"))
sc_rows = [[s_["name"], s_.get("en", ""), sum(c["ok"] for c in s_["checks"]), len(s_["checks"])] for s_ in mot["scenarios"]]
n_ok = sum(r[2] for r in sc_rows)
n_all = sum(r[3] for r in sc_rows)
simmd = f"""# 仿真：电路核对 + 固件在虚拟硬件里跑

## 电路：计算书里的“仿真”判定

每个功能块的关键数（母线纹波、采样放大、栅极驱动、降压电源……）都拿数字工厂“电路分析”的例题跑 ngspice，和公式比：共 {len(sims)} 项，
通过 {sims.count('通过')} 项（案例 A 就是其中“相电流采样”一块展开讲）。

## 固件：Renode 虚拟硬件，{len(sc_rows)} 个场景

B 版示例固件（C，`factory/designs/drv-joint-b/fw/`）在 Renode 里跑：自写的 STM32G431 平台、WQ-ENCIF 芯片寄存器级模型、虚拟逆变桥 + 电机 + 减速器 + 摆臂、
CAN、SSI 编码器、抱闸线圈（第 100–114 轮）。每个场景有自动判定：

{L.md_table(["场景", "English", "通过", "判定项"], sc_rows)}

合计 **{n_ok} / {n_all}** 项判定通过。板子还没做出来，固件已经在“虚拟的这块板”上把上电对零、电流环、速度环、位置环、各种保护、抱闸时序跑过一遍。
"""
case.step("sim", f"电路核对 {sims.count('通过')} / {len(sims)} 项通过；固件在 Renode 里 {len(sc_rows)} 个场景、{n_ok} / {n_all} 项判定通过。",
          f"Circuit cross-checks {sims.count('通过')} / {len(sims)} pass; firmware on Renode: {len(sc_rows)} scenarios, {n_ok} / {n_all} checks pass.",
          md=case.text("4_电路与固件仿真.md", simmd), tools=tools("circuit", "pcb"),
          facts=[("固件场景", "Firmware scenarios", len(sc_rows), ""), ("固件判定通过", "Firmware checks passed", f"{n_ok}/{n_all}", "")])
case.check("sim", "电路仿真核对通过率", "Circuit cross-check pass rate", round(sims.count("通过") / len(sims) * 100), "==", 100, "%", "计算书")
case.check("sim", "固件场景判定通过率", "Firmware scenario pass rate", round(n_ok / n_all * 100), "==", 100, "%", "Renode 仿真")

# ================================================================ 5 原理图、PCB、三维、电气规则与可制造性


def svg_png(svg, png, w=1400):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": w, "height": int(w * 0.75)}, device_scale_factor=3)
        pg.goto(Path(svg).resolve().as_uri())
        pg.wait_for_timeout(300)
        pg.query_selector("svg").screenshot(path=str(png))
        br.close()


svg_png(B / "out" / "pcb" / "F_Silk.svg", case.path("5_顶面装配.png"))
svg_png(B / "out" / "pcb" / "F_Cu.svg", case.path("5_顶层铜.png"))
bom = list(csv.DictReader((B / "out" / "bom.csv").open(encoding="utf-8")))
n_parts = sum(int(r["数量"]) for r in bom)
drc, dfm = dj["drc"], json.loads((B / "out" / "dfm.json").read_text(encoding="utf-8"))
dfm_rows = [[c["name"], f"{c['value']} {c.get('unit', '')}", f"{c['limit']} {c.get('unit', '')}", "✓" if c["pass"] else "✗"] for c in dfm["checks"]]
n_dfm = len(dfm["checks"])
LIBP = [L.lib_part("A-ELE-LQFP48", "STM32G431CBT6"), L.lib_part("A-ELE-SOIC8", "IR2101S"), L.lib_part("A-ELE-SOIC8", "INA240A1D"), L.lib_part("A-ELE-SOIC8", "MCP2562-E-SN"),
        L.lib_part("A-ELE-SOIC8", "MAX3485"), L.lib_part("A-ELE-SOT", "LMR16006YQ"), L.lib_part("A-ELE-SHUNT", "2M"), L.lib_part("A-ELE-MOSTDSON", "BSC040N08NS5")]
cadmd = f"""# 原理图、PCB 与检查（KiCad 产物，`factory/designs/drv-joint-b/out/`）

| 产物 | |
|---|---|
| 原理图 | {len(list((B / 'out' / 'schematic').glob('*.svg')))} 页 SVG（每个功能块一页），KiCad 工程 `kicad-project.zip` |
| PCB | {dj['board_mm'][0]:g} × {dj['board_mm'][1]:g} mm、{dj['layers']} 层，Freerouting 自动布线；Gerber、坐标文件 `pos.csv` |
| 三维 | `drv-joint-b.step`、`drv-joint-b.glb`（板形与安装孔；元件三维在“电路板设计”页看） |
| 物料清单 | {len(bom)} 行、{n_parts} 个元件（`bom.csv`） |
| 电气规则检查（DRC） | 错误 **{drc['errors']}**、未连接 **{drc['unconnected']}**、警告 {drc['warnings']}（丝印重叠一类） |
| 可制造性（DFM，对照电路板厂工艺能力） | {n_dfm} 项检查，{'全部通过' if dfm['pass'] else '有不通过'}（下表） |

{L.md_table(["可制造性检查", "本板", "板厂能力", ""], dfm_rows)}

![顶面装配](5_顶面装配.png)

**零件库里的主要器件**（设计描述的器件取自 KiCad 官方库，零件库电子元件第一批就是从这块板导进来的，第 88 轮）：

{L.lib_md(LIBP)}
"""
case.step("cad", f"原理图、{dj['layers']} 层 PCB、三维；DRC 错误 {drc['errors']}、未连接 {drc['unconnected']}；DFM {n_dfm} 项{'全过' if dfm['pass'] else '有不过'}；{len(bom)} 行物料、{n_parts} 个元件。",
          f"Schematic, {dj['layers']}-layer PCB, 3D; DRC {drc['errors']} errors, {drc['unconnected']} unconnected; DFM {n_dfm} checks {'all pass' if dfm['pass'] else 'with failures'}; {len(bom)} BOM lines, {n_parts} parts.",
          md=case.text("5_原理图与PCB.md", cadmd), figs=[("5_顶面装配.png", "顶面装配图（丝印 + 装配层）", "Top assembly (silkscreen + fab)"), ("5_顶层铜.png", "顶层铜", "Top copper")],
          tools=tools("pcb") + L.lib_tools(LIBP), facts=[("元件", "Parts", n_parts, ""), ("DRC 错误", "DRC errors", drc["errors"], "")])
case.check("cad", "电气规则错误", "DRC errors", drc["errors"], "==", 0, "", "KiCad DRC")
case.check("cad", "未连接", "Unconnected items", drc["unconnected"], "==", 0, "", "KiCad DRC")
case.check("cad", "可制造性检查", "DFM checks", 1 if dfm["pass"] else 0, "==", 1, "", "电路板厂工艺能力")

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt_smt = F.ROUTINGS[F.BOMS["SMT-DRV-B"][0]]
rt_be = F.ROUTINGS[F.BOMS["DRV-JOINT-B"][0]]
procmd = f"""# 工艺：两层物料清单、两条路线

电路板厂的物料清单是两层：贴片板 SMT-DRV-B（光板 + 全部贴片元件 + 锡膏）→ 成品板 DRV-JOINT-B（贴片板 + 插座 + 三防漆 + 防静电袋）。
贴片元件数量和 KiCad 物料清单一致（测试核对，第 88 轮）。

{L.md_table(["线", "工序", "设备", "工时 / min"], [["贴片线", op, F.OPERATIONS[op], m] for op, m in rt_smt] + [["后段", op, F.OPERATIONS[op], m] for op, m in rt_be])}

- 贴片程序直接用 KiCad 导出的坐标文件 `pos.csv`；钢网由 Gerber 的锡膏层出。
- 芯片 WQ-ENCIF 向工业园芯片厂整批买（一批 34 000 只，第 106 轮）。
- 老化 120 分钟是整炉走；功能测试台按板写入相电流标定值（案例 A）。
"""
case.step("process", f"两层物料清单；贴片线 {len(rt_smt)} 道 + 后段 {len(rt_be)} 道；贴片坐标和钢网直接来自 KiCad。",
          f"Two-level BOM; {len(rt_smt)} SMT + {len(rt_be)} back-end operations; placement and stencil straight from KiCad.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt_smt) + len(rt_be), "")])

# ================================================================ 7 制造：贴片板 20 + 成品板 20
s1 = L.run_shop("SMT-DRV-B", 50, "WO-CASE-PCB-C1", seed=1624)
r1, c1, f1, st1 = L.shop_table([m for m in s1["measurements"] if m["item"] == "SMT-DRV-B"])
s2 = L.run_shop("DRV-JOINT-B", 50, "WO-CASE-PCB-C2", seed=1625)
r2, c2, f2, st2 = L.shop_table([m for m in s2["measurements"] if m["item"] == "DRV-JOINT-B"])
makemd = f"""# 制造：一批 50 块

## 贴片线（SMT-DRV-B，AOI 工位记锡膏检测、炉温、贴装偏移、缺陷数）

{L.md_table(["特性", "公差", "块数", "均值", "标准差", "Cpk"], r1)}

## 后段（DRV-JOINT-B，功能测试）

{L.md_table(["特性", "公差", "块数", "均值", "标准差", "Cpk"], r2)}

贴片不合格 {f1}、功能测试不合格 {f2}；最低 Cpk 贴片 {c1:.2f}、功能测试 {c2:.2f}。
"""
case.step("make", f"贴片 50 块（不合格 {f1}、最低 Cpk {c1:.2f}），后段 50 块（不合格 {f2}、最低 Cpk {c2:.2f}）。",
          f"50 boards through SMT ({f1} failures, lowest Cpk {c1:.2f}) and back end ({f2} failures, lowest Cpk {c2:.2f}).",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality", "fct", "lab39"),
          facts=[("贴片最低 Cpk", "SMT lowest Cpk", round(c1, 2), ""), ("功能测试最低 Cpk", "FCT lowest Cpk", round(c2, 2), "")])
case.check("make", "贴片 + 功能测试不合格", "SMT + FCT failures", f1 + f2, "==", 0, "", "AOI、功能测试")
case.check("make", "最低 Cpk", "Lowest Cpk", round(min(c1, c2), 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **设计描述是源头**：原理图、PCB、物料清单、计算书、贴片坐标都从一份设计描述生成，改设计只改它（第 102–104 轮）。
2. **“通过”之外还有“待核对”“未知”**：{tot['待核对']} 项待核对、{tot['未知']} 项未知——工具诚实地告诉你哪些还没验证，投产前要一项项清掉。
3. **板子没做出来，固件已经跑过**：{len(sc_rows)} 个场景在虚拟硬件上过了，硬件到手只需要验证模型和实物的差别。
4. **设计和工厂接上**：KiCad 物料清单 = 工厂物料清单，坐标文件 = 贴片程序，计算出的公差 = 功能测试公差。

## 留给学生的问题

1. 在“电路板设计”页把 A、B 版切换着看：抱闸驱动加在了哪里？为什么放在那里？
2. 计算书里挑一项“待核对”，找到规格书对应的那一页，把它变成“通过”或“不通过”。
3. 做实验 39，跟着一块驱动板从订单走到交付。

相关：数字工厂“电路板设计”“电路分析”“芯片设计”“功能测试台”；电路板厂实验 37、39；案例 A（相电流采样）、B（读头板）；芯片厂案例 C（WQ-ENCIF）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；待核对 {tot['待核对']}、未知 {tot['未知']} 项是投产前要清的账。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; {tot['待核对']} to-verify and {tot['未知']} unknown items remain before production.",
          md=case.text("8_总结.md", review), tools=tools("pcb", "lab39"))
case.write()
print("ok", tot, len(sims), n_ok, n_all, drc, dfm["pass"], c1, c2, f1, f2)
