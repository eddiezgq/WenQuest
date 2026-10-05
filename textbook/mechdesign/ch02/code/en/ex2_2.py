"""Section 2.2, functional decomposition and morphological matrix: the docking mechanism of an automatic charging dock for
the Go2 (Example 2.2.1, Fig. 2.2.1)."""
import itertools
import math

import _ch2 as H
import _dock as K
from bookout import T, figure, out, style

g = H.go2()
n_all = math.prod(len(f[2]) for f in K.FUNCS)


def ok(combo):
    pick = set(enumerate(combo))
    return not any(a in pick and b in pick for a, b in K.INCOMPATIBLE)


n_ok = sum(ok(c) for c in itertools.product(*[range(len(f[2])) for f in K.FUNCS]))

plt = style()
fig, ax = plt.subplots(figsize=(6.9, 3.6))
ncol = max(len(f[2]) for f in K.FUNCS)
cols = {"A": "#2c6fbb", "B": "#2ca02c", "C": "#c0392b", "D": "#8e44ad"}
for i, (zh, en, opts) in enumerate(K.FUNCS):
    y = len(K.FUNCS) - 1 - i
    H.box(ax, 0, y + 0.1, 1.9, 0.8, T(zh, en), H.PALE["blue"], 7.5, True)
    for j, (oz, oe) in enumerate(opts):
        H.box(ax, 2.1 + j * 1.75, y + 0.1, 1.6, 0.8, T(oz, oe), "#ffffff", 7)
        ax.texts[-1].set_y(y + 0.62)
for k, (name, (cz, ce, pick)) in enumerate(K.CONCEPTS.items()):
    for i, j in enumerate(pick):
        y = len(K.FUNCS) - 1 - i
        x = 2.1 + j * 1.75 + 0.2 + k * 0.4
        ax.add_patch(H.FancyBboxPatch((x - 0.15, y + 0.13), 0.3, 0.2, boxstyle="round,pad=0.01", fc=cols[name], ec="none"))
        ax.text(x, y + 0.23, name, ha="center", va="center", fontsize=6.5, color="white", weight="bold")
    ax.plot([], [], "s", color=cols[name], ms=7, label=T("{}：{}", "{}: {}").format(name, T(cz, ce)))
ax.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.55, -0.02), ncol=4)
ax.set_xlim(-0.1, 2.1 + ncol * 1.75)
ax.set_ylim(-0.1, len(K.FUNCS) + 0.05)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig2_2_1")

out(n_func=len(K.FUNCS), n_all=n_all, n_ok=n_ok, n_concepts=len(K.CONCEPTS), weight=g["weight_kg"], payload=g["payload_kg"],
    footprint=g["footprint_mm"], height=g["height_mm"], opts=T("、", ", ").join(str(len(f[2])) for f in K.FUNCS))
