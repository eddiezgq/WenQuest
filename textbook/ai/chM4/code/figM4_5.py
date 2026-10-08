"""M4.5 节的示意图。

图 M4.5.1：（a）$e^{z}$ 在哪里撞上各格式的上限（FP16 在 11 上就溢出，FP32 在 88，FP64 在 709），
以及"先减最大值"把得分搬到 0 以下之后，指数永远落在安全区；
（b）一句话的似然：概率连乘按项数指数下降，双精度撑不过三百来项就下溢成 0，
同一串数在对数域里只是线性地变负。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.0))

z = np.linspace(-20, 1100, 1200)
LOG10E = 1 / np.log(10)
a.plot(z, z * LOG10E, color=C["x"], lw=1.8,
       label=T("$e^{z}$（直接取指数）", "$e^{z}$ (direct)"))
for name, lim, col in ((T("FP16 上限", "FP16 max"), float(np.finfo(np.float16).max), C["y"]),
                       (T("FP32 上限", "FP32 max"), float(np.finfo(np.float32).max), C["accent"]),
                       (T("FP64 上限", "FP64 max"), float(np.finfo(np.float64).max), C["ink"])):
    a.axhline(np.log10(lim), color=col, lw=1.1, ls="--", label=name)
    a.axvline(np.log(lim), color=col, lw=0.8, ls=":", alpha=0.7)
a.plot([-20, 0], [-20 * LOG10E, 0.0], color=C["z"], lw=2.8,
       label=T("减最大值之后：指数不超过 1", "after shifting: exponent at most 1"))
a.fill_between([-20, 0], -9, 0.5, color=C["z"], alpha=0.10)
a.set_ylim(-9, 480)
a.set_xlabel(T("得分 $z$", "logit $z$"))
a.set_ylabel(T("$\\log_{10} e^{z}$（结果有多少位数）", "$\\log_{10} e^{z}$ (digits in the result)"))
a.set_title(T("(a) 得分一大，指数就算不出来", "(a) Large logits overflow"), fontsize=10)
a.legend(fontsize=7.5, loc="upper left")
a.grid(alpha=0.25, lw=0.5)

g = np.random.default_rng(45)
p = g.uniform(0.01, 0.2, 500)
ns = np.arange(1, 501)
logp = np.cumsum(np.log(p))
prod = np.array([float(np.prod(p[:n])) for n in ns])
b.plot(ns, np.maximum(prod, 1e-320), color=C["x"], lw=1.8,
       label=T("直接连乘（双精度）", "direct product (FP64)"))
b.axhline(float(np.finfo(np.float64).tiny), color=C["muted"], lw=1.0, ls=":",
          label=T("双精度最小正规数", "FP64 smallest normal"))
b.set_yscale("log")
b.set_ylim(1e-310, 10)
b.set_xlabel(T("连乘的项数 $n$", "number of factors $n$"))
b.set_ylabel(T("似然 $\\prod p_i$", "likelihood $\\prod p_i$"))
b.set_title(T("(b) 概率连乘很快下溢成 0", "(b) Products of probabilities underflow"), fontsize=10)
b.legend(fontsize=8, loc="lower left")
b.grid(alpha=0.25, lw=0.5, which="both")
c = b.twinx()
c.plot(ns, logp, color=C["y"], lw=1.6)
c.set_ylabel(T("对数域：$\\sum\\log p_i$（右轴）", "log domain: $\\sum\\log p_i$ (right axis)"), color=C["y"])
c.tick_params(axis="y", labelcolor=C["y"])

fig.tight_layout()
figure(fig, "figM4_5_1")
