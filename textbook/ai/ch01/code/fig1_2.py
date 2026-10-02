"""1.2 节的示意图。

图 1.2.1：感知机的结构：输入 x₁…x_d 乘以权重，加上偏置，求和后取符号。
图 1.2.3：（a）零件检验数据、感知机学到的分界线与最大间隔分界线；（b）异或问题的四个点，没有一条直线能分开。
图 1.2.2：一次更新的几何意义：样本 x̃ 被判错（y = +1 而 w·x̃ < 0），w 加上 x̃ 后转向它。
"""
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

from _perceptron import PARTS, XOR, augmented, max_margin, perceptron
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
POS, NEG = C["z"], C["x"]

# ---------------------------------------------------------------- 图 1.2.1
fig, ax = plt.subplots(figsize=(7.6, 3.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.6)
ax.axis("off")
ys = [3.8, 2.8, 1.3]
names = ["$x_1$", "$x_2$", "$x_d$"]
for yy, nm, wn in zip(ys, names, ["$w_1$", "$w_2$", "$w_d$"]):
    ax.add_patch(Circle((1.0, yy), 0.32, fc="#ffffff", ec=C["ink"], lw=1.2))
    ax.text(1.0, yy, nm, ha="center", va="center", fontsize=12)
    ax.add_patch(FancyArrowPatch((1.35, yy), (4.55, 2.45 + (yy - 2.45) * 0.15), arrowstyle="-|>", mutation_scale=12, lw=1.2,
                                 color=C["ink"]))
    ax.text(2.7, yy + (2.45 - yy) * 0.36 + 0.18, wn, fontsize=11, color=C["accent"])
ax.text(1.0, 2.05, "$\\vdots$", ha="center", va="center", fontsize=14)
ax.add_patch(Circle((1.0, 0.35), 0.0))
ax.text(4.9, 0.7, T("偏置 $b$", "bias $b$"), ha="center", fontsize=11, color=C["accent"])
ax.add_patch(FancyArrowPatch((4.9, 1.0), (4.9, 1.95), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=C["accent"]))
ax.add_patch(Circle((4.9, 2.45), 0.5, fc="#fdf3dc", ec=C["ink"], lw=1.3))
ax.text(4.9, 2.45, "$\\Sigma$", ha="center", va="center", fontsize=16)
ax.add_patch(FancyArrowPatch((5.4, 2.45), (6.6, 2.45), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=C["ink"]))
ax.text(6.0, 2.75, "$z$", ha="center", fontsize=12)
ax.add_patch(plt.Rectangle((6.6, 1.95), 1.3, 1.0, fc="#eef3f8", ec=C["ink"], lw=1.2))
xs = np.linspace(6.75, 7.75, 3)
ax.plot([6.75, 7.25, 7.25, 7.75], [2.2, 2.2, 2.7, 2.7], color=C["z"], lw=1.8)
ax.text(7.25, 1.7, "sign", ha="center", fontsize=10, color=C["muted"])
ax.add_patch(FancyArrowPatch((7.9, 2.45), (9.0, 2.45), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=C["ink"]))
ax.text(9.35, 2.45, "$\\hat y$", ha="center", va="center", fontsize=13)
ax.text(5.0, 4.25, "$z = w_1x_1 + w_2x_2 + \\cdots + w_dx_d + b,\\qquad \\hat y = \\mathrm{sign}(z)$", ha="center",
        fontsize=12, color=C["ink"])
figure(fig, "fig1_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.2.3（零件数据）
X, y = augmented(PARTS)
w, k, epochs, hist, ok = perceptron(PARTS)
ws, gamma = max_margin(PARTS)
fig, axs = plt.subplots(1, 2, figsize=(10.2, 4.4), gridspec_kw={"width_ratios": [1.45, 1]})
ax = axs[0]
xx = np.linspace(-0.2, 3.4, 50)
ax.fill_between(xx, (-ws[0] * xx - ws[2] - 1) / ws[1], (-ws[0] * xx - ws[2] + 1) / ws[1], color="#e9e3d0", alpha=0.7,
                lw=0, label=T("最大间隔带", "maximum-margin band"))
ax.plot(xx, (-w[0] * xx - w[2]) / w[1], color=C["muted"], lw=1.6, ls="--", label=T("感知机学到的分界线", "perceptron boundary"))
ax.plot(xx, (-ws[0] * xx - ws[2]) / ws[1], color=C["accent"], lw=2.0, label=T("最大间隔分界线", "maximum-margin boundary"))
for (a, b, c) in PARTS:
    ax.plot(a, b, "o" if c > 0 else "s", color=POS if c > 0 else NEG, ms=6.5, mfc="white" if c > 0 else NEG, mew=1.6)
sv = np.where(np.abs(y * (X @ ws) - 1) < 1e-9)[0]
for i in sv:
    ax.add_patch(Circle((X[i, 0], X[i, 1]), 0.13, fill=False, ec=C["ink"], lw=1.0))
ax.plot([], [], "o", color=POS, mfc="white", mew=1.6, label=T("合格（y = +1）", "accepted (y = +1)"))
ax.plot([], [], "s", color=NEG, label=T("不合格（y = −1）", "rejected (y = −1)"))
ax.set_xlim(-0.2, 3.4)
ax.set_ylim(-0.2, 3.8)
ax.set_aspect("equal")
ax.set_xlabel(T("$x_1$：外径偏差的绝对值（10 μm）", "$x_1$: |diameter deviation| (10 μm)"))
ax.set_ylabel(T("$x_2$：圆度误差（10 μm）", "$x_2$: roundness error (10 μm)"))
ax.legend(fontsize=8, loc="upper right", frameon=True, framealpha=0.9)
ax.set_title(T("（a）零件检验数据", "(a) Part inspection data"), fontsize=11)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax = axs[1]
for (a, b, c) in XOR:
    ax.plot(a, b, "o" if c > 0 else "s", color=POS if c > 0 else NEG, ms=11, mfc="white" if c > 0 else NEG, mew=2)
    ax.text(a + 0.08, b + 0.1, f"({a:.0f}, {b:.0f})", fontsize=10, color=C["ink"])
ax.plot([-0.2, 1.2], [0.75, 0.35], color=C["muted"], lw=1.2, ls=":")
ax.plot([0.3, 0.9], [-0.2, 1.2], color=C["muted"], lw=1.2, ls=":")
ax.set_xlim(-0.3, 1.45)
ax.set_ylim(-0.3, 1.45)
ax.set_aspect("equal")
ax.set_xlabel("$x_1$")
ax.set_ylabel("$x_2$")
ax.set_title(T("（b）异或：任何直线都分不开", "(b) XOR: no line separates"), fontsize=11)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_2_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.2.2（二维示意，略去偏置）
fig, axs = plt.subplots(1, 2, figsize=(9.0, 4.0))
w_old = np.array([1.6, -0.4])
xm = np.array([-0.6, 1.4])                     # y = +1，但 w·x < 0：判错
w_new = w_old + xm
for ax, wv, title in ((axs[0], w_old, T("更新前：$\\boldsymbol{w}\\cdot\\tilde{\\boldsymbol{x}} < 0$，判错",
                                            "Before: $\\boldsymbol{w}\\cdot\\tilde{\\boldsymbol{x}} < 0$, wrong")),
                      (axs[1], w_new, T("更新后：$\\boldsymbol{w}' = \\boldsymbol{w} + \\tilde{\\boldsymbol{x}}$",
                                        "After: $\\boldsymbol{w}' = \\boldsymbol{w} + \\tilde{\\boldsymbol{x}}$"))):
    nrm = wv / np.linalg.norm(wv)
    perp = np.array([-nrm[1], nrm[0]])
    ax.fill([0, 2.4 * perp[0] + 2.4 * nrm[0], 2.4 * nrm[0] - 2.4 * perp[0]],
            [0, 2.4 * perp[1] + 2.4 * nrm[1], 2.4 * nrm[1] - 2.4 * perp[1]], color="#dbe7f3", alpha=0.0)
    ts = np.linspace(-6, 6, 2)
    ax.plot(ts * perp[0], ts * perp[1], color=C["ink"], lw=1.6)
    # 判为 +1 的一侧着色
    big = 6.0
    corners = [big * perp, big * perp + big * nrm, -big * perp + big * nrm, -big * perp]
    ax.fill([p[0] for p in corners], [p[1] for p in corners], color="#dbe7f3", alpha=0.7, lw=0)
    ax.add_patch(FancyArrowPatch((0, 0), tuple(wv), arrowstyle="-|>", mutation_scale=16, lw=2.2, color=C["accent"]))
    ax.text(wv[0] + 0.08, wv[1] - 0.05, "$\\boldsymbol{w}'$" if wv is w_new else "$\\boldsymbol{w}$", fontsize=13, color=C["accent"])
    ax.plot(*xm, "o", color=POS, ms=10, mfc="white", mew=2)
    ax.add_patch(FancyArrowPatch((0, 0), tuple(xm), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=POS, ls="--"))
    ax.text(xm[0] - 0.55, xm[1] + 0.1, T("$\\tilde{\\boldsymbol{x}}$（$y = +1$）", "$\\tilde{\\boldsymbol{x}}$ ($y = +1$)"),
            fontsize=11, color=POS)
    if wv is w_new:
        ax.add_patch(FancyArrowPatch(tuple(w_old), tuple(w_new), arrowstyle="-|>", mutation_scale=12, lw=1.0, color=C["muted"],
                                     ls=":"))
        ax.add_patch(FancyArrowPatch((0, 0), tuple(w_old), arrowstyle="-|>", mutation_scale=12, lw=1.0, color=C["muted"]))
    ax.text(1.3, -1.9, T("着色一侧判为 +1", "shaded side → +1"), fontsize=9, color=C["muted"])
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11)
fig.tight_layout()
figure(fig, "fig1_2_2")
plt.close(fig)
