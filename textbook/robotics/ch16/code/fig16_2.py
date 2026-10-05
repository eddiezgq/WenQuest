"""16.2 节的示意图。

图 16.2.1：ZYX 欧拉角速率与角速度：ω_s = ẑ α̇ + R_z(α) ŷ β̇ + R_z(α) R_y(β) x̂ γ̇。三根轴就是 B(η) 的三列；
           (a) β = 30°：三轴张成空间；(b) β = 90°：第一、第三根轴共线，det B = −cos β = 0（万向节锁）。
图 16.2.2：算例 16.2.3：法兰盘以 20°/s 绕水平轴转过 180°，俯仰角最大 89°。(a) 三个欧拉角；(b) 欧拉角速率、
           指数坐标速率与关节转速（对数坐标）。
"""
import math

import numpy as np

from _fig16 import C, axes3d, logaxis
from _jac import gimbal_path, rotz, roty
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 16.2.1
fig = plt.figure(figsize=(10.4, 4.6))
for k, (b_deg, title) in enumerate(((30, T("(a) β = 30°：三根轴张成空间", "(a) β = 30°: the three axes span space")),
                                    (90, T("(b) β = 90°：第一、三根轴共线", "(b) β = 90°: the first and third axes line up")))):
    _, ax = axes3d(plt, fig=fig, pos=121 + k, elev=18, azim=15)
    a, b = math.radians(35), math.radians(b_deg)
    cols = [C["z"], C["y"], C["x"]]
    vecs = [np.array([0, 0, 1.0]), rotz(a) @ np.array([0, 1.0, 0]), rotz(a) @ roty(b) @ np.array([1.0, 0, 0])]
    names = [r"$\hat z\ \ (\dot\alpha)$", r"$R_z(\alpha)\hat y\ \ (\dot\beta)$", r"$R_z(\alpha)R_y(\beta)\hat x\ \ (\dot\gamma)$"]
    offs = [np.array([0.06, 0.0, 0.08]), np.array([0.0, -0.45, 0.12]), np.array([0.05, 0.0, -0.2])]
    if b_deg == 90:
        offs[0] = np.array([0.1, 0.0, 0.0])
        offs[2] = np.array([0.08, 0.0, -0.05])
    for v, c, nm, o in zip(vecs, cols, names, offs):
        ax.quiver(0, 0, 0, *v, color=c, lw=2.4, arrow_length_ratio=0.12)
        ax.text(*(v * 1.02 + o), nm, fontsize=10.5, color=c)
    t = np.linspace(0, 2 * math.pi, 100)
    ax.plot(np.cos(t), np.sin(t), 0 * t, color="#cfd6db", lw=0.8)
    ax.plot(0 * t, np.cos(t), np.sin(t), color="#e3e8eb", lw=0.6)
    ax.plot(np.cos(t), 0 * t, np.sin(t), color="#e3e8eb", lw=0.6)
    for i, c in enumerate((C["x"], C["y"], C["z"])):
        e = np.eye(3)[i] * 0.35
        ax.plot([0, e[0]], [0, e[1]], [0, e[2]], color=c, lw=1.0, alpha=0.5)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.set_box_aspect((1, 1, 1), zoom=1.25)
    ax.text2D(0.0, 0.95, title, transform=ax.transAxes, fontsize=10.5)
    detb = -math.cos(b)
    ax.text2D(0.0, 0.03, "α = 35°,  det B = −cos β = " + (f"{detb:.3f}".replace("-", "−") if abs(detb) > 1e-9 else "0"),
              transform=ax.transAxes, fontsize=10, color=C["muted"])
fig.tight_layout()
figure(fig, "fig16_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 16.2.2
H, u = gimbal_path()
t = H["t"]
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.1))
ax = axs[0]
for i, (c, nm) in enumerate(((C["z"], "α"), (C["y"], "β"), (C["x"], "γ"))):
    ax.plot(t, np.degrees(H["eta"][:, i]), color=c, lw=1.8, label=nm)
ax.axhline(90, color=C["muted"], lw=0.8, ls=":")
ax.text(0.1, 93, T("β = 90°：万向节锁", "β = 90°: gimbal lock"), fontsize=9, color=C["muted"])
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("ZYX 欧拉角 / (°)", "ZYX Euler angles / (°)"))
ax.legend(fontsize=9.5, frameon=False, loc="lower left")
ax.set_ylim(-200, 200)
ax.set_title(T("(a) 欧拉角：β 升到 89° 时 α、γ 急转", "(a) Euler angles: α and γ swing as β nears 89°"), fontsize=10.5, loc="left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax = axs[1]
ax.plot(t, np.degrees(np.abs(H["etad"][:, 0])), color=C["z"], lw=1.8, label=r"$|\dot\alpha|$")
ax.plot(t, np.degrees(np.abs(H["etad"][:, 2])), color=C["x"], lw=1.2, ls="--", label=r"$|\dot\gamma|$")
ax.plot(t, np.degrees(np.abs(H["rd"]).max(1)), color=C["accent"], lw=1.8, label=T("指数坐标速率 ", "exponential-coordinate rate ") + r"$\max|\dot r_i|$")
ax.plot(t, np.degrees(np.abs(H["qd"]).max(1)), color=C["ink"], lw=1.8, label=T("关节转速 ", "joint speed ") + r"$\max|\dot\theta_i|$")
ax.axhline(20, color=C["muted"], lw=0.8, ls=":")
ax.text(6.6, 23, "|ω| = 20°/s", fontsize=9, color=C["muted"])
logaxis(ax)
ax.set_ylim(1, 5000)
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("速率 / (°/s)", "rate / (°/s)"))
ax.legend(fontsize=8.8, frameon=False, loc="upper right")
ax.set_title(T("(b) 欧拉角速率与关节转速", "(b) Euler-angle rates and joint speeds"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig16_2_2")
plt.close(fig)
