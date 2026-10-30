"""29.2 节的示意图。

图 29.2.1：(a) WQ-CR5 在工作姿态带标准负载时，质量矩阵对角元中电机转子（armature）与连杆各占多少，UR5e（Menagerie）对比；
          (b) 出厂位置环（没有重力补偿）下各关节的下垂角与 TCP 的偏离。
"""
import math

import mujoco
import numpy as np

from _ch29 import Q_CR, Q_WORK, cr_chain, cr_load, cr_load_xml, cr_text, mjcf_text, wqcr5
from bookout import COLORS as C, T, figure, style

plt = style()
W = wqcr5()
m = mujoco.MjModel.from_xml_string(cr_text(tool=cr_load_xml(), option='<option><flag contact="disable"/></option>'))
d = mujoco.MjData(m)
d.qpos[:] = Q_CR
mujoco.mj_forward(m, d)
M = np.zeros((6, 6))
mujoco.mj_fullM(m, d, M)
arm = np.array(W.armature())
mu = mujoco.MjModel.from_xml_string(mjcf_text(option='<option><flag contact="disable"/></option>'))
du = mujoco.MjData(mu)
du.qpos[:] = Q_WORK
mujoco.mj_forward(mu, du)
Mu = np.zeros((6, 6))
mujoco.mj_fullM(mu, du, Mu)

fig, axs = plt.subplots(1, 2, figsize=(11.6, 3.9))
ax = axs[0]
x = np.arange(6)
sh_cr = arm / np.diag(M) * 100
sh_ur = mu.dof_armature / np.diag(Mu) * 100
ax.bar(x - 0.18, sh_cr, 0.36, color=C["z"], label=T("WQ-CR5（带 5 kg 标准负载）", "WQ-CR5 (5 kg standard load)"))
ax.bar(x + 0.18, sh_ur, 0.36, color=C["muted"], label=T("UR5e（Menagerie，空载）", "UR5e (Menagerie, no load)"))
for i, v in enumerate(sh_cr):
    ax.text(i - 0.18, v + 1.5, f"{v:.0f}", ha="center", fontsize=8)
ax.set_xticks(x, [f"J{i + 1}" for i in range(6)])
ax.set_ylim(0, 112)
ax.set_ylabel(T("转子惯量占 $M_{ii}$ 的比例 / %", "rotor share of $M_{ii}$ / %"))
ax.set_title(T("(a) 电机转子在等效惯量中的份额", "(a) share of the motor rotors in the inertia"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25, axis="y")

ax = axs[1]
P = cr_load()
ch = cr_chain(payload=P)
kp = np.array(W.SERVO_KP)
q = Q_CR.copy()
for _ in range(60):
    _, _, g = ch.closed_form(q, np.zeros(6))
    q = Q_CR - g / kp
sag = np.degrees(q - Q_CR)
ax.bar(x, sag, 0.55, color=[C["accent"] if abs(s) > 0.5 else C["muted"] for s in sag])
for i, v in enumerate(sag):
    ax.text(i, v + (0.08 if v >= 0 else -0.25), f"{v:.2f}°", ha="center", fontsize=8)
tcp = lambda qq: (ch.flange_pose(qq) @ np.array([0.05, 0, 0.10, 1.0]))[:3]  # noqa: E731
e = np.linalg.norm(tcp(q) - tcp(Q_CR)) * 1000
ax.text(2.6, max(sag) * 0.8, T(f"TCP 偏离 {e:.0f} mm", f"TCP off by {e:.0f} mm"), fontsize=10)
ax.set_xticks(x, [f"J{i + 1}" for i in range(6)])
ax.set_ylim(min(0, sag.min()) - 0.2, sag.max() * 1.25)
ax.set_ylabel(T("下垂角 / (°)", "sag / (°)"))
ax.set_title(T("(b) 出厂位置环的下垂（无重力补偿）", "(b) sag under the stock position loop (no gravity compensation)"), fontsize=11)
ax.axhline(0, color=C["ink"], lw=0.6)
ax.grid(alpha=0.25, axis="y")
fig.tight_layout()
figure(fig, "fig29_2_1")
