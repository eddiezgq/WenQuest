"""Section 2.4, concept evaluation: Pugh matrix and weighted scores of the four docking concepts for the Go2 charging dock;
whether the ranking holds when the weights are perturbed at random (Examples 2.4.1 and 2.4.2, Fig. 2.4.1)."""
import numpy as np

import _ch2 as H
import _dock as K
from bookout import T, figure, out, style

names = list(K.CONCEPTS)
w = np.array([c[2] for c in K.CRITERIA])
assert abs(w.sum() - 1) < 1e-12
S = np.array([K.SCORES[n] for n in names], float)
total = S @ w
order = list(np.argsort(-total))
pugh = {n: (sum(v > 0 for v in K.PUGH[n]), sum(v < 0 for v in K.PUGH[n]), sum(K.PUGH[n])) for n in K.PUGH}

# ---- sensitivity to the weights: weights perturbed about their nominal values by a Dirichlet distribution (concentration 50); count how often each concept ranks first
rng = np.random.default_rng(2026)
W = rng.dirichlet(w * 50, size=20000)
win = np.bincount(np.argmax(W @ S.T, axis=1), minlength=len(names)) / len(W)
# result when the weight of "docking success" is raised from 0.25 to 0.40 (the others scaled down in proportion)
w2 = w * (0.60 / (1 - w[0]))
w2[0] = 0.40
total2 = S @ w2

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.9, 2.8), gridspec_kw={"width_ratios": [1.1, 1]})
cols = ["#2c6fbb", "#2ca02c", "#c0392b", "#8e44ad"]
a1.bar(range(len(names)), total, color=cols, width=0.6)
for k, v in enumerate(total):
    a1.text(k, v + 0.03, "{:.2f}".format(v), ha="center", fontsize=8)
a1.set_xticks(range(len(names)))
a1.set_xticklabels(names)
a1.set_ylim(0, 5)
a1.set_ylabel(T("加权得分（满分 5）", "weighted score (max 5)"), fontsize=9)
a1.set_title(T("名义权重", "nominal weights"), fontsize=9)
a2.bar(range(len(names)), win * 100, color=cols, width=0.6)
for k, v in enumerate(win):
    a2.text(k, v * 100 + 1, "{:.0f}%".format(v * 100), ha="center", fontsize=8)
a2.set_xticks(range(len(names)))
a2.set_xticklabels(names)
a2.set_ylim(0, 100)
a2.set_ylabel(T("排第一的概率 / %", "chance of ranking first / %"), fontsize=9)
a2.set_title(T("权重随机扰动 2 万次", "20 000 random weight sets"), fontsize=9)
for ax in (a1, a2):
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_4_1")

out(n_crit=len(K.CRITERIA), **{"t_" + n: float(total[k]) for k, n in enumerate(names)}, **{"t2_" + n: float(total2[k]) for k, n in enumerate(names)},
    **{"win_" + n: float(win[k] * 100) for k, n in enumerate(names)},
    **{"p_" + n: pugh[n][0] for n in pugh}, **{"m_" + n: pugh[n][1] for n in pugh}, **{"net_" + n: pugh[n][2] for n in pugh},
    best=names[order[0]], second=names[order[1]], best2=names[int(np.argmax(total2))], gap=float(total[order[0]] - total[order[1]]))
