"""31.1 节的示意图。

图 31.1.1：WQ-CR5 手臂水平伸直、工具朝下、带 5 kg：(a) 侧视简图与各零件的重力（箭头长短按重量）；
          (b) 沿大臂、小臂的剪力、弯矩、扭矩图（wqcr5.py 的 section()），竖虚线是 J3。
"""
import numpy as np

from _ch31 import G0, Q_OUT, W
from bookout import COLORS as C, T, figure, style

plt = style()
q = Q_OUT
a2, a3 = abs(W.DH[1]["a"]), abs(W.DH[2]["a"])
o2 = W.link_world(q)[1][:3, 3]
fig = plt.figure(figsize=(11.0, 7.4))
gs = fig.add_gridspec(4, 1, height_ratios=[1.3, 1, 1, 1], hspace=0.18)
ax = fig.add_subplot(gs[0])
# 侧视：x 取离 J2 的水平距离（伸直沿 −x），z 取高度
pts = W.gravity_points(q)
groups = {}
for i, m, r, name in pts:
    key = "管与罩壳" if ("铝管" in name or "罩壳" in name) else name
    x = o2[0] - r[0]
    if key == "管与罩壳":
        groups.setdefault((key, i), []).append((x, r[2], m))
    else:
        groups.setdefault((key, i), []).append((x, r[2], m))
ax.plot([0, a2], [0, 0], color=C["muted"], lw=9, solid_capstyle="round", alpha=0.5)
ax.plot([a2, a2 + a3], [0, 0], color=C["muted"], lw=7, solid_capstyle="round", alpha=0.5)
for x, lab in ((0, "J2"), (a2, "J3")):
    ax.plot(x, 0, "o", ms=18, color=C["z"], alpha=0.8)
    ax.text(x, 0.06, lab, ha="center", fontsize=9)
sc = 0.006                                                       # m / N
for (key, i), v in groups.items():
    v = np.array(v)
    m = v[:, 2].sum()
    x = (v[:, 0] * v[:, 2]).sum() / m
    z = (v[:, 1] * v[:, 2]).sum() / m - o2[2]
    if key == "管与罩壳" or m < 0.05 or i == 0:                  # 构件 0（J2 模组在肩座上）不压在手臂上
        continue
    ax.annotate("", xy=(x, z - sc * m * G0), xytext=(x, z), arrowprops=dict(arrowstyle="->", color=C["x"] if key == "负载" else C["ink"], lw=1.3))
xs = np.linspace(0, a2, 9)[1:-1]
for x in xs:
    ax.annotate("", xy=(x, -0.06), xytext=(x, -0.01), arrowprops=dict(arrowstyle="->", color=C["muted"], lw=0.8))
for x in np.linspace(a2, a2 + a3, 8)[1:-1]:
    ax.annotate("", xy=(x, -0.05), xytext=(x, -0.01), arrowprops=dict(arrowstyle="->", color=C["muted"], lw=0.8))
tcp = W.link_world(q)[5] @ np.append(W.tcp_local(), 1.0)
ax.plot([a2 + a3, o2[0] - tcp[0]], [0, tcp[2] - o2[2]], color=C["ink"], lw=1.2)
ax.text(o2[0] - tcp[0] + 0.02, tcp[2] - o2[2] - 0.12, T("5 kg 负载", "5 kg payload"), color=C["x"], fontsize=9)
ax.text(0.05, 0.12, T("黑箭头：模组、连接件、法兰；灰箭头：管与罩壳（均布）", "black: modules, connectors, flange; grey: tubes and covers (spread)"), fontsize=8)
ax.set_xlim(-0.08, 1.0)
ax.set_ylim(-0.5, 0.16)
ax.axis("off")
ax.set_title(T("(a) 手臂水平伸直、工具朝下、带 5 kg：各零件的重力", "(a) outstretched, tool down, 5 kg: the weights"), fontsize=11)
s = np.linspace(0, 1, 81)
xu = s * a2
xf = a2 + s * a3
su = [W.section(q, 1, v) for v in s]
sf = [W.section(q, 2, v) for v in s]
labels = [("V", T("剪力 V / N", "shear V / N")), ("Mb", T("弯矩 M / (N·m)", "bending M / (N·m)")), ("T", T("扭矩 T / (N·m)", "torsion T / (N·m)"))]
for k, (key, lab) in enumerate(labels):
    ax = fig.add_subplot(gs[k + 1])
    yu = np.abs([x[key] for x in su])
    yf = np.abs([x[key] for x in sf])
    ax.fill_between(xu, 0, yu, color=C["z"], alpha=0.25)
    ax.fill_between(xf, 0, yf, color=C["y"], alpha=0.25)
    ax.plot(xu, yu, color=C["z"], lw=1.5)
    ax.plot(xf, yf, color=C["y"], lw=1.5)
    ax.axvline(a2, color=C["muted"], ls="--", lw=0.8)
    ax.set_ylabel(lab, fontsize=9)
    ax.set_xlim(-0.08, 1.0)
    ax.set_ylim(0, max(yu.max(), yf.max()) * 1.2)
    ax.text(0.01, yu[0] * 1.02, "{:.1f}".format(yu[0]), fontsize=8, va="bottom")
    ax.text(a2 + 0.01, yf[0] * 1.02, "{:.1f}".format(yf[0]), fontsize=8, va="bottom")
    if k == 0:
        ax.set_title(T("(b) 沿手臂的剪力、弯矩、扭矩图", "(b) shear, bending and torsion along the arm"), fontsize=11)
    if k < 2:
        ax.set_xticklabels([])
    else:
        ax.set_xlabel(T("离 J2 轴的距离 / m（蓝：大臂，绿：小臂）", "distance from the J2 axis / m (blue: upper arm, green: forearm)"))
figure(fig, "fig31_1_1")
