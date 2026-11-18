"""21.3 节的图之一：轴承故障在振动里长什么样。

图 21.3.1：（a）时域——一串等间隔的冲击，每次冲击激起一段高频衰减振荡；
（b）频谱与包络谱叠在一起：**故障频率在原始频谱上几乎看不见，在包络谱上一目了然**。
"""
import numpy as np

from _ch21 import bearing_freqs, bearing_signal, envelope, peak_near, spectrum
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
FS, SECONDS, RPM = 12000.0, 2.0, 1797.0
f = bearing_freqs(9, 7.94, 39.04, RPM)
# 图里为了看得清，噪声取得比算例小（算例 21.3 用的是 0.35）
x = bearing_signal(FS, SECONDS, f["BPFO"], RPM, carrier_hz=3200.0, noise=0.12, seed=0)


def avg_spectrum(sig, fs, n_seg=8):
    """分段平均的幅值谱：段数越多越平滑，峰也越清楚（车间里也是这么做的）。"""
    m = len(sig) // n_seg
    acc = None
    for k in range(n_seg):
        fk, Xk = spectrum(sig[k * m:(k + 1) * m], fs)
        acc = Xk if acc is None else acc + Xk
    return fk, acc / n_seg

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 时域
n_show = int(0.06 * FS)
t = np.arange(n_show) / FS * 1000.0
a.plot(t, x[:n_show], color=C["z"], lw=1.0)
env = envelope(x)[:n_show]
a.plot(t, env, color=C["x"], lw=1.8, label=T("包络", "envelope"))
period_ms = 1000.0 / f["BPFO"]
for k in range(1, int(60 / period_ms) + 1):
    a.axvline(k * period_ms, color=C["accent"], ls=":", lw=1.2)
a.annotate(T(f"冲击间隔 {period_ms:.2f} 毫秒 = 1 / {f['BPFO']:.1f} Hz",
             f"impact spacing {period_ms:.2f} ms = 1 / {f['BPFO']:.1f} Hz"),
           xy=(0.03, 0.92), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["accent"])
a.set_xlabel(T("时间（毫秒）", "time (ms)"))
a.set_ylabel(T("加速度（任意单位）", "acceleration (arbitrary units)"))
a.set_title(T("(a) 时域：等间隔的冲击，各自激起一段高频振荡",
              "(a) time domain: evenly spaced impacts ringing at a high frequency"),
            fontsize=10)
a.legend(fontsize=8, loc="lower right", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 频谱 vs 包络谱
fa, X = avg_spectrum(x, FS)
full_env = envelope(x)
fe, E = avg_spectrum(full_env - full_env.mean(), FS)
m = fa <= 600
b.plot(fa[m], X[m] / X[m].max(), color=C["muted"], lw=1.4,
           label=T("原始频谱（归一化）", "raw spectrum (normalised)"))
me = fe <= 600
b.plot(fe[me], E[me] / E[me].max(), color=C["x"], lw=1.8,
           label=T("包络谱（归一化）", "envelope spectrum (normalised)"))
for k, col in ((1, C["accent"]), (2, C["y"]), (3, C["z"])):
    hz, amp = peak_near(fe, E, k * f["BPFO"], 2.0)
    b.axvline(k * f["BPFO"], color=col, ls="--", lw=1.1)
    b.annotate(T(f"{k}×BPFO = {k * f['BPFO']:.0f} Hz", f"{k}×BPFO = {k * f['BPFO']:.0f} Hz"),
               xy=(k * f["BPFO"], amp / E[me].max()), xytext=(5, 6),
               textcoords="offset points", fontsize=7.5, color=col)
b.axvline(f["fr"], color=C["ink"], ls=":", lw=1.1)
b.annotate(T(f"轴频 {f['fr']:.0f} Hz", f"shaft {f['fr']:.0f} Hz"),
           xy=(f["fr"], 0.08), xytext=(4, 0), textcoords="offset points",
           fontsize=7.5, color=C["ink"])
b.set_xlabel(T("频率（Hz）", "frequency (Hz)"))
b.set_ylabel(T("幅值（各自归一化）", "amplitude (each normalised)"))
b.set_title(T("(b) 不做包络就看不见故障频率",
              "(b) without the envelope the fault frequency is invisible"), fontsize=10)
b.legend(fontsize=8, loc="lower right", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)
b.set_ylim(0, 1.25)

fig.tight_layout()
figure(fig, "fig21_3_1")
