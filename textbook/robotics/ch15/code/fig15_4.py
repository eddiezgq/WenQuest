"""15.4 节的示意图。

图 15.4.1：Panda 的关节限位（算例 15.4.1）。(a) 四种做法所得的关节角在各自限位区间中的位置（0 为下限，1 为上限）；
           (b) 60 个目标上四种做法的成功率（收敛且在限位以内），以及再加 5 个随机起点后的成功率。
图 15.4.2：平面 3R 臂的两个任务（算例 15.4.2）。(a) 加权最小二乘与任务优先级的最终形态、可行朝向的范围；
           (b) 迭代过程中的位置误差与工具朝向。
数据与 ex15_4.py 相同（重算一遍）。
"""
import math

import numpy as np

from _fig15 import C, arc, arm_pts, base_mark, draw_arm, plane
import bookout
from bookout import T, figure, style
import contextlib
import io
import os
import runpy

plt = style()
_env = os.environ.pop("WQ_BOOK_OUT", None)                                  # 重算 ex15_4.py，但不把它的数交给正文
with contextlib.redirect_stdout(io.StringIO()):
    E = runpy.run_path("ex15_4.py")
bookout._values.clear()
if _env is not None:
    os.environ["WQ_BOOK_OUT"] = _env
lo, hi, Q, qt = E["lo"], E["hi"], E["Q"], E["qt"]
wrap_into = E["wrap_into"]

# ---------------------------------------------------------------- 图 15.4.1
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.4), gridspec_kw={"width_ratios": [1.35, 1]})
ax = axs[0]
ax.axhspan(0, 1, color="#e8f1fa", zorder=0)
ax.axhline(0, color=C["muted"], lw=0.8)
ax.axhline(1, color=C["muted"], lw=0.8)
marks = [("free", "o", C["x"], T("不管限位（加减 360° 后）", "ignore limits (after ±360°)")),
         ("clamp", "s", C["accent"], T("每步截断（未收敛）", "clip each step (not converged)")),
         ("center", "^", "#6baed6", T("零空间居中", "null-space centring")),
         ("box", "D", C["z"], T("有界的一步", "bounded step"))]
x = np.arange(1, 8)
for k, (m, mk, c, lab) in enumerate(marks):
    y = (wrap_into(Q[m]) - lo) / (hi - lo)
    ax.plot(x + (k - 1.5) * 0.13, y, mk, color=c, ms=6, label=lab, zorder=3)
ax.plot(x, (qt - lo) / (hi - lo), "_", color=C["ink"], ms=16, mew=1.6, label=T("生成目标所用的关节角", "joint angles that generated the target"), zorder=2)
ax.set_xticks(x)
ax.set_xticklabels([T(f"关节 {i}", f"joint {i}") for i in x], fontsize=9)
ax.set_ylabel(T("(θ − 下限) / (上限 − 下限)", "(θ − lower) / (upper − lower)"))
ax.set_ylim(-0.45, 1.75)
ax.text(0.45, 0.5, T("允许\n范围", "allowed"), va="center", ha="center", fontsize=8.5, color=C["z"])
ax.set_xlim(0.2, 7.5)
ax.legend(fontsize=8, frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.1))
ax.set_title(T("(a) 算例 15.4.1：各关节在限位中的位置", "(a) Example 15.4.1: each joint within its limits"), fontsize=10, loc="left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax = axs[1]
names = [T("不管限位", "ignore"), T("截断", "clip"), T("零空间居中", "null-space"), T("有界的一步", "bounded")]
vals = [E["pct"](E["inl"][m]) for m in ("free", "clamp", "center", "box")]
cols = [C["x"], C["accent"], "#6baed6", C["z"]]
xb = np.arange(4)
ax.bar(xb, vals, color=cols, width=0.6)
for i, v in enumerate(vals):
    ax.text(i, v + 2, f"{v:.0f}%", ha="center", fontsize=9)
rr = [None, E["pct"](E["restart"]["clamp"]), None, E["pct"](E["restart"]["box"])]
for i, v in enumerate(rr):
    if v is not None:
        ax.bar(i, v - vals[i], bottom=vals[i], color=cols[i], alpha=0.3, width=0.6, hatch="//", edgecolor=cols[i], lw=0)
        ax.text(i, v + 2, f"{v:.0f}%", ha="center", fontsize=9, color=C["muted"])
ax.set_xticks(xb)
ax.set_xticklabels(names, fontsize=9)
ax.set_ylim(0, 112)
ax.set_ylabel(T("收敛且在限位以内的目标 / %", "targets solved within limits / %"))
ax.set_title(T("(b) 60 个目标，从 ready 姿态出发", "(b) 60 targets, starting from ready"), fontsize=10, loc="left")
ax.text(3.35, 104, T("斜线：再加 5 个随机起点", "hatched: plus 5 random starts"), fontsize=8, color=C["muted"], ha="right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
figure(fig, "fig15_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 15.4.2
PL = E["PL"]
pd, phi_lo, phi_hi, phi_d = E["pd"], E["phi_lo"], E["phi_hi"], E["phi_d"]
thp, thw = E["thp"], E["thw"]
hp, hw = E["hp"], E["hw"]
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.6), gridspec_kw={"width_ratios": [1.15, 1]})
ax = axs[0]
plane(ax, (-0.08, 1.0), (-0.85, 0.45))
R = PL[0] + PL[1]
arc(ax, (0, 0), R, -0.15, 0.55, C["muted"], lw=0.9, ls=":")
ax.text(R * math.cos(0.5) + 0.02, R * math.sin(0.5), T("2R 外圆 r = l₁ + l₂", "2R outer circle r = l₁ + l₂"), fontsize=8.5, color=C["muted"], ha="left")
base_mark(ax)
draw_arm(ax, arm_pts(thw, PL), C["accent"], lw=5, alpha=0.9)
draw_arm(ax, arm_pts(thp, PL), C["z"], lw=4)
ax.plot(*pd, "o", color=C["x"], ms=5, zorder=8)
ax.text(-0.06, 0.42, T("黄：加权最小二乘（w = 0.1 m/rad）\n蓝：任务优先级", "gold: weighted least squares (w = 0.1 m/rad)\nblue: task priority"), fontsize=9, color=C["ink"], va="top")
box = (pd[0] - 0.16, pd[0] + 0.1, pd[1] - 0.1, pd[1] + 0.17)
ins = ax.inset_axes([0.36, 0.0, 0.64, 0.56], transform=ax.transAxes)
ins.set_facecolor("white")
ins.set_zorder(20)
ins.set_aspect("equal", adjustable="box")
ins.set_xticks([])
ins.set_yticks([])
for sp in ins.spines.values():
    sp.set_color(C["muted"])
    sp.set_linewidth(0.7)
ins.set_xlim(box[0], box[1])
ins.set_ylim(box[2], box[3])
t = np.linspace(0, 2 * math.pi, 400)
bt = math.atan2(pd[1], pd[0])
ok = np.cos(t - bt) >= math.cos(phi_hi - bt) - 1e-12
wc = np.c_[pd[0] - PL[2] * np.cos(t), pd[1] - PL[2] * np.sin(t)]
ins.plot(*np.where(ok[:, None], wc, np.nan).T, color=C["z"], lw=1.0, alpha=0.6)
ins.plot(*np.where(~ok[:, None], wc, np.nan).T, color=C["x"], lw=1.0, ls="--", alpha=0.6)
tt = np.linspace(-0.4, 0.4, 100)
ins.plot(R * np.cos(tt), R * np.sin(tt), color=C["muted"], lw=0.9, ls=":")
draw_arm(ins, arm_pts(thw, PL), C["accent"], lw=6, alpha=0.9, jr=0.006)
draw_arm(ins, arm_pts(thp, PL), C["z"], lw=5, jr=0.006)
ins.plot(*pd, "o", color=C["x"], ms=6, zorder=8)
ins.annotate("", xy=pd + 0.09 * np.array([math.cos(phi_d), math.sin(phi_d)]), xytext=pd,
             arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.2, ls="--", mutation_scale=10), zorder=9)
ins.text(pd[0] - 0.155, pd[1] + 0.148, T(r"要求的朝向 $\varphi_d$ = 160°", r"required $\varphi_d$ = 160°"), fontsize=8.5, color=C["x"])
ins.text(pd[0] - 0.155, pd[1] + 0.105, T("腕点圆：实线可行，\n虚线超出外圆", "wrist circle: solid feasible,\ndashed outside"), fontsize=8, color=C["z"])
ins.text(pd[0] + 0.005, pd[1] + 0.115, T(f"优先级：φ = {math.degrees(E['phip']):.1f}°\n加权：φ = {math.degrees(E['phiw']):.1f}°", f"priority: φ = {math.degrees(E['phip']):.1f}°\nweighted: φ = {math.degrees(E['phiw']):.1f}°"), fontsize=8.5, color=C["ink"])
ax.indicate_inset_zoom(ins, edgecolor=C["muted"])
ax.set_title(T("(a) 最终形态（目标 (0.75, 0.10) m；右下为放大）", "(a) Final postures (target (0.75, 0.10) m; inset enlarged)"), fontsize=10, loc="left")
ax = axs[1]
k1 = np.arange(len(hp))
k2 = np.arange(len(hw))
ax.plot(k1, np.maximum([h[1] for h in hp], 1e-16), color=C["z"], lw=1.6, label=T("优先级：位置误差", "priority: position error"))
ax.plot(k2[:60], np.maximum([h[1] for h in hw], 1e-17)[:60], color=C["accent"], lw=1.6, label=T("加权（w = 0.1 m/rad）：位置误差", "weighted (w = 0.1 m/rad): position error"))
ax.set_yscale("log")
ax.set_ylim(1e-16, 1)
ax.set_xlim(0, 60)
ax.set_xlabel(T("迭代次数 k", "iteration k"))
ax.set_ylabel(T("位置误差 / m", "position error / m"))
ax2 = ax.twinx()
ax2.plot(k1, np.degrees([h[2] for h in hp]), color=C["z"], lw=1.1, ls="--")
ax2.plot(k2[:60], np.degrees([h[2] for h in hw])[:60], color=C["accent"], lw=1.1, ls="--")
ax2.axhline(math.degrees(phi_hi), color=C["muted"], lw=0.8, ls=":")
ax2.axhline(math.degrees(phi_d), color=C["x"], lw=0.8, ls=":")
ax2.text(59, math.degrees(phi_hi) - 9, T(f"可行上限 {math.degrees(phi_hi):.1f}°", f"feasible limit {math.degrees(phi_hi):.1f}°"), fontsize=8.5, color=C["muted"], ha="right")
ax2.text(59, math.degrees(phi_d) + 3, r"$\varphi_d$ = 160°", fontsize=8.5, color=C["x"], ha="right")
ax2.set_ylabel(T("工具朝向 φ / (°)（虚线）", "tool angle φ / (°) (dashed)"))
ax2.set_ylim(-20, 180)
ax.legend(fontsize=8, frameon=False, loc="center right")
ax.set_title(T("(b) 迭代过程", "(b) Iterations"), fontsize=10, loc="left")
fig.tight_layout()
figure(fig, "fig15_4_2")
plt.close(fig)
