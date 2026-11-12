"""第 161e 轮：传感器厂案例 C——关节扭矩传感器 WQ-TS 整机：产品定义、误差预算、调零与温度补偿、砝码标定、批量生产（第一批出问题、8D、第二批）。

    python3 tools/cases/sensor_c.py

弹性体取案例 B、信号链取案例 A 的结果；标定曲线用“虚拟仪器”力矩传感器同一个模型（cae/instruments.py 的 torque_out 公式）；
制造用传感器厂仿真车间，第一批注入实验同款车间故障（固化炉温度偏低），质量 8D 下发措施后做第二批。输出到 factory/cases/sensor/C/。
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-sensor.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
import tslib as T  # noqa: E402
from sim import errors as ER  # noqa: E402

TOOLS = {
    "inst": ("虚拟仪器（扭矩传感器标定）", "Virtual instruments (torque calibration)", "/instruments"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "q8d": ("质量 8D", "8D problem solving", "/quality/8d"),
    "cost": ("经营与财务", "Business & finance", "/finance"),
    "cae": ("仿真与分析", "Simulation & analysis", "/cae"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("sensor", "C", "完整", "关节扭矩传感器 WQ-TS：从产品定义到批量交付", "Joint torque sensor WQ-TS: from product definition to volume delivery", "WQ-TS",
              "把弹性体（案例 B）和信号链（案例 A）做成一个能卖的传感器：产品指标、误差预算、调零与温度补偿、砝码标定；"
              "传感器厂做第一批 20 台——蠕变、滞后、温漂成片超差，8D 追到固化炉，改固化曲线后第二批全部合格。",
              "Turning the flexure (case B) and the signal chain (case A) into a sensor that sells: specification, error budget, zero balancing and temperature compensation, "
              "dead-weight calibration; the first batch of 20 fails on creep, hysteresis and thermal zero drift, the 8D leads to the curing oven, and after a new cure profile the second batch passes.",
              "tools/cases/sensor_c.py")


def fact(cid, name):
    d = json.loads((ROOT / "factory" / "cases" / "sensor" / cid / "case.json").read_text(encoding="utf-8"))
    for s_ in d["steps"]:
        for f in s_.get("facts", []):
            if f["name"] == name:
                return float(str(f["value"]).replace(",", ""))
    raise KeyError(name)


MV = fact("B", "定稿输出")
K_S = fact("B", "扭转刚度")
NOISE_PP = fact("A", "噪声峰峰值")
GAIN = fact("A", "增益")
from factory import data as F  # noqa: E402

TOL = {c["code"]: c for m in F.PLANT.get("measurements", []) if m["item"] == "WQ-TS" for c in m["chars"]} if hasattr(F, "PLANT") else {}
if not TOL:
    import yaml
    _pl = yaml.safe_load((ROOT / "factory" / "plants" / "wenquest-sensor.yaml").read_text(encoding="utf-8"))
    TOL = {c["code"]: c for m in _pl["measurements"] if m["item"] == "WQ-TS" for c in m["chars"]}
PRICE = 320

# ================================================================ 1 任务书
ATI = [L.lib_part("D-FTS-ATI-FT", s_) for s_ in ("Delta", "Omega85", "Theta")]
spec = [["量程 / 过载", f"±{T.T_FS:g} N·m / {T.T_OVL:g} N·m", "清单；案例 B"],
        ["额定输出（调理前）", f"{MV:.2f} mV/V", "案例 B 有限元"],
        ["输出", "CAN，1 kHz，24 位", "案例 A"],
        ["非线性 / 滞后", f"≤ {TOL['ts_nonlin']['hi']} / ≤ {TOL['ts_hyst']['hi']} %FS", "终检公差"],
        ["零点输出", f"±{TOL['ts_zero']['hi']} %FS", "终检公差"],
        ["蠕变（满量程 30 min）", f"≤ {TOL['ts_creep']['hi']} %FS", "终检公差"],
        ["零点温漂", f"≤ {TOL['ts_tczero']['hi']} %FS / 10 K（0–50 ℃）", "终检公差"],
        ["扭转刚度", f"{K_S:.3g} N·m/rad", "案例 B"],
        ["外形", "Ø90 × 14，中空 Ø20", "案例 B"],
        ["综合精度", "≤ ±1 %FS（0–50 ℃，各项按公差上限合成）", "本案例设定（关节力矩传感器常见档次）"],
        ["售价", f"{PRICE} 美元", "传感器厂清单"]]
brief = f"""# 设计任务书：关节扭矩传感器 WQ-TS

**卖给谁**　协作机器人厂、伺服电机厂、自动化设备厂（传感器厂清单里的三家示例客户）：装在关节减速器输出端，做力控、碰撞检测、拖动示教。

{L.md_table(["指标", "要求", "出处"], spec)}

**这个案例要做的**：把 A、B 两个案例的结果合成一个产品——误差怎么分配、零点和温漂怎么补、出厂怎么标定、批量做出来是不是都合格。
"""
case.step("brief", f"±{T.T_FS:g} N·m，非线性 ≤ {TOL['ts_nonlin']['hi']}、滞后 ≤ {TOL['ts_hyst']['hi']}、蠕变 ≤ {TOL['ts_creep']['hi']}、温漂 ≤ {TOL['ts_tczero']['hi']} %FS/10K；售价 {PRICE} 美元。",
          f"±{T.T_FS:g} N·m; non-linearity ≤ {TOL['ts_nonlin']['hi']}, hysteresis ≤ {TOL['ts_hyst']['hi']}, creep ≤ {TOL['ts_creep']['hi']}, thermal zero ≤ {TOL['ts_tczero']['hi']} %FS/10 K; price USD {PRICE}.",
          md=case.text("1_任务书.md", brief), tools=tools("engineer"),
          facts=[("量程", "Range", T.T_FS, "N·m"), ("售价", "Price", PRICE, "USD")])

# ================================================================ 2 方案：产品结构、对照
ati_rows = [[p["size"], p["row"]["Tz_range_Nm"], p["row"]["Tz_resolution_Nm"], p["row"]["diameter_mm"], p["row"]["weight_g"], "六维（三个力 + 三个力矩）"] for p in ATI]
res_nm = NOISE_PP / 100 * T.T_FS
concept = f"""# 方案：产品结构

| 部分 | 来自 | 说明 |
|---|---|---|
| 弹性体 BODY-TS | 案例 B | 轮辐 + 剪切腹板，17-4PH，外协加工 |
| 应变片 SG-350 × 4 + 应变胶 | 外购 | 剪切型双栅，热固化环氧粘贴 |
| 补偿电阻 RES-COMP | 外购 | 调零电阻 + 温度补偿电阻，焊在电桥里（放大之前） |
| 信号调理板 SIG-TS | 案例 A | 两运放前置级 + 24 位 ADC + MCU（温度补偿表、CAN 输出） |
| 盖板、线缆、6 × M3 | 外购 | 盖住凹槽和应变片，防碰、防潮 |

**对照：零件库里的商用力/力矩传感器**（`D-FTS-ATI-FT`，厂商目录）——

{L.md_table(["型号", "Tz 量程 N·m", "Tz 分辨率 N·m", "直径 mm", "质量 g", "测量"], ati_rows)}

ATI 是装在机器人手腕上的六维传感器，测全部三个力、三个力矩；WQ-TS 只测关节一个轴的力矩，分辨率（噪声峰峰值）约 {res_nm:.2f} N·m，
用在关节里，结构简单、刚度高、便宜。**定位：关节专用、单轴、高刚度、低成本**——不和六维传感器比全能，比的是装进每一个关节的成本。
"""
case.step("concept", f"弹性体 + 4 片应变片 + 补偿电阻 + 调理板 + 盖板；对照零件库 ATI 六维传感器，定位关节专用单轴、分辨率约 {res_nm:.2f} N·m。",
          f"Flexure + 4 gauges + compensation resistors + conditioning board + cover; compared with the ATI six-axis sensors in the library, positioned as a single-axis joint sensor with ~{res_nm:.2f} N·m resolution.",
          md=case.text("2_方案.md", concept), tools=L.lib_tools(ATI), facts=[("分辨率", "Resolution", round(res_nm, 2), "N·m")])

# ================================================================ 3 计算：误差预算、调零、标定砝码
# 误差预算（%FS，额定条件；按 RSS 合成）——每项是终检公差或设计值
budget = [["非线性", TOL["ts_nonlin"]["hi"], "终检公差（弹性体 + 应变片）"],
          ["滞后", TOL["ts_hyst"]["hi"], "终检公差（胶层、结合面）"],
          ["零点（调零后残差）", TOL["ts_zero"]["hi"], "终检公差"],
          ["零点温漂 × 2.5（±25 K 工作范围）", TOL["ts_tczero"]["hi"] * 2.5, "终检公差 × 温差"],
          ["蠕变", TOL["ts_creep"]["hi"], "终检公差"],
          ["噪声（峰峰值）", round(NOISE_PP, 3), "案例 A"],
          ["标定不确定度", 0.05, "砝码 + 力臂（下面计算）"]]
rss = math.sqrt(sum(b[1] ** 2 for b in budget))
lin_sum = sum(b[1] for b in budget)
# 调零：桥路零点 z0 (mV/V) ≈ ΔR / (4R) → 在一个桥臂里串 ΔR = 4·R·z0
z_examples = [0.2, 0.6, 1.2]
bal = [[f"{z:+.1f} mV/V（{z / MV * 100:.0f} %FS）", f"{4 * T.R_ARM * z / 1000:.2f} Ω", "电阻低的那一臂"] for z in z_examples]
# 砝码标定：力臂 500 mm，5 级
ARM_M, G_LOC = 0.500, 9.80665
step_nm = T.T_FS / 5
m_step = step_nm / ARM_M / G_LOC
u_arm = 0.05 / 500 * 100            # 力臂长度 ±0.05 mm
u_mass = 0.005                      # 砝码 M1 级的量级 ±0.005 %（示例）
calcmd = f"""# 计算：误差预算、调零电阻、标定砝码

## 误差预算（%FS）

{L.md_table(["来源", "%FS", "依据"], [[b[0], f"{b[1]:.3f}", b[2]] for b in budget])}

每项都按终检公差的**上限**取（实际产品大多远小于上限，见第 7 步），各项独立，按方和根合成：**{rss:.2f} %FS**（最坏情况直接相加 {lin_sum:.2f} %FS）——
满足任务书的 ±1 %FS，对外标“综合精度 ±{math.ceil(rss * 10) / 10:.1f} %FS（0–50 ℃）”。
最大的两项是**零点温漂**和**零点残差**：这两项靠下面的补偿和工艺，不靠弹性体。

## 调零电阻（RES-COMP）

组桥后测到的零点 z₀（mV/V）近似等于 ΔR/(4R)，在电阻偏低的那一个桥臂里串一个 ΔR = 4·R·z₀ 的电阻就能调平（R = {T.R_ARM:g} Ω）：

{L.md_table(["组桥后零点", "串联电阻", "串在"], bal)}

几欧姆的电阻用低温漂锰铜丝或箔电阻：它自己的温度系数要远小于应变片，否则调平了零点、又引进了温漂。调完零点残差 ≤ ±{TOL['ts_zero']['hi']} %FS 交终检。

## 零点温漂补偿（两步）

1. **电桥里**：温度补偿箱测 0、25、50 ℃ 三点零点，算出零点温漂斜率，在相应桥臂串一段铜电阻（铜的温度系数大，几十毫欧就能抵掉）——粗补。
2. **调理板里**：MCU 读板上温度，按三点表做二次插值修正——细补（第 4 步仿真）。

## 砝码标定

力臂 {ARM_M * 1000:.0f} mm 的标定杠杆，每级 {step_nm:g} N·m → 砝码 {step_nm:g} / ({ARM_M:g} × {G_LOC}) = **{m_step:.3f} kg**，5 级共 {5 * m_step:.2f} kg（正、反向各一套）。
不确定度：力臂 ±0.05 mm → {u_arm:.3f} %，砝码 ±{u_mass} %（示例），重力加速度按当地值修正——合计远小于预算里的 0.05 %FS。
"""
case.step("calc", f"误差预算方和根 {rss:.2f} %FS，温漂和零点是大头；调零串几欧电阻；标定杠杆 {ARM_M * 1000:.0f} mm、每级砝码 {m_step:.2f} kg。",
          f"Error budget {rss:.2f} %FS RSS, thermal zero and zero residual dominate; a few ohms in series balances the zero; 500 mm calibration lever, {m_step:.2f} kg per step.",
          md=case.text("3_计算书.md", calcmd), tools=tools("inst"),
          facts=[("综合误差（方和根）", "Total error (RSS)", round(rss, 2), "%FS"), ("每级砝码", "Mass per step", round(m_step, 3), "kg")])
case.check("calc", "综合误差（方和根，按公差上限）", "Total error (RSS of tolerance limits)", round(rss, 2), "<=", 1.0, "%FS", "任务书")

# ================================================================ 4 仿真：一台传感器的标定、温度补偿（200 台统计）
rnd = random.Random(1617)


def torque_out(x, s_mv_v, nl, hys, zero_pct, down=False):
    """“虚拟仪器”力矩传感器同一个模型（cae/instruments.torque_out）：y = x + 4·nl·x(1−x) [+ 4·hys·x(1−x) 卸载]，输出按满量程归一（%FS 计）"""
    y = x + 4 * nl * x * (1 - x) + (4 * hys * x * (1 - x) if down else 0)
    return s_mv_v * y + zero_pct / 100 * s_mv_v


S_UNIT, NL, HY, Z0 = MV * 1.004, 0.0011, 0.0009, 0.12      # 一台的“真值”（示例）：比设计灵敏 0.4 %、非线性 0.11 %、滞后 0.09 %、零点 +0.12 %FS
levels = np.linspace(0, 1, 6)
cyc = []
for c_ in range(3):
    up = [torque_out(x, S_UNIT, NL, HY, Z0) + rnd.gauss(0, NOISE_PP / 6.6 / 100 * MV) for x in levels]
    dn = [torque_out(x, S_UNIT, NL, HY, Z0, down=True) + rnd.gauss(0, NOISE_PP / 6.6 / 100 * MV) for x in levels[::-1]][::-1]
    cyc.append((up, dn))
up_m = np.mean([c[0] for c in cyc], axis=0)
dn_m = np.mean([c[1] for c in cyc], axis=0)
allx = np.concatenate([levels, levels])
ally = np.concatenate([up_m, dn_m])
k_fit, b_fit = np.polyfit(levels * T.T_FS, (up_m + dn_m) / 2, 1)
span = k_fit * T.T_FS
nonlin = np.max(np.abs((up_m + dn_m) / 2 - (k_fit * levels * T.T_FS + b_fit))) / span * 100
hyst = np.max(np.abs(dn_m - up_m)) / span * 100
zero_cal = b_fit / span * 100

# 温度补偿：200 台，零点温漂（示例模型）= 斜率 + 弯曲；粗补（铜电阻）后斜率剩 ±20 %，细补（MCU 三点二次插值）后只剩高阶
temps = np.linspace(0, 50, 51)


def tc_unit():
    a1 = rnd.gauss(0, 0.04)             # %FS/K（应变片温度系数不匹配，示例：未补偿约 ±0.4 %FS/10K）
    a2 = rnd.gauss(0, 0.0012)           # %FS/K²
    a3 = rnd.gauss(0, 0.000003)         # %FS/K³（±25 K 时约 ±0.05 %FS）
    return lambda t: a1 * (t - 25) + a2 * (t - 25) ** 2 + a3 * (t - 25) ** 3, a1


def per10k(curve):
    """零点温漂指标：0–50 ℃ 内任意相隔 10 K 两点之差的最大值（%FS/10K）"""
    v = curve(temps)
    return max(abs(v[i + 10] - v[i]) for i in range(len(temps) - 10))


raw_, coarse_, fine_ = [], [], []
ex_curves = None
for i in range(200):
    f_, a1 = tc_unit()
    raw_.append(per10k(f_))
    resid = rnd.uniform(-0.2, 0.2)
    fc = (lambda f_, a1, resid: (lambda t: f_(t) - a1 * (1 - resid) * (t - 25)))(f_, a1, resid)
    coarse_.append(per10k(fc))
    tp = np.array([0.0, 25.0, 50.0])
    meas = fc(tp) + np.array([rnd.gauss(0, 0.005) for _ in tp])        # 补偿箱测三点（含测量噪声）
    poly = np.polyfit(tp, meas, 2)
    ff = (lambda fc, poly: (lambda t: fc(t) - np.polyval(poly, t)))(fc, poly)
    fine_.append(per10k(ff))
    if i == 3:
        ex_curves = (f_, fc, ff)
raw_, coarse_, fine_ = map(np.array, (raw_, coarse_, fine_))
tc_lim = TOL["ts_tczero"]["hi"]
fine_ok = float(np.mean(fine_ <= tc_lim) * 100)
coarse_ok = float(np.mean(coarse_ <= tc_lim) * 100)

fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.1))
for (u, d) in cyc:
    axs[0].plot(levels * T.T_FS, (np.array(u) - (k_fit * levels * T.T_FS + b_fit)) / span * 100, "o-", ms=2.5, color=L.ACCENT, lw=0.7)
    axs[0].plot(levels * T.T_FS, (np.array(d) - (k_fit * levels * T.T_FS + b_fit)) / span * 100, "s--", ms=2.5, color="#8aa4bd", lw=0.7)
axs[0].axhline(0, color=L.MUTED, lw=0.5)
axs[0].set_xlabel("力矩 / N·m")
axs[0].set_ylabel("偏离拟合直线 / %FS")
axs[0].set_title(f"标定 3 个循环：非线性 {nonlin:.2f}、滞后 {hyst:.2f} %FS", fontsize=9)
for fn, lab, col in zip(ex_curves, ("未补偿", "粗补（铜电阻）", "细补（MCU 三点）"), ("#c0c8d0", "#8aa4bd", L.ACCENT)):
    axs[1].plot(temps, fn(temps), color=col, label=lab)
axs[1].set_xlabel("温度 / ℃")
axs[1].set_ylabel("零点 / %FS")
axs[1].set_title("一台的零点温漂", fontsize=9)
axs[1].legend(fontsize=7.5)
bins = np.linspace(0, max(raw_.max(), 0.8), 30)
axs[2].hist(raw_, bins=bins, color="#c0c8d0", label="未补偿")
axs[2].hist(coarse_, bins=bins, color="#8aa4bd", label="粗补")
axs[2].hist(fine_, bins=bins, color=L.ACCENT, label="细补")
axs[2].axvline(tc_lim, color=L.BAD, ls=":", lw=1)
axs[2].set_xlabel("零点温漂 / %FS·(10 K)⁻¹")
axs[2].set_title("200 台", fontsize=9)
axs[2].legend(fontsize=7.5)
case.fig(fig, "4_标定与温度补偿.png")
simmd = f"""# 仿真：砝码标定与温度补偿

## 一台传感器的砝码标定（“虚拟仪器”力矩传感器同一个模型）

模型 y = x + 4·nl·x(1−x)（加载），卸载再加 4·hys·x(1−x)，噪声取案例 A 的 {NOISE_PP:.3f} %FS 峰峰值。这一台的“真值”（示例）：灵敏度比设计高 0.4 %、非线性 0.11 %、滞后 0.09 %、零点 +0.12 %FS。
0、40 … 200 N·m 六级，加载、卸载各一遍，做 3 个循环：

{L.md_table(["标定结果", "值", "终检公差"], [
    ["灵敏度", f"{span:.4f} mV/V（设计 {MV:.4f}）", "—（写进证书，调理板按它换算）"],
    ["非线性（最佳直线）", f"{nonlin:.3f} %FS", f"≤ {TOL['ts_nonlin']['hi']}"],
    ["滞后", f"{hyst:.3f} %FS", f"≤ {TOL['ts_hyst']['hi']}"],
    ["零点", f"{zero_cal:+.3f} %FS", f"±{TOL['ts_zero']['hi']}"],
])}

标定把灵敏度的 0.4 % 偏差和零点修掉（写进调理板）；**非线性、滞后修不掉**，只能靠弹性体、粘片和固化。

## 零点温漂：200 台的统计（示例模型）

每台的零点温漂 = 斜率 + 二次 + 三次项（应变片温度系数不匹配、胶层，系数随机）。

{L.md_table(["", "未补偿", "粗补（铜电阻，斜率剩 ±20 %）", "细补（MCU 三点二次插值）"], [
    ["零点温漂中位数 %FS/10K", f"{np.median(raw_):.3f}", f"{np.median(coarse_):.3f}", f"{np.median(fine_):.3f}"],
    ["最大 %FS/10K", f"{raw_.max():.3f}", f"{coarse_.max():.3f}", f"{fine_.max():.3f}"],
    [f"≤ {tc_lim} 的比例", f"{np.mean(raw_ <= tc_lim) * 100:.0f} %", f"{coarse_ok:.0f} %", f"**{fine_ok:.0f} %**"],
])}

只靠铜电阻粗补，{100 - coarse_ok:.0f} % 的传感器温漂超差；加上 MCU 的三点修正，剩下的只有三次项和测量噪声。这就是温度补偿工序要 240 分钟（三个温度点、每点等热平衡）的原因。
"""
case.step("sim", f"虚拟标定：非线性 {nonlin:.2f}、滞后 {hyst:.2f} %FS；温度补偿 200 台：只粗补 {coarse_ok:.0f} % 合格，加 MCU 三点修正 {fine_ok:.0f} % 合格。",
          f"Virtual calibration: non-linearity {nonlin:.2f}, hysteresis {hyst:.2f} %FS; temperature compensation of 200 units: {coarse_ok:.0f} % pass with coarse compensation only, {fine_ok:.0f} % with the 3-point MCU correction.",
          md=case.text("4_标定与温度补偿.md", simmd), figs=[("4_标定与温度补偿.png", "标定曲线、一台的温漂、200 台的温漂分布", "Calibration curves, thermal zero of one unit, distribution over 200 units")],
          tools=tools("inst"), facts=[("非线性", "Non-linearity", round(nonlin, 3), "%FS"), ("滞后", "Hysteresis", round(hyst, 3), "%FS"), ("细补后合格率", "Pass rate after fine compensation", round(fine_ok), "%")])
case.check("sim", "虚拟标定非线性", "Virtual-calibration non-linearity", round(nonlin, 3), "<=", TOL["ts_nonlin"]["hi"], "%FS", "终检公差")
case.check("sim", "虚拟标定滞后", "Virtual-calibration hysteresis", round(hyst, 3), "<=", TOL["ts_hyst"]["hi"], "%FS", "终检公差")
case.check("sim", "温度补偿后零点温漂合格率", "Thermal-zero pass rate after compensation", round(fine_ok), ">=", 99, "%", "终检公差")

# ================================================================ 5 三维与装配、物料清单
import build123d as bd  # noqa: E402

g = T.GEOM
body = T.solid(g, holes=True)
cover = bd.Pos(0, 0, g["H"] / 2 + 0.5) * (bd.Cylinder(37.5, 1.0) - bd.Cylinder(21.0, 1.0))
for k in range(4):
    cover -= bd.Rot(0, 0, 90 * k) * bd.Pos(36, 0, g["H"] / 2 + 0.5) * bd.Cylinder(1.6, 1.0)
board = bd.Pos(0, 0, -g["H"] / 2 - 2.5) * (bd.Cylinder(33.0, 1.6) - bd.Cylinder(23.0, 1.6))
asm = bd.Compound([body, cover, board])
bd.export_step(asm, str(case.path("WQ-TS.step")))
L.render_solid(bd.Compound([body, cover]), case.path("5_整机三维.png"), elev=40, azim=-60, size=(6.0, 4.8), swap=False)
LIBP = [L.lib_part("A-SCR-SHC", "M3x8"), L.lib_part("A-SCR-SHC", "M5x20"), L.lib_part("A-SCR-SHC", "M6x25"), L.lib_part("A-PIN-TAPER", "6x30"),
        L.lib_part("A-ELE-XH", "5P"), L.lib_part("A-ELE-XH", "4P"), L.lib_part("A-ELE-LQFP48", "STM32G431CBT6"), L.lib_part("A-ELE-SOIC8", "MCP2562-E-SN")]
bom = F.BOMS["WQ-TS"][1]
bom_rows = [[c, F.ITEMS[c][0] if c in F.ITEMS else c, q] for c, q in bom]
cadmd = f"""# 三维、装配与物料清单

`WQ-TS.step`：弹性体（案例 B）+ 正面盖板（铝 1 mm，盖住凹槽和应变片，4 × M3×8 拧在外圈内侧）+ 背面环形调理板（SIG-TS，2 × M3×8）。

**物料清单**（传感器厂清单，一层）：

{L.md_table(["物料", "名称", "用量"], bom_rows)}

**零件库里选的标准件、元件**：

{L.lib_md(LIBP, {"A-SCR-SHC/M3x8": "盖板 ×4、调理板 ×2（= 清单 SCR-M3 ×6）", "A-SCR-SHC/M5x20": "客户安装：外圈 ×8（随货附）", "A-SCR-SHC/M6x25": "客户安装：内毂 ×6（随货附）",
                 "A-PIN-TAPER/6x30": "客户安装：内毂 ×2（与减速器配铰）", "A-ELE-XH/5P": "调理板：电桥插座", "A-ELE-XH/4P": "调理板：输出插座",
                 "A-ELE-LQFP48/STM32G431CBT6": "调理板：MCU", "A-ELE-SOIC8/MCP2562-E-SN": "调理板：CAN 收发器"})}

清单里的 SCR-M3（内六角螺钉 M3×8）就是零件库的 `A-SCR-SHC/M3x8`（GB/T 70.1）；客户安装用的 M5、M6 螺钉和锥销是案例 B 第 5 步算出来的，随货附安装说明。
"""
case.step("cad", f"整机三维（弹性体 + 盖板 + 调理板）；物料清单 {len(bom_rows)} 行；{len(LIBP)} 种标准件、元件从零件库选。",
          f"3D assembly (flexure + cover + conditioning board); {len(bom_rows)}-line BOM; {len(LIBP)} standard parts and components from the library.",
          md=case.text("5_三维与物料清单.md", cadmd), figs=[("5_整机三维.png", "WQ-TS 整机（正面盖板）", "WQ-TS assembly (front cover)")],
          files=[("WQ-TS.step", "整机 STEP", "Assembly (STEP)")], tools=tools("engineer") + L.lib_tools(LIBP), facts=[("物料清单", "BOM lines", len(bom_rows), "")])

# ================================================================ 6 工艺：八道工序
rt = F.ROUTINGS[F.BOMS["WQ-TS"][0]]
keys = {"来料检验": "弹性体四个腹板厚度（案例 B：±0.01）；应变片阻值分选，同一台的 8 个栅相互差 ≤ 0.1 %（减小调零量）",
        "应变片粘贴": "粘贴面喷砂、清洗；对中误差 ≤ 0.2 mm、角度 ≤ 1°（偏了，相对轮辐串联抵消不完全）；加压夹具",
        "胶固化": "**固化曲线**：按应变胶要求升温、保温、后固化；炉温要实测（胶没固化透：蠕变、滞后、温漂一起变大）",
        "组桥焊线": "按案例 A 的接线表；四个臂阻值、未调零零点记录",
        "温度补偿": "0、25、50 ℃ 三点，每点等热平衡；算调零、铜补偿电阻，焊上后复测；MCU 写三点修正表",
        "砝码标定": f"杠杆 {ARM_M * 1000:.0f} mm，0–200 N·m 六级，正反向、加卸载各 3 个循环；写灵敏度、零点",
        "扭矩终检": "复测非线性、滞后、零点；满量程保持 30 min 测蠕变；读温漂记录",
        "包装": "防静电盒；随货：标定证书、安装螺钉与锥销、安装说明"}
procmd = f"""# 工艺：扭矩传感器线

{L.md_table(["工序", "名称", "设备", "工时 / min", "要点"], [[i + 1, op, F.OPERATIONS[op], m, next((v for k_, v in keys.items() if op.startswith(k_)), "")] for i, (op, m) in enumerate(rt)])}

合计 {sum(m for _, m in rt)} 分钟/台，其中胶固化 180、温度补偿 240 分钟是炉子整批走，摊到每台很少；人工工时集中在粘片（45）、组桥（40）、标定（45）。
"""
case.step("process", f"{len(rt)} 道工序，每道写明要点；固化曲线、温度补偿三点、标定 3 个循环。",
          f"{len(rt)} operations with key points; cure profile, three-point temperature compensation, three calibration cycles.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt), "")])

# ================================================================ 7 制造：第一批出问题 → 8D → 第二批
sh1 = L.run_shop("WQ-TS", 20, "WO-CASE-SN-C1", seed=1618, problems=[("cure_low", None)])
rows1, cpk1, fails1, st1 = L.shop_table(sh1["measurements"])
bad_units = len({m["part_serial"] for m in sh1["measurements"] if m["result"] != "pass"})
pb = ER.PROBLEMS["cure_low"]
sh2 = L.run_shop("WQ-TS", 20, "WO-CASE-SN-C2", seed=1619)
rows2, cpk2, fails2, st2 = L.shop_table(sh2["measurements"])
codes = ("ts_nonlin", "ts_hyst", "ts_creep", "ts_tczero", "ts_zero")
fig, ax = plt.subplots(figsize=(8.4, 3.0))
x = np.arange(len(codes))
ax.bar(x - 0.2, [st1[c]["mean"] / st1[c]["hi"] * 100 for c in codes], 0.4, color=L.BAD, alpha=0.7, label="第一批（固化炉温偏低）")
ax.bar(x + 0.2, [abs(st2[c]["mean"]) / st2[c]["hi"] * 100 if c != "ts_zero" else st2[c]["sd"] * 3 / st2[c]["hi"] * 100 for c in codes], 0.4, color=L.ACCENT, label="第二批（改固化曲线后）")
ax.axhline(100, color=L.MUTED, ls=":", lw=0.9)
ax.set_xticks(x, [st1[c]["name"].split("（")[0] for c in codes])
ax.set_ylabel("均值占公差 / %（零点为 3σ）")
ax.legend(fontsize=8)
case.fig(fig, "7_两批对比.png")
makemd = f"""# 制造：第一批出问题，8D，第二批

## 第一批 20 台

{L.md_table(["特性（%FS）", "公差", "台数", "均值", "标准差", "Cpk"], rows1)}

**{bad_units} 台**至少一项超差（共 {fails1} 项次）。看哪几项坏了：**蠕变、滞后、零点温漂**一起变大，非线性略升，零点不受影响。

## 8D 追因（数字工厂“质量 → 8D”）

- **哪里共有**：三项都和**胶层**有关——胶层没完全固化就像一层软垫，受力后慢慢“流”（蠕变），加卸载走不同的路（滞后），温度一变胶层模量变、零点跟着跑（温漂）。
  零点由调零电阻定，和胶无关，所以零点没事。这一个模式就排除了弹性体（会影响非线性、全批一样）和应变片批次（会影响阻值、零点）。
- **查设备**：这一批都在固化炉 cur-1 走，炉子实测温度比设定低——**根因：{pb['name']}**。
- **措施**：重新做固化炉温度曲线（实测、校准热电偶、按应变胶的后固化要求延长保温）——仿真车间“质量 → 8D”下发措施 `profile_cure`。
- **已做出的 {bad_units} 台**：重新后固化后复测；复测仍不合格的报废弹性体以外的部分（应变片拆不下来——弹性体也只能报废）。

## 第二批 20 台（措施生效后）

{L.md_table(["特性（%FS）", "公差", "台数", "均值", "标准差", "Cpk"], rows2)}

不合格 **{fails2}** 项，最低 Cpk {cpk2:.2f}。
"""
case.step("make", f"第一批 {bad_units}/20 台超差（蠕变、滞后、温漂），8D 追到固化炉温偏低，改固化曲线；第二批不合格 {fails2}、最低 Cpk {cpk2:.2f}。",
          f"First batch: {bad_units}/20 out of tolerance (creep, hysteresis, thermal zero); the 8D traces it to a low curing-oven temperature and the cure profile is redone; second batch: {fails2} failures, lowest Cpk {cpk2:.2f}.",
          md=case.text("7_两批与8D.md", makemd), figs=[("7_两批对比.png", "两批终检对比（均值占公差）", "Two batches compared (mean as % of tolerance)")],
          tools=tools("planner", "operator", "quality", "q8d"),
          facts=[("第一批超差台数", "Batch-1 units out of tolerance", bad_units, ""), ("第二批最低 Cpk", "Batch-2 lowest Cpk", round(cpk2, 2), "")])
case.check("make", "第一批超差台数（问题批次，追因）", "Batch-1 units out of tolerance (problem batch)", bad_units, ">", 0, "", "记录：注入固化炉故障")
case.check("make", "第二批不合格项", "Batch-2 failures", fails2, "==", 0, "", "扭矩终检台")
case.check("make", "第二批最低 Cpk", "Batch-2 lowest Cpk", round(cpk2, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

（“第一批超差台数 > 0”是记录问题批次，不是要求。）

1. **产品 = 三个案例的合成**：弹性体定了非线性和刚度（B），信号链定了噪声和零点能不能调（A），补偿、标定和工艺定了最后的精度（C）。
2. **误差预算里最大的是温漂和零点**：靠铜电阻粗补 + MCU 三点细补，200 台仿真合格率从 {coarse_ok:.0f} % 提到 {fine_ok:.0f} %。
3. **标定修得掉的是“比例和偏移”，修不掉的是非线性、滞后、蠕变**——这些只能在设计和工艺里控制。
4. **一种故障一个“指纹”**：蠕变 + 滞后 + 温漂一起变大、零点不变 → 胶层 → 固化炉。读懂测量数据的组合，比一项一项查快得多。

## 留给学生的问题

1. 误差预算里把零点温漂降到 0.08 %FS/10K，综合精度变成多少？值不值得为它多花 60 分钟补偿箱时间？
2. 在仿真车间注入“固化炉温度偏低”，自己做一遍 8D：只看终检数据，能不能排除弹性体和应变片？
3. 如果客户要 ±100 N·m 的版本，弹性体、调理板、标定各要改什么？

相关：传感器厂帮助“产品与物料”“扭矩传感器线”；数字工厂“质量 → 8D”“虚拟仪器（扭矩传感器）”；案例 A、B。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；综合精度 ±{math.ceil(rss * 10) / 10:.1f} %FS；第二批全部合格。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; overall accuracy ±{math.ceil(rss * 10) / 10:.1f} %FS; second batch all good.",
          md=case.text("8_总结.md", review), tools=tools("q8d", "inst"))
case.write()
print("ok", rss, nonlin, hyst, coarse_ok, fine_ok, bad_units, fails1, fails2, cpk2)
