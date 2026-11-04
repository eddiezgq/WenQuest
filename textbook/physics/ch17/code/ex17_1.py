"""17.1 节的计算：

算例 17.1.1  几种系统的自由度：单摆、双摆、平面两连杆机械臂、空间中的刚体、六轴机械臂、差速驱动的移动机器人。
算例 17.1.2  平面两连杆机械臂（大臂 0.425 m，小臂 0.392 m，与第 14 章相同）的正向运动学：由关节角 q₁ = 30°、q₂ = −50°
            求末端位置；同一个末端位置还能用哪一组关节角达到；画出工作空间（图 17.1.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 17.1.1：自由度 = 坐标数 − 独立的完整约束数
systems = {
    "pend": (2, 1),          # 平面上一个质点（2 个坐标），绳长不变（1 个约束）
    "dpend": (4, 2),         # 平面上两个质点，两根绳长不变
    "arm2": (6, 4),          # 两根平面刚体（各 3 个坐标），两个转动关节（各 2 个约束）
    "body": (6, 0),          # 空间刚体：质心 3 个 + 姿态 3 个
    "arm6": (36, 30),        # 六根刚体，六个转动关节（各 5 个约束）
    "agv": (3, 0),           # 差速小车在平面上的位形 (x, y, φ)；不能侧滑是速度约束，不减少位形坐标
}
dof = {k: n - c for k, (n, c) in systems.items()}
assert dof == {"pend": 1, "dpend": 2, "arm2": 2, "body": 6, "arm6": 6, "agv": 3}
out(**{f"dof_{k}": v for k, v in dof.items()})

# ---- 算例 17.1.2：正向运动学
L1, L2 = 0.425, 0.392


def fk(q1, q2):
    """末端位置（m）。q₁ 是大臂与水平方向的夹角，q₂ 是小臂相对大臂转过的角（逆时针为正）。"""
    return (L1 * math.cos(q1) + L2 * math.cos(q1 + q2), L1 * math.sin(q1) + L2 * math.sin(q1 + q2))


def ik(x, y):
    """两组解：(q₁, q₂)，q₂ 取正、负各一组（肘在下方、上方）。"""
    c2 = (x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    sols = []
    for s in (1, -1):
        q2 = s * math.acos(c2)
        q1 = math.atan2(y, x) - math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2))
        sols.append((q1, q2))
    return sols


q1, q2 = math.radians(30), math.radians(-50)
x, y = fk(q1, q2)
sols = ik(x, y)
other = [s for s in sols if abs(s[1] - q2) > 1e-6][0]
assert all(abs(a - b) < 1e-12 for a, b in zip(fk(*other), (x, y)))
out(x=x, y=y, q1b=math.degrees(other[0]), q2b=math.degrees(other[1]), rmin=abs(L1 - L2), rmax=L1 + L2)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 4.0))
th = np.linspace(0, 2 * math.pi, 300)
ax.fill(np.concatenate([(L1 + L2) * np.cos(th), (L1 - L2) * np.cos(th[::-1])]),
        np.concatenate([(L1 + L2) * np.sin(th), (L1 - L2) * np.sin(th[::-1])]), color="#dfe9f5", lw=0)
ax.plot((L1 + L2) * np.cos(th), (L1 + L2) * np.sin(th), color=d.MUTED, lw=0.8)
for (a1, a2), col, lab in [((q1, q2), d.VA, T("肘在上方（q₂ < 0）", "elbow up (q₂ < 0)")),
                           (other, d.VB, T("肘在下方（q₂ > 0）", "elbow down (q₂ > 0)"))]:
    ex, ey = L1 * math.cos(a1), L1 * math.sin(a1)
    ax.plot([0, ex, x], [0, ey, y], "-o", color=col, lw=3, ms=5, label=lab)
ax.plot([x], [y], "o", color=d.VR, ms=8, zorder=5)
ax.annotate(T("末端", "end effector"), (x, y), xytext=(x + 0.05, y + 0.12), fontsize=9, color=d.VR,
            arrowprops=dict(arrowstyle="->", color=d.VR, lw=0.8))
ax.plot([0], [0], "s", color=d.INK, ms=8)
ax.text(0.03, -0.09, T("肩", "shoulder"), fontsize=9)
ax.text(-0.78, 0.66, T("工作空间", "workspace"), fontsize=9, color=d.VA)
ax.set_aspect("equal"); ax.set_xlim(-0.9, 0.9); ax.set_ylim(-0.9, 0.9)
ax.set_xlabel("x / m"); ax.set_ylabel("y / m")
ax.legend(frameon=False, fontsize=8.5, loc="lower left")
d.spines(ax)
figure(fig, "fig17_1_1")
