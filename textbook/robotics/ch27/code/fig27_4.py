"""27.4 节的示意图。

图 27.4.1：(a) 两指捏住宽 40 mm 的零件（平面），μ = 0.2：两个接触点错开 Δ = 6 mm 时两点的连线在两个摩擦锥内（力封闭），
              错开 10 mm 时在锥外（不是力封闭）；(b) 上下料动作（A → B）中平口与 V 形夹爪所需的最小夹紧力（线性规划，含惯性力），
              细虚线是同一姿态静止时的值；B 点平口夹爪若两端法向力相等（指面均匀压紧）需要的夹紧力。
"""
import math

import numpy as np

from _ch27 import MU_JAW, blank_wrench, cell_move, hand_motion, jaw_contacts, min_grip, quintic, ur_chain
from bookout import COLORS as C, T, figure, style

plt = style()
from matplotlib.patches import Polygon, Rectangle   # noqa: E402

fig, axs = plt.subplots(1, 2, figsize=(12.0, 4.3), gridspec_kw=dict(width_ratios=[1, 1.35]))
ax = axs[0]
w, mu = 40.0, 0.2
for x0, delta, ok in ((0, 6.0, True), (75, 10.0, False)):
    ax.add_patch(Rectangle((x0 - 25, -w / 2), 50, w, fc="#d9dde1", ec=C["ink"], lw=1.2))
    p1, p2 = np.array([x0 - delta / 2, w / 2]), np.array([x0 + delta / 2, -w / 2])
    for p, n in ((p1, np.array([0, -1.0])), (p2, np.array([0, 1.0]))):
        L = 15
        a = math.atan(mu)
        ends = []
        for s in (1, -1):
            d = np.array([n[0] * math.cos(a) - s * n[1] * math.sin(a), s * n[0] * math.sin(a) + n[1] * math.cos(a)])
            ends.append(p + L * d)
            ax.plot([p[0], ends[-1][0]], [p[1], ends[-1][1]], color=C["z"], lw=1.2)
        ax.add_patch(Polygon([p, ends[0], ends[1]], fc=C["z"], alpha=0.15, ec="none"))
        ax.add_patch(Polygon([p + [-5, -n[1] * 0], p + [5, 0], p + [0, -n[1] * 7]], fc="#6b7680", ec=C["ink"]))
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=C["y"] if ok else C["x"], lw=2, ls="-" if ok else "--")
    ax.text(x0, -w / 2 - 12, (T("Δ = {:.0f} mm：力封闭", "Δ = {:.0f} mm: force closure") if ok else
                               T("Δ = {:.0f} mm：不是力封闭", "Δ = {:.0f} mm: no force closure")).format(delta),
            ha="center", fontsize=9.5, color=C["y"] if ok else C["x"])
ax.text(37.5, w / 2 + 14, T(f"μ = {mu}，摩擦锥半顶角 {math.degrees(math.atan(mu)):.1f}°；Δ ≤ μw = {mu * w:.0f} mm",
                            f"μ = {mu}, cone half-angle {math.degrees(math.atan(mu)):.1f}°; Δ ≤ μw = {mu * w:.0f} mm"), ha="center", fontsize=9.5)
ax.set_xlim(-35, 110)
ax.set_ylim(-38, 40)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("(a) 两指对径：连线必须在两个摩擦锥内", "(a) two-finger antipodal grasp: the line must lie in both cones"), fontsize=11)
# (b) 上下料动作
ax = axs[1]
ch = ur_chain()
thA, thB, Tm = cell_move()
ts = np.linspace(0, Tm, 81)
res = {"flat": [], "V": [], "flat0": [], "V0": []}
for t in ts:
    q, qd, qdd = quintic(thA, thB, Tm, t)
    V, Vd = hand_motion(ch, q, qd, qdd)
    V0, Vd0 = hand_motion(ch, q, np.zeros(6), np.zeros(6))
    for jaw in ("flat", "V"):
        res[jaw].append(min_grip(jaw_contacts(jaw), blank_wrench(V, Vd))[0])
        res[jaw + "0"].append(min_grip(jaw_contacts(jaw), blank_wrench(V0, Vd0))[0])
ax.plot(ts, res["flat"], color=C["z"], lw=2, label=T("平口夹爪", "flat jaws"))
ax.plot(ts, res["flat0"], color=C["z"], lw=0.9, ls=":")
ax.plot(ts, res["V"], color=C["accent"], lw=2, label=T("V 形夹爪", "V-jaws"))
ax.plot(ts, res["V0"], color=C["accent"], lw=0.9, ls=":")
VB, VdB = hand_motion(ch, thB, np.zeros(6), np.zeros(6))
Feq = min_grip(jaw_contacts("flat"), blank_wrench(VB, VdB), equal_ends=True)[0]
ax.plot([Tm], [Feq], "s", color=C["x"], ms=7, label=T("B 点平口，两端法向力相等", "flat at B, equal end forces"))
ax.text(0.02, res["flat"][0] + 8, T("A：毛坯竖直", "A: blank vertical"), fontsize=9)
ax.text(Tm - 0.02, res["flat"][-1] - 22, T("B：毛坯水平", "B: blank horizontal"), fontsize=9, ha="right")
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("最小夹紧力 / N", "minimum grip force / N"))
ax.set_title(T(f"(b) 上下料动作中所需的夹紧力（μ = {MU_JAW}）", f"(b) grip force needed along the loading move (μ = {MU_JAW})"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="center left")
ax.grid(alpha=0.25)
ax.set_xlim(0, Tm * 1.02)
ax.set_ylim(0, 270)
fig.tight_layout()
figure(fig, "fig27_4_1")
