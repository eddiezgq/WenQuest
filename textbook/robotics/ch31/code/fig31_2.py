"""31.2 节的示意图。

图 31.2.1：(a) 手臂水平伸直、加上 5 kg 负载时 TCP 又下沉多少，按来源分（关节按 K1、K3 两种算）；
          (b) 工具朝下、手臂伸到不同远处时 TCP 的竖直刚度 k_z = 1/C_zz（只计关节，K1、K3）。
"""
import math

import numpy as np

from _ch31 import Q_OUT, W, deflection, joint_K, joint_compliance_x, load_points, tcp_point
from bookout import COLORS as C, T, figure, style

plt = style()
q = Q_OUT
fig, axs = plt.subplots(1, 2, figsize=(11.8, 4.0), gridspec_kw={"width_ratios": [1.1, 1.0]})
ax = axs[0]
src = [("J2", T("J2 减速器", "J2 gear")), ("J3", T("J3 减速器", "J3 gear")), ("wrist", T("J4–J6 减速器", "J4–J6 gears")),
       ("upper_bend", T("大臂弯曲", "upper-arm bending")), ("fore_bend", T("小臂弯曲", "forearm bending")), ("tors", T("两管扭转", "tube torsion"))]
cols = [C["x"], "#ff9896", "#f7b6d2", C["z"], "#9ecae1", C["muted"]]
for row, (which, lab) in enumerate(((0, "K1"), (2, "K3"))):
    d = deflection(q, load_points(q, self_weight=False), K=joint_K(which), n_sec=100)
    z = {k: -v[2] * 1000 for k, v in d.items()}
    vals = [z["J2"], z["J3"], z["J4"] + z["J5"] + z["J6"] + z["J1"], z["upper_bend"], z["fore_bend"], z["upper_tors"] + z["fore_tors"]]
    left = 0.0
    for k, v in enumerate(vals):
        ax.barh(row, v, left=left, color=cols[k], edgecolor="white", label=src[k][1] if row == 0 else None)
        left += v
    ax.text(left + 0.02, row, "{:.2f} mm".format(left), va="center", fontsize=9)
ax.set_yticks([0, 1], [T("关节按 K1", "joints at K1"), T("关节按 K3", "joints at K3")])
ax.invert_yaxis()
ax.set_xlim(0, 1.45)
ax.set_xlabel(T("加 5 kg 后 TCP 又下沉 / mm", "extra TCP sag with 5 kg / mm"))
ax.legend(fontsize=8, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.22))
ax.set_title(T("(a) 下沉从哪里来（手臂水平伸直）", "(a) where the sag comes from (outstretched)"), fontsize=11)
ax = axs[1]
for which, col, lab in ((0, C["x"], "K1"), (2, C["z"], "K3")):
    rows = []
    for al in np.radians(np.arange(0.0, 70.1, 2.5)):
        qq = np.array([0, -al, 2 * al, 0, -math.pi / 2, 0.0])
        qq[3] = -(qq[1] + qq[2]) - math.pi / 2
        rows.append((float(np.hypot(*tcp_point(qq)[:2])), 1 / joint_compliance_x(qq, joint_K(which))[2, 2] / 1000))
    rows = np.array(rows)
    ax.plot(rows[:, 0], rows[:, 1], color=col, lw=1.6, label=lab)
ax.set_xlabel(T("TCP 离 J1 轴的水平距离 / m（工具朝下）", "horizontal distance of the TCP from J1 / m (tool down)"))
ax.set_ylabel(T("竖直刚度 $k_z$ / (N/mm)", "vertical stiffness $k_z$ / (N/mm)"))
ax.set_ylim(0, None)
ax.legend(fontsize=8, frameon=False)
ax.set_title(T("(b) 伸得越远越软（只计关节）", "(b) softer the farther it reaches (joints only)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig31_2_1")
