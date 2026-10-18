"""22.3 节的示意图。

图 22.3.1：上下料循环前半段经过路径点 R、A、M、B（算例 22.3.1）：关节 1 与关节 4 的角度、速度、加速度。
          四种做法：每点停下（五次多项式）、经验速度（三次埃尔米特）、三次样条、抛物线过渡；竖线为经过路径点的时刻。
图 22.3.2：抛物线过渡（定理 22.3.2）：在路径点前后各 t_b/2 内以恒定加速度把速度从 v_in 变到 v_out，
          曲线从路径点旁经过，偏离 (v_out − v_in) t_b/8。取在 M 处速度变化最大的关节的实际数据。
图 22.3.3：TCP 的路径（算例 22.3.1）：(a) 俯视；(b) 高度随时间的变化。每点停下与三次样条经过 R、A、M、B；抛物线过渡从 A、M 旁边经过。
"""
import math

import numpy as np

from _fig22 import C, COL3, COL5, LIM, axes3d, base_frame, curves, draw_chain, draw_tool, equal3d, floor3d, ur_chain, workcell
from _traj import (AMAX, JMAX, VMAX, cell_joints, cubic_spline, heuristic_vel, hermite_segments, lspb_via, poly_coeffs, poly_eval,
                   s_quintic, segs_eval, t_min_poly, tcp_fk, via_joints)
from bookout import T, figure, style
import ex22_3 as E

plt = style()
deg = np.degrees
thR, thA, thB, thC = cell_joints()
thM = via_joints()
Q = np.array([thR, thA, thM, thB])
COLH = "#7a868d"
COLB = "#2ca02c"

# 四种轨迹的采样
stop_t, stop_q, stop_v, stop_a = [], [], [], []
t0 = 0.0
for k in range(3):
    Tk = E.T_seg[k]
    tt = np.linspace(0, Tk, 200)
    dq = Q[k + 1] - Q[k]
    stop_t.append(t0 + tt)
    stop_q.append(Q[k] + np.outer(s_quintic(tt / Tk), dq))
    stop_v.append(np.outer(s_quintic(tt / Tk, 1) / Tk, dq))
    stop_a.append(np.outer(s_quintic(tt / Tk, 2) / Tk ** 2, dq))
    t0 += Tk
stop = [np.concatenate(x) for x in (stop_t, stop_q, stop_v, stop_a)]
ts_s = np.concatenate([[0.0], np.cumsum(E.lam_s * E.T_seg)])
ts_h = np.concatenate([[0.0], np.cumsum(E.lam_h * E.T_seg)])
tS = np.linspace(0, ts_s[-1], 800)
tH = np.linspace(0, ts_h[-1], 800)
spl = [tS] + [segs_eval(E.S, tS, r) for r in (0, 1, 2)]
heu = [tH] + [segs_eval(E.H, tH, r) for r in (0, 1, 2)]
f = lspb_via(ts_s, Q, E.tb)
tL = np.linspace(-E.tb[0] / 2, ts_s[-1] + E.tb[3] / 2, 1200)
lsp = [tL + E.tb[0] / 2] + [np.array([f(t, r) for t in tL]) for r in (0, 1, 2)]

# ---------------------------------------------------------------- 图 22.3.1
fig, axs = plt.subplots(2, 3, figsize=(13.4, 6.4))
specs = [(0, T("角度 / (°)", "angle / (°)"), deg), (1, T("速度 / (°/s)", "velocity / (°/s)"), deg), (2, T("加速度 / (rad/s²)", "acceleration / (rad/s²)"), lambda x: x)]
for row, j in enumerate((0, 3)):
    for col, (r, name, cv) in enumerate(specs):
        ax = axs[row, col]
        curves(ax, T("时间 $t$ / s", "time $t$ / s") if row == 1 else None, name)
        for data, c, lw, ls, lab in ((stop, COL5, 1.6, "-", T("每点停下（五次）", "stop at each point (quintic)")),
                                     (heu, COLH, 1.4, "--", T("经验速度", "heuristic velocities")),
                                     (spl, COL3, 2.0, "-", T("三次样条", "cubic spline")),
                                     (lsp, COLB, 1.5, "-.", T("抛物线过渡", "parabolic blends"))):
            ax.plot(data[0], cv(data[r + 1][:, j]), color=c, lw=lw, ls=ls, label=lab)
        for tk in ts_s[1:3]:
            ax.axvline(tk, color=LIM, lw=0.8, ls=":")
        if r == 0:
            ax.plot(ts_s, deg(Q[:, j]), "o", color=C["ink"], ms=4, zorder=6)
            for k, nm in enumerate("RAMB"):
                ax.annotate(nm, (ts_s[k], deg(Q[k, j])), textcoords="offset points", xytext=(4, 6 if (j == 0 or k == 0) else -12), fontsize=9)
        if r == 2:
            ax.axhline(AMAX[j], color=LIM, lw=0.9, ls="--")
            ax.axhline(-AMAX[j], color=LIM, lw=0.9, ls="--")
        if r == 1:
            ax.axhline(180, color=LIM, lw=0.9, ls="--")
            ax.axhline(-180, color=LIM, lw=0.9, ls="--")
            ax.set_ylim(-200, 200)
        ax.set_title(T(f"关节 {j + 1}", f"joint {j + 1}") + "：" + name.split(" /")[0] if T("中", "en") == "中" else f"joint {j + 1}: " + name.split(" /")[0], fontsize=10.5)
axs[0, 0].legend(loc="lower right", fontsize=8.2, frameon=False)
fig.tight_layout()
figure(fig, "fig22_3_1")

# ---------------------------------------------------------------- 图 22.3.2
k = 2                                        # 路径点 M
vv_in = (Q[k] - Q[k - 1]) / (ts_s[k] - ts_s[k - 1])
vv_out = (Q[k + 1] - Q[k]) / (ts_s[k + 1] - ts_s[k])
j = int(np.argmax(np.abs(vv_out - vv_in)))   # 在 M 处速度变化最大的关节
tb = E.tb[2]
tk = ts_s[k]
vin = (Q[k, j] - Q[k - 1, j]) / (ts_s[k] - ts_s[k - 1])
vout = (Q[k + 1, j] - Q[k, j]) / (ts_s[k + 1] - ts_s[k])
fig, ax = plt.subplots(figsize=(7.4, 4.4))
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T(f"关节 {j + 1} 的角度 / (°)", f"joint {j + 1} angle / (°)"))
tt = np.linspace(tk - 0.30, tk + 0.30, 400)
line_in = Q[k, j] + vin * (tt - tk)
line_out = Q[k, j] + vout * (tt - tk)
ax.plot(tt[tt <= tk], deg(line_in[tt <= tk]), color=C["ink"], lw=1.0, ls="--")
ax.plot(tt[tt >= tk], deg(line_out[tt >= tk]), color=C["ink"], lw=1.0, ls="--")
ax.plot(tt[tt > tk], deg(line_in[tt > tk]), color=C["muted"], lw=0.7, ls=":")
ax.plot(tt[tt < tk], deg(line_out[tt < tk]), color=C["muted"], lw=0.7, ls=":")
qq = np.array([f(t)[j] for t in tt])
ax.plot(tt, deg(qq), color=COLB, lw=2.2, label=T("抛物线过渡", "parabolic blend"))
ax.plot([tk], [deg(Q[k, j])], "o", color=C["ink"], ms=6, zorder=6)
ax.annotate(T("路径点 M", "via point M"), (tk, deg(Q[k, j])), textcoords="offset points", xytext=(-70, 8), fontsize=10)
qb = f(tk)[j]
ax.plot([tk, tk], [deg(Q[k, j]), deg(qb)], color=C["x"], lw=1.6)
ax.annotate(r"$(v_{\rm out}-v_{\rm in})\,t_b/8$", (tk, deg((Q[k, j] + qb) / 2)), textcoords="offset points", xytext=(10, -26),
            fontsize=12, color=C["x"], arrowprops=dict(arrowstyle="-", color=C["x"], lw=0.8))
for x in (tk - tb / 2, tk + tb / 2):
    ax.axvline(x, color=LIM, lw=0.8, ls=":")
y0 = ax.get_ylim()[0]
ax.annotate("", xy=(tk + tb / 2, y0 + 0.4), xytext=(tk - tb / 2, y0 + 0.4), arrowprops=dict(arrowstyle="<->", color=C["muted"], lw=1))
ax.text(tk, y0 + 0.6, "$t_b$", ha="center", fontsize=11)
ax.text(tk - 0.27, deg(Q[k, j] - vin * 0.25) + 1.0, r"$v_{\rm in}$", fontsize=11)
ax.text(tk + 0.22, deg(Q[k, j] + vout * 0.22) + 1.0, r"$v_{\rm out}$", fontsize=11)
fig.tight_layout()
figure(fig, "fig22_3_2")

# ---------------------------------------------------------------- 图 22.3.3
fig, axs = plt.subplots(1, 2, figsize=(12.6, 4.6), gridspec_kw=dict(width_ratios=[1.0, 1.25]))
ax = axs[0]
ax.set_aspect("equal")
curves(ax, "$x_s$ / m", "$y_s$ / m")
import matplotlib.patches as mp
from _traj import P_CHUCK, P_PICK
ax.add_patch(mp.Rectangle((P_PICK[0] - 0.10, P_PICK[1] - 0.08), 0.20, 0.16, fc="#8c6d1f", alpha=0.15, ec="#8c6d1f"))
ax.text(P_PICK[0] + 0.11, P_PICK[1] - 0.07, T("料架", "rack"), fontsize=9, color="#8c6d1f")
ax.add_patch(mp.Rectangle((P_CHUCK[0] - 0.36, P_CHUCK[1] - 0.10), 0.24, 0.20, fc="#5d6b73", alpha=0.15, ec="#5d6b73"))
ax.text(P_CHUCK[0] - 0.36, P_CHUCK[1] + 0.12, T("车床床头箱", "lathe headstock"), fontsize=9, color="#5d6b73")
ax.plot(0, 0, "s", color=C["ink"], ms=6)
ax.text(0.02, -0.05, T("基座", "base"), fontsize=9)
paths = {}
for data, c, lw, ls, lab, key in ((stop, COL5, 1.6, "-", T("每点停下", "stop at each point"), "stop"),
                                  (spl, COL3, 2.2, "-", T("三次样条", "cubic spline"), "spl"),
                                  (lsp, COLB, 1.6, "-.", T("抛物线过渡", "parabolic blends"), "lsp")):
    P = np.array([tcp_fk(q)[:3, 3] for q in data[1][::2]])
    paths[key] = (data[0][::2], P)
    ax.plot(P[:, 0], P[:, 1], color=c, lw=lw, ls=ls, label=lab)
for k2, nm in enumerate("RAMB"):
    X = tcp_fk(Q[k2])[:3, 3]
    ax.plot(X[0], X[1], "o", color=C["ink"], ms=4, zorder=6)
    ax.annotate(nm, (X[0], X[1]), textcoords="offset points", xytext=(6, -12 if nm == "R" else 5), fontsize=10)
ax.set_xlim(-0.30, 0.65)
ax.set_ylim(-0.62, 0.52)
ax.legend(loc="lower left", fontsize=8.5, frameon=False)
ax.set_title(T("(a) 俯视：TCP 的路径", "(a) top view: TCP paths"), fontsize=10.5)
ax = axs[1]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("TCP 的高度 $z$ / m", "TCP height $z$ / m"))
for key, c, lw, ls in (("stop", COL5, 1.6, "-"), ("spl", COL3, 2.2, "-"), ("lsp", COLB, 1.6, "-.")):
    tt, P = paths[key]
    ax.plot(tt, P[:, 2], color=c, lw=lw, ls=ls)
ax.axhline(0.30, color=LIM, lw=0.9, ls="--")
ax.text(0.02, 0.305, T("防护罩上沿（示意）", "top of the guard (illustrative)"), fontsize=9, color=C["muted"])
for k2, nm in enumerate("RAMB"):
    ax.plot(ts_s[k2], tcp_fk(Q[k2])[2, 3], "o", color=C["ink"], ms=4, zorder=6)
    ax.annotate(nm, (ts_s[k2], tcp_fk(Q[k2])[2, 3]), textcoords="offset points", xytext=(4, 6), fontsize=10)
ax.set_title(T("(b) TCP 的高度：样条与过渡都越过防护罩", "(b) TCP height: spline and blends clear the guard"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig22_3_3")
