"""12.3 节的示意图。

图 12.3.1：一万组随机关节角下，厂家 DH 参数与零件库模型算出的 UR5e 末端位置之差（直方图）。
图 12.3.2：SCARA 零位与四个关节：三个竖直转轴、一个竖直移动方向。
"""
import numpy as np

from _fig12 import C, axes3d, equal3d, frame3d
from _poe import Model
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 12.3.1
ur = Model("B-ARM-UR5E", "base", "wrist_3_link", (0, 0.1, 0))
dh = ur.entry["dh"]["params"]


def fk_dh(q):
    T = np.eye(4)
    for (a, d, al), qi in zip(dh, q):
        ct, st, ca, sa = np.cos(qi), np.sin(qi), np.cos(al), np.sin(al)
        T = T @ np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]])
    return T


rng = np.random.default_rng(12)
gaps = np.array([np.linalg.norm(fk_dh(q)[:3, 3] - ur.fk(q)[:3, 3]) for q in rng.uniform(-np.pi, np.pi, (10000, 6))]) * 1000
fig, ax = plt.subplots(figsize=(5.6, 3.2))
ax.hist(gaps, bins=40, color=C["z"], alpha=0.8, edgecolor="white", lw=0.5)
ax.axvline(gaps.mean(), color=C["accent"], lw=1.5)
box = dict(facecolor="white", edgecolor="none", pad=1.5)
ax.text(gaps.mean() - 0.02, ax.get_ylim()[1] * 0.95, T(f"平均 {gaps.mean():.2f} mm", f"mean {gaps.mean():.2f} mm"), color=C["accent"], fontsize=9.5, ha="right", bbox=box)
ax.axvline(gaps.max(), color=C["x"], lw=1.2, ls="--")
ax.text(gaps.max() - 0.02, ax.get_ylim()[1] * 0.95, T(f"最大 {gaps.max():.2f} mm", f"max {gaps.max():.2f} mm"), color=C["x"], fontsize=9.5, ha="right", bbox=box)
ax.set_xlabel(T("末端位置之差 / mm", "Difference in end-effector position / mm"))
ax.set_ylabel(T("关节角组数", "Number of joint-angle sets"))
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig12_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 12.3.2
sc = Model("B-SCA-WQ4", "base", "tool")
M = sc.fk(np.zeros(4))
scr = sc.screws()
fig, ax = axes3d(plt, size=(6.0, 4.4), elev=14, azim=-70)
col = np.array([[0, 0, 0], [0, 0, 0.4]])
ax.plot(*col.T, color="#9aa6ad", lw=10, solid_capstyle="round")
arm = np.array([[0, 0, 0.4], [0.35, 0, 0.4], [0.6, 0, 0.448]])
ax.plot(*arm.T, color="#9aa6ad", lw=8, solid_capstyle="round")
quill = np.array([[0.6, 0, 0.5], [0.6, 0, M[2, 3]]])
ax.plot(*quill.T, color="#6d7a82", lw=4)
labels = [T("轴1（转动）", "axis 1 (revolute)"), T("轴2（转动）", "axis 2 (revolute)"),
          T("关节3（移动）\n向下为正", "joint 3 (prismatic)\npositive downwards"), T("轴4（转动）", "axis 4 (revolute)")]
for i, (name, kind, w, q, S) in enumerate(scr):
    if kind == "prismatic":
        ax.quiver(*(q + np.array([0.05, 0, 0.05])), *(0.15 * w), color=C["x"], lw=2.4, arrow_length_ratio=0.25)
        ax.text(*(q + np.array([-0.04, 0, -0.19])), labels[i], fontsize=9.5, color=C["x"], ha="right")
    else:
        ax.quiver(*(q - 0.06 * w), *(0.2 * w), color=C["accent"], lw=2.2, arrow_length_ratio=0.2)
        off = np.array([-0.3, 0, -0.3]) if i == 3 else np.array([0.01, 0, 0])
        ax.text(*(q + 0.16 * w + off), labels[i], fontsize=9.5, color=C["accent"])
frame3d(ax, np.eye(4), 0.12, "{s}")
frame3d(ax, M, 0.08, "")
ax.text(*(M[:3, 3] + np.array([0.03, 0, -0.06])), "{b}", fontsize=10)
equal3d(ax, np.r_[col, arm, quill, [[0.7, 0.1, 0.0]]], pad=0.0)
ax.set_box_aspect((1, 1, 1), zoom=1.25)
figure(fig, "fig12_3_2")
plt.close(fig)
