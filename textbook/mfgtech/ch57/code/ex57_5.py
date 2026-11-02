"""算例 57.5.1–57.5.3：SH-101 车削切削用量的确定与校核。
57.5.1 粗车（工序 20，ap 2.5、f 0.3、vc 120）：切削功率（Kienzle，hub/process.cutting_power_kw）与数控车床 CNC-L01 的功率；
57.5.2 半精车轴承位（工序 30，两顶尖，Ø25.4）：粗糙度（残留面积，hub/surface.ra_theory）、让刀引起的直径误差（第 54 章 hub/accuracy，
        头架、尾座 20 000 N/mm，刀架 50 000 N/mm）、刀具寿命（扩展泰勒公式 vc·T^0.25·f^0.35 = C，C 按刀具卡的寿命 20 min 标定，示意），
        在 f–vc 平面上画出可行域，看工艺规程选的点（f 0.15、vc 150）在哪里；
57.5.3 背吃刀量的选择：半精车单边余量 0.45–0.58 一刀切完。画图 57.5.2、57.5.3。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

P = M.plan101()
A = M.acc()
S = M.surf()
PR = M.proc()
o20, o30 = M.op(P, 20), M.op(P, 30)
c20, c30 = o20["cut"], o30["cut"]
mat = P["material"]
P20, Fc20, cite = PR.cutting_power_kw(mat, c20)
pw, eta = PR.WORKCENTER_POWER[o20["workstation"]]
P30, Fc30, _ = PR.cutting_power_kw(mat, {"vc_m_min": 150, "f_mm_r": 0.15, "ap_mm": 0.55})
# 半精车轴承位：两顶尖，L = 136，刀具在右轴承位中点 x = 127.5，工件按 Ø25 计（右侧短悬伸，最细处）
L, x, d = 136.0, 127.5, 25.4
kh = kt = 20000.0
kk = 50000.0
comp = A.compliance_between_centers(x, L, d, kh, kt, kk)["total"]
comp_mid = A.compliance_between_centers(L / 2, L, 25.0, kh, kt, kk)["total"]
r_nose = 0.4
RA_MAX = 3.2
TOL30 = 0.05
C_TAYLOR = 150 * 20 ** 0.25 * 0.15 ** 0.35            # vc·T^0.25·f^0.35 = C：按 vc 150、f 0.15 时刀刃寿命 20 min 标定（示意）
T_MIN = 15.0


def life(vc, f):
    return (C_TAYLOR / (vc * f ** 0.35)) ** 4


def dd(f, ap=0.55):
    """让刀引起的直径误差（mm）：2·Fp·柔度。"""
    return 2 * A.kienzle_turning(ap, f)["Fp"] * comp


f_ra = S.feed_for_ra(RA_MAX, r_nose)
fs = np.linspace(0.05, 0.4, 300)
f_dd = max(f for f in fs if dd(f) <= TOL30 / 3)            # 让刀误差不超过工序公差的 1/3
vc_life = lambda f: C_TAYLOR / (f ** 0.35 * T_MIN ** 0.25)  # noqa: E731  寿命不小于 15 min 的最高切削速度

plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.0))
F, V = np.meshgrid(np.linspace(0.05, 0.4, 200), np.linspace(60, 260, 200))
ok = (F <= f_ra) & (F <= f_dd) & (V <= vc_life(F))
ax.contourf(F, V, ok, levels=[0.5, 1.5], colors=[M.GREEN], alpha=0.18)
ax.axvline(f_ra, color=M.WARM, lw=1.2); ax.text(f_ra - 0.004, 245,  T(f"Ra ≤ 3.2：f ≤ {f_ra:.2f}", f"Ra ≤ 3.2: f ≤ {f_ra:.2f}"), fontsize=7, color=M.WARM, ha="right")
ax.axvline(f_dd, color=M.ACCENT, lw=1.2, ls="--"); ax.text(f_dd + 0.004, 225, T(f"让刀 ≤ 公差/3：f ≤ {f_dd:.2f}", f"deflection: f ≤ {f_dd:.2f}"), fontsize=7, color=M.ACCENT)
ax.plot(fs, [vc_life(f) for f in fs], color=M.RED, lw=1.2); ax.text(0.3, vc_life(0.3) + 6, T("刀具寿命 ≥ 15 min", "tool life ≥ 15 min"), fontsize=7, color=M.RED)
for k in (0.06, 0.1, 0.16):
    ff = np.linspace(0.06, 0.4, 100)
    ax.plot(ff, 19 * math.pi * 26.5 / (1000 * k * ff), color=M.MUTED, lw=0.6, ls=":")
    fk = 19 * math.pi * 26.5 / (1000 * k * 70)
    if fk < 0.39:
        ax.text(fk + 0.003, 72, T(f"机动 {k:g} min", f"{k:g} min"), fontsize=6, color=M.MUTED)
ax.plot(0.15, 150, "o", color=M.INK, ms=5); ax.text(0.155, 140, T("工艺规程：f 0.15、vc 150", "plan: f 0.15, vc 150"), fontsize=7)
ax.set_xlim(0.05, 0.4); ax.set_ylim(60, 260)
ax.set_xlabel(T("进给量 f / (mm/r)", "feed f / (mm/r)")); ax.set_ylabel(T("切削速度 vc / (m/min)", "cutting speed vc / (m/min)"))
ax.grid(lw=0.3, alpha=0.4)
figure(fig, "fig57_5_2")

# 图 57.5.3：粗车的功率、力随背吃刀量
aps = np.linspace(0.5, 5, 50)
fig, ax = plt.subplots(figsize=(5.4, 2.4))
pp = [PR.cutting_power_kw(mat, {"vc_m_min": 120, "f_mm_r": 0.3, "ap_mm": a})[0] for a in aps]
ax.plot(aps, pp, color=M.ACCENT, lw=1.4, label=T("f 0.3", "f 0.3"))
pp2 = [PR.cutting_power_kw(mat, {"vc_m_min": 120, "f_mm_r": 0.4, "ap_mm": a})[0] for a in aps]
ax.plot(aps, pp2, color=M.WARM, lw=1.2, label=T("f 0.4", "f 0.4"))
ax.axhline(pw * eta, color=M.RED, ls="--", lw=0.9); ax.text(0.6, pw * eta + 0.3, T(f"主电机 {pw:g} kW × 效率 {eta:g}", f"motor {pw:g} kW × {eta:g}"), fontsize=7, color=M.RED)
ax.plot(c20["ap_mm"], P20, "o", color=M.INK, ms=4); ax.text(c20["ap_mm"] + 0.1, P20 - 0.9, T("工艺规程", "plan"), fontsize=7)
ax.set_xlabel(T("背吃刀量 ap / mm（vc 120 m/min）", "depth of cut ap / mm (vc 120)")); ax.set_ylabel(T("切削功率 / kW", "cutting power / kW"))
ax.grid(lw=0.3, alpha=0.4); ax.legend(fontsize=7, loc="upper left"); ax.set_ylim(0, 12)
figure(fig, "fig57_5_3")

ap_max = max(a for a in np.linspace(0.5, 10, 951) if PR.cutting_power_kw(mat, {"vc_m_min": 120, "f_mm_r": 0.3, "ap_mm": a})[0] <= pw * eta)
out(P20=P20, Fc20=Fc20, pw=pw, eta=eta, P_avail=pw * eta, ap_max=ap_max, P30=P30, Fc30=Fc30, cite=cite,
    f_ra=f_ra, ra_plan=S.ra_theory(0.15, r_nose), r_nose=r_nose, f_dd=f_dd, dd_plan=dd(0.15), comp=comp * 1000, comp_mid=comp_mid * 1000,
    Fp_plan=A.kienzle_turning(0.55, 0.15)["Fp"], life_plan=life(150, 0.15), life_rough=life(120, 0.3), vc_life_plan=vc_life(0.15),
    C_taylor=C_TAYLOR, ap_semi_min=(26.3 - 25.4) / 2, ap_semi_max=(26.5 - 25.35) / 2, kh=kh, kk=kk)
