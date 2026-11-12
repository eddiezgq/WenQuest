"""第 161d 轮：电机厂案例 C——伺服电机 WQ-SM200 整机：转矩—转速特性、温升（有限元）、轴与轴承、抱闸、三维装配、全工艺路线，出厂 20 台。

    python3 tools/cases/motor_c.py

电磁数据取案例 B（tools/cases/sm200.py + motorlib 有限元）；机壳温升用数字工厂“仿真与分析”的热分析（cae/thermal.py，CalculiX）；
轴承从零件库 A-BRG-DG 选；制造用电机厂仿真车间。输出到 factory/cases/motor/C/。
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
os.environ.setdefault("WQ_CCX_SOLVER", "SPOOLES")

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
import motorlib as ML  # noqa: E402
import sm200 as S  # noqa: E402

TOOLS = {
    "wave": ("电机终检波形", "Motor test waveforms", "/motor-wave"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "cae": ("仿真与分析", "Simulation & analysis", "/cae"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "finance": ("经营与财务", "Business & finance", "/finance"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731
G = dict(S.GEOM)
P = G["p"]
COILS = ML.tooth_winding(G["Q"], P)

case = L.Case("motor", "C", "完整", "伺服电机 WQ-SM200（整机）", "Servo motor WQ-SM200 (complete)", "WQ-SM200",
              "整台 200 W 伺服电机：转矩—转速特性、效率、机壳温升（有限元）、轴与轴承（零件库）、抱闸，三维装配，13 道工序做出 20 台、全部测试项和成本。",
              "The complete 200 W servo motor: torque–speed curve, efficiency, housing temperature rise (FEA), shaft and bearings (parts library), brake, 3D assembly, 13 operations, 20 motors with all tests and cost.",
              "tools/cases/motor_c.py")

# ---------------------------------------------------------------- 电磁（案例 B 的定稿，重算一次磁链）
xy, tris, reg = ML.build_mesh(G, h_gap=0.12, h=1.0)
angs = np.radians(np.linspace(0, 72, 25))
la = []
for a in angs:
    A = ML.solve(xy, tris, reg, a, G, mu_r_iron=S.MU_IRON, Br=S.BR)
    sf, _, _, _ = ML.slot_side_flux(xy, tris, reg, A, G, S.L_STK)
    la.append(ML.phase_flux(sf, COILS, 1)["A"])
la = np.array(la)
lam1 = (la.max() - la.min()) / 2
w_max = S.N_MAX * 2 * math.pi / 60 * P
NC = int(math.floor(0.8 * S.V_DC / (math.sqrt(3) * w_max * lam1)))
psi = lam1 * NC                                       # 每相磁链幅值 Wb
Kt = 1.5 * P * psi
halves = ML.slot_halves(xy, tris, reg, G)
A_half = float(np.mean([h[1] for k in halves for h in k]))
a_wire = S.FILL * A_half / NC
l_turn = 2 * S.L_STK + 2 * (G["bt"] / 1000 + 2 * math.sqrt(A_half) * 0.6)
R_ph = S.RHO_CU * l_turn * NC * 4 / a_wire
# 同步电感：磁钢“关掉”（Br = 0），通三相对称电流 I（A 相峰值），A 相磁链 / I
I_test = 10.0
J_t = ML.current_density(xy, tris, reg, G, COILS, NC, {"A": I_test, "B": -I_test / 2, "C": -I_test / 2})
A_t = ML.solve(xy, tris, reg, 0.0, G, mu_r_iron=S.MU_IRON, Br=0.0, J=J_t)
sf_t, _, _, _ = ML.slot_side_flux(xy, tris, reg, A_t, G, S.L_STK)
Ls = ML.phase_flux(sf_t, COILS, NC)["A"] / I_test               # H（不含端部漏感）

# ================================================================ 1 任务书
brief = f"""# 设计任务书：伺服电机 WQ-SM200

| 项目 | 要求 | 出处 |
|---|---|---|
| 额定 | 200 W、{S.N_RATED:.0f} r/min、{S.T_RATED} N·m；峰值约 3.5 倍（2.23 N·m）；最高 {S.N_MAX:.0f} r/min | 电机选型助手（伺服 200 W） |
| 驱动 | {S.V_DC:g} V 母线、磁场定向控制 | 关节驱动板 DRV-JOINT-B |
| 抱闸 | 失电制动，静态保持力矩 ≥ 额定转矩（终检 0.64–1.4 N·m） | 电机厂终检公差 |
| 温升 | 连续额定、40 ℃ 环境（装在关节模组里），绕组 F 级（155 ℃）留余量 | GB/T 755 绝缘等级 |
| 电磁 | 12 槽 10 极、定子 Ø{2 * G['R_so']:g} × {S.L_STK * 1000:.0f}、每线圈 {NC} 匝 | 案例 A、B |
| 寿命 | 轴承 L₁₀ ≥ 20 000 h（与关节模组同） | 机器人厂案例 B |

**交付物**：特性曲线、温升、轴与轴承校核、三维装配、全工艺路线、首批 20 台的全部测试和成本。
"""
case.step("brief", f"200 W、{S.N_RATED:.0f} r/min、{S.V_DC:g} V；抱闸 ≥ 额定转矩；40 ℃ 环境连续额定；电磁用案例 B 定稿。",
          f"200 W, {S.N_RATED:.0f} rpm, {S.V_DC:g} V; brake ≥ rated torque; continuous rating at 40 °C; electromagnetics from case B.",
          md=case.text("1_任务书.md", brief), tools=tools("engineer"),
          facts=[("额定功率", "Rated power", 200, "W"), ("每线圈匝数", "Turns per coil", NC, ""), ("转矩常数", "Torque constant", Kt, "N·m/A")])

# ================================================================ 2 方案：机壳散热
concept = """# 方案：机壳怎么散热

| 方案 | 说明 | 结论 |
|---|---|---|
| 光机壳、自然冷却 | 铝机壳 60 方，靠外表面对流和辐射；电机装在关节模组里，法兰贴在关节壳体上 | ✓ 选定（第 4 步有限元核对） |
| 机壳加散热筋 | 外形超出 60 方，关节模组里放不下 | ✗ |
| 风扇 | 协作机器人关节是封闭的，没地方装 | ✗ |

所以温升只能靠**降低损耗**（案例 B 把电流密度降到 7 A/mm² 就是为了这个）和**机壳散热面积**。
"""
case.step("concept", "关节模组里装不下散热筋和风扇：光铝机壳自然冷却，靠低损耗和机壳面积。",
          "No room for fins or a fan inside the joint: plain aluminium housing with natural cooling, relying on low loss and housing area.",
          md=case.text("2_方案.md", concept), tools=tools("engineer"), facts=[("冷却", "Cooling", "自然冷却", "")])

# ================================================================ 3 计算：特性曲线、效率、轴承、抱闸
Vph_max = S.V_DC / math.sqrt(3)                        # 正弦调制下相电压峰值上限（SVPWM）
I_pk_max = 2.23 / Kt
n_list = np.linspace(0, S.N_MAX, 61)
T_curve = []
for n in n_list:
    we = n * 2 * math.pi / 60 * P
    # 电压限：√((R i_q + ω_e ψ)² + (ω_e L i_q)²) ≤ V_ph,max（q 轴电流、不弱磁）
    Iv = 0.0
    if we > 0:
        lo, hi = 0.0, I_pk_max
        for _ in range(40):
            mid = (lo + hi) / 2
            v = math.hypot(R_ph * mid + we * psi, we * Ls * mid)     # q 轴电流：v_q = R i_q + ω_e ψ，v_d = −ω_e L i_q
            lo, hi = (mid, hi) if v <= Vph_max else (lo, mid)
        Iv = lo
    else:
        Iv = I_pk_max
    T_curve.append(Kt * min(I_pk_max, Iv))
T_curve = np.array(T_curve)
I_rated = S.T_RATED / Kt
P_cu = 1.5 * I_rated ** 2 * R_ph
eta = 200.0 / (200.0 + P_cu)
# 轴承：零件库 A-BRG-DG 608（d 8，D 22，B 7，C 来自零件库）
brg = L.lib_part("A-BRG-DG", "608")
Cr = float(brg["row"]["Cr_kN"]) * 1e3
m_rot = math.pi * ((G["R_si"] - G["gap"]) ** 2 - G["R_shaft"] ** 2) * 1e-6 * S.L_STK * 7650   # 转子铁心 + 磁钢（密度取 7.65 g/cm³ 量级）
F_belt = 0.0                                            # 直接带谐波减速器，没有皮带拉力
F_r = m_rot * 9.81 / 2 + 20.0                           # 每只轴承：自重一半 + 预紧弹簧片的径向分量（示例 20 N）
L10 = (Cr / (1.2 * F_r)) ** 3 * 1e6 / (60 * S.N_RATED)
brake_min = 0.64
calcmd = f"""# 计算：特性、效率、轴承、抱闸

## 电参数（由案例 B 的有限元）

每相磁链幅值 ψ = {psi * 1e3:.2f} mWb（每线圈 {NC} 匝），K_t = 1.5 p ψ = {Kt:.4f} N·m/A；相电阻（100 ℃）{R_ph * 1000:.0f} mΩ；同步电感（有限元，磁钢置零、通三相电流）{Ls * 1e6:.0f} μH（不含端部漏感）。

## 转矩—转速特性（{S.V_DC:g} V 母线，q 轴电流、不弱磁）

相电压峰值上限 V_dc/√3 = {Vph_max:.1f} V；峰值电流 {I_pk_max:.1f} A（峰值转矩 2.23 N·m）。转速升高后反电势吃掉电压，电流被电压限住：
{S.N_MAX:.0f} r/min 时还能出 **{T_curve[-1]:.2f} N·m**（额定 {S.T_RATED}），满足最高转速下带额定转矩。

## 效率（额定点，只计铜耗）

铜耗 1.5 I² R = **{P_cu:.1f} W**，η ≈ 200 / (200 + {P_cu:.1f}) = {eta:.1%}。铁耗、机械损耗还要加几瓦，这台示例设计没有硅钢片的损耗曲线，**铁耗没有算**（实测在终检台的空载电流里）。

## 轴承（零件库 `A-BRG-DG/608`，d 8 × D 22 × B 7，C = {Cr / 1e3:.2f} kN，零件库数据来源 SKF）

转子质量约 {m_rot:.2f} kg；电机直连谐波减速器，没有皮带拉力；每只轴承径向载荷 ≈ {F_r:.0f} N（含预紧）。L₁₀ ≈ **{L10:,.0f} h**。

## 抱闸

静态保持力矩下限 {brake_min} N·m ≥ 额定转矩 {S.T_RATED} N·m（断电时能抱住额定负载）。
"""
case.step("calc", f"K_t {Kt:.4f}；{S.N_MAX:.0f} r/min 仍出 {T_curve[-1]:.2f} N·m；额定铜耗 {P_cu:.1f} W、效率约 {eta:.0%}（未计铁耗）；608 轴承 L₁₀ {L10:,.0f} h。",
          f"K_t {Kt:.4f}; {T_curve[-1]:.2f} N·m still available at {S.N_MAX:.0f} rpm; rated copper loss {P_cu:.1f} W, efficiency about {eta:.0%} (iron loss not included); 608 bearings L₁₀ {L10:,.0f} h.",
          md=case.text("3_计算.md", calcmd), tools=tools("engineer") + L.lib_tools([brg]),
          facts=[("最高转速转矩", "Torque at max speed", T_curve[-1], "N·m"), ("铜耗", "Copper loss", P_cu, "W"), ("轴承寿命", "Bearing life", L10, "h")])
case.check("calc", "最高转速时可用转矩不低于额定", "Torque at max speed ≥ rated", T_curve[-1], ">=", S.T_RATED, "N·m", "任务书")
case.check("calc", "轴承寿命", "Bearing life", L10, ">=", 20000, "h", "ISO 281；零件库 608")
case.check("calc", "抱闸保持力矩下限不低于额定转矩", "Brake minimum ≥ rated torque", brake_min, ">=", S.T_RATED, "N·m", "任务书")

# ================================================================ 4 仿真：特性曲线图 + 机壳温升（有限元）
fig, ax = plt.subplots(figsize=(7.6, 3.2))
ax.plot(n_list, T_curve, color=L.ACCENT, lw=1.6, label="峰值（电压、电流限）")
ax.axhline(S.T_RATED, color=L.MUTED, ls="--", lw=0.8)
ax.text(100, S.T_RATED + 0.05, "额定 0.637 N·m", fontsize=8.5, color=L.MUTED)
ax.set_xlabel("转速 / r/min")
ax.set_ylabel("转矩 / N·m")
ax.set_ylim(0, 2.5)
case.fig(fig, "4_转矩转速.png")
import build123d as bd  # noqa: E402
from cae import geometry as GE, materials as MA, thermal as TH  # noqa: E402

L_house = S.L_STK * 1000 + 45                           # 机壳长：铁心 + 端部绕组 + 轴承座（不含抱闸、编码器段）
house = bd.Box(60, 60, L_house, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)) - bd.Cylinder(G["R_so"], L_house - 8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
bd.export_step(house, str(case.path("_house.step")))
step_bytes = case.path("_house.step").read_bytes()
os.remove(case.path("_house.step"))
faces, _, _ = GE.faces(step_bytes)
inner = [f["id"] for f in faces if f["kind"] != "plane" and abs(math.hypot(f["center"][0], f["center"][1])) < G["R_so"] + 0.5 and f["center"][2] < L_house - 8.5]
inner += [f["id"] for f in faces if f["kind"] == "plane" and abs(f["center"][2] - (L_house - 8)) < 1e-3]
outer = [f["id"] for f in faces if f["id"] not in inner]
H_CONV, T_AMB = 10.0, 40.0
setup = {"analysis": "thermal", "material": MA.get("6061-T6"),
         "thermal": [{"type": "heat_flux", "faces": inner, "power_w": round(P_cu, 2)}, {"type": "convection", "faces": outer, "h_w_m2k": H_CONV, "t_inf_c": T_AMB}],
         "mesh": {"size_mm": 4.0}}
st, surf, _ = TH.solve(step_bytes, setup)
A_out = (4 * 60 * L_house + 2 * 60 * 60) * 1e-6
T_formula = T_AMB + P_cu / (H_CONV * A_out)
T_wind = st["t_max_c"] + 15.0                           # 绕组比机壳内壁高约 15 K（槽绝缘、浸漆的热阻，示例）
simmd = f"""# 仿真：特性曲线与机壳温升

## 转矩—转速特性

见图：低速段受电流限（峰值 2.23 N·m），高速段受 48 V 电压限往下掉，{S.N_MAX:.0f} r/min 时 {T_curve[-1]:.2f} N·m。

## 机壳温升（数字工厂“仿真与分析”的热分析，CalculiX）

铝机壳 60 × 60 × {L_house:.0f} mm，内孔 Ø{2 * G['R_so']:g}（定子热套在里面）；铜耗 {P_cu:.1f} W 从内孔面进，外表面按 h = {H_CONV:g} W/(m²·K)（自然对流加辐射的量级）向 {T_AMB:g} ℃ 散热，
法兰贴关节壳体那面也按对流算（偏保守）。

| 量 | 有限元 | 公式 t = t₀ + P/(hA) |
|---|---|---|
| 机壳外表面平均 | {st['t_surface_mean_c']:.1f} ℃ | {T_formula:.1f} ℃ |
| 机壳最高 | {st['t_max_c']:.1f} ℃ | — |

绕组比机壳内壁再高约 15 K（槽绝缘、浸漆的热阻，示例值）：绕组约 **{T_wind:.0f} ℃**，F 级绝缘 155 ℃，余量充足。
铁耗没算、关节里空气不流通——实测以负载跑合台（机器人厂实验 28）上的温度为准。
"""
case.step("sim", f"特性曲线：{S.N_MAX:.0f} r/min 仍有 {T_curve[-1]:.2f} N·m；机壳有限元 {st['t_surface_mean_c']:.0f} ℃（公式 {T_formula:.0f} ℃），绕组约 {T_wind:.0f} ℃。",
          f"Torque–speed: {T_curve[-1]:.2f} N·m still at {S.N_MAX:.0f} rpm; housing FEA {st['t_surface_mean_c']:.0f} °C (formula {T_formula:.0f} °C), winding about {T_wind:.0f} °C.",
          md=case.text("4_特性与温升.md", simmd), figs=[("4_转矩转速.png", "转矩—转速特性（48 V）", "Torque–speed curve (48 V)")], tools=tools("cae", "wave"),
          facts=[("机壳温度", "Housing temp.", st["t_surface_mean_c"], "℃"), ("绕组温度", "Winding temp.", T_wind, "℃")])
case.check("sim", "机壳温度：有限元与公式相差", "Housing temperature: FEA vs formula", abs(st["t_surface_mean_c"] - T_formula), "<=", 5.0, "K", "核对有限元")
case.check("sim", "绕组温度（F 级 155 ℃ 留 25 K）", "Winding temperature (class F with 25 K margin)", T_wind, "<=", 130.0, "℃", "GB/T 755")

# ================================================================ 5 三维装配
A0 = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
polys = G["_polys"]
lam = bd.Face(bd.Wire.make_circle(G["R_so"])) - bd.Face(bd.Wire.make_circle(G["R_si"]))
for pl in polys:
    lam = lam - bd.Face(bd.Wire.make_polygon([bd.Vector(float(x), float(y), 0) for x, y in pl], close=True))
z0 = 12.0
stator = bd.Pos(0, 0, z0) * bd.extrude(lam, amount=S.L_STK * 1000)
r_m = G["R_si"] - G["gap"]
magnets = bd.Pos(0, 0, z0) * (bd.Cylinder(r_m, S.L_STK * 1000, align=A0) - bd.Cylinder(r_m - G["t_m"], S.L_STK * 1000, align=A0))
rotor = bd.Pos(0, 0, z0) * (bd.Cylinder(r_m - G["t_m"], S.L_STK * 1000, align=A0) - bd.Cylinder(G["R_shaft"], S.L_STK * 1000, align=A0))
shaft = bd.Pos(0, 0, -25) * bd.Cylinder(G["R_shaft"], L_house + 45, align=A0)
b_d, b_D, b_B = (float(brg["row"][k]) for k in ("d_mm", "D_mm", "B_mm"))
bearings = [bd.Pos(0, 0, z) * (bd.Cylinder(b_D / 2, b_B, align=A0) - bd.Cylinder(b_d / 2, b_B, align=A0)) for z in (2.0, L_house - 10)]
brake = bd.Pos(0, 0, L_house + 2) * (bd.Cylinder(26, 14, align=A0) - bd.Cylinder(G["R_shaft"], 14, align=A0))
enc = bd.Pos(0, 0, L_house + 18) * bd.Cylinder(24, 12, align=A0)
cut = bd.Pos(0, 40, L_house / 2 + 20) * bd.Box(80, 80, L_house + 120)
housing = house - cut
asm = bd.Compound([housing, stator - cut, magnets - cut, rotor - cut, shaft, brake - cut, enc - cut] + [b - cut for b in bearings])
bd.export_step(bd.Compound([house, stator, magnets, rotor, shaft, brake, enc] + bearings), str(case.path("WQ-SM200.step")))
L.render_solid(asm, case.path("5_三维剖视.png"), elev=20, azim=-35, size=(6.4, 5.6), swap=False)
LIBP = [brg, L.lib_part("A-SCR-SHC", "M4x12")]
cadmd = f"""# 三维装配

从输出端起：轴伸 Ø{2 * G['R_shaft']:g} → 前轴承 608 → 定子（Ø{2 * G['R_so']:g} × {S.L_STK * 1000:.0f}，热套在铝机壳里）、转子（10 块磁钢表贴）→ 后轴承 608 → 失电制动器 → 编码器。
机壳 60 × 60 × {L_house:.0f}（不含抱闸、编码器段）。

## 用到的零件库零件

{L.lib_md(LIBP, {"A-BRG-DG/608": "前、后轴承（物料 BRG-M）", "A-SCR-SHC/M4x12": "端盖联接（物料 SCR-M4）"})}

电机厂物料清单里轴承还写着“BRG-M 电机轴承（型号待确认）”——本案例按零件库定为 608，清单要跟着更新。
"""
case.step("cad", f"机壳 60 × 60 × {L_house:.0f}；定子、转子、磁钢、两只 608（零件库）、抱闸、编码器；物料清单的“BRG-M 待确认”定为 608。",
          f"Housing 60 × 60 × {L_house:.0f}; stator, rotor, magnets, two 608 bearings (library), brake, encoder; BOM item “BRG-M (TBD)” set to 608.",
          md=case.text("5_三维装配.md", cadmd), figs=[("5_三维剖视.png", "WQ-SM200 三维剖视", "WQ-SM200 3D cut-away")],
          files=[("WQ-SM200.step", "整机 STEP", "Motor (STEP)")], tools=L.lib_tools(LIBP), facts=[("机壳长", "Housing length", L_house, "mm")])

# ================================================================ 6 工艺：全路线
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["WQ-SM200"][0]]
procmd = f"""# 工艺：全工艺路线

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

单件工时合计 {sum(m for _, m in rt)} 分钟，其中浸漆烘干 180 分钟一炉 24 只，摊到每只 7.5 分钟——真正卡产能的是绕线（实验 42）。
"""
case.step("process", f"{len(rt)} 道工序；浸漆一炉 24 只，瓶颈在绕线。", f"{len(rt)} operations; varnish 24 per batch, winding is the bottleneck.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt), "")])

# ================================================================ 7 制造：20 台
from hub import mrp  # noqa: E402

sh = L.run_shop("WQ-SM200", 20, "WO-CASE-MT-C", seed=363)
rows_q, cpk_min, fails, st2 = L.shop_table(sh["measurements"])
mc, oc = mrp.std_unit_cost("WQ-SM200")
makemd = f"""# 出厂 20 台

电机厂仿真车间 20 台 WQ-SM200 一张工单，从来料检验到包装用 {sh['hours']:.1f} 小时；定子测试台、动平衡机、抱闸测试台、终检台的全部测量：

{L.md_table(["特性", "公差", "件数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}** 个，最低 Cpk {cpk_min:.2f}。标准成本：材料 ${mc:.2f} + 加工 ${oc:.2f} = **${mc + oc:.2f} / 台**。
机器人厂按这个价向电机厂买（WQJ-M 的 MTR-SV-200）。
"""
case.step("make", f"20 台、{len(sh['measurements'])} 个测量值，不合格 {fails} 个，最低 Cpk {cpk_min:.2f}；标准成本 ${mc + oc:.2f}/台。",
          f"20 motors, {len(sh['measurements'])} measurements, {fails} out of tolerance, lowest Cpk {cpk_min:.2f}; standard cost ${mc + oc:.2f}.",
          md=case.text("7_出厂.md", makemd), tools=tools("planner", "operator", "quality", "wave", "finance"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", cpk_min, ""), ("标准成本", "Standard cost", f"${mc + oc:.2f}", "")])
case.check("make", "20 台测量不合格数", "Failures in 20 motors", fails, "==", 0, "", "各测试台")
case.check("make", "最低过程能力 Cpk", "Lowest Cpk", cpk_min, ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

## 整机的结论

1. **48 V 母线定了转矩常数**：{S.N_MAX:.0f} r/min 刚好还能出额定转矩，再高就要弱磁。
2. **散热只能靠低损耗**：关节里装不下散热筋和风扇；案例 B 把电流密度降到 7 A/mm²，温升才够用。
3. **物料清单要更新**：BRG-M 定为零件库的 608。
4. 铁耗没算（没有硅钢片损耗数据），实测看终检的空载电流。

## A、B、C 连起来看

A 定槽极和绕组 → B 定铁心、磁钢和匝数（第一版饱和、改了一次）→ C 做成整机、算温升和特性、出厂。

## 留给学生的问题

1. 母线改 24 V：匝数、电流、温升怎样变？
2. 用弱磁把最高转速提到 8000 r/min，需要多大的 d 轴电流？
3. 机壳外表面 h 从 10 降到 6（关节里空气更不流动），绕组温度多少？

相关：电机厂帮助；实验 35、42；机器人厂案例 A、B（这台电机装在 WQJ-M 里）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；48 V 定 K_t、散热靠低损耗、轴承定为零件库 608。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; 48 V sets K_t, cooling relies on low loss, bearing set to library 608.",
          md=case.text("8_总结.md", review), tools=tools("wave"))
case.write()
