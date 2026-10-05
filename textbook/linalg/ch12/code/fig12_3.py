"""图 12.3.1：冗余臂的两种关节速度。平面三连杆臂（姿态 30°, 60°, −45°）末端以 0.2 m/s 竖直向上运动。
(a) 机械臂与末端速度；(b) 欧氏最小范数解 J⁺v 与最小动能解（M-内积下的最小范数解）的三个关节速度与动能。"""
import numpy as np

from _arm3 import jac, mass, points
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

q = np.radians([30.0, 60.0, -45.0])
J, M = jac(q), mass(q)
v = np.array([0.0, 0.2])
qe = np.linalg.pinv(J) @ v
Mi = np.linalg.inv(M)
qm = Mi @ J.T @ np.linalg.solve(J @ Mi @ J.T, v)
ke = lambda w: 0.5 * w @ M @ w
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.2))
P = points(q)
a1.plot(P[:, 0], P[:, 1], "-", color=INK, lw=5, solid_capstyle="round")
a1.plot(P[:-1, 0], P[:-1, 1], "o", color="white", mec=INK, ms=8, mew=2)
a1.plot([-0.08, 0.08], [-0.02, -0.02], color=INK, lw=3)
a1.annotate("", xy=P[-1] + 1.0 * v, xytext=P[-1], arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.2, mutation_scale=14))
a1.text(P[-1, 0] + 0.03, P[-1, 1] + 0.1, "v = 0.2 m/s", color=RED, fontsize=10)
for i, n in enumerate(("1", "2", "3")):
    a1.text(P[i, 0] + 0.03, P[i, 1] - 0.07, T(f"关节 {n}", f"joint {n}"), fontsize=9, color=MUTED)
a1.set_aspect("equal"); a1.set_xlim(-0.15, 0.7); a1.set_ylim(-0.1, 1.08); a1.axis("off")
a1.set_title(T("(a) 末端竖直向上运动", "(a) The tool moves straight up"), fontsize=11)
x = np.arange(3)
a2.bar(x - 0.18, qe, 0.34, color=BLUE, label=T(f"欧氏最小范数：动能 {ke(qe):.3f} J", f"min Euclidean norm: KE {ke(qe):.3f} J"))
a2.bar(x + 0.18, qm, 0.34, color=ACC, label=T(f"最小动能：动能 {ke(qm):.3f} J", f"min kinetic energy: KE {ke(qm):.3f} J"))
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xticks(x); a2.set_xticklabels([T("关节 1", "joint 1"), T("关节 2", "joint 2"), T("关节 3", "joint 3")])
a2.set_ylabel(T("关节速度 / (rad/s)", "joint velocity / (rad/s)"))
a2.legend(frameon=False, fontsize=9, loc="upper left")
a2.set_ylim(-1.1, 2.0)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 两种解的关节速度", "(b) Joint velocities of the two solutions"), fontsize=11)
fig.tight_layout()
figure(fig, "fig12_3_1")
