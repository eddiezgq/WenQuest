"""图 3.2.1：关节误差数列与 ±2% 误差带（示意模型 e_k = 10° · 0.99^k cos 0.03k）。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, clean, figure, plt

k = np.arange(0, 701)
e = 10 * 0.99**k * np.cos(0.03 * k)
N = int(np.nonzero(np.abs(e) >= 0.2)[0][-1]) + 1
first = int(np.nonzero(np.abs(e) < 0.2)[0][0])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [1.2, 1]})
a1.plot(k, e, ".", color=BLUE, ms=1.5)
a1.axhspan(-0.2, 0.2, color=RED, alpha=0.12)
a1.axvline(N, color=RED, lw=1, ls="--")
a1.text(N + 8, 6, T(f"N = {N}：此后永远在带内", f"N = {N}: inside for good"), color=RED, fontsize=9)
a1.annotate(T("第一次进入带内，\n但还没有到位", "first enters the band,\nbut not settled"), xy=(first, 0), xytext=(110, 4),
            arrowprops=dict(arrowstyle="->", color=INK), fontsize=9)
a1.set_xlabel(T("步数 k（1 ms 一步）", "step k (1 ms)"))
a1.set_ylabel(T("误差 / (°)", "error / (°)"))
a1.set_title(T("关节误差数列", "Joint error sequence"), fontsize=10)
clean(a1)
a2.plot(k, e, ".", color=BLUE, ms=1.5)
a2.axhspan(-0.2, 0.2, color=RED, alpha=0.12)
a2.axhspan(-0.05, 0.05, color=RED, alpha=0.25)
N2 = int(np.nonzero(np.abs(e) >= 0.05)[0][-1]) + 1
a2.axvline(N, color=RED, lw=1, ls="--")
a2.axvline(N2, color=RED, lw=1, ls=":")
a2.text(N2 + 5, 0.4, f"N = {N2}", color=RED, fontsize=9)
a2.set_ylim(-0.6, 0.6)
a2.set_xlim(150, 700)
a2.set_xlabel("k")
a2.set_title(T("放大：带收窄到 ±0.5%，N 后移", "Zoom: a ±0.5% band needs a later N"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig3_2_1")
