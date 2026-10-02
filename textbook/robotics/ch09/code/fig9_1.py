"""9.1 节的示意图。

图 9.1.1：算例 9.1.2 的 2000 个测力读数的直方图，与高斯密度曲线。
图 9.1.2：概率密度与分布函数：区间 (a, b] 上的面积 = F(b) − F(a)。
图 9.1.3：编码器的量化：读数是阶梯，误差是锯齿，在 ±q/2 内均匀分布。
图 9.1.4：标准高斯分布落在 ±1、±2、±3 个标准差内的概率。
图 9.1.5：中心极限定理：1、2、12 个均匀随机数之和的直方图趋近高斯曲线。
"""
import math

import numpy as np

from _prob import gauss_pdf, p_within
from bookout import COLORS as C, T, figure, style

plt = style()


def clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


# ---------------------------------------------------------------- 图 9.1.1（数据与算例 9.1.2 相同）
rng = np.random.default_rng(901)
F0, sig, n = 15.0, 0.08, 2000
x = F0 + sig * rng.standard_normal(n)
mean, s = x.mean(), x.std(ddof=1)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
w = 0.02
bins = np.arange(14.70, 15.30 + w / 2, w)
ax.hist(x, bins=bins, color="#c9d3d9", edgecolor="white", lw=0.6)
xs = np.linspace(14.70, 15.30, 400)
ax.plot(xs, n * w * gauss_pdf(xs, mean, s), color=C["z"], lw=1.8)
ax.axvline(mean, color=C["ink"], lw=1.0, ls="--")
for k in (-1, 1):
    ax.annotate("", xy=(mean + k * s, 228), xytext=(mean, 228),
                arrowprops=dict(arrowstyle="-|>", color=C["accent"], lw=1.2, shrinkA=0, shrinkB=0))
ax.text(mean + s + 0.008, 228, r"$\pm s$", color=C["accent"], fontsize=11, va="center")
ax.text(mean + 0.006, 258, T(f"样本均值 {mean:.3f} N", f"sample mean {mean:.3f} N"), fontsize=9)
ax.text(15.12, 150, T(f"高斯密度曲线\n（均值 {mean:.3f} N，标准差 {s:.3f} N）",
                      f"Gaussian density\n(mean {mean:.3f} N, std {s:.3f} N)"), fontsize=9, color=C["z"])
ax.set_xlim(14.70, 15.30)
ax.set_ylim(0, 285)
ax.set_xlabel(T("读数 / N", "Reading / N"))
ax.set_ylabel(T("每个区间内的读数个数", "Readings per bin"))
clean(ax)
figure(fig, "fig9_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.1.2 密度与分布函数
from math import erf
mu, sd = 15.0, 0.08
a, b = 14.95, 15.10
F = lambda v: 0.5 * (1 + np.vectorize(erf)((np.asarray(v) - mu) / (sd * math.sqrt(2))))
xs = np.linspace(14.72, 15.28, 400)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.2))
ax1.plot(xs, gauss_pdf(xs, mu, sd), color=C["z"], lw=1.8)
m = (xs > a) & (xs <= b)
ax1.fill_between(xs[m], gauss_pdf(xs[m], mu, sd), color=C["z"], alpha=0.25, lw=0)
ax1.set_xticks([a, mu, b])
ax1.set_xticklabels(["$a$", r"$\mu$", "$b$"])
ax1.text(15.0, 5.75, r"$\Pr(a < X \leq b) = \int_a^b p(x)\,\mathrm{d}x$", ha="center", fontsize=10, color=C["z"])
ax1.text(15.16, 4.2, "$p(x)$", color=C["z"], fontsize=12)
ax1.set_ylim(0, 6.6)
ax1.set_title(T("概率密度：面积就是概率", "Density: area is probability"), fontsize=10)
ax1.set_yticks([])
clean(ax1)
ax2.plot(xs, F(xs), color=C["x"], lw=1.8)
Fa, Fb = float(F(a)), float(F(b))
for v, Fv in ((a, Fa), (b, Fb)):
    ax2.plot([v, v], [0, Fv], color=C["muted"], lw=0.8, ls=":")
    ax2.plot([14.72, v], [Fv, Fv], color=C["muted"], lw=0.8, ls=":")
ax2.annotate("", xy=(14.76, Fb), xytext=(14.76, Fa), arrowprops=dict(arrowstyle="<|-|>", color=C["z"], lw=1.2))
ax2.text(14.775, (Fa + Fb) / 2, "$F(b) - F(a)$", color=C["z"], fontsize=10, va="center")
ax2.set_xticks([a, mu, b])
ax2.set_xticklabels(["$a$", r"$\mu$", "$b$"])
ax2.set_yticks([0, 0.5, 1])
ax2.text(15.15, 0.80, "$F(x)$", color=C["x"], fontsize=12)
ax2.set_xlim(14.72, 15.28)
ax2.set_ylim(0, 1.05)
ax2.set_title(T("分布函数：从左边累积到 x 的概率", "Distribution function: probability accumulated up to x"), fontsize=10)
clean(ax2)
fig.tight_layout()
figure(fig, "fig9_1_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.1.4 标准高斯的 1σ、2σ、3σ
z = np.linspace(-4, 4, 600)
fig, ax = plt.subplots(figsize=(6.6, 3.3))
ax.plot(z, gauss_pdf(z), color=C["ink"], lw=1.8)
shades = ("#9ecae1", "#c6dbef", "#e4eef7")
for k, col in ((3, shades[2]), (2, shades[1]), (1, shades[0])):
    m = np.abs(z) <= k
    ax.fill_between(z[m], gauss_pdf(z[m]), color=col, lw=0)
ys = (0.20, 0.10, 0.025)
for k, yv in zip((1, 2, 3), ys):
    ax.annotate("", xy=(k, yv), xytext=(-k, yv), arrowprops=dict(arrowstyle="<|-|>", color=C["z"], lw=1.0))
    ax.text(0, yv + 0.012, f"{100 * p_within(k):.2f}%", ha="center", fontsize=9.5, color=C["z"],
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
ax.set_xticks(range(-3, 4))
ax.set_xticklabels([r"$\mu-3\sigma$", r"$\mu-2\sigma$", r"$\mu-\sigma$", r"$\mu$", r"$\mu+\sigma$", r"$\mu+2\sigma$", r"$\mu+3\sigma$"], fontsize=9)
ax.set_yticks([])
ax.set_xlim(-4, 4)
ax.set_ylim(0, 0.44)
ax.text(2.2, 0.33, T("曲线下总面积 = 1", "total area under the curve = 1"), fontsize=9, color=C["muted"])
clean(ax)
ax.spines["left"].set_visible(False)
figure(fig, "fig9_1_4")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.1.3 编码器的量化（为看清阶梯，q 画得很大）
q = 1.0
th = np.linspace(0, 5, 1000)
rd = np.round(th / q) * q
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.2), gridspec_kw={"width_ratios": [1.15, 1]})
ax1.plot(th, th, color=C["muted"], lw=1.0, ls="--")
ax1.plot(th, rd, color=C["z"], lw=1.8, drawstyle="steps-mid")
ax1.set_xlabel(T("真实角度 / q", "True angle / q"))
ax1.set_ylabel(T("读数 / q", "Reading / q"))
ax1.text(3.3, 2.2, T("读数（阶梯）", "reading (staircase)"), color=C["z"], fontsize=9)
ax1.text(0.35, 2.1, T("真实角度（虚线）", "true angle (dashed)"), color=C["muted"], fontsize=9)
ax1.set_title(T("编码器只能读出 q 的整数倍", "The encoder reads whole multiples of q"), fontsize=10)
clean(ax1)
e = rd - th
ax2.plot(th, e, color=C["x"], lw=1.4)
ax2.axhline(0.5, color=C["muted"], lw=0.8, ls=":")
ax2.axhline(-0.5, color=C["muted"], lw=0.8, ls=":")
ax2.set_yticks([-0.5, 0, 0.5])
ax2.set_yticklabels(["$-q/2$", "0", "$q/2$"])
ax2.set_xlabel(T("真实角度 / q", "True angle / q"))
ax2.set_ylabel(T("量化误差", "Quantization error"))
ax2.fill_betweenx([-0.5, 0.5], 5.25, 5.75, color=C["x"], alpha=0.25, lw=0, clip_on=False)
ax2.text(5.5, 0.62, T("均匀密度 1/q", "uniform density 1/q"), fontsize=9, ha="center", color=C["x"])
ax2.set_xlim(0, 5.0)
ax2.set_ylim(-0.75, 0.8)
ax2.set_title(T("误差是锯齿，在 ±q/2 内均匀分布", "The error is a sawtooth, uniform in ±q/2"), fontsize=10)
clean(ax2)
fig.tight_layout()
figure(fig, "fig9_1_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.1.5 中心极限定理
rng = np.random.default_rng(915)
fig, axs = plt.subplots(1, 3, figsize=(9.6, 2.9), sharey=True)
zz = np.linspace(-4, 4, 400)
for ax, k in zip(axs, (1, 2, 12)):
    u = rng.uniform(0, 1, (100000, k)).sum(axis=1)
    zst = (u - k / 2) / math.sqrt(k / 12)          # 化为均值 0、标准差 1
    ax.hist(zst, bins=np.linspace(-4, 4, 41), density=True, color="#c9d3d9", edgecolor="white", lw=0.5)
    ax.plot(zz, gauss_pdf(zz), color=C["z"], lw=1.6)
    ax.set_title(T(f"{k} 个均匀随机数之和", f"sum of {k} uniform number" + ("s" if k > 1 else "")), fontsize=10)
    ax.set_xlim(-4, 4)
    ax.set_xticks([-3, 0, 3])
    clean(ax)
axs[0].set_ylabel(T("密度（化为标准差 1）", "density (scaled to std 1)"))
axs[2].text(1.2, 0.33, T("高斯曲线", "Gaussian"), color=C["z"], fontsize=9)
fig.tight_layout()
figure(fig, "fig9_1_5")
plt.close(fig)
