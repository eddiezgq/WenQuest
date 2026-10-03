"""14.1 节的示意图。

图 14.1.1：平面 2R 臂（l1 = 0.425 m、l2 = 0.392 m）的解的个数：圆环内两组（A 点的肘上、肘下两种形态），
           外边界上一组（B 点，手臂伸直），圆环外和中间的小圆内没有解（C、D 点）。
图 14.1.2：一般 6R 臂从 600 个随机初值出发用数值法求逆解，各个初值收敛到哪一组解（数据与程序 14.1.1 相同）。
"""
import math

import numpy as np

from _fig14 import BLUE2, C, PALE, arm_pts, base_mark, draw_arm, plane
from _ik import ik2r, random6r
from bookout import T, figure, style

plt = style()
l1, l2 = 0.425, 0.392
ro, ri = l1 + l2, abs(l1 - l2)

# ---------------------------------------------------------------- 图 14.1.1
fig, ax = plt.subplots(figsize=(6.6, 5.4))
plane(ax, (-1.08, 1.12), (-0.92, 0.98))
t = np.linspace(0, 2 * math.pi, 300)
ax.fill(ro * np.cos(t), ro * np.sin(t), color=PALE, zorder=0)
ax.fill(ri * np.cos(t), ri * np.sin(t), color="white", zorder=1)
ax.plot(ro * np.cos(t), ro * np.sin(t), color=BLUE2, lw=1.6, zorder=1)
ax.plot(ri * np.cos(t), ri * np.sin(t), color=BLUE2, lw=1.2, zorder=1)
base_mark(ax)
A = (0.45, 0.35)
sA = ik2r(*A, l1, l2)
cols = {1: C["accent"], -1: C["z"]}
for s in sA:
    sg = 1 if s[1] > 0 else -1
    draw_arm(ax, arm_pts(s, (l1, l2)), cols[sg], lw=5)
ax.plot([0, A[0]], [0, A[1]], color=C["muted"], lw=0.9, ls=":", zorder=2)
ax.plot(*A, "o", color=C["x"], ms=7, zorder=8)
ax.text(A[0] + 0.03, A[1] + 0.02, "A", fontsize=12, color=C["x"])
el_dn = arm_pts(sA[0], (l1, l2))[1]
el_up = arm_pts(sA[1], (l1, l2))[1]
ax.text(el_dn[0] + 0.03, el_dn[1] - 0.06, T("肘下（θ₂ > 0）", "elbow down (θ₂ > 0)"), fontsize=9.5, color=C["accent"])
ax.text(el_up[0] - 0.36, el_up[1] + 0.03, T("肘上（θ₂ < 0）", "elbow up (θ₂ < 0)"), fontsize=9.5, color=C["z"])
# B：外边界上，手臂伸直
aB = math.radians(-35)
B = ro * np.array([math.cos(aB), math.sin(aB)])
draw_arm(ax, arm_pts(ik2r(B[0], B[1], l1, l2)[0], (l1, l2)), C["muted"], lw=4, alpha=0.8)
ax.plot(*B, "o", color=C["x"], ms=7, zorder=8)
ax.text(B[0] + 0.03, B[1] - 0.05, T("B：一组（伸直）", "B: one (arm straight)"), fontsize=9.5, color=C["ink"])
C_ = (0.9, 0.3)
ax.plot(*C_, "x", color=C["x"], ms=9, mew=2, zorder=8)
ax.text(C_[0] - 0.12, C_[1] + 0.06, T("C：无解", "C: none"), fontsize=9.5, color=C["ink"])
ax.annotate(T("D：无解（小圆内）", "D: none (inner disc)"), xy=(0.02, 0.0), xytext=(-0.62, -0.38), fontsize=9.5, color=C["ink"],
            arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.8))
ax.plot(0.02, 0.0, "x", color=C["x"], ms=6, mew=1.6, zorder=8)
ax.text(-0.55, -0.62, T("圆环内：两组解", "inside the ring: two solutions"), fontsize=10, color=C["z"])
ax.text(0.30, -0.86, T("外圆 r = l₁ + l₂", "outer circle r = l₁ + l₂"), fontsize=9, color=C["muted"])
ax.annotate(T("内圆 r = |l₁ − l₂|（很小）", "inner circle r = |l₁ − l₂| (tiny)"), xy=(-0.025, 0.02), xytext=(-1.07, 0.86), fontsize=9,
            color=C["muted"], arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.8))
figure(fig, "fig14_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 14.1.2
P, Td, found, hits = random6r()
n_none = sum(f is None for f in found)
fig, ax = plt.subplots(figsize=(6.4, 3.3))
k = np.arange(1, len(hits) + 1)
ax.bar(k, hits, color=BLUE2, edgecolor=C["z"], lw=0.8)
ax.bar([len(hits) + 1.5], [n_none], color="#e0e0e0", edgecolor=C["muted"], lw=0.8)
for x, h in zip(list(k) + [len(hits) + 1.5], hits + [n_none]):
    ax.text(x, h + 3, str(h), ha="center", fontsize=9, color=C["ink"])
ax.set_xticks(list(k) + [len(hits) + 1.5])
ax.set_xticklabels([str(i) for i in k] + [T("未收敛", "no conv.")], fontsize=9)
ax.set_xlabel(T("收敛到的解的编号", "solution reached"), fontsize=10)
ax.set_ylabel(T("初值个数", "starting points"), fontsize=10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_ylim(0, max(hits + [n_none]) * 1.15)
figure(fig, "fig14_1_2")
plt.close(fig)
