"""第 161h 轮：缝纫机厂案例 B——平缝机控制器 CTRL-LS。
不重做设计：读第 138 轮 GC 控制仿真（docs/设计/WQ-LS/GC/仿真结果.json、控制器方案与选型.md、图）和第 159 轮板子报告
（factory/designs/ctrl-ls/report/report.json、out/pcb 铜层图），整理成八步；“制造”一步看缝纫机厂出厂测试里和控制器有关的停针定位误差。
第 159 轮还在做（待核对项），重跑本脚本跟着更新。

    python3 tools/cases/sewing_b.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-sewing.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import caselib as L  # noqa: E402

GC = ROOT / "docs" / "设计" / "WQ-LS" / "GC"
DS = ROOT / "factory" / "designs" / "ctrl-ls"
SIM = json.loads((GC / "仿真结果.json").read_text(encoding="utf-8"))
REP = json.loads((DS / "report" / "report.json").read_text(encoding="utf-8"))
SP = REP["spec"]
GCMD = (GC / "控制器方案与选型.md").read_text(encoding="utf-8")

TOOLS = {
    "circuit": ("电路分析", "Circuit analysis", "/circuit"),
    "pcb": ("电路板设计", "PCB design", "/pcb-design"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间执行", "Shop floor", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("sewing", "B", "中等", "平缝机控制器 CTRL-LS", "Lockstitch machine controller CTRL-LS", "CTRL-LS 电控板",
              "单相 110–250 V 进、驱动 550 W 直驱伺服的一块板：功率因数校正、智能功率模块、反激辅助电源、磁场定向控制、电磁铁和针距步进驱动。"
              "整理第 138 轮 GC 的控制仿真（起停、停针）和第 159 轮的板子报告（电气、工艺、热，真器件型号），看平缝机出厂测试里的停针定位误差。",
              "One board from 110–250 V single phase to a 550 W direct-drive servo: PFC, intelligent power module, flyback auxiliary supply, field-oriented control, solenoid and stitch-stepper drives. "
              "Round 138 GC control simulation (start, stop, needle positioning) and round 159 board report (electrical, process, thermal, real parts) organised; needle-stop error from the end-of-line test.",
              "tools/cases/sewing_b.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：平缝机控制器

**用在哪**　问渠直驱平缝机 WQ-LS 的电控箱（缝纫机厂清单里的外购件 BUY-CTRL-LS，出厂测试时烧录本厂固件）。

| 项目 | 要求 | 出处 |
|---|---|---|
| 输入 | 单相交流 {SP['vin_min_vac']}–{SP['vin_max_vac']} V，50/60 Hz，宽电压一个型号 | 第 138 轮 GC（Eddie 11-10 定） |
| 母线 | 有源功率因数校正，{SP['bus_voltage_v']} V | GC 方案 |
| 电机 | 永磁同步直驱 {SP['motor_power_w']} W，峰值力矩 ≥ {SP['torque_peak_nm']:g} N·m，最高 {SP['speed_max_rpm']} r/min | 第 138 轮 G2 |
| 执行器 | 剪线、拨线、抬压脚电磁铁；针距步进电机；照明 | GC |
| 停针 | 停在设定针位，误差 ±1°（出厂测试 lsa_stop） | 缝纫机厂清单 |
| 电控箱内环境 | {SP['ambient_c']} ℃（示例） | 第 159 轮 |

示例设计，未经硬件验证，不能直接投产；器件为示例选型（第 159 轮在 LCSC / DigiKey 核实过型号）。
"""
case.step("brief", f"{SP['vin_min_vac']}–{SP['vin_max_vac']} V 单相进、{SP['bus_voltage_v']} V 母线、{SP['motor_power_w']} W 直驱伺服；停针 ±1°。",
          f"{SP['vin_min_vac']}–{SP['vin_max_vac']} V single phase, {SP['bus_voltage_v']} V bus, {SP['motor_power_w']} W direct-drive servo; needle stop ±1°.",
          md=case.text("1_任务书.md", brief), facts=[("母线", "Bus", SP["bus_voltage_v"], "V"), ("电机", "Motor", SP["motor_power_w"], "W")])

# ================================================================ 2 方案
sec1 = re.search(r"## 一、(.*?)\n(.*?)(?=\n## )", GCMD, re.S)
concept = f"""# 方案（摘自第 138 轮 GC《控制器方案与选型》、第 159 轮细则）

## {sec1.group(1) if sec1 else '一块板'}

{sec1.group(2).strip() if sec1 else ''}

## 控制

磁场定向控制（沿用关节驱动板 B 版固件）+ 缝纫状态机：待机、起缝加固、缝纫、停针、剪线、拨线、抬压脚。
速度环带宽和前馈在第 4 步仿真里定；固件在 Renode 里跑真代码、接 G2 的机构动力学模型（第 159 轮）。
"""
case.step("concept", "功率和主控做在一块板上，主控以母线负端为地、对人能碰到的接口隔离；磁场定向控制 + 缝纫状态机。",
          "Power and control on one board, control referenced to bus minus, isolated towards touchable ports; FOC plus a sewing state machine.",
          md=case.text("2_方案.md", concept))

# ================================================================ 3 计算
sec2 = re.search(r"## 二、(.*?)\n(.*?)(?=\n## )", GCMD, re.S)
ecount = REP["electrical"]["count"]
urows = []
for u in REP["electrical"]["units"]:
    st = [c["status"] for c in u["checks"]]
    urows.append([u["name"], st.count("pass"), st.count("fail"), st.count("pending"), st.count("unknown")])
calc = f"""# 计算

## {sec2.group(1) if sec2 else '额定值'}（第 138 轮 GC）

{sec2.group(2).strip() if sec2 else ''}

## 第 159 轮计算书：每个功能块（问渠电子统一检查引擎，判定全由确定性代码做）

{L.md_table(["功能块", "通过", "不通过", "待核对", "未知"], urows)}

合计：通过 {ecount['pass']}、**不通过 {ecount['fail']}**、待核对 {ecount['pending']}、未知 {ecount['unknown']}。
“待核对”是用到的器件参数还没逐页对过规格书（第 159 轮在做），不算通过也不算不通过；完整计算书见 `factory/designs/ctrl-ls/report/calc.md`。
"""
case.step("calc", f"母线 {SP['bus_voltage_v']} V、输入约 7.9 A；功能块校核：通过 {ecount['pass']}、不通过 {ecount['fail']}、待核对 {ecount['pending']}（第 159 轮在做）。",
          f"{SP['bus_voltage_v']} V bus, about 7.9 A input; block checks: {ecount['pass']} pass, {ecount['fail']} fail, {ecount['pending']} pending (round 159 in progress).",
          md=case.text("3_计算.md", calc), tools=tools("circuit"),
          facts=[("通过", "Pass", ecount["pass"], ""), ("不通过", "Fail", ecount["fail"], ""), ("待核对", "Pending", ecount["pending"], "")])
case.check("calc", "电气校核不通过项", "Electrical checks failed", ecount["fail"], "==", 0, "", "第 159 轮计算书")

# ================================================================ 4 仿真
cy = SIM["cycle"]
bw = SIM["bandwidth"]
brow = [[f"{b['f_s']} Hz", f"{b['ff']:g}", f"{b['ripple']:.2f} %", f"{b['T_rms']:.2f} N·m", f"{b['T_peak']:.2f} N·m"] for b in bw]
th = REP["thermal"]
simmd = f"""# 仿真

## 主轴伺服（第 138 轮 GC，`tools/wqls/gc_sim.py`：G2 的一转力矩 + 电机 + 速度环）

速度环带宽、力矩前馈怎么取（转速起伏和力矩的折中）：

{L.md_table(["速度环带宽", "前馈", "转速起伏", "力矩均方根", "力矩峰值"], brow)}

选 {cy['f_s']:g} Hz、前馈 {cy['ff']:g}。一个工作周期（起步 → 5000 r/min → 停针）：
到 5000 r/min 用 **{cy['t_reach_5000'] * 1000:.0f} ms**；停针误差 **{cy['stop_error_deg']:+.2f}°**（要求 ±1°）；松脚踏到停稳 {cy['t_from_release']:.2f} s；力矩峰值 {cy['T_peak']:.1f} N·m。

## 板子温度（第 159 轮，简化平板模型）

{th['ambient_c']:.0f} ℃ 环境、两面自然对流：板上最热 **{th['t_max_c']:.0f} ℃**（允许 105 ℃）。{th['detail']}。
"""
case.step("sim", f"速度环 {cy['f_s']:g} Hz：{cy['t_reach_5000'] * 1000:.0f} ms 到 5000 r/min，停针误差 {cy['stop_error_deg']:+.2f}°；板上最热 {th['t_max_c']:.0f} ℃。",
          f"{cy['f_s']:g} Hz speed loop: 5000 rpm in {cy['t_reach_5000'] * 1000:.0f} ms, needle stop error {cy['stop_error_deg']:+.2f}°; hottest board spot {th['t_max_c']:.0f} °C.",
          md=case.text("4_仿真.md", simmd),
          figs=[(case.raw("4_工作周期.png", (GC / "1_工作周期.png").read_bytes()), "一个工作周期（GC 仿真）", "One work cycle (GC simulation)"),
                (case.raw("4_速度环带宽.png", (GC / "2_速度环带宽.png").read_bytes()), "速度环带宽的取舍", "Speed-loop bandwidth trade-off")],
          facts=[("停针误差", "Stop error", round(cy["stop_error_deg"], 2), "°"), ("板上最热", "Hottest spot", round(th["t_max_c"]), "℃")])
case.check("sim", "停针误差（仿真）", "Needle-stop error (simulation)", round(abs(cy["stop_error_deg"]), 2), "<=", 1.0, "°", "出厂测试 lsa_stop")
case.check("sim", "板上最高温度", "Hottest board temperature", round(th["t_max_c"], 1), "<=", 105.0, "℃", "第 159 轮热检查")


# ================================================================ 5 电路板
def svg_png(svg, png, w=1400):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": w, "height": int(w * 0.75)}, device_scale_factor=2)
        pg.goto(Path(svg).resolve().as_uri())
        pg.wait_for_timeout(300)
        pg.query_selector("svg").screenshot(path=str(png))
        br.close()


svg_png(DS / "out" / "pcb" / "F_Cu.svg", case.path("5_顶层铜.png"))
case.raw("5_ctrl-ls.step", (DS / "out" / "ctrl-ls.step").read_bytes())
bom_n = sum(1 for _ in (DS / "out" / "bom.csv").open(encoding="utf-8")) - 1
cadmd = f"""# 电路板：CTRL-LS A 版

![顶层铜](5_顶层铜.png)

KiCad 工程由设计描述（`factory/designs/ctrl-ls/design.yaml`）生成：原理图 12 页、物料清单 {bom_n} 行（带立创编号）、坐标文件、Gerber、三维模型。
器件全部用 KiCad 官方库的符号和封装；大电流走线外层 3 oz。三维模型 `5_ctrl-ls.step`。
"""
case.step("cad", f"KiCad 工程由设计描述生成；物料清单 {bom_n} 行（真型号、立创编号）；顶层铜、三维模型。",
          f"KiCad project generated from the design description; {bom_n}-line BOM (real parts, LCSC numbers); top copper and 3D model.",
          md=case.text("5_电路板.md", cadmd), figs=[("5_顶层铜.png", "顶层铜（KiCad 产物）", "Top copper (KiCad output)")],
          files=[("5_ctrl-ls.step", "电路板三维模型（STEP）", "Board 3D model (STEP)")], tools=tools("pcb"))

# ================================================================ 6 工艺
proc = REP["process"]
prow = [[x["key"], x["name"], {"pass": "通过", "fail": "不通过", "unknown": "未知", "pending": "待核对"}.get(x["status"], x["status"]),
         f"{x['value']} / {x['limit']}" if x["value"] is not None else "—"] for x in proc]
p_fail = sum(1 for x in proc if x["status"] == "fail")
procmd = f"""# 工艺：贴片可制造性（第 159 轮板子报告）

工艺能力表：{REP['factory']}。

{L.md_table(["项", "检查", "结论", "量到 / 限值"], prow)}

在缝纫机厂：电控箱作为外购件进厂，**出厂测试时烧录本厂固件**，在出厂测试工位量停针定位误差。
"""
case.step("process", f"贴片可制造性 {len(proc)} 项：不通过 {p_fail}；进厂后在出厂测试工位烧固件、量停针。",
          f"{len(proc)} manufacturability checks, {p_fail} failed; firmware flashed and needle stop measured at end-of-line.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工艺检查", "Process checks", len(proc), "")])
case.check("process", "贴片可制造性不通过项", "Manufacturability checks failed", p_fail, "==", 0, "", "第 159 轮板子报告")

# ================================================================ 7 制造：出厂测试里的停针
sh = L.run_shop("WQ-LS", 40, "WO-CASE-SW-B", seed=1612)
stop = [m for m in sh["measurements"] if m["characteristic"] == "lsa_stop"]
rows_q, cpk_min, fails, st = L.shop_table(stop)
makemd = f"""# 制造：40 台平缝机出厂测试里的停针

缝纫机厂仿真车间总装线做 40 台 WQ-LS（{sh['hours']:.1f} 小时），出厂测试工位烧录固件后量停针定位误差：

{L.md_table(["特性", "公差", "台数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}**，Cpk {cpk_min:.2f}；仿真的停针误差 {cy['stop_error_deg']:+.2f}° 在实测散布中间。电路板本身的贴片、测试在电路板厂（第 159 轮决定 5，缝纫机厂接入工业园后改向电路板厂买）。
"""
case.step("make", f"40 台出厂测试：停针误差 Cpk {cpk_min:.2f}，不合格 {fails}。",
          f"40 machines at end-of-line: needle-stop Cpk {cpk_min:.2f}, {fails} failures.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("Cpk", "Cpk", round(cpk_min, 2), "")])
case.check("make", "停针误差不合格", "Needle-stop failures", fails, "==", 0, "", "出厂测试")
case.check("make", "停针误差 Cpk", "Needle-stop Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **控制器的规格来自机构**：一转 ±5 N·m 的惯性力矩（案例 A）决定了峰值力矩、速度环带宽和相电流。
2. **真器件、可追溯**：每个器件都有型号和立创编号，参数没对过规格书的显示“待核对”，不算通过——{ecount['pending']} 项待核对是第 159 轮正在做的。
3. **板子在电路板厂做、固件在缝纫机厂烧**：同一块板，两座厂各管一段。

## 留给学生的问题

1. 速度环带宽从 40 Hz 提到 80 Hz：转速起伏和力矩均方根各怎么变（第 4 步的表）？
2. 输入最低电压从 90 V 改成 180 V（只卖 220 V 地区），哪些器件可以降一档？

相关：第 138 轮 GC（`docs/设计/WQ-LS/GC/`）、第 159 轮（`factory/designs/ctrl-ls/`）；案例 A、C。截至 {case.meta['generated']}。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；待核对 {ecount['pending']} 项（第 159 轮在做）。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; {ecount['pending']} items pending (round 159 in progress).",
          md=case.text("8_总结.md", review), tools=tools("quality"))
case.write()
