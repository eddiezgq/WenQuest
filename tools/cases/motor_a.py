"""第 161d 轮：电机厂案例 A——伺服电机的定子绕组：槽极配合、绕组系数、绕组排布，到定子测试台测 20 只定子。

    python3 tools/cases/motor_a.py

绕组分析用 tools/cases/motorlib.py（槽电势星形图）；反电势、齿槽转矩波形用电机厂原件 sim/motorwave.py（终检台同一个函数）；
制造用电机厂仿真车间（定子测试台、终检台）。输出到 factory/cases/motor/A/。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-motor.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
import motorlib as ML  # noqa: E402
from sim import motorwave as MW  # noqa: E402

TOOLS = {
    "wave": ("电机终检波形", "Motor test waveforms", "/motor-wave"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "circuit": ("电路分析", "Circuit analysis", "/circuit"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("motor", "A", "简单", "伺服电机定子绕组：槽极配合与绕组排布", "Servo-motor stator winding: slot/pole combination and layout", "WQ-SM200 定子",
              "给 200 W 伺服电机选槽数和极数：比较四种槽极配合的绕组系数、谐波、齿槽转矩阶次和单边磁拉力，排出 10 极 12 槽的集中绕组，再在定子测试台测 20 只定子。",
              "Choosing slots and poles for a 200 W servo motor: four slot/pole combinations compared on winding factor, harmonics, cogging order and unbalanced magnetic pull; the 10-pole 12-slot concentrated winding laid out; 20 stators tested.",
              "tools/cases/motor_a.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：伺服电机定子绕组

**用在哪**　电机厂的 WQ-SM200（200 W，带抱闸），装在机器人厂 WQJ-M 关节模组里，由关节驱动板（48 V 母线）驱动。

| 项目 | 要求 | 出处 |
|---|---|---|
| 额定 | 200 W、3000 r/min、0.637 N·m；最高 6000 r/min | 电机选型助手 `cae/motors.py`（伺服 200 W） |
| 驱动 | 正弦波（磁场定向控制），48 V 母线 | 关节驱动板 DRV-JOINT-B |
| 平稳性 | 反电势正弦（谐波畸变 THD ≤ 5 %），齿槽转矩峰峰值 ≤ 额定的 2.5 % | 电机厂终检公差 |
| 工艺 | 绕线机直接绕在齿上（集中绕组），不用嵌线下线的分布绕组 | 电机厂设备：绕线机 wd-1、wd-2 |

**要定的**：几槽几极、绕组怎么排（每个齿上的线圈属于哪一相、正绕还是反绕）。
"""
case.step("brief", "200 W、3000 r/min、48 V 驱动；反电势 THD ≤ 5 %、齿槽转矩 ≤ 2.5 %；齿上直接绕的集中绕组。",
          "200 W, 3000 rpm, 48 V drive; back-EMF THD ≤ 5 %, cogging ≤ 2.5 %; concentrated windings wound on the teeth.",
          md=case.text("1_任务书.md", brief), tools=tools("engineer"),
          facts=[("额定转矩", "Rated torque", 0.637, "N·m"), ("额定转速", "Rated speed", 3000, "r/min"), ("母线", "DC bus", 48, "V")])

# ================================================================ 2 方案：四种槽极配合
combos = [(9, 4), (12, 4), (12, 5), (12, 7)]
rows = []
for Q, p in combos:
    k1 = ML.winding_factor(Q, p, 1)[0]
    k5 = ML.winding_factor(Q, p, 5)[0]
    k7 = ML.winding_factor(Q, p, 7)[0]
    g = math.gcd(Q, 2 * p)
    rows.append([f"{Q} 槽 {2 * p} 极", f"{k1:.3f}", f"{k5:.3f} / {k7:.3f}", ML.cogging_order(Q, p), g,
                 "有（不对称）" if g % 2 else "无", "✓ 选定" if (Q, p) == (12, 5) else ""])
concept = f"""# 方案：几槽几极

集中绕组（每个齿绕一个线圈，线圈跨一个齿）常见的四种配合。绕组系数由槽电势星形图算（第 3 步）：

{L.md_table(["配合", "基波绕组系数 k_w1", "5、7 次绕组系数", "齿槽转矩每圈周期数 LCM(Q, 2p)", "GCD(Q, 2p)", "单边磁拉力", ""], rows)}

- **12 槽 8 极**：基波只有 0.866，5、7 次谐波也是 0.866——反电势不正弦，转矩脉动大；齿槽转矩每圈 24 个周期，幅值大。
- **9 槽 8 极**：基波 0.945 最高，齿槽转矩每圈 72 个周期很小；但 GCD = 1，三相线圈不对称地分布在圆周上，**转子受单边磁拉力**，轴承和噪声吃亏。
- **12 槽 10 极**：基波 0.933，5、7 次只有 0.067（反电势很正弦），齿槽转矩每圈 60 个周期，GCD = 2 对称，没有单边磁拉力。
- 12 槽 14 极和 10 极一样好，但极数多，6000 r/min 时电频率 700 Hz，铁耗和驱动开关频率都吃紧。

**选定 12 槽 10 极**（电机厂现行的就是它，`sim/motorwave.py` 的示例电机）。
"""
case.step("concept", "四种槽极配合比较：12/8 谐波大，9/8 有单边磁拉力，12/14 电频率高；选 12 槽 10 极（k_w1 = 0.933，5、7 次 0.067）。",
          "Four combinations compared: 12/8 has large harmonics, 9/8 unbalanced pull, 12/14 high electrical frequency; 12-slot 10-pole chosen (k_w1 = 0.933, 5th/7th 0.067).",
          md=case.text("2_方案.md", concept), tools=tools("engineer"),
          facts=[("基波绕组系数", "Fundamental winding factor", ML.winding_factor(12, 5)[0], ""), ("齿槽转矩周期", "Cogging periods / rev", 60, "")])
case.check("concept", "选定配合的基波绕组系数", "Fundamental winding factor of the chosen combination", ML.winding_factor(12, 5)[0], ">=", 0.9, "", "常用要求")

# ================================================================ 3 计算：星形图、绕组排布、谐波
Q, p = 12, 5
star = ML.slot_star(Q, p)
coils = ML.tooth_winding(Q, p)
lay = " ".join(("" if s > 0 else "−") + ph for _, ph, s in coils)
nus = list(range(1, 20, 2))
kws = [ML.winding_factor(Q, p, n)[0] for n in nus]
fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.0), gridspec_kw={"width_ratios": [1, 1.3]})
ax = axs[0]
ax.set_aspect("equal")
col = {"A": "#c0392b", "B": "#2f9e44", "C": "#2c6fbb"}
alpha = p * 360 / Q
for k, ph, s in coils:
    a = math.radians(k * alpha)
    ax.annotate("", (math.cos(a), math.sin(a)), (0, 0), arrowprops=dict(arrowstyle="->", color=col[ph], lw=1.6))
    ax.text(1.14 * math.cos(a), 1.14 * math.sin(a), f"{k + 1}{'' if s > 0 else '′'}", ha="center", va="center", fontsize=9, color=col[ph])
ax.set_xlim(-1.35, 1.35)
ax.set_ylim(-1.35, 1.35)
ax.set_axis_off()
ax.set_title("线圈电势星形图（颜色 = 相，′ = 反绕）", fontsize=9.5)
axs[1].bar([str(n) for n in nus], kws, color=L.ACCENT)
axs[1].set_xlabel("谐波次数 ν")
axs[1].set_ylabel("绕组系数 k_wν")
axs[1].set_title("12 槽 10 极的各次绕组系数", fontsize=9.5)
case.fig(fig, "3_星形图与绕组系数.png")
k1, kp, kd, n_ph = ML.winding_factor(Q, p, 1)
calcmd = f"""# 计算：槽电势星形图与绕组排布

**槽距电角** α = p·360°/Q = {p}·360°/{Q} = {alpha:g}°。第 k 个线圈的电势相位 = k·α；把 {Q} 个线圈归到最近的六个相轴（+A、−C、+B、−A、+C、−B），三相各 {n_ph} 个。

**绕组排布**（齿 1–12，“−”表示反绕）：

`{lay}`

**基波绕组系数** k_w1 = k_p · k_d：
- 节距系数 k_p = sin(α/2) = sin({alpha / 2:g}°) = {kp:.3f}（线圈跨一个齿）；
- 分布系数 k_d = |每相线圈相量之和| / 线圈数 = {kd:.3f}；
- k_w1 = **{k1:.3f}**。

各次谐波：{", ".join(f"ν = {n}：{k:.3f}" for n, k in zip(nus, kws))}。5、7 次被压到 0.067，11、13 次又回到 0.933——它们是“齿谐波”（ν = Q/p ± 1），由磁钢形状和斜极去削弱。
"""
case.step("calc", f"槽距电角 {alpha:g}°；排布 {lay}；k_w1 = {k1:.3f}（k_p {kp:.3f} × k_d {kd:.3f}）。",
          f"Slot pitch {alpha:g}° electrical; layout {lay}; k_w1 = {k1:.3f} (k_p {kp:.3f} × k_d {kd:.3f}).",
          md=case.text("3_计算.md", calcmd), figs=[("3_星形图与绕组系数.png", "线圈电势星形图与各次绕组系数", "Coil EMF star and harmonic winding factors")],
          tools=tools("engineer"), facts=[("k_w1", "k_w1", k1, ""), ("5 次", "5th", kws[2], "")])
case.check("calc", "三相线圈数相等", "Equal number of coils per phase", 1 if len({sum(1 for c in coils if c[1] == x) for x in 'ABC'}) == 1 else 0, "==", 1, "", "星形图")

# ================================================================ 4 仿真：终检台的反电势与齿槽转矩（同一个函数），好磁钢 vs 贴歪的磁钢
import random  # noqa: E402

ren_g = MW.render(MW.params(random.Random(1), "CASE-A-GOOD"))
ren_b = MW.render(MW.params(random.Random(1), "CASE-A-BAD", mag_extra=1.0))
fig, axs = plt.subplots(2, 1, figsize=(8.6, 5.0), sharex=False)
x = ren_g["deg"]
for k, c in enumerate(("#c0392b", "#2f9e44", "#2c6fbb")):
    axs[0].plot(x, ren_g["emf"][k], color=c, lw=1)
axs[0].set_ylabel("相反电势（相对）")
axs[0].set_title("反电势：转一圈 5 个电周期（10 极）", fontsize=9.5)
xc = ren_g["deg"]
axs[1].plot(xc, ren_g["cog_curve"], color=L.ACCENT, lw=1, label="磁钢贴得准")
axs[1].plot(xc, ren_b["cog_curve"], color=L.BAD, lw=1, alpha=0.8, label="磁钢贴歪、强弱不一")
axs[1].set_xlabel("转子机械角 / °")
axs[1].set_ylabel("齿槽转矩 / % 额定")
axs[1].legend(fontsize=8.5, frameon=False)
case.fig(fig, "4_反电势与齿槽转矩.png")
mg = {"ke_pct": ren_g["ke"], "unbalance_pct": ren_g["unbal"], "thd_pct": ren_g["thd"], "cog_pp_pct": ren_g["cog"]}
mb = {"ke_pct": ren_b["ke"], "unbalance_pct": ren_b["unbal"], "thd_pct": ren_b["thd"], "cog_pp_pct": ren_b["cog"]}
simmd = f"""# 仿真：终检台上看到的反电势和齿槽转矩

用电机厂终检台同一个函数（`sim/motorwave.py`）生成一台好电机和一台磁钢贴歪的电机：

{L.md_table(["量", "磁钢贴得准", "磁钢贴歪、强弱不一", "终检公差"], [
    ["反电势常数（相对额定）", f"{mg['ke_pct']:.1f} %", f"{mb['ke_pct']:.1f} %", "95–105 %"],
    ["三相不平衡", f"{mg['unbalance_pct']:.2f} %", f"{mb['unbalance_pct']:.2f} %", "≤ 2 %"],
    ["线反电势 THD", f"{mg['thd_pct']:.2f} %", f"{mb['thd_pct']:.2f} %", "≤ 5 %"],
    ["齿槽转矩峰峰值", f"{mg['cog_pp_pct']:.2f} %", f"{mb['cog_pp_pct']:.2f} %", "≤ 2.5 %"],
])}

12 槽 10 极的好处在磁钢贴得准时才兑现：10 块磁钢一样、位置准，齿槽转矩只剩每圈 60 次、峰峰值很小；
贴歪了，每圈 12、24 次的低次成分抵消不掉，峰峰值变大——这就是实验 35 追的“磁钢定位工装”问题。
"""
case.step("sim", f"同一个终检函数：好电机齿槽转矩 {mg['cog_pp_pct']:.2f} %、THD {mg['thd_pct']:.2f} %；磁钢贴歪后齿槽转矩 {mb['cog_pp_pct']:.2f} %。",
          f"Same test-bench function: a good motor shows {mg['cog_pp_pct']:.2f} % cogging and {mg['thd_pct']:.2f} % THD; with misplaced magnets cogging rises to {mb['cog_pp_pct']:.2f} %.",
          md=case.text("4_波形.md", simmd), figs=[("4_反电势与齿槽转矩.png", "三相反电势；齿槽转矩（好 / 磁钢贴歪）", "Three-phase back-EMF; cogging torque (good / misplaced magnets)")],
          tools=tools("wave"), facts=[("THD", "THD", mg["thd_pct"], "%"), ("齿槽转矩", "Cogging", mg["cog_pp_pct"], "%")])
case.check("sim", "好电机反电势 THD", "Back-EMF THD of a good motor", mg["thd_pct"], "<=", 5.0, "%", "终检公差")
case.check("sim", "好电机齿槽转矩峰峰值", "Cogging of a good motor", mg["cog_pp_pct"], "<=", 2.5, "%", "终检公差")

# ================================================================ 5 绕组图
fig, ax = plt.subplots(figsize=(9.0, 2.6))
for k, ph, s in coils:
    ax.add_patch(plt.Rectangle((k - 0.3, 0), 0.6, 1, color="#9aa5b1"))
    ax.annotate("", (k + 0.25 * s, 1.3), (k - 0.25 * s, 1.3), arrowprops=dict(arrowstyle="->", color=col[ph], lw=2))
    ax.text(k, 1.6, ("" if s > 0 else "−") + ph, ha="center", color=col[ph], fontsize=11, weight="bold")
    ax.text(k, -0.35, f"齿 {k + 1}", ha="center", fontsize=8.5)
ax.set_xlim(-0.8, Q - 0.2)
ax.set_ylim(-0.6, 2.0)
ax.set_axis_off()
ax.set_title("展开绕组图：每个齿一个线圈，箭头是绕向", fontsize=10)
case.fig(fig, "5_展开绕组图.png")
conn = {ph: [f"{'' if s > 0 else '−'}{k + 1}" for k, x, s in coils if x == ph] for ph in "ABC"}
cadmd = f"""# 绕组图与接线

{L.md_table(["相", "线圈（齿号，−为反绕）", "接法"], [[ph, "、".join(v), "四个线圈串联"] for ph, v in conn.items()])}

三相星形连接，中性点在定子里焊好、套管绝缘，引出 U、V、W 三根线。反绕的线圈在绕线机上只是起绕方向反过来，不用换机器。
"""
case.step("cad", "展开绕组图、每相四个线圈串联、星形连接。", "Developed winding diagram, four coils in series per phase, star connection.",
          md=case.text("5_绕组图.md", cadmd), figs=[("5_展开绕组图.png", "12 槽 10 极展开绕组图", "12-slot 10-pole developed winding diagram")], tools=tools("engineer"),
          facts=[("每相线圈", "Coils per phase", 4, "")])

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["WQ-SM200"][0]]
stator_ops = rt[:6]
procmd = f"""# 工艺：定子

定子在电机厂的前六道工序（工艺路线 {F.BOMS['WQ-SM200'][0]} 的前半段）：

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(stator_ops)])}

- 绕线：两台绕线机 wd-1、wd-2，按第 5 步的绕组图逐齿绕，绕向由程序控制；张力不稳会造成匝间短路（实验 35 的“绕线机 wd-2 张力”问题）。
- 浸漆烘干：一炉 24 只，180 分钟——摊到每只只有 7.5 分钟，不是瓶颈（实验 42）。
- 定子测试：三相电阻不平衡、匝间冲击波形面积差、耐压漏电流（1500 V 1 s）。
"""
case.step("process", f"定子 6 道工序；绕线按绕组图、浸漆一炉 24 只；测试三项。", "Six stator operations; winding per the diagram, varnish 24 per batch; three tests.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(stator_ops), "")])

# ================================================================ 7 制造
sh = L.run_shop("WQ-SM200", 20, "WO-CASE-MT-A", seed=161)
stator_meas = [m for m in sh["measurements"] if "定子测试台" in m["name"]]
rows_q, cpk_min, fails, st = L.shop_table(stator_meas)
makemd = f"""# 定子测试台测 20 只

电机厂仿真车间下 20 台 WQ-SM200 的工单，定子测试台的三项：

{L.md_table(["特性", "公差", "件数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}** 个，最低 Cpk {cpk_min:.2f}。整台电机的终检（反电势、齿槽转矩）见案例 B、C。
"""
case.step("make", f"20 只定子三项测试，不合格 {fails} 个，最低 Cpk {cpk_min:.2f}。", f"20 stators, three tests, {fails} out of tolerance, lowest Cpk {cpk_min:.2f}.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", cpk_min, "")])
case.check("make", "定子测试不合格数", "Stator test failures", fails, "==", 0, "", "定子测试台")
case.check("make", "定子测试最低 Cpk", "Lowest stator-test Cpk", cpk_min, ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **12 槽 10 极**：基波绕组系数 0.933，5、7 次谐波 0.067，没有单边磁拉力，齿槽转矩每圈 60 个周期。
2. 绕组排布 `{lay}`，每相四个线圈串联、星形连接。
3. 好处要靠工艺兑现：磁钢贴歪，齿槽转矩会大好几倍。

## 留给学生的问题

1. 用第 3 步的方法算 9 槽 8 极的排布和绕组系数，验证 0.945。
2. 12 槽 10 极的 11、13 次绕组系数为什么和基波一样？怎样削弱它们（斜极、磁钢形状）？
3. 每个线圈多少匝？取决于什么（案例 B 用有限元算）？

相关：电机厂帮助“产品与物料”“定子线”；实验 35（电机质量异常追因）、实验 42（一台伺服电机从订单到交付）；案例 B（电磁有限元）、案例 C（整机）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；12 槽 10 极，k_w1 0.933。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; 12-slot 10-pole, k_w1 0.933.", md=case.text("8_总结.md", review), tools=tools("wave"))
case.write()
