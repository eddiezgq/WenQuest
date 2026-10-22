"""25.1 节的示意图。

图 25.1.1：牛顿-欧拉递推的两遍：前向（基座 → 末端）传运动旋量与加速度，反向（末端 → 基座）传力旋量，关节力矩是 ℱ_i 在关节轴上的分量。
图 25.1.2：算例 25.1.1 的上下料动作（第 22 章，T = 最短时间）。
          (a) 各连杆坐标系原点与 TCP 的速度大小随时间的变化（前向递推的结果）；
          (b) TCP 速度最大的时刻，每个关节单独转动给 TCP 的速度（各矢量的大小）与实际的合速度。
"""
import numpy as np

from _ch25 import TCP, adjoint, cell_move, inv, quintic, ur_chain
from bookout import COLORS as C, T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 25.1.1
fig, ax = plt.subplots(figsize=(10.4, 4.3))
ax.set_xlim(-0.6, 10.5)
ax.set_ylim(-0.4, 4.2)
ax.axis("off")
xs = [0.3, 2.5, 4.7, 7.6, 9.6]
labels = [T("基座 {0}", "base {0}"), T("连杆 1", "link 1"), T("连杆 2", "link 2"), T("连杆 n", "link n"), T("外界 {n+1}", "environment {n+1}")]
for x, lab in zip(xs, labels):
    fc = "#eef2f4" if x in (xs[0], xs[-1]) else "#dbe9f6"
    ax.add_patch(plt.Rectangle((x - 0.75, 1.55), 1.5, 0.9, fc=fc, ec=C["ink"], lw=1.1))
    ax.text(x, 2.0, lab, ha="center", va="center", fontsize=11)
ax.text((xs[2] + xs[3]) / 2, 2.0, "……", ha="center", va="center", fontsize=14, color=C["muted"])


def arr(p, q, color, lw=1.8):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=14, shrinkA=0, shrinkB=0))


# 前向
for a, b in ((0, 1), (1, 2), (3, 4)):
    arr((xs[a] + 0.8, 2.85), (xs[b] - 0.8, 2.85), C["z"])
arr((xs[2] + 0.8, 2.85), (xs[2] + 1.2, 2.85), C["z"])
arr((xs[3] - 1.2, 2.85), (xs[3] - 0.8, 2.85), C["z"])
ax.text(xs[0] + 1.1, 3.05, r"$\mathcal{V}_0 = 0,\ \dot{\mathcal{V}}_0 = (0, -\mathfrak{g})$", fontsize=11, color=C["z"])
ax.text(xs[1] + 0.9, 3.45, r"$\mathcal{V}_i = [\mathrm{Ad}_{T_{i,i-1}}]\mathcal{V}_{i-1} + \mathcal{A}_i\dot\theta_i$", fontsize=11, color=C["z"])
ax.text(xs[1] + 0.9, 3.85, r"$\dot{\mathcal{V}}_i = [\mathrm{Ad}_{T_{i,i-1}}]\dot{\mathcal{V}}_{i-1} + [\mathrm{ad}_{\mathcal{V}_i}]\mathcal{A}_i\dot\theta_i + \mathcal{A}_i\ddot\theta_i$",
        fontsize=11, color=C["z"])
ax.text(-0.25, 3.45, T("前向：运动", "forward: motion"), fontsize=11, color=C["z"], fontweight="bold")
# 反向
for a, b in ((1, 0), (2, 1), (4, 3)):
    arr((xs[a] - 0.8, 1.15), (xs[b] + 0.8, 1.15), C["x"])
arr((xs[3] - 0.8, 1.15), (xs[3] - 1.2, 1.15), C["x"])
arr((xs[2] + 1.2, 1.15), (xs[2] + 0.8, 1.15), C["x"])
ax.text(xs[4] - 1.15, 0.72, r"$\mathcal{F}_{n+1} = \mathcal{F}_{\mathrm{tip}}$", fontsize=11, color=C["x"])
ax.text(xs[1] - 0.2, 0.32, r"$\mathcal{F}_i = [\mathrm{Ad}_{T_{i+1,i}}]^{\mathrm{T}}\mathcal{F}_{i+1} + \mathcal{G}_i\dot{\mathcal{V}}_i - [\mathrm{ad}_{\mathcal{V}_i}]^{\mathrm{T}}\mathcal{G}_i\mathcal{V}_i$",
        fontsize=11, color=C["x"])
ax.text(xs[1] - 0.2, -0.15, r"$\tau_i = \mathcal{A}_i^{\mathrm{T}}\mathcal{F}_i$", fontsize=12, color=C["x"])
ax.text(-0.25, 0.72, T("反向：力", "backward: force"), fontsize=11, color=C["x"], fontweight="bold")
# 每个关节的 θ 输入
for x in xs[1:4]:
    ax.text(x - 0.75, 2.52, r"$\theta,\dot\theta,\ddot\theta$", fontsize=9, color=C["muted"], ha="center")
figure(fig, "fig25_1_1")

# ---------------------------------------------------------------- 图 25.1.2
ch = ur_chain()
thA, thB, T_move = cell_move()
Tf6 = inv(ch.Mf)
r_tcp = np.array([0, TCP, 0])
ts = np.linspace(0, T_move, 400)
sp = np.zeros((len(ts), 7))
for k, t in enumerate(ts):
    q, qd, qdd = quintic(thA, thB, T_move, t)
    _, Vs, _ = ch.forward(q, qd, qdd)
    for i in range(6):
        sp[k, i] = np.linalg.norm(Vs[i][3:])
    Vf = adjoint(Tf6) @ Vs[-1]
    sp[k, 6] = np.linalg.norm(Vf[3:] + np.cross(Vf[:3], r_tcp))
fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.0), gridspec_kw=dict(width_ratios=[1.45, 1]))
ax = axs[0]
cols = ["#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"]
for i in range(6):
    ax.plot(ts, sp[:, i], color=cols[i], lw=1.3, label=T(f"连杆 {i + 1} 原点", f"origin of link {i + 1}"))
ax.plot(ts, sp[:, 6], color=C["x"], lw=2.0, label="TCP")
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("速度大小 / (m/s)", "speed / (m/s)"))
ax.set_title(T("(a) 各连杆原点和 TCP 的速度", "(a) speeds of the link origins and the TCP"), fontsize=11)
ax.legend(fontsize=8.5, ncol=2, frameon=False, loc="upper left")
ax.grid(alpha=0.25)
ax.set_xlim(0, T_move)
k = int(np.argmax(sp[:, 6]))
t_pk = ts[k]
q, qd, _ = quintic(thA, thB, T_move, t_pk)
J = adjoint(Tf6) @ ch.jacobians(q)[-1]
cvec = np.array([J[3:, j] * qd[j] + np.cross(J[:3, j] * qd[j], r_tcp) for j in range(6)])
ax.axvline(t_pk, color=C["muted"], lw=0.8, ls="--")
ax = axs[1]
mag = np.linalg.norm(cvec, axis=1)
ax.bar(range(1, 7), mag, color=cols, ec=C["ink"], lw=0.6)
tot = np.linalg.norm(cvec.sum(0))
ax.bar(7.4, tot, color=C["x"], ec=C["ink"], lw=0.6, width=0.9)
ax.set_xticks(list(range(1, 7)) + [7.4])
ax.set_xticklabels([T(f"关节{j}", f"J{j}") for j in range(1, 7)] + [T("合", "sum")], fontsize=9)
ax.set_ylabel(T("TCP 速度 / (m/s)", "TCP speed / (m/s)"))
ax.set_title(T(f"(b) t = {t_pk:.2f} s 时各关节的贡献", f"(b) each joint's share at t = {t_pk:.2f} s"), fontsize=11)
ax.grid(alpha=0.25, axis="y")
fig.tight_layout()
figure(fig, "fig25_1_2")
