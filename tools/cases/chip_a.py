"""第 161g 轮：芯片封测厂案例 A——编码器接口芯片的输入施密特触发器：手算门限 → 晶体管级仿真（SKY130）→ 工艺角 → 晶圆测试量门限。

    python3 tools/cases/chip_a.py

晶体管级仿真是第 93 轮已有的结果（factory/designs/wq-encif/flow/schmitt.py，CI 里用 SKY130 器件模型跑，结果 out/transistor/schmitt.json）；
本案例补手算、把结果按八步整理，补“制造”：芯片封测厂仿真车间晶圆测试量 VT+、VT−，成品测试量回差。输出到 factory/cases/chip/A/。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-chip.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402

TOOLS = {
    "chip": ("芯片设计：晶体管级", "Chip design: transistor level", "/chip-design"),
    "wafer": ("晶圆图", "Wafer map", "/wafer-map"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731
SJ = json.loads((ROOT / "factory" / "designs" / "wq-encif" / "out" / "transistor" / "schmitt.json").read_text(encoding="utf-8"))
D, NOM = SJ["design"], SJ["nominal"]
VDD = SJ["vdd"]

case = L.Case("chip", "A", "简单", "输入施密特触发器：门限与回差", "Input Schmitt trigger: thresholds and hysteresis", "WQ-ENCIF 输入级",
              "编码器信号线长、边沿慢、有干扰：芯片输入用施密特触发器。手算上下门限，晶体管级仿真（SKY130）扫反馈管宽度、选回差 ≥ 0.6 V 的最小一档，"
              "七个工艺角与温度复核，慢边沿加 ±0.3 V 干扰数翻转次数；芯片封测厂晶圆测试量门限、成品测试量回差。",
              "Encoder lines are long, slow and noisy, so the chip inputs use Schmitt triggers: thresholds by hand, transistor-level simulation (SKY130) sweeping the feedback width "
              "for the smallest one with ≥ 0.6 V hysteresis, seven process/temperature corners, toggles counted on a slow edge with ±0.3 V noise; thresholds measured at wafer probe, hysteresis at final test.",
              "tools/cases/chip_a.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：输入施密特触发器

**用在哪**　编码器接口芯片 WQ-ENCIF（芯片厂案例 C）的 A、B、Z 三个输入脚，接电机编码器的线（经驱动板上的线接收器）。线长、边沿慢，还叠着逆变器开关的干扰。

| 项目 | 要求 | 出处 |
|---|---|---|
| 电源 | {VDD} V（SKY130 1.8 V 器件） | 芯片工艺 |
| 回差 | ≥ {SJ['target_hyst']} V（大于 ±0.3 V 干扰的峰峰值） | 本案例设定 |
| 门限 | 晶圆测试 VT+ 1.10–1.40 V、VT− 0.45–0.75 V | 芯片厂晶圆测试公差 |
| 面积 | 尽量小：反馈管宽度取满足回差的最小一档 | — |
"""
case.step("brief", f"{VDD} V；回差 ≥ {SJ['target_hyst']} V；晶圆测试 VT+ 1.10–1.40、VT− 0.45–0.75 V；面积尽量小。",
          f"{VDD} V; hysteresis ≥ {SJ['target_hyst']} V; wafer-probe limits VT+ 1.10–1.40 V, VT− 0.45–0.75 V; minimum area.",
          md=case.text("1_任务书.md", brief), tools=tools("chip"), facts=[("电源", "Supply", VDD, "V"), ("回差要求", "Hysteresis target", SJ["target_hyst"], "V")])

# ================================================================ 2 方案
concept = f"""# 方案

| 输入级 | 慢边沿 + 干扰时 | 代价 |
|---|---|---|
| 普通反相器 | 输入在翻转点附近晃，输出来回翻（一个边沿变成几十个） | 最小 |
| 数字滤波（连续 N 拍才认） | 能滤掉短毛刺；慢边沿上的连续抖动滤不干净，还增加延迟 | 触发器 + 计数器 |
| **施密特触发器** | 上升过 VT+ 才翻高、下降过 VT− 才翻低，中间的晃动不理 | 多两只反馈管 |

**选施密特触发器 + 后面再加数字滤波**（芯片里两样都有：模拟的回差挡慢边沿抖动，数字滤波挡窄毛刺）。结构：6 管 CMOS 施密特（主通路 N 管两只串联、P 管两只串联，
中间节点各接一只反馈管到输出）+ 输出反相器；主通路与《数字集成电路设计》第 1 章反相器同尺寸（Wn {D['wn']}、Wp {D['wp']} μm，L {SJ['l_um']} μm）。
"""
case.step("concept", "普通反相器、数字滤波、施密特比较；选 6 管施密特 + 数字滤波，主通路与教材反相器同尺寸。",
          "Plain inverter, digital filter and Schmitt trigger compared; a 6-transistor Schmitt plus digital filter, main path sized like the textbook inverter.",
          md=case.text("2_方案.md", concept), tools=tools("chip"))

# ================================================================ 3 计算：平方律手算门限
VT = 0.45            # 手算取的阈值电压量级（SKY130 1.8 V 管约 0.4–0.5 V，示例）


def vt_plus(k):
    r = math.sqrt(1 / k)              # β_主 / β_反馈 = 1/k（同 L）：(VDD − V)/(V − Vt) = √(β1/β3)
    return (VDD + r * VT) / (1 + r)


def vt_minus(k):
    r = math.sqrt(1 / k)              # P 侧对称：V / (VDD − V − |Vtp|) = √(β5/β6)
    return r * (VDD - VT) / (1 + r)


rows = [[s_["k"], f"{s_['wfn']:.2f} / {s_['wfp']:.2f}", f"{vt_plus(s_['k']):.3f}", f"{vt_minus(s_['k']):.3f}", f"{vt_plus(s_['k']) - vt_minus(s_['k']):.3f}"] for s_ in SJ["sweep"]]
calcmd = f"""# 计算：平方律手算门限

输出为低、输入上升时，下面两只串联 N 管里靠下的 M1 导通，反馈 N 管 M3 把中间节点往 V_DD 拉；当 M1 的电流压过 M3，中间节点被拉下来、输出翻转。
两管都在饱和区、用平方律：

  β₁ (V − V_t)² = β₃ (V_DD − V − V_t)²　→　**VT+ = (V_DD + √(β₁/β₃)·V_t) / (1 + √(β₁/β₃))**

P 侧对称：**VT− = √(β₅/β₆)·(V_DD − |V_tp|) / (1 + √(β₅/β₆))**。反馈管宽度 = k × 主通路宽度（同 L），β 比 = 1/k。取 V_t ≈ {VT} V：

{L.md_table(["k", "反馈管 Wn / Wp μm", "VT+ 手算 V", "VT− 手算 V", "回差 手算 V"], rows)}

k 越大反馈越强、回差越大，但管子越大。手算的规律对、数是近似（平方律忽略了体效应、短沟道效应，V_t 也是估的）——下一步用 SKY130 的器件模型算准。
"""
case.step("calc", f"平方律手算：k = 1.5 时 VT+ {vt_plus(1.5):.2f}、VT− {vt_minus(1.5):.2f}、回差 {vt_plus(1.5) - vt_minus(1.5):.2f} V；k 越大回差越大。",
          f"Square-law estimate: at k = 1.5, VT+ {vt_plus(1.5):.2f}, VT− {vt_minus(1.5):.2f}, hysteresis {vt_plus(1.5) - vt_minus(1.5):.2f} V; larger k, larger hysteresis.",
          md=case.text("3_计算书.md", calcmd), tools=tools("chip"),
          facts=[("手算 VT+（k=1.5）", "Hand VT+ (k=1.5)", round(vt_plus(1.5), 3), "V"), ("手算 VT−（k=1.5）", "Hand VT− (k=1.5)", round(vt_minus(1.5), 3), "V")])

# ================================================================ 4 仿真：SKY130 晶体管级
corners = SJ["corners"]
fig, axs = plt.subplots(1, 3, figsize=(10.6, 3.1))
cu, cd, ci = np.array(NOM["curve_up"]), np.array(NOM["curve_dn"]), np.array(NOM["curve_inv"])
axs[0].plot(ci[:, 0], ci[:, 1], color="#c0c8d0", label="普通反相器")
axs[0].plot(cu[:, 0], cu[:, 1], color=L.ACCENT, label="施密特（上升）")
axs[0].plot(cd[:, 0], cd[:, 1], color=L.BAD, ls="--", label="施密特（下降）")
axs[0].set_xlabel("输入 / V")
axs[0].set_ylabel("输出 / V")
axs[0].set_title(f"回差 {NOM['hyst']:.3f} V（k = {NOM['k']}）", fontsize=9.5)
axs[0].legend(fontsize=7)
ks = [s_["k"] for s_ in SJ["sweep"]]
axs[1].plot(ks, [s_["hyst"] for s_ in SJ["sweep"]], "o-", color=L.ACCENT, label="SKY130 仿真")
axs[1].plot(ks, [vt_plus(k) - vt_minus(k) for k in ks], "s--", color="#8aa4bd", label="平方律手算")
axs[1].axhline(SJ["target_hyst"], color=L.BAD, ls=":", lw=0.9)
axs[1].set_xlabel("反馈管宽度倍数 k")
axs[1].set_ylabel("回差 / V")
axs[1].set_title("扫反馈管宽度", fontsize=9.5)
axs[1].legend(fontsize=7.5)
w = np.array(SJ["noise"]["wave"])
axs[2].plot(w[:, 0], w[:, 1], color="#c0c8d0", lw=0.6, label="输入（慢边沿 + 干扰）")
axs[2].plot(w[:, 0], w[:, 3], color=L.BAD, lw=0.5, alpha=0.6, label="普通反相器输出")
axs[2].plot(w[:, 0], w[:, 2], color=L.ACCENT, lw=1.2, label="施密特输出")
axs[2].set_xlabel("时间 / ns")
axs[2].set_title(f"翻转次数：施密特 {SJ['noise']['schmitt_toggles']}，反相器 {SJ['noise']['inv_toggles']}", fontsize=9.5)
axs[2].legend(fontsize=7)
case.fig(fig, "4_晶体管级仿真.png")
crow = [[f"{c['corner']}", f"{c['temp']} ℃", f"{c['vt_plus']:.3f}", f"{c['vt_minus']:.3f}", f"{c['hyst']:.3f}", f"{c['tplh']:.0f} / {c['tphl']:.0f}"] for c in corners]
hmin = min(c["hyst"] for c in corners)
vtp_rng = (min(c["vt_plus"] for c in corners), max(c["vt_plus"] for c in corners))
vtm_rng = (min(c["vt_minus"] for c in corners), max(c["vt_minus"] for c in corners))
simmd = f"""# 仿真：晶体管级（ngspice + SKY130 器件模型，第 93 轮）

CI 的芯片工作流里跑（`factory/designs/wq-encif/flow/schmitt.py`，镜像 `{SJ['image'].split('@')[0]}`），结果在 `out/transistor/schmitt.json`。

## 扫反馈管宽度

{L.md_table(["k", "VT+ V", "VT− V", "回差 V", "手算回差 V"], [[s_['k'], f"{s_['vt_plus']:.3f}", f"{s_['vt_minus']:.3f}", f"{s_['hyst']:.3f}", f"{vt_plus(s_['k']) - vt_minus(s_['k']):.3f}"] for s_ in SJ['sweep']])}

回差 ≥ {SJ['target_hyst']} V 的最小一档是 **k = {D['k']}**（反馈管 Wn {D['wfn']}、Wp {D['wfp']} μm）。手算 VT− 很准，VT+ 偏低约 0.06 V（N 管体效应：M3 的源端不在地上）。

## 工艺角与温度

{L.md_table(["工艺角", "温度", "VT+ V", "VT− V", "回差 V", "延迟 上升 / 下降 ps"], crow)}

七种情况回差最小 **{hmin:.3f} V**（{min(corners, key=lambda c: c['hyst'])['corner']}、{min(corners, key=lambda c: c['hyst'])['temp']} ℃），都 ≥ {SJ['target_hyst']} V；VT+ 在 {vtp_rng[0]:.2f}–{vtp_rng[1]:.2f} V、VT− 在 {vtm_rng[0]:.2f}–{vtm_rng[1]:.2f} V，
都在晶圆测试公差里——**晶圆测试的公差就是按工艺角的范围再放一点定的**。

## 干扰

{SJ['noise']['edge_us']} μs 的慢边沿叠 ±{SJ['noise']['noise_v']} V 干扰：普通反相器输出翻了 {SJ['noise']['inv_toggles']} 次，施密特 {SJ['noise']['schmitt_toggles']} 次（一上一下，正确）。
"""
case.step("sim", f"SKY130：k = {D['k']} 回差 {NOM['hyst']:.3f} V；七个工艺角最小 {hmin:.3f} V；干扰下施密特翻 {SJ['noise']['schmitt_toggles']} 次、反相器 {SJ['noise']['inv_toggles']} 次。",
          f"SKY130: k = {D['k']} gives {NOM['hyst']:.3f} V; minimum over seven corners {hmin:.3f} V; with noise the Schmitt toggles {SJ['noise']['schmitt_toggles']} times, the inverter {SJ['noise']['inv_toggles']}.",
          md=case.text("4_晶体管级仿真.md", simmd), figs=[("4_晶体管级仿真.png", "传输特性、扫反馈管宽度、干扰下的翻转", "Transfer curves, feedback-width sweep, toggles under noise")],
          tools=tools("chip"), facts=[("回差（典型）", "Hysteresis (typical)", NOM["hyst"], "V"), ("工艺角最小回差", "Min. hysteresis over corners", hmin, "V")])
case.check("sim", "七个工艺角的最小回差", "Minimum hysteresis over seven corners", round(hmin, 3), ">=", SJ["target_hyst"], "V", "任务书")
case.check("sim", "工艺角 VT+ 最大值", "Highest VT+ over corners", round(vtp_rng[1], 3), "<=", 1.40, "V", "晶圆测试公差")
case.check("sim", "工艺角 VT− 最小值", "Lowest VT− over corners", round(vtm_rng[0], 3), ">=", 0.45, "V", "晶圆测试公差")
case.check("sim", "干扰下施密特翻转次数", "Schmitt toggles under noise", SJ["noise"]["schmitt_toggles"], "==", 2, "", "一上一下")

# ================================================================ 5 版图：芯片版图里的输入级
cadmd = f"""# 版图

施密特触发器在 WQ-ENCIF 里不是单独画的：芯片用 LibreLane（开源数字流程）自动布局布线，输入级用 SKY130 标准单元库里的施密特缓冲单元；
本案例的 6 管电路是**把那个单元拆开讲**，尺寸按上面的仿真定，和标准单元同一思路。

![芯片版图（器件层）](5_版图器件层.png)

整颗芯片的版图、时序、设计规则检查见芯片厂案例 C。
"""
import shutil  # noqa: E402

shutil.copy(ROOT / "factory" / "designs" / "wq-encif" / "out" / "layout" / "layout-devices.png", case.path("5_版图器件层.png"))
case.step("cad", "芯片自动布局布线用标准单元库的施密特缓冲单元；本案例把它拆开讲；整颗芯片版图见案例 C。",
          "The automated layout uses the standard-cell Schmitt buffer; this case opens that cell up; the full chip layout is in case C.",
          md=case.text("5_版图.md", cadmd), figs=[("5_版图器件层.png", "WQ-ENCIF 版图（器件层）", "WQ-ENCIF layout (device layers)")], tools=tools("chip"))

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["WAF-ENCIF-CP"][0]]
procmd = f"""# 工艺：晶圆测试怎么量门限

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

晶圆测试（CP）时探针卡扎在每颗芯片的焊盘上：输入脚加慢三角波（上升、下降各一次），找输出翻转时的输入电压——就是 VT+、VT−。
每颗都测，超出 VT+ 1.10–1.40 V、VT− 0.45–0.75 V 的打成坏芯片（晶圆图上标出来）；每片记中位数。
"""
case.step("process", f"晶圆测试 {len(rt)} 道工序；每颗芯片扫输入找 VT+、VT−，超差打坏点。",
          f"{len(rt)} wafer-probe operations; every die swept for VT+ and VT−, outliers inked.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer", "wafer"))

# ================================================================ 7 制造：一批 25 片晶圆
sh = L.run_shop("WAF-ENCIF-CP", 25, "WO-CASE-CHIP-A", seed=1631)
meas = [m for m in sh["measurements"] if m["characteristic"] in ("cp_vtp", "cp_vtm", "cp_yield")]
rows_q, cpk_min, fails, st = L.shop_table(meas)
makemd = f"""# 制造：一批 25 片晶圆

芯片封测厂仿真车间晶圆测试 25 片（{sh['hours']:.0f} 小时），每片的中位数：

{L.md_table(["特性", "公差", "片数", "均值", "标准差", "Cpk"], rows_q)}

VT+ 均值 {st['cp_vtp']['mean']:.3f} V、VT− {st['cp_vtm']['mean']:.3f} V——和 tt 工艺角的仿真（{NOM['vt_plus']:.3f} / {NOM['vt_minus']:.3f} V）对得上。
不合格 {fails}，最低 Cpk {cpk_min:.2f}。
"""
case.step("make", f"25 片晶圆：VT+ {st['cp_vtp']['mean']:.3f}、VT− {st['cp_vtm']['mean']:.3f} V（仿真 {NOM['vt_plus']:.3f} / {NOM['vt_minus']:.3f}）；不合格 {fails}、最低 Cpk {cpk_min:.2f}。",
          f"25 wafers: VT+ {st['cp_vtp']['mean']:.3f}, VT− {st['cp_vtm']['mean']:.3f} V (simulated {NOM['vt_plus']:.3f} / {NOM['vt_minus']:.3f}); {fails} failures, lowest Cpk {cpk_min:.2f}.",
          md=case.text("7_晶圆测试.md", makemd), tools=tools("planner", "operator", "quality", "wafer"),
          facts=[("VT+ 均值", "Mean VT+", round(st["cp_vtp"]["mean"], 3), "V"), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), "")])
case.check("make", "晶圆测试不合格", "Wafer-probe failures", fails, "==", 0, "", "晶圆测试")
case.check("make", "最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **手算给规律，模型给数**：平方律公式说清楚“反馈越强、回差越大”，VT− 算得很准、VT+ 差 0.06 V（体效应）。
2. **一个设计要在所有工艺角下都成立**：典型值 {NOM['hyst']:.3f} V，最差 {hmin:.3f} V 也要过线。
3. **测试公差来自工艺角**：晶圆测试的 VT+、VT− 公差就是仿真的工艺角范围放宽一点。

## 留给学生的问题

1. 用公式算 k = 4 的回差，和仿真比；为什么 k 再大回差涨得越来越慢？
2. 电源从 1.8 V 降到 1.6 V，门限、回差怎么变？
3. 晶圆图上门限超差的芯片如果集中在晶圆边缘，可能是什么原因？

相关：数字工厂“芯片设计”（晶体管级）、“晶圆图”；芯片厂实验 38、40；案例 B（SSI 接收模块）、C（WQ-ENCIF 整颗芯片）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；k = {D['k']}，回差 {NOM['hyst']:.3f} V。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; k = {D['k']}, hysteresis {NOM['hyst']:.3f} V.", md=case.text("8_总结.md", review), tools=tools("chip", "wafer"))
case.write()
print("ok", hmin, vtp_rng, vtm_rng, cpk_min, fails, st["cp_vtp"]["mean"])
