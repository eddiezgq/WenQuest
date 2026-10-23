"""26.2 节的示意图。

图 26.2.1：程序 26.2.1 优化得到的激励轨迹（一个周期 10 s）：(a) 六个关节偏离初始姿态的角度；(b) 关节速度，虚线为 1.5 rad/s。
图 26.2.2：三种轨迹的基参数回归矩阵（1000 个时刻叠起来，52 列）的奇异值，从大到小：第 22 章的上下料动作（往返）、
          一条满足同样限制的随机傅里叶轨迹、优化后的轨迹。纵轴为对数刻度；奇异值之比就是条件数。
"""
import numpy as np

from _ch26 import (EXC_A, EXC_B, EXC_Q0, EXC_TF, Fourier, cell_move, exc_violation, full_regressor, quintic, ur_base_set, ur_chain)
from bookout import COLORS as C, T, figure, style

plt = style()
ch = ur_chain()
W, ind, dep, K, rank = ur_base_set()
tr = Fourier(EXC_Q0, EXC_A, EXC_B, EXC_TF)
ts = np.linspace(0, EXC_TF, 1001)[:-1]
q, qd, qdd = tr.eval(ts)
JC = ["#7a868d", C["z"], C["y"], C["x"], C["accent"], "#9467bd"]
fig, axs = plt.subplots(1, 2, figsize=(11.2, 3.8))
for j in range(6):
    axs[0].plot(ts, np.degrees(q[:, j] - EXC_Q0[j]), color=JC[j], lw=1.4, label=T(f"关节 {j + 1}", f"joint {j + 1}"))
    axs[1].plot(ts, qd[:, j], color=JC[j], lw=1.4)
for s in (1, -1):
    axs[1].axhline(1.5 * s, color=C["ink"], lw=0.9, ls="--")
axs[0].set_ylabel(T("偏离初始姿态 / (°)", "offset from the initial pose / (°)"))
axs[1].set_ylabel(T("关节速度 / (rad/s)", "joint rate / (rad/s)"))
for ax, ti in zip(axs, (T("(a) 关节角", "(a) joint angles"), T("(b) 关节速度", "(b) joint rates"))):
    ax.set_xlabel(T("时间 t / s", "time t / s"))
    ax.set_title(ti, fontsize=11)
    ax.grid(alpha=0.25)
    ax.set_xlim(0, EXC_TF)
axs[0].legend(fontsize=8.5, ncol=3, frameon=False, loc="lower left")
fig.tight_layout()
figure(fig, "fig26_2_1")

# ---------------------------------------------------------------- 图 26.2.2


def sv(qq, vv, aa):
    Wb = np.vstack([full_regressor(ch, qq[k], vv[k], aa[k]) for k in range(len(qq))])[:, ind]
    return np.linalg.svd(Wb, compute_uv=False)


thA, thB, T_move = cell_move()
tm = np.linspace(0, 2 * T_move, 400)
M = np.array([quintic(thA, thB, T_move, t) if t <= T_move else quintic(thB, thA, T_move, t - T_move) for t in tm])
s_m = sv(M[:, 0], M[:, 1], M[:, 2])
rng = np.random.default_rng(2621)
x = rng.normal(0, 0.15, 60)
s_ = 1.0
while exc_violation(ch, Fourier(EXC_Q0, s_ * x[:30].reshape(6, 5), s_ * x[30:].reshape(6, 5), EXC_TF), ts[::17]) > 0:
    s_ *= 0.9
trr = Fourier(EXC_Q0, s_ * x[:30].reshape(6, 5), s_ * x[30:].reshape(6, 5), EXC_TF)
s_r = sv(*trr.eval(ts))
s_o = sv(q, qd, qdd)
fig, ax = plt.subplots(figsize=(7.6, 4.0))
k = np.arange(1, len(s_o) + 1)
ax.semilogy(k, np.maximum(s_m, 1e-16), "s-", color=C["muted"], ms=3, lw=1.2,
            label=T(f"上下料动作（条件数 {s_m[0] / max(s_m[-1], 1e-300):.0e}）", f"loading move (cond. {s_m[0] / max(s_m[-1], 1e-300):.0e})"))
ax.semilogy(k, s_r, "^-", color=C["accent"], ms=3, lw=1.2,
            label=T(f"随机傅里叶轨迹（条件数 {s_r[0] / s_r[-1]:.0f}）", f"random Fourier (cond. {s_r[0] / s_r[-1]:.0f})"))
ax.semilogy(k, s_o, "o-", color=C["z"], ms=3, lw=1.5,
            label=T(f"优化后的轨迹（条件数 {s_o[0] / s_o[-1]:.0f}）", f"optimized (cond. {s_o[0] / s_o[-1]:.0f})"))
ax.set_xlabel(T("奇异值的序号", "index of the singular value"))
ax.set_ylabel(T("奇异值", "singular value"))
ax.set_ylim(1e-14, 1e4)
ax.legend(fontsize=9, frameon=False, loc="lower left")
ax.grid(alpha=0.25, which="both")
figure(fig, "fig26_2_2")
