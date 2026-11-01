"""16.8 节的示意图。

图 16.8.1：案例用的缺陷图长什么样——一行三类缺陷，从轻到重；最右是合格件。
图 16.8.2：（a）三种训练集的检出曲线；（b）分类看：合成图分布一偏，没合成的那一类掉得最狠。
"""
import numpy as np

from _ch16 import (auc, dataset, defect_image, knn_score, recall_at_fpr, KINDS, SEV)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 16.8.1
g = np.random.default_rng(321)
sevs = (0.10, 0.20, 0.35)
fig, axes = plt.subplots(4, 4, figsize=(9.2, 9.2))
for i, kind in enumerate((1, 2, 3)):
    for j, s in enumerate(sevs):
        ax = axes[i][j]
        im = defect_image(kind, s, g)
        ax.imshow(im, cmap="gray", vmin=im.min(), vmax=im.max())
        ax.set_xticks([])
        ax.set_yticks([])
        if i == 0:
            ax.set_title(T(f"严重度 {s:.2f}", f"severity {s:.2f}"), fontsize=9)
        if j == 0:
            ax.set_ylabel(T(KINDS[kind], ("scratch", "dent", "rust")[kind - 1]), fontsize=10)
    ax = axes[i][3]
    im = defect_image(0, 0.0, g)
    ax.imshow(im, cmap="gray", vmin=im.min(), vmax=im.max())
    ax.set_xticks([])
    ax.set_yticks([])
    if i == 0:
        ax.set_title(T("合格件", "defect-free"), fontsize=9)
# 第四行：偏了的那批合成图——底纹的朝向与照明是固定的，一眼就与上面三行不一样
for j, kind in enumerate((1, 2, 3)):
    ax = axes[3][j]
    im = defect_image(kind, 0.30, g, plain_bg=True)
    ax.imshow(im, cmap="gray", vmin=im.min(), vmax=im.max())
    ax.set_xticks([])
    ax.set_yticks([])
    if j == 0:
        ax.set_ylabel(T("偏了的合成图\n（都是 0.30）", "biased synthetic\n(all at 0.30)"), fontsize=9)
ax = axes[3][3]
im = defect_image(0, 0.0, g, plain_bg=True)
ax.imshow(im, cmap="gray", vmin=im.min(), vmax=im.max())
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel(T("底纹的朝向与照明固定了", "texture orientation and lighting frozen"), fontsize=8)
fig.suptitle(T(f"案例里的缺陷图（对比度已拉开）：严重度在 {SEV[0]:.2f}—{SEV[1]:.2f} 之间，"
               f"起伏常比磨削刀纹还小",
               f"Defect images (contrast stretched): severity {SEV[0]:.2f}–{SEV[1]:.2f}, "
               f"often fainter than the machining texture"),
             fontsize=10)
fig.tight_layout()
figure(fig, "fig16_8_1")

# ---------------------------------------------------------------- 图 16.8.2
N_TEST, N_REAL, N_SYN, SEEDS = 3000, 60, 900, 5
Xte, yte, kte = dataset(N_TEST, seed=99)
Xs, ys, _ = dataset(N_SYN, seed=2)
Xb, yb, _ = dataset(N_SYN, seed=3, sev_range=(0.25, SEV[1]), kinds=(0, 1, 3), p=[0.7, 0.15, 0.15],
                    plain_bg=True)

cases = [
    (T(f"只用 {N_REAL} 张真实图", f"{N_REAL} real only"), C["x"], lambda Xr, yr: (Xr, yr)),
    (T(f"+{N_SYN} 张合成（分布对得上）", f"+{N_SYN} synthetic (matched)"), C["y"],
     lambda Xr, yr: (np.r_[Xr, Xs], np.r_[yr, ys])),
    (T(f"+{N_SYN} 张合成（分布偏了）", f"+{N_SYN} synthetic (biased)"), C["z"],
     lambda Xr, yr: (np.r_[Xr, Xb], np.r_[yr, yb])),
]

fig2, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.3))
fprs = np.linspace(0.01, 0.5, 30)
per_case = {}
for lab, col, make in cases:
    curves, aucs, pers = [], [], []
    for s in range(SEEDS):
        Xr, yr, _ = dataset(N_REAL, seed=10 + s)
        X, y = make(Xr, yr)
        sc = knn_score(X, y, Xte)
        curves.append([recall_at_fpr(sc, yte, f) for f in fprs])
        aucs.append(auc(sc, yte))
        pers.append([recall_at_fpr(sc[(kte == 0) | (kte == k)],
                                   (kte[(kte == 0) | (kte == k)] == k).astype(int)) for k in (1, 2, 3)])
    m = np.mean(curves, 0)
    a.plot(fprs * 100, m * 100, color=col, lw=1.9,
           label=T(f"{lab}（曲线下面积 {np.mean(aucs):.3f}）", f"{lab} (AUC {np.mean(aucs):.3f})"))
    per_case[lab] = np.mean(pers, 0) * 100

Xb2, yb2, _ = dataset(N_REAL + N_SYN, seed=20)
sc = knn_score(Xb2, yb2, Xte)
a.plot(fprs * 100, [recall_at_fpr(sc, yte, f) * 100 for f in fprs], color=C["muted"], ls="--", lw=1.6,
       label=T(f"{N_REAL + N_SYN} 张全是真实图（参照，曲线下面积 {auc(sc, yte):.3f}）",
               f"{N_REAL + N_SYN} real (reference, AUC {auc(sc, yte):.3f})"))
a.set_xlabel(T("误报率（%）", "false-alarm rate (%)"))
a.set_ylabel(T("查出的缺陷比例（%）", "defects caught (%)"))
a.set_title(T("(a) 补对了的合成图几乎追平全真", "(a) Matched synthetic nearly matches all-real"),
            fontsize=10)
a.legend(fontsize=7.5, loc="lower right")
a.grid(alpha=0.25, lw=0.5)

labels = [c[0] for c in cases]
kinds_zh = [T(KINDS[k], ("scratch", "dent", "rust")[k - 1]) for k in (1, 2, 3)]
width = 0.26
xs = np.arange(len(kinds_zh))
for i, (lab, col, _) in enumerate(cases):
    b.bar(xs + (i - 1) * width, per_case[lab], width, color=col, label=lab)
b.set_xticks(xs)
b.set_xticklabels(kinds_zh)
b.set_ylabel(T("误报压到 5% 时的查出率（%）", "recall at 5% false-alarm rate (%)"))
b.set_title(T("(b) 补错了，三类全倒退，没合成的那一类最惨",
               "(b) Biased synthetic data hurts every class, the missing one most"),
            fontsize=10)
b.legend(fontsize=7.5)
b.grid(alpha=0.25, lw=0.5, axis="y")
b.annotate(T("合成时漏掉的就是这一类", "this class was missing from the synthetic set"),
           xy=(1 + width, per_case[labels[2]][1]), xytext=(0.55, 68), fontsize=8,
           arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.0))

fig2.tight_layout()
figure(fig2, "fig16_8_2")
