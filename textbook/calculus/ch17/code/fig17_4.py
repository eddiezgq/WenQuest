"""图 17.4.1：左：均匀细杆分成 10 段，每段对转动惯量的贡献 r²Δm（绕端点与绕中点）；
右：UR5e 上臂绕肩关节轴的转动惯量构成（自身绕质心的部分、平行轴项 m d²），与电机转子经减速器折算的惯量比较。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
n = 10
xm = (np.arange(n) + 0.5) / n
a1.bar(xm - 0.02, xm ** 2 / n, width=0.04, color=BLUE, label=T("绕端点：Σ = 0.3325 → 1/3", "about the end: Σ = 0.3325 → 1/3"))
a1.bar(xm + 0.02, (xm - 0.5) ** 2 / n, width=0.04, color=GREEN, label=T("绕中点：Σ = 0.0825 → 1/12", "about the middle: Σ = 0.0825 → 1/12"))
a1.set_xlabel(T("小段的位置 x / L", "segment position x / L"))
a1.set_ylabel(T("贡献 r²Δm / (mL²)", "contribution r²Δm / (mL²)"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("离轴越远的部分，贡献越大（与 r² 成正比）", "Parts far from the axis dominate (∝ r²)"), fontsize=10)
clean(a1)
labels = [T("上臂绕质心\n0.134", "arm about CM\n0.134"), T("平行轴项 m d²\n0.379", "parallel-axis m d²\n0.379"), T("合计（绕肩轴）\n0.513", "total (shoulder)\n0.513"), T("转子折算 N²I_m\n1.02", "rotor reflected N²I_m\n1.02")]
vals = [0.1339, 0.3790, 0.5129, 1.0201]
a2.bar(range(4), vals, color=[BLUE, ACC, RED, MUTED])
a2.set_xticks(range(4))
a2.set_xticklabels(labels, fontsize=9)
a2.set_ylabel(T("转动惯量 / (kg·m²)", "moment of inertia / (kg·m²)"))
a2.set_title(T("UR5e 上臂（零件库模型）与电机转子的折算惯量", "UR5e upper arm (library model) vs reflected rotor inertia"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig17_4_1")
