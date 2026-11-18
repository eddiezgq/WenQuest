"""20.4 节的图：划分口径第三次露面——按帧、按体系、按成分，三个误差差几倍。

图 20.4.2：（a）一条结构松弛轨迹的相邻帧有多像（帧与帧之间原子位移的量级），
这就是“按帧随机划分”会泄漏的原因；（b）总帧数固定，把它们摊成“少体系多帧”还是
“多体系少帧”，泄漏严重程度差一个数量级——而前者正是这类数据集最常见的形状。
"""
import numpy as np

from _ch20 import (BASIS, basis_centers, energy_mae, fit_potential, force_mae,
                   make_trajectories, split_frames)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
L, N = 12.0, 10
CENTERS, WIDTH = basis_centers(), BASIS["width"]

N_SYS, N_FRAMES = 10, 36          # 与算例 20.5 同一套数据，数字对得上
systems = make_trajectories(N_SYS, N, L, seed=0, n_frames=N_FRAMES)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 相邻帧有多像
spacing = L / N
first = []
for s_, col in zip(systems[:3], (C["z"], C["y"], C["x"])):
    xs = [fr["x"] for fr in s_["frames"]][-12:]
    step = [float(np.abs(xs[i + 1] - xs[i]).max()) / spacing * 100
            for i in range(len(xs) - 1)]
    first.extend(step)
    a.semilogy(np.arange(1, len(xs)), step, "o-", color=col, lw=1.8, ms=5,
               label=T(f"体系 {s_['sys']}", f"system {s_['sys']}"))
a.set_xlabel(T("第几对相邻帧（取自同一条松弛轨迹）",
               "consecutive frame pair (same relaxation trajectory)"))
a.set_ylabel(T("两帧之间最大的原子位移（占晶格间距的百分之几）",
               "largest displacement between frames (% of lattice spacing)"))
a.set_title(T("(a) 松弛轨迹的帧挤在收敛那一头", "(a) frames crowd near convergence"),
            fontsize=10)
a.annotate(T(f"相邻两帧最多只差晶格间距的 {max(first):.3f}%——\n"
             f"把它们分到训练集与测试集两边，测试集里每一帧\n"
             f"在训练集里都有一个几乎相同的孪生兄弟",
             f"neighbouring frames differ by at most {max(first):.3f}% of the spacing"),
           xy=(0.03, 0.30), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["accent"])
a.legend(fontsize=8, loc="upper right", framealpha=0.92)
a.margins(y=0.3)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 泄漏有多严重，取决于数据集的形状（与算例 20.5 第二部分同一套做法）
SHAPES = [(5, 72), (10, 36), (30, 12), (60, 6)]
SEEDS = range(8)
ratios, e_frame_abs = [], []
for n_sys, n_fr in SHAPES:
    sysx = make_trajectories(n_sys, N, L, seed=5, n_frames=n_fr)
    got = {}
    for h in ("frame", "system"):
        es = []
        for sd in SEEDS:
            tr, te = split_frames(sysx, h, seed=sd)
            w = fit_potential([(fr["x"], fr["e"]) for _, _, fr in tr], L, CENTERS, WIDTH,
                              force_weight=0.1, force_data=[fr["f"] for _, _, fr in tr])
            es.append(energy_mae(w, te, L, CENTERS, WIDTH))
        got[h] = float(np.median(es))
    ratios.append(got["system"] / got["frame"])
    e_frame_abs.append(got["frame"])

xs = np.arange(len(SHAPES))
cols = [C["x"], C["accent"], C["y"], C["muted"]]
b.bar(xs, ratios, 0.55, color=cols)
b.axhline(1.0, color=C["ink"], ls=":", lw=1.2)
for i, r in enumerate(ratios):
    b.annotate(f"×{r:.1f}", xy=(i, r), xytext=(0, 5), textcoords="offset points",
               ha="center", fontsize=9, color=cols[i])
b.set_yscale("log")
b.set_xticks(xs)
b.set_xticklabels([T(f"{a} 个体系\n× 每个 {c} 帧", f"{a} systems\n× {c} frames")
                   for a, c in SHAPES], fontsize=8.5)
b.set_ylabel(T("按体系划分的误差是按帧划分的几倍（对数轴）",
               "times worse when split by system (log scale)"))
b.set_title(T("(b) 总帧数一样，泄漏严重到什么程度全看形状",
              "(b) same total frames: the shape decides how bad the leak is"), fontsize=10)
b.annotate(T(f"总帧数都是 {SHAPES[0][0] * SHAPES[0][1]} 帧，{len(list(SEEDS))} 折取中位数。"
             f"\n“少体系、多帧”恰恰是结构松弛轨迹数据集最常见的形状——"
             f"\n而它正是泄漏最厉害的那一种",
             f"few systems with many frames is both the commonest shape and the leakiest"),
           xy=(0.5, 0.80), xycoords="axes fraction", ha="center",
           fontsize=8.5, color=C["accent"])
b.margins(y=0.45)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig20_4_2")
