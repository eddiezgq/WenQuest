"""第 166b 轮：计算机厂案例 C——20 柜算力中心：20 台 WQ-RACK42（每柜 16 台 WQ-SV2U）组成的机房。
供配电（变压器、UPS 3+1、电池、柴油发电机）、制冷（背门换热器 + 18/24 ℃ 温水 + 自然冷却）、布置；全年 8760 小时逐时仿真算 PUE（三个方案同一套气候）；
N+1 设备可用性：解析式对照蒙特卡洛；FreeCAD 同一内核（build123d）出机房三维；到计算机厂整机柜联调 20 台；现场安装与综合测试写工艺。

    python3 tools/cases/computer_c.py

气候、设备效率曲线、可靠性数据都是示例值（量级按华东沿海、常见设备）。输出到 factory/cases/computer/C/。
"""
from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-computer.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402

TOOLS = {
    "energy": ("能源与环境", "Energy & environment", "/energy"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间执行", "Shop floor", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "burnin": ("整机老化曲线", "System burn-in curves", "/burn-in"),
    "3d": ("3D 车间", "3D shop", "/3d"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("computer", "C", "完整", "20 柜算力中心", "A 20-rack computing center", "20 × WQ-RACK42 机房",
              "20 台整机柜（320 台服务器）组成的算力中心：比较三种制冷方案，选背门换热器 + 18/24 ℃ 温水 + 自然冷却；算供配电（变压器、UPS 3+1、电池 15 分钟、发电机）、"
              "冷机和水泵；全年 8760 小时逐时仿真年 PUE；N+1 冗余的可用性用公式和蒙特卡洛对照；出机房三维和平面图；整机柜联调 20 台，写现场安装与综合测试。",
              "A computing center of 20 racks (320 servers): three cooling options compared, rear-door heat exchangers on 18/24 °C warm water with free cooling chosen; "
              "power chain (transformers, 3+1 UPS, 15-minute battery, generators), chillers and pumps sized; annual PUE from an 8760-hour simulation; "
              "N+1 availability by formula and Monte Carlo; 3D hall and floor plan; 20 racks integration-tested, site installation and integrated systems test planned.",
              "tools/cases/computer_c.py")

# ---------------------------------------------------------------- 任务（示例值）
N_RACK, SV_PER = 20, 16
P_RACK_DES = 13.0           # 每柜设计功率 kW（计算机厂整机柜联调 rk_power 上限）
P_RACK_OP = 10.8            # 每柜满载实测量级 kW（rk_power 名义值）
IT_DES = N_RACK * P_RACK_DES
IT_OP = N_RACK * P_RACK_OP  # 算力中心长时间满载，全年按这个算
PUE_REQ = 1.30              # 国内新建大型数据中心常见要求
AVAIL_REQ = 99.98           # 年可用性 %（常见的“容错到 N+1”级别）
T_SUPPLY_AIR = 25.0         # 机房送风（服务器进风）
CFM = 2118.88
Q_SV = 211.0 / CFM          # 一台服务器满转风量（案例 B 第 3 步）
RHO_A, CP_A = 1.16, 1007.0
CP_W = 4.18                 # kJ/(kg·K)
TW_S, TW_R = 18.0, 24.0     # 温水供 / 回
EPS_RDHX = 0.70             # 背门换热器效能（厂家曲线，示例）

# 气候（示例，量级按华东沿海）：月平均干球温度、日较差、平均相对湿度
TM = [6.0, 7.5, 11.0, 16.0, 21.0, 25.0, 29.0, 28.5, 25.0, 20.0, 14.5, 8.5]
RHM = [74, 76, 78, 78, 79, 84, 80, 80, 79, 74, 73, 71]
DIURNAL = 3.5
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def wet_bulb(t, rh):
    """Stull（2011）经验式：干球温度 ℃、相对湿度 % → 湿球温度 ℃"""
    return (t * math.atan(0.151977 * math.sqrt(rh + 8.313659)) + math.atan(t + rh) - math.atan(rh - 1.676331)
            + 0.00391838 * rh ** 1.5 * math.atan(0.023101 * rh) - 4.686035)


def climate(seed=1663):
    rng = random.Random(seed)
    tdb, twb = [], []
    for m, nd in enumerate(DAYS):
        for _ in range(nd):
            day = rng.gauss(0, 2.2)
            for h in range(24):
                t = TM[m] + day + DIURNAL * math.cos(2 * math.pi * (h - 15) / 24)
                rh = min(97.0, max(35.0, RHM[m] - 9 * DIURNAL / 3.5 * math.cos(2 * math.pi * (h - 15) / 24) + rng.gauss(0, 3)))
                tdb.append(t)
                twb.append(wet_bulb(t, rh))
    return np.array(tdb), np.array(twb)


TDB, TWB = climate()


def ups_eff(x):
    """UPS 效率随负载率（示例曲线：空载损耗 + 固定 + 与负载成正比）"""
    return 1 - (0.006 / x + 0.012 + 0.012 * x)


# 三个制冷方案（示例参数）：蒸发温度、冷却方式、空气侧风机（占 IT）、自然冷却、压缩机效率（占卡诺）：风冷小压缩机 0.35、水冷离心冷机 0.55
OPTS = {
    "A": dict(name="房间精密空调（风冷直膨）", t_evap=8.0, air_cooled=True, fan_frac=0.07, fc_full=None, eta=0.35),
    "B": dict(name="冷冻水 7/12 ℃ + 房间空调", t_evap=4.0, air_cooled=False, fan_frac=0.05, fc_full=1.0, eta=0.55),
    "C": dict(name="背门换热器 + 18/24 ℃ 温水 + 自然冷却", t_evap=16.0, air_cooled=False, fan_frac=0.006, fc_full=TW_S - 6.0, eta=0.55),
}
APPROACH_TOWER, RANGE_CW, LIFT = 4.0, 5.0, 2.0
P_LIGHT = 3.0                # 照明、楼宇控制 kW
N_UPS_MOD, UPS_MOD_KW = 4, 100.0


def plant_hour(opt, tdb, twb, it):
    """一小时：各项功率 kW。热负荷 = IT + UPS 损耗 + 配电损耗 + 照明 + 空气侧风机"""
    o = OPTS[opt]
    x = it / (N_UPS_MOD * UPS_MOD_KW)
    p_ups = it / ups_eff(x) - it
    p_dist = 0.010 * it + 0.005 * it          # 变压器 1 %、配电与线缆 0.5 %
    p_fan = o["fan_frac"] * it
    heat = it + p_ups + p_dist + P_LIGHT + p_fan
    p_pump = 0.0 if o["air_cooled"] else 0.012 * heat          # 冷冻水泵
    heat += p_pump
    # 自然冷却：湿球温度低到能让冷却塔 + 板换出 TW_S 时全部免费，往上 5 K 部分预冷
    fc = 0.0
    if o["fc_full"] is not None:
        fc = 1.0 if twb <= o["fc_full"] else max(0.0, (o["fc_full"] + 5 - twb) / 5)
    if o["air_cooled"]:
        t_cond = tdb + 12.0
    else:
        t_cond = twb + APPROACH_TOWER + RANGE_CW + LIFT
    t_e = o["t_evap"] + 273.15
    cop = min(11.0, o["eta"] * t_e / max(3.0, t_cond + 273.15 - t_e))
    p_chiller = heat * (1 - fc) / cop
    p_tower = 0.0 if o["air_cooled"] else 0.012 * (heat + p_chiller) + 0.010 * (heat + p_chiller)   # 冷却塔风机 + 冷却水泵
    total = it + p_ups + p_dist + P_LIGHT + p_fan + p_pump + p_chiller + p_tower
    return dict(total=total, ups=p_ups, dist=p_dist, fan=p_fan, pump=p_pump, chiller=p_chiller, tower=p_tower, fc=fc, cop=cop, heat=heat)


def annual(opt, it=IT_OP):
    rows = [plant_hour(opt, a, b, it) for a, b in zip(TDB, TWB)]
    tot = np.array([r["total"] for r in rows])
    return dict(rows=rows, total=tot, pue=tot.sum() / (it * len(rows)), peak=tot.max(), fc_h=sum(r["fc"] >= 0.999 for r in rows),
                part_h=sum(0 < r["fc"] < 0.999 for r in rows), mwh=tot.sum() / 1000, pue_h=tot / it)


ANN = {k: annual(k) for k in OPTS}
SEL = "C"
A_SEL = ANN[SEL]

# ================================================================ 1 任务书
brief = f"""# 设计任务书：20 柜算力中心

**用在哪**　计算机厂把 20 台 42U 整机柜 WQ-RACK42（每柜 16 台 2U 服务器 WQ-SV2U，案例 B）交付给一个算力中心（示例客户），
机房、供电、制冷由同一个设计组一起做——**整机柜的功率和散热决定机房怎么建**。

| 项目 | 要求 | 出处 |
|---|---|---|
| 机柜 | {N_RACK} 柜 × {SV_PER} 台 = {N_RACK * SV_PER} 台服务器 | 客户订单 |
| 每柜功率 | 设计 {P_RACK_DES:g} kW，满载实测约 {P_RACK_OP:g} kW | 计算机厂整机柜联调 rk_power |
| IT 负荷 | 设计 {IT_DES:.0f} kW；长时间满载约 {IT_OP:.0f} kW | 算力中心训练、计算任务 |
| 服务器进风 | {T_SUPPLY_AIR:g} ℃（A1 推荐区间 18–27 ℃） | 案例 B 按最高 35 ℃ 设计，留余量 |
| 年 PUE | ≤ {PUE_REQ:g} | 国内新建大型数据中心常见要求 |
| 可用性 | ≥ {AVAIL_REQ:g} %（关键设备 N+1，一台坏了不停机） | 客户要求 |
| 停电 | 电池撑 15 分钟，柴油发电机接上 | 常规 |
| 场地 | 华东沿海城市（气候示例），一层厂房改造，室外设备场 | 客户提供 |

PUE = 全年总用电 / 全年 IT 用电。冷机、UPS、水泵、冷却塔、照明都是外购设备，写通用名称和示例参数。
"""
case.step("brief", f"{N_RACK} 柜 × {SV_PER} 台；IT 设计 {IT_DES:.0f} kW、满载约 {IT_OP:.0f} kW；年 PUE ≤ {PUE_REQ:g}；可用性 ≥ {AVAIL_REQ:g} %。",
          f"{N_RACK} racks × {SV_PER} servers; IT {IT_DES:.0f} kW design, about {IT_OP:.0f} kW at full load; annual PUE ≤ {PUE_REQ:g}; availability ≥ {AVAIL_REQ:g} %.",
          md=case.text("1_任务书.md", brief),
          facts=[("IT 设计负荷", "IT design load", IT_DES, "kW"), ("PUE 要求", "PUE target", PUE_REQ, ""), ("服务器", "Servers", N_RACK * SV_PER, "")])

# ================================================================ 2 方案
crow = []
for k, o in OPTS.items():
    a = ANN[k]
    crow.append([k, o["name"], f"{a['pue']:.3f}", f"{a['mwh']:,.0f} MWh", f"{a['fc_h']:,} h", "✓ 选定" if k == SEL else ("✗ PUE 超" if a["pue"] > PUE_REQ else "")])
concept = f"""# 方案：怎么把 {IT_OP:.0f} kW 热量搬出去

## 三种制冷（同一套全年气候、同一个负荷，第 4 步逐时仿真的结果）

{L.md_table(["", "方案", "年 PUE", "年用电", "全自然冷却小时", ""], crow)}

- **A 房间精密空调**：每台空调自带压缩机，冷风吹进机房、热风回来；蒸发温度低、风机多，PUE 最高。
- **B 冷冻水 + 房间空调**：冷机集中、效率高一些；但 7 ℃ 冷水要冷机一直开，自然冷却几乎用不上。
- **C 背门换热器 + 温水**：每个机柜后门是一块水冷盘管，服务器自己的风扇把热风吹过盘管，**热量在机柜里就交给水**，
  机房不用大风机；水温可以高到 {TW_S:g}/{TW_R:g} ℃，冷机效率高，冬春秋湿球温度低时冷却塔直接出冷水（自然冷却），冷机停。

**选 C**。整机柜上本来就带背门换热器 RDHX（计算机厂整机柜 BOM），联调时量“换热器进出风温差”。

## 供电：两路市电 → 变压器 → UPS（3+1）→ 列头柜 → 机柜两路配电单元

UPS 模块化 {N_UPS_MOD} × {UPS_MOD_KW:.0f} kW（3 块够设计负荷，多 1 块冗余）；锂电池撑 15 分钟，柴油发电机 1 分钟内起来接上。
"""
case.step("concept", f"选背门换热器 + 18/24 ℃ 温水 + 自然冷却：年 PUE {ANN['C']['pue']:.3f}（房间精密空调 {ANN['A']['pue']:.3f}、冷冻水 {ANN['B']['pue']:.3f}）。",
          f"Rear-door heat exchangers on 18/24 °C warm water with free cooling: annual PUE {ANN['C']['pue']:.3f} (room DX units {ANN['A']['pue']:.3f}, chilled water {ANN['B']['pue']:.3f}).",
          md=case.text("2_方案.md", concept), facts=[("选定方案 PUE", "Chosen PUE", round(ANN["C"]["pue"], 3), "")])

# ================================================================ 3 计算
q_air_rack = SV_PER * Q_SV
c_air = RHO_A * CP_A * q_air_rack / 1000            # kW/K
dt_srv = P_RACK_DES / c_air
t_ex = T_SUPPLY_AIR + dt_srv
q_rdhx = EPS_RDHX * c_air * (t_ex - TW_S)
t_out = t_ex - q_rdhx / c_air
m_w_rack = P_RACK_DES / (CP_W * (TW_R - TW_S))
peak_h = max(range(len(A_SEL["rows"])), key=lambda i: A_SEL["rows"][i]["total"])
pk = plant_hour(SEL, TDB[peak_h], TWB[peak_h], IT_DES)
heat_peak = pk["heat"]
n_ch = math.ceil(heat_peak / 150.0)
m_w = heat_peak / (CP_W * (TW_R - TW_S))
p_fac_peak = pk["total"]
kva = p_fac_peak / 0.95
tr_sizes = [400, 500, 630, 800, 1000, 1250]
tr = next(s for s in tr_sizes if s >= kva * 1.15)
n_ups_need = math.ceil(IT_DES / UPS_MOD_KW)
e_bat = IT_DES * 0.25 / (0.96 * 0.90)
bat_cab = math.ceil(e_bat / 30.0)
gen_kva = p_fac_peak / 0.8
gen_sizes = [400, 500, 630, 800, 1000]
gen = next(s for s in gen_sizes if s >= gen_kva)
calc = f"""# 计算书 Calculation

## 1 机柜换热 Rack heat exchanger（每柜设计 {P_RACK_DES:g} kW）

| 量 Quantity | 公式 Formula | 结果 Result |
|---|---|---|
| 机柜风量 | {SV_PER} 台 × {Q_SV * CFM:.0f} CFM（案例 B 满转） | {q_air_rack:.2f} m³/s |
| 空气热容流量 | ρ·c_p·Q | {c_air:.2f} kW/K |
| 服务器出风温度 | {T_SUPPLY_AIR:g} + P/(ρ·c_p·Q) | {t_ex:.1f} ℃ |
| 背门换热器换热量 | ε·(ρ·c_p·Q)·(T_出风 − T_水供)，ε = {EPS_RDHX:g} | **{q_rdhx:.1f} kW** ≥ {P_RACK_DES:g} kW |
| 换热后回到机房的空气 | T_出风 − Q/(ρ·c_p·Q) | {t_out:.1f} ℃（≤ 送风 {T_SUPPLY_AIR:g} ℃，机房不额外加热） |
| 每柜水量 | P/(c_p·ΔT_水) | {m_w_rack:.2f} kg/s（{m_w_rack * 3.6:.1f} m³/h） |

## 2 冷源 Cooling plant（最热那一小时、IT 按设计 {IT_DES:.0f} kW）

最热小时湿球 {TWB[peak_h]:.1f} ℃：总热负荷（IT + UPS + 配电 + 照明 + 水泵）**{heat_peak:.0f} kW**；冷机按 150 kW 一台需要 {n_ch} 台 → **{n_ch}+1 台**；
温水总流量 {m_w:.1f} kg/s；冷却塔、冷冻水泵、冷却水泵同样 N+1。冷机 COP = 0.55 × 卡诺（蒸发 {OPTS['C']['t_evap']:g} ℃）= {pk['cop']:.1f}。

## 3 供配电 Power

| 量 | 算法 | 结果 |
|---|---|---|
| 最热小时总用电（IT 设计负荷） | 第 4 步同一个逐时模型 | {p_fac_peak:.0f} kW |
| 变压器 | ÷ 功率因数 0.95 × 1.15 余量，取标准容量；两台互为备用（2N） | **2 × {tr} kVA** |
| UPS | ⌈{IT_DES:.0f} / {UPS_MOD_KW:.0f}⌉ = {n_ups_need} 块 + 1 冗余 | **{n_ups_need + 1} × {UPS_MOD_KW:.0f} kW** |
| 电池（15 分钟） | P·t / (η_逆变 0.96 × 放电深度 0.9) = {e_bat:.0f} kWh | **{bat_cab} 柜 × 30 kWh** |
| 柴油发电机 | 总用电 ÷ 0.8 = {gen_kva:.0f} kVA | **{gen} kVA × 2（N+1）** |
| 每柜配电 | 两路 PDU 各能带满 {P_RACK_DES:g} kW：400 V 三相、32 A | 案例 B 的服务器两只电源各接一路 |
"""
case.step("calc", f"背门换热器每柜 {q_rdhx:.1f} kW ≥ {P_RACK_DES:g} kW；冷机 {n_ch}+1 × 150 kW；变压器 2 × {tr} kVA；UPS {n_ups_need}+1 × 100 kW；电池 {bat_cab} × 30 kWh。",
          f"RDHX {q_rdhx:.1f} kW per rack ≥ {P_RACK_DES:g} kW; chillers {n_ch}+1 × 150 kW; transformers 2 × {tr} kVA; UPS {n_ups_need}+1 × 100 kW; battery {bat_cab} × 30 kWh.",
          md=case.text("3_计算书.md", calc),
          facts=[("每柜换热", "RDHX capacity", round(q_rdhx, 1), "kW"), ("冷机", "Chillers", f"{n_ch}+1", ""), ("变压器", "Transformers", f"2×{tr}", "kVA"),
                 ("UPS", "UPS", f"{n_ups_need}+1×100", "kW")])
case.check("calc", "背门换热器换热量（每柜设计功率）", "RDHX capacity at rack design power", round(q_rdhx, 1), ">=", P_RACK_DES, "kW", "第 1 节")
case.check("calc", "换热后回机房空气温度", "Air back into the room after the RDHX", round(t_out, 1), "<=", T_SUPPLY_AIR, "℃", "不额外加热机房")
case.check("calc", "UPS 去掉一块后的容量", "UPS capacity with one module out", n_ups_need * UPS_MOD_KW, ">=", IT_DES, "kW", "N+1")

# ================================================================ 4 仿真：全年逐时 PUE + 可用性
months = np.repeat(np.arange(12), [d * 24 for d in DAYS])
pue_m = {k: [ANN[k]["total"][months == m].sum() / (IT_OP * (months == m).sum()) for m in range(12)] for k in OPTS}
fc_m = [np.mean([A_SEL["rows"][i]["fc"] for i in np.where(months == m)[0]]) for m in range(12)]
fig, axs = plt.subplots(1, 3, figsize=(11.6, 3.2))
hrs = np.arange(len(TDB)) / 24
axs[0].plot(hrs, TDB, color="#c7a17a", lw=0.3, label="干球")
axs[0].plot(hrs, TWB, color=L.ACCENT, lw=0.3, label="湿球")
axs[0].axhline(OPTS["C"]["fc_full"], color=L.OK, ls="--", lw=0.8, label=f"湿球 ≤ {OPTS['C']['fc_full']:g} ℃：全自然冷却")
axs[0].set_xlabel("一年中的第几天")
axs[0].set_ylabel("℃")
axs[0].set_title("示例气候（华东沿海量级）", fontsize=9.5)
axs[0].legend(fontsize=7.5, frameon=False, loc="upper left")
for k, c in zip(OPTS, (L.BAD, L.MUTED, L.ACCENT)):
    axs[1].plot(range(1, 13), pue_m[k], "o-", ms=3, color=c, label=f"{k}：年 {ANN[k]['pue']:.3f}")
axs[1].axhline(PUE_REQ, color=L.BAD, ls="--", lw=0.8)
axs[1].set_xticks(range(1, 13))
axs[1].set_xlabel("月")
axs[1].set_ylabel("PUE")
axs[1].set_title("三个方案逐月 PUE", fontsize=9.5)
axs[1].legend(fontsize=7.5, frameon=False)
parts = ["ups", "dist", "fan", "pump", "chiller", "tower"]
labs = ["UPS 损耗", "变压器与配电", "空气侧风机", "冷冻水泵", "冷机", "冷却塔与水泵"]
vals = [sum(r[p] for r in A_SEL["rows"]) / 1000 for p in parts] + [P_LIGHT * len(TDB) / 1000]
axs[2].barh(labs + ["照明与控制"], vals, color="#8aa4bd")
axs[2].set_xlabel("方案 C 全年 / MWh（IT 本身 {:,.0f} MWh）".format(IT_OP * len(TDB) / 1000))
axs[2].set_title("非 IT 用电在哪里", fontsize=9.5)
fig.subplots_adjust(wspace=0.45)
case.fig(fig, "4_全年PUE.png")

# 可用性：N+1 设备组（示例 MTBF / MTTR）
GROUPS = [("UPS 模块", 4, 3, 200000, 8), ("冷机", n_ch + 1, n_ch, 25000, 24), ("冷冻水泵", 3, 2, 50000, 12), ("冷却塔", n_ch + 1, n_ch, 40000, 24),
          ("柴油发电机（停电时）", 2, 1, 2500, 24)]


def a_analytic(n, k, mtbf, mttr):
    a = mtbf / (mtbf + mttr)
    return sum(math.comb(n, j) * a ** j * (1 - a) ** (n - j) for j in range(k, n + 1))


def mc_group(n, k, mtbf, mttr, years=200000, rng=None):
    """N 选 K 系统按马尔可夫链逐事件模拟：每台独立故障（指数）、独立修理（指数）。→ 不可用小时 / 年"""
    rng = rng or random.Random(1664)
    t, up, down_t = 0.0, n, 0.0
    horizon = years * 8760.0
    lam, mu = 1 / mtbf, 1 / mttr
    while t < horizon:
        rate = up * lam + (n - up) * mu
        dt = rng.expovariate(rate)
        if up < k:
            down_t += min(dt, horizon - t)
        t += dt
        if rng.random() < up * lam / rate:
            up -= 1
        else:
            up += 1
    return down_t / years


p_outage = 2.0 / 8760 * 4        # 市电一年停约 2 次、每次约 4 小时（示例）：只有这段时间发电机组才要工作
av_rows, u_tot_a, u_tot_m, u_n = [], 0.0, 0.0, 0.0
for i, (nm, n, k, mtbf, mttr) in enumerate(GROUPS):
    ua = (1 - a_analytic(n, k, mtbf, mttr)) * 8760
    um = mc_group(n, k, mtbf, mttr, years=2000000, rng=random.Random(1664 + i))
    un = (1 - a_analytic(k, k, mtbf, mttr)) * 8760
    if nm.startswith("柴油"):
        ua, um, un = ua * p_outage, um * p_outage, un * p_outage
    u_tot_a, u_tot_m, u_tot_n = u_tot_a + ua, u_tot_m + um, u_n + un
    u_n = u_tot_n
    av_rows.append([nm, f"{n} 选 {k}", f"{mtbf:,} h / {mttr} h", f"{ua * 60:.3f} min", f"{um * 60:.3f} min", f"{un * 60:.0f} min"])
avail = 100 * (1 - u_tot_a / 8760)
avail_n = 100 * (1 - u_n / 8760)
d_mc = abs(u_tot_m - u_tot_a) / u_tot_a * 100
simmd = f"""# 仿真：全年逐时 PUE + 可用性

## 1 全年 8760 小时（三个方案同一套气候、同一个负荷 {IT_OP:.0f} kW）

逐时：UPS 效率随负载率、变压器与配电 1.5 %、空气侧风机、冷冻水泵、冷机（COP = 卡诺 × 0.35（风冷直膨）/ 0.55（水冷离心），冷凝温度跟干球或湿球走）、冷却塔与冷却水泵、照明；
方案 C 湿球 ≤ {OPTS['C']['fc_full']:g} ℃ 时冷却塔经板换直接出 {TW_S:g} ℃ 水（冷机停），往上 5 K 部分预冷。

![全年](4_全年PUE.png)

{L.md_table(["方案", "年 PUE", "年用电", "全自然冷却", "部分自然冷却", "最热小时总用电"], [[k + " " + OPTS[k]['name'], f"{ANN[k]['pue']:.3f}", f"{ANN[k]['mwh']:,.0f} MWh", f"{ANN[k]['fc_h']:,} h", f"{ANN[k]['part_h']:,} h", f"{ANN[k]['peak']:.0f} kW"] for k in OPTS])}

方案 C 比 A 一年少用 **{ANN['A']['mwh'] - ANN['C']['mwh']:,.0f} MWh**。最热的 7 月 PUE {pue_m['C'][6]:.3f}，最冷的 1 月 {pue_m['C'][0]:.3f}（自然冷却 {fc_m[0] * 100:.0f} %）。

## 2 可用性：N+1 设备组（MTBF / MTTR 示例值）

每组“n 台里至少 k 台好的”：公式 A = Σ C(n,j)·a^j·(1−a)^(n−j)，a = MTBF/(MTBF + MTTR)；蒙特卡洛按逐次故障、修理的马尔可夫链每组模拟两百万年。

{L.md_table(["设备组", "配置", "MTBF / MTTR", "年停机（公式）", "年停机（蒙特卡洛）", "不冗余时（n = k）"], av_rows)}

合计年停机：公式 {u_tot_a * 60:.2f} 分钟、蒙特卡洛 {u_tot_m * 60:.2f} 分钟（相差 {d_mc:.1f} %）；**可用性 {avail:.4f} %**。
如果都不冗余，年停机 {u_n:.1f} 小时、可用性 {avail_n:.3f} %——N+1 是必须的。（市电由 UPS + 发电机接住；配电、管路按双路 / 环路不算单点。）
"""
case.step("sim", f"全年逐时：方案 C 年 PUE {A_SEL['pue']:.3f}，全自然冷却 {A_SEL['fc_h']:,} 小时；可用性 {avail:.4f} %（公式与蒙特卡洛相差 {d_mc:.0f} %）。",
          f"8760 hours: option C annual PUE {A_SEL['pue']:.3f}, {A_SEL['fc_h']:,} h of full free cooling; availability {avail:.4f} % (formula vs Monte Carlo within {d_mc:.0f} %).",
          md=case.text("4_全年仿真.md", simmd), figs=[("4_全年PUE.png", "气候、逐月 PUE、非 IT 用电", "Climate, monthly PUE, non-IT energy")], tools=tools("energy"),
          facts=[("年 PUE", "Annual PUE", round(A_SEL["pue"], 3), ""), ("自然冷却", "Free cooling", int(A_SEL["fc_h"]), "h"), ("可用性", "Availability", round(avail, 4), "%")])
case.check("sim", "年 PUE（方案 C）", "Annual PUE (option C)", round(A_SEL["pue"], 3), "<=", PUE_REQ, "", "任务书")
case.check("sim", "年可用性", "Annual availability", round(avail, 4), ">=", AVAIL_REQ, "%", "任务书")
case.check("sim", "可用性：蒙特卡洛与公式相差", "Availability: Monte Carlo vs formula", round(d_mc, 1), "<=", 5.0, "%", "核对公式")

# ================================================================ 5 三维与平面图
import build123d as bd  # noqa: E402

A0 = (bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)
RW, RD, RH = 0.6, 1.2, 2.0
hall = bd.Box(12.0, 9.0, 0.05, align=A0)
row_y = (2.2, 5.0)                     # 两排：机柜正面朝中间冷通道
items = []
for r, y0 in enumerate(row_y):
    for i in range(N_RACK // 2):
        x0 = 3.0 + i * RW
        items.append(bd.Pos(x0, y0, 0.05) * bd.Box(RW - 0.01, RD, RH, align=A0))
        door_y = y0 - 0.15 if r == 0 else y0 + RD
        items.append(bd.Pos(x0, door_y, 0.05) * bd.Box(RW - 0.01, 0.15, RH, align=A0))
for x0 in (1.0, 10.0):
    for y0 in row_y:
        items.append(bd.Pos(x0, y0, 0.05) * bd.Box(0.8, RD, RH, align=A0))          # 列头柜
model = hall
for it_ in items:
    model = model + it_
bd.export_step(model, str(case.path("5_机房.step")))
L.render_solid(model, case.path("5_机房三维.png"), elev=32, azim=-62, color=(0.62, 0.68, 0.76), size=(9, 5), swap=False)

fig, ax = plt.subplots(figsize=(9.6, 5.6))
ax.add_patch(plt.Rectangle((0, 0), 12, 9, fc="#f4f6f8", ec=L.INK, lw=1.2))
ax.text(0.2, 8.6, "IT 机房 12 × 9 m", fontsize=9)
for r, y0 in enumerate(row_y):
    for i in range(N_RACK // 2):
        x0 = 3.0 + i * RW
        ax.add_patch(plt.Rectangle((x0, y0), RW - 0.01, RD, fc="#c9d6e4", ec=L.INK, lw=0.5))
        door_y = y0 - 0.15 if r == 0 else y0 + RD
        ax.add_patch(plt.Rectangle((x0, door_y), RW - 0.01, 0.15, fc="#7fb3d5", ec="none"))
    for x0 in (1.0, 10.0):
        ax.add_patch(plt.Rectangle((x0, y0), 0.8, RD, fc="#e9d4d4", ec=L.INK, lw=0.5))
ax.text(6.0, 1.75, "背门换热器（蓝）", ha="center", fontsize=7.5, color=L.ACCENT)
ax.text(6.0, 4.0, "冷通道（机柜正面朝里）", ha="center", fontsize=8)
ax.text(1.4, 3.9, "列头柜", ha="center", fontsize=7)
ax.add_patch(plt.Rectangle((12.4, 0), 6.0, 9, fc="#f8f1e5", ec=L.INK, lw=1.0))
ax.text(15.4, 8.4, "电力室", ha="center", fontsize=9)
for i in range(N_UPS_MOD):
    ax.add_patch(plt.Rectangle((12.9 + i * 0.7, 5.5), 0.6, 1.0, fc="#e2c799", ec=L.INK, lw=0.5))
ax.text(14.3, 6.7, f"UPS {N_UPS_MOD} × 100 kW", ha="center", fontsize=7.5)
for i in range(bat_cab):
    ax.add_patch(plt.Rectangle((12.9 + i * 0.7, 3.6), 0.6, 1.0, fc="#d5e8d4", ec=L.INK, lw=0.5))
ax.text(14.0, 3.2, f"锂电池 {bat_cab} 柜", ha="center", fontsize=7.5)
ax.add_patch(plt.Rectangle((16.4, 3.4), 1.6, 3.2, fc="#e9d4d4", ec=L.INK, lw=0.5))
ax.text(17.2, 5.0, "低压\n配电柜", ha="center", va="center", fontsize=7.5)
ax.add_patch(plt.Rectangle((0, -5.2), 18.4, 4.6, fc="#eef3ea", ec=L.INK, lw=1.0, ls="--"))
ax.text(0.3, -1.1, "室外设备场", fontsize=9)
for i in range(n_ch + 1):
    ax.add_patch(plt.Rectangle((0.8 + i * 2.4, -4.2), 2.0, 1.4, fc="#c9d6e4", ec=L.INK, lw=0.5))
    ax.text(1.8 + i * 2.4, -3.5, f"冷机{i + 1}", ha="center", va="center", fontsize=7)
for i in range(n_ch + 1):
    ax.add_patch(plt.Circle((9.4 + i * 1.9, -3.0), 0.75, fc="#dfe9f3", ec=L.INK, lw=0.5))
    ax.text(9.4 + i * 1.9, -3.0, f"塔{i + 1}", ha="center", va="center", fontsize=7)
ax.add_patch(plt.Rectangle((15.6, -4.6), 2.4, 1.2, fc="#f0e0c0", ec=L.INK, lw=0.5))
ax.text(16.8, -4.0, f"发电机 2 × {gen} kVA", ha="center", va="center", fontsize=7)
ax.add_patch(plt.Rectangle((15.6, -2.9), 2.4, 1.0, fc="#e2e2e2", ec=L.INK, lw=0.5))
ax.text(16.8, -2.4, f"变压器 2 × {tr} kVA", ha="center", va="center", fontsize=7)
ax.set_xlim(-0.5, 18.9)
ax.set_ylim(-5.6, 9.4)
ax.set_aspect("equal")
ax.set_xlabel("m")
ax.set_title("算力中心平面布置（示意）", fontsize=10)
case.fig(fig, "5_平面图.png")
cadmd = f"""# 三维与平面图

![平面](5_平面图.png)

![三维](5_机房三维.png)

- **IT 机房 12 × 9 m**：两排各 {N_RACK // 2} 柜，正面朝中间冷通道（1.6 m），后面是背门换热器和检修通道；两头是列头柜（每排两台，两路供电）。
  背门换热器让机房基本“热中性”，不用封冷 / 热通道；房间里只留两台小空调除湿。
- **温水管**走架空地板下，环形布置（任意一段坏了可以从另一头供水），每柜一对软管快接头 + 关断阀 + 漏水检测绳。
- **电力室**：UPS、锂电池、低压配电；**室外**：{n_ch}+1 台冷机、{n_ch}+1 台冷却塔、板式换热器（自然冷却）、2 台变压器、2 台柴油发电机。

三维模型 `5_机房.step`（机柜、背门换热器、列头柜，示意尺寸）。
"""
case.step("cad", f"IT 机房 12 × 9 m，两排各 {N_RACK // 2} 柜、中间冷通道；温水管环形布置；电力室、室外冷机和冷却塔。",
          f"12 × 9 m IT hall with two rows of {N_RACK // 2} racks facing a cold aisle; warm-water ring under the floor; power room, chillers and towers outdoors.",
          md=case.text("5_三维与平面图.md", cadmd), figs=[("5_平面图.png", "平面布置", "Floor plan"), ("5_机房三维.png", "IT 机房三维", "IT hall 3D")],
          files=[("5_机房.step", "机房三维模型（STEP）", "Hall 3D model (STEP)")])

# ================================================================ 6 工艺：工厂联调 + 现场安装与综合测试
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["WQ-RACK42"][0]]
site = [("场地准备", "架空地板、承重（每柜满装约 900 kg）、排水", "1 周"),
        ("供配电", "变压器、低压柜、UPS、电池、列头柜；绝缘测试、相序", "2 周"),
        ("水系统", "温水环管、冷机、冷却塔、板换；**1.5 倍工作压力保压 30 分钟不降**；冲洗到水质合格", "2 周"),
        ("机柜就位", "整机柜整柜运到（工厂已联调），就位、调平、接地；软管快接、开阀查漏", "2 天"),
        ("综合测试（IST）", "全部服务器满载 24 小时；逐项故障演练：拔一块 UPS 模块、停一台冷机、停一台水泵、断市电让发电机接上——每项都不能有服务器掉电或超温", "1 周")]
procmd = f"""# 工艺：工厂里整柜联调，现场装好再综合测试

## 计算机厂：整机柜

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

16 台服务器（各自已经过 12 小时老化，案例 B）在工厂里上架、布线、接背门换热器的水，**整柜满载联调**：量整柜功率、换热器进出风温差、交换机链路误码，
合格后整柜装木箱发运——现场不再拆装服务器。

## 算力中心现场

{L.md_table(["阶段", "做什么", "工期"], [list(x) for x in site])}
"""
case.step("process", f"工厂整柜联调 {len(rt)} 道；现场五个阶段：场地、供配电、水系统（保压、冲洗）、机柜就位、综合测试（满载 24 小时 + 逐项故障演练）。",
          f"{len(rt)} rack operations in the plant; five site stages: room, power, water (pressure test, flushing), rack placement, integrated systems test (24 h full load + failure drills).",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("现场阶段", "Site stages", len(site), "")])

# ================================================================ 7 制造
sh = L.run_shop("WQ-RACK42", N_RACK, "WO-CASE-PC-C", seed=1663)
meas = sh["measurements"]
rows_q, cpk_min, fails, st = L.shop_table(meas)
pwr = st["rk_power"]
makemd = f"""# 制造：{N_RACK} 台整机柜

计算机厂仿真车间整机柜联调台做 {N_RACK} 台 WQ-RACK42（联调台一台，{sh['hours']:.0f} 小时 ≈ {sh['hours'] / 24:.1f} 天）：

{L.md_table(["特性", "公差", "台数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}**，最低 Cpk {cpk_min:.2f}。整柜满载功率平均 {pwr['mean']:.2f} kW、最大 {max(m['value_mm'] for m in meas if m['characteristic'] == 'rk_power'):.2f} kW，
都在设计 {P_RACK_DES:g} kW 以内——第 3 步的冷量、配电按 {P_RACK_DES:g} kW 算是够的；全年 PUE 按 {P_RACK_OP:g} kW 算也对得上实测。
联调台只有一台，{N_RACK} 柜要 {sh['hours'] / 24:.1f} 天，交付计划要把它排进去（或者加一台联调台）。
"""
case.step("make", f"{N_RACK} 台整机柜：满载功率平均 {pwr['mean']:.2f} kW（设计 {P_RACK_DES:g}），不合格 {fails}，最低 Cpk {cpk_min:.2f}；联调台 {sh['hours'] / 24:.1f} 天。",
          f"{N_RACK} racks: average full-load power {pwr['mean']:.2f} kW (design {P_RACK_DES:g}); {fails} failures, lowest Cpk {cpk_min:.2f}; {sh['hours'] / 24:.1f} days on the test bench.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality", "3d"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ""), ("联调天数", "Bench days", round(sh["hours"] / 24, 1), "d")])
case.check("make", "不合格项", "Failures", fails, "==", 0, "", "整机柜联调")
case.check("make", "最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")
case.check("make", "实测整柜功率最大值", "Largest measured rack power", round(max(m["value_mm"] for m in meas if m["characteristic"] == "rk_power"), 2), "<=", P_RACK_DES, "kW", "第 3 步按设计功率")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **产品决定机房**：每柜 {P_RACK_DES:g} kW、服务器风量（案例 B）决定了背门换热器够不够、水温能多高；水温高，自然冷却小时就多，PUE 才下得来。
2. **PUE 主要看冷机开多久**：方案 C 一年有 {A_SEL['fc_h']:,} 小时冷机不开；剩下的非 IT 用电里 UPS 损耗是大头——UPS 负载率、效率曲线值得算。
3. **冗余靠算，不靠感觉**：N+1 把年停机从 {u_n:.0f} 小时降到 {u_tot_a * 60:.1f} 分钟；公式和蒙特卡洛对上了。
4. **整柜在工厂联调**：现场只接水接电，交付快；但联调台是瓶颈。

## 留给学生的问题

1. 温水从 18/24 ℃ 提到 22/28 ℃：自然冷却小时、PUE 怎么变？服务器进风还能保持 25 ℃ 吗（第 3 步换热器公式）？
2. 把这个算力中心搬到西北（年均温 8 ℃、空气干）：哪个方案最好？
3. 每柜功率升到 40 kW（新一代加速卡）：背门换热器还够吗？要改成什么（提示：冷板液冷）？

相关：案例 A（主板供电）、案例 B（服务器散热）；计算机厂帮助“主板、内存条、结构件与整机柜”；数字工厂“能源与环境”。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；年 PUE {A_SEL['pue']:.3f}、可用性 {avail:.4f} %。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; annual PUE {A_SEL['pue']:.3f}, availability {avail:.4f} %.",
          md=case.text("8_总结.md", review), tools=tools("energy", "quality"))
case.write()
print("ok", {k: round(ANN[k]["pue"], 3) for k in ANN}, A_SEL["fc_h"], A_SEL["part_h"], round(q_rdhx, 1), round(t_out, 1), round(heat_peak), n_ch, tr, gen, bat_cab,
      round(u_tot_a * 60, 3), round(u_tot_m * 60, 3), round(avail, 5), round(u_n, 1), cpk_min)
