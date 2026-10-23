"""26.3 节的示意图。

图 26.3.1：算例 26.3.1 的验证：“真实”UR5e（带夹爪和毛坯、有摩擦）做第 22 章的上下料动作并返回，(a) 关节 2、(b) 关节 4 的
          实测电机力矩（滤波后）、辨识得到的模型的预测、名义模型（不带负载和摩擦）的预测。
图 26.3.2：12 个有代表性的基参数的估计值与真值之比，误差棒为 ±3 倍标准差（σ̂²(WᵀW)⁻¹ 给出的随机误差）。
"""
import numpy as np

from _ch26 import (FC_TRUE, FV_TRUE, base_from_full, cell_move, exc_experiment, full_names, full_pi, full_regressor,
                   lowpass_derivatives, payload_parts, quintic, run_experiment, ur_base_set, ur_chain)
from bookout import COLORS as C, T, figure, style

plt = style()
W0, ind, dep, K, rank = ur_base_set()
names = full_names(6)
pl = payload_parts()
ch_nom = ur_chain()
pb_true = base_from_full(full_pi(ur_chain(payload=pl), FC_TRUE, FV_TRUE), ind, dep, K)
E = exc_experiment(payload=pl, seed=263)
Wm, y = E["W"][:, ind], E["y"]
pb = np.linalg.lstsq(Wm, y, rcond=None)[0]
res = y - Wm @ pb
s2 = res @ res / (len(y) - len(pb))
std = np.sqrt(np.diag(s2 * np.linalg.inv(Wm.T @ Wm)))
thA, thB, T_move = cell_move()


def traj_v(t):
    return quintic(thA, thB, T_move, t) if t <= T_move else quintic(thB, thA, T_move, t - T_move)


tv, Qv, TAUv, _, _ = run_experiment(traj_v, 2 * T_move + 0.5, payload=pl, model=ch_nom, seed=264)
t1, Qf, Qd, Qdd, TAUf = lowpass_derivatives(tv, Qv, TAUv)
P_id = np.array([full_regressor(ch_nom, Qf[k], Qd[k], Qdd[k])[:, ind] @ pb for k in range(len(t1))])
P_nom = np.array([ch_nom.rnea(Qf[k], Qd[k], Qdd[k]) for k in range(len(t1))])
fig, axs = plt.subplots(1, 2, figsize=(11.2, 3.9))
for ax, j, ti in ((axs[0], 1, T("(a) 关节 2", "(a) joint 2")), (axs[1], 3, T("(b) 关节 4", "(b) joint 4"))):
    ax.plot(t1, TAUf[:, j], color=C["ink"], lw=2.2, label=T("实测（滤波后）", "measured (filtered)"))
    ax.plot(t1, P_id[:, j], "--", color=C["x"], lw=1.5, label=T("辨识的模型", "identified model"))
    ax.plot(t1, P_nom[:, j], ":", color=C["z"], lw=1.6, label=T("名义模型（无负载、无摩擦）", "nominal model (no payload, no friction)"))
    ax.set_xlabel(T("时间 t / s", "time t / s"))
    ax.set_ylabel(T("电机力矩 / (N·m)", "motor torque / (N·m)"))
    ax.set_title(ti, fontsize=11)
    ax.grid(alpha=0.25)
axs[0].legend(fontsize=8.5, frameon=False)
fig.tight_layout()
figure(fig, "fig26_3_1")

SHOW = ["J_r1", "mc_z^2", "J_r2", "mc_z^3", "I_yy^3", "mc_z^5", "J_r4", "f_c1", "f_c2", "f_v2", "f_c6", "f_v6"]
idx = [list(ind).index(names.index(s)) for s in SHOW]
ratio = pb[idx] / pb_true[idx]
bar = 3 * std[idx] / np.abs(pb_true[idx])
fig, ax = plt.subplots(figsize=(9.6, 3.6))
x = np.arange(len(SHOW))
ax.errorbar(x, ratio, yerr=bar, fmt="o", color=C["z"], ecolor=C["z"], capsize=4, ms=5)
ax.axhline(1.0, color=C["ink"], lw=1.0)
lab = []
for s in SHOW:
    base, _, k = s.partition("^")
    lab.append(f"${base.replace('mc_z', 'mc_z').replace('I_yy', 'I_{yy}').replace('J_r', 'J_{r').replace('f_c', 'f_{c').replace('f_v', 'f_{v')}" +
               ("}" if s.startswith(("J_r", "f_")) else "") + (f"^{{{k}}}$" if k else "$"))
ax.set_xticks(x)
ax.set_xticklabels(lab, fontsize=10)
ax.set_ylabel(T("估计值 / 真值", "estimate / true value"))
ax.set_ylim(0.7, 1.5)
ax.grid(alpha=0.25, axis="y")
ax.set_title(T("基参数的估计（误差棒 ±3σ，只含随机误差）", "base-parameter estimates (bars ±3σ, random error only)"), fontsize=11)
figure(fig, "fig26_3_2")
