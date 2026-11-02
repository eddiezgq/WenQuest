"""18.1 节的示意图。

图 18.1.1：（a）两种完全不同的"错"——整个域摆一下，与每个残基各抖一点；
（b）四个指标在这两种错上给出**方向相反**的结论。
"""
import numpy as np

from _ch18 import gdt_ts, hinge, jitter, lddt, rmsd, tm_score, two_domain
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

ref = two_domain()
half = len(ref) // 2

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.4))

# ---------------- (a) 两种错长什么样（投影到 xz 平面；只画点，连线会成一团乱麻）
bent = hinge(ref, 90)
shook = jitter(ref, 1.0)
MARK = half + 8                      # 盯住第二个域里的一个残基，看它去了哪

a.scatter(ref[:half, 0], ref[:half, 2], s=14, color=C["muted"], alpha=0.55,
          label=T("真实结构", "reference"))
a.scatter(ref[half:, 0], ref[half:, 2], s=14, color=C["muted"], alpha=0.55)
a.scatter(bent[half:, 0], bent[half:, 2], s=14, color=C["y"], alpha=0.75,
          label=T("整个域摆了 90°", "one domain swung 90°"))
a.scatter(shook[:half, 0], shook[:half, 2], s=10, color=C["z"], alpha=0.6, marker="x",
          label=T("每个残基各抖 1 Å", "every residue jittered 1 Å"))
a.annotate("", xy=(bent[MARK, 0], bent[MARK, 2]), xytext=(ref[MARK, 0], ref[MARK, 2]),
           arrowprops=dict(arrowstyle="->", color=C["y"], lw=1.6))
a.plot([ref[MARK, 0]], [ref[MARK, 2]], "o", color=C["x"], ms=7)
a.plot([bent[MARK, 0]], [bent[MARK, 2]], "o", color=C["x"], ms=7, mfc="none", mew=1.6)
a.annotate(T("同一个残基，域内一点没变", "same residue; nothing inside the domain moved"),
           xy=(ref[MARK, 0], ref[MARK, 2]), xytext=(2.0, 9.4), fontsize=8, color=C["x"])
a.set_xlabel("x (Å)")
a.set_ylabel("z (Å)")
a.set_title(T("(a) 两种完全不同的错", "(a) Two very different kinds of error"), fontsize=10)
a.legend(fontsize=8, loc="lower left")
a.set_aspect("equal", adjustable="datalim")
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 四个指标，两种错
angles = np.arange(0, 95, 5)
sigmas = np.linspace(0, 2.2, 20)
h = [(gdt_ts(hinge(ref, t), ref) / 100, lddt(hinge(ref, t), ref),
      tm_score(hinge(ref, t), ref)) for t in angles]
j = [(gdt_ts(jitter(ref, s), ref) / 100, lddt(jitter(ref, s), ref),
      tm_score(jitter(ref, s), ref)) for s in sigmas]
h = np.array(h); j = np.array(j)

xs_h = np.linspace(0, 1, len(angles))
xs_j = np.linspace(0, 1, len(sigmas))
for k, (col, name) in enumerate(((C["x"], "GDT_TS/100"), (C["y"], "lDDT"), (C["z"], "TM-score"))):
    b.plot(xs_h, h[:, k], "-", color=col, lw=2.0, label=f"{name}" + T("（域摆动）", " (swing)"))
    b.plot(xs_j, j[:, k], "--", color=col, lw=1.6, label=f"{name}" + T("（残基抖动）", " (jitter)"))
b.set_xlabel(T("错得越来越厉害 →（实线：域摆 0—90°；虚线：抖 0—2.2 Å）",
               "worse to the right (solid: swing 0–90°; dashed: jitter 0–2.2 Å)"), fontsize=9)
b.set_ylabel(T("指标值", "metric"))
b.set_ylim(0, 1.05)
b.set_title(T("(b) 同样是'变差'，三条线走法完全不同",
              "(b) The same 'getting worse', three different curves"), fontsize=10)
b.legend(fontsize=7.5, ncol=2, loc="lower left")
b.grid(alpha=0.25, lw=0.5)
b.annotate(T("域摆动：lDDT 几乎不动", "swing: lDDT barely moves"),
           xy=(0.95, lddt(hinge(ref, 90), ref)), xytext=(0.42, 0.93), fontsize=8,
           color=C["y"], arrowprops=dict(arrowstyle="->", color=C["y"], lw=1.0))
b.annotate(T("残基抖动：lDDT 塌得最快", "jitter: lDDT falls fastest"),
           xy=(0.95, lddt(jitter(ref, 2.2), ref)), xytext=(0.30, 0.22), fontsize=8,
           color=C["y"], arrowprops=dict(arrowstyle="->", color=C["y"], lw=1.0))

fig.tight_layout()
figure(fig, "fig18_1_1")
