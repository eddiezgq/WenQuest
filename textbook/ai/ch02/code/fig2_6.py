"""2.6 节的示意图。

图 2.6.1：病态二次函数 L = ½(w₁² + 100 w₂²) 上三种方法的前 60 步：梯度下降沿陡峭方向来回振荡、沿平缓方向缓慢前进；
动量法积累了平缓方向的速度；Adam 按各坐标梯度的大小自动缩放步长。
图 2.6.2：（a）小批量随机梯度下降：批越小，损失的波动越大；（b）20 层 ReLU 网络各层输出的标准差：He 初始化保持稳定。
"""
import math

import numpy as np

from _ch2 import rig_data
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
lam = np.array([1.0, 100.0])
w0 = np.array([-5.0, 1.0])


def traj(kind, n=60):
    w, v, m, s = w0.copy(), np.zeros(2), np.zeros(2), np.zeros(2)
    pts = [w.copy()]
    for k in range(1, n + 1):
        g = lam * w
        if kind == "gd":
            w = w - 2 / 101 * g
        elif kind == "mom":
            v = 0.6694 * v - 0.03306 * g
            w = w + v
        else:
            m = 0.9 * m + 0.1 * g
            s = 0.999 * s + 0.001 * g * g
            w = w - 0.05 * (m / (1 - 0.9 ** k)) / (np.sqrt(s / (1 - 0.999 ** k)) + 1e-8)
        pts.append(w.copy())
    return np.array(pts)


fig, ax = plt.subplots(figsize=(9.6, 3.9))
g1, g2 = np.meshgrid(np.linspace(-5.5, 1.0, 300), np.linspace(-1.3, 1.3, 200))
ax.contour(g1, g2, 0.5 * (g1 ** 2 + 100 * g2 ** 2), levels=np.geomspace(0.05, 60, 12), colors=[C["muted"]], linewidths=0.6)
for kind, col, name in (("gd", C["x"], T("梯度下降", "gradient descent")), ("mom", C["z"], T("动量法", "momentum")),
                        ("adam", C["accent"], "Adam")):
    p = traj(kind)
    ax.plot(p[:, 0], p[:, 1], "o-", color=col, ms=2.5, lw=1.1, label=name)
ax.plot(0, 0, "*", color=C["ink"], ms=12)
ax.plot(*w0, "s", color=C["ink"], ms=6)
ax.text(w0[0], w0[1] + 0.12, T("起点", "start"), fontsize=9)
ax.set_xlabel("$w_1$")
ax.set_ylabel("$w_2$")
ax.legend(fontsize=9, frameon=True, framealpha=0.9, loc="lower right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig2_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.6.2
x, y = rig_data()
A = np.c_[(x - x.mean()) / x.std(), np.ones(len(x))]
L_star = float(np.mean((A @ np.linalg.lstsq(A, y, rcond=None)[0] - y) ** 2))
rng = np.random.default_rng(5)
fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.8))
ax = axs[0]
for Bsz, col in ((1, C["x"]), (4, C["accent"]), (40, C["z"])):
    v = np.zeros(2)
    ls = []
    for step in range(600):
        idx = rng.choice(len(y), Bsz, replace=False)
        v = v - 0.05 * 2 / Bsz * A[idx].T @ (A[idx] @ v - y[idx])
        ls.append(np.mean((A @ v - y) ** 2) - L_star)
    ax.semilogy(np.maximum(ls, 1e-6), color=col, lw=1.0, label=T(f"批大小 {Bsz}", f"batch {Bsz}") + (T("（全批）", " (full)") if Bsz == 40 else ""))
ax.set_xlabel(T("步数", "steps"))
ax.set_ylabel(T("训练损失 − 最小值", "training loss − minimum"))
ax.set_ylim(1e-6, 1e3)
ax.legend(fontsize=9, frameon=False)
ax.set_title(T("（a）小批量随机梯度下降", "(a) Mini-batch SGD"), fontsize=11)
ax = axs[1]
width, depth = 256, 20
rng = np.random.default_rng(1)
X0 = rng.normal(size=(512, width))
for name, s, col in ((T("标准差 0.01", "std 0.01"), 0.01, C["muted"]), (T("泽维尔：$\\sqrt{1/n}$", "Xavier: $\\sqrt{1/n}$"), math.sqrt(1 / width), C["accent"]),
                     (T("何恺明：$\\sqrt{2/n}$", "He: $\\sqrt{2/n}$"), math.sqrt(2 / width), C["z"])):
    h, st = X0, []
    for _ in range(depth):
        h = np.maximum(h @ rng.normal(0, s, (width, width)), 0)
        st.append(max(h.std(), 1e-30))
    ax.semilogy(range(1, depth + 1), st, "o-", ms=3, color=col, label=name)
ax.set_xlabel(T("层号", "layer"))
ax.set_ylabel(T("该层输出的标准差", "std of the layer output"))
ax.set_xticks([1, 5, 10, 15, 20])
ax.legend(fontsize=9, frameon=False)
ax.set_title(T("（b）初始化对深层网络的影响（ReLU，宽 256）", "(b) Initialization in a deep ReLU net (width 256)"), fontsize=11)
for a_ in axs:
    for s in ("top", "right"):
        a_.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_6_2")
plt.close(fig)
