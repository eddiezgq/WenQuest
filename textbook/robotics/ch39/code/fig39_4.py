"""图 39.4.1：(a) 算例 39.4.1 的原始读数、滑动平均（N = 20）、一阶低通（f_c = 10 Hz）；(b) 两种滤波器的幅频响应。"""
import math

import numpy as np

from bookout import COLORS as C, figure, style

plt = style()
fs = 1000.0
t = np.arange(0, 0.6, 1 / fs)
rng = np.random.default_rng(394)
u = np.clip(t / 0.2, 0, 1)
clean = 30 * u ** 2 * (3 - 2 * u)
x = clean + 2 * np.sin(2 * math.pi * 50 * t) + rng.normal(0, 0.3, t.size)
N = 20
ma = np.convolve(x, np.ones(N) / N, mode="full")[: t.size]
alpha = 1 - math.exp(-2 * math.pi * 10 / fs)
y = np.zeros_like(x)
for k in range(1, x.size):
    y[k] = y[k - 1] + alpha * (x[k] - y[k - 1])

fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw={"width_ratios": [1.35, 1]})
a.plot(t * 1e3, x, color=C["muted"], lw=0.6, label="原始读数")
a.plot(t * 1e3, clean, color=C["ink"], lw=1, ls="--", label="真实的力")
a.plot(t * 1e3, ma, color=C["z"], lw=1.8, label="滑动平均 N = 20")
a.plot(t * 1e3, y, color=C["x"], lw=1.8, label="一阶低通 $f_c$ = 10 Hz")
a.set_xlabel("时间 / ms")
a.set_ylabel("力 / N")
a.legend(fontsize=8.5, frameon=False, loc="lower right")
a.set_title("(a) 滤波前后", fontsize=10.5)
f = np.linspace(0.5, 200, 2000)
w = np.pi * f / fs
Hma = np.abs(np.sin(N * w) / (N * np.sin(w)))
z = np.exp(1j * 2 * np.pi * f / fs)
Hlp = np.abs(alpha / (1 - (1 - alpha) / z))
b.semilogy(f, Hma, color=C["z"], lw=1.6, label="滑动平均 N = 20")
b.semilogy(f, Hlp, color=C["x"], lw=1.6, label="一阶低通 $f_c$ = 10 Hz")
b.axvline(50, color=C["accent"], lw=1, ls=":")
b.text(52, 0.4, "50 Hz", color=C["accent"], fontsize=9)
b.set_ylim(1e-3, 1.5)
b.set_xlabel("频率 / Hz")
b.set_ylabel("|H(f)|")
b.legend(fontsize=8.5, frameon=False)
b.set_title("(b) 幅频响应", fontsize=10.5)
for ax in (a, b):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig39_4_1")
plt.close(fig)
