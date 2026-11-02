"""图 20.4.1：(a) 浮点数的间距：相邻两个浮点数之差（ulp）随数的大小成比例增长，相对间距在 ε/2 与 ε 之间锯齿形变化
（单精度与双精度，双对数坐标）；(b) 单精度时钟：机器人控制器每 1 ms 把 0.001 s 加到单精度变量上，时钟读数与真实时间之差。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.5))
x = np.logspace(-3, 6, 4000)
for t_, col, nm in ((np.float32, RED, T("单精度", "single")), (np.float64, BLUE, T("双精度", "double"))):
    ulp = np.array([float(np.spacing(t_(v))) for v in x])
    a1.loglog(x, ulp / x, color=col, lw=1.2, label=nm + T("：相对间距 ulp(x)/x", ": relative spacing ulp(x)/x"))
    eps = float(np.finfo(t_).eps)
    a1.axhline(eps, color=col, lw=0.6, ls="--")
    a1.text(1.3e-3, eps * 1.35, f"ε = {eps:.2e}", color=col, fontsize=9)
a1.set_xlabel("x")
a1.set_ylim(1e-17, 1e-5)
a1.legend(frameon=False, fontsize=8.5, loc="center right")
a1.set_title(T("(a) 相对间距在 ε/2 与 ε 之间", "(a) Relative spacing between ε/2 and ε"), fontsize=11)

dt = float(np.float32(0.001))
hours = np.linspace(0, 8, 801)
clock, steps, e = 0.0, 0, -10
err = []
for hr in hours:
    target = round(hr * 3600 * 1000)
    while steps < target:
        while 2.0 ** (e + 1) <= clock:
            e += 1
        if clock < 1.0:
            clock = float(np.float32(np.float32(clock) + np.float32(0.001))); steps += 1; continue
        ulp = 2.0 ** (e - 23)
        inc = round(dt / ulp) * ulp
        if inc == 0:
            steps = target
            break
        n = min(math.ceil((2.0 ** (e + 1) - clock) / inc), target - steps)
        clock += n * inc; steps += n
    err.append(clock - hr * 3600)
a2.plot(hours, np.array(err) / 60, color=RED, lw=2)
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xlabel(T("真实运行时间 / h", "real running time / h"))
a2.set_ylabel(T("时钟读数 − 真实时间 / min", "clock − real time / min"))
a2.annotate(T("读数到 2¹⁵ s 后\n加 0.001 不再改变它：停走", "after 2¹⁵ s adding 0.001\nno longer changes it: stalls"),
            xy=(7.6, err[760] / 60), xytext=(2.2, 35), fontsize=9, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
a2.annotate(T("2¹⁴ s 以后每步加 1.95 ms：走快", "after 2¹⁴ s each step adds 1.95 ms: runs fast"),
            xy=(5.8, err[580] / 60), xytext=(0.3, 100), fontsize=9, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
a2.set_title(T("(b) 单精度时钟（每 1 ms 加 0.001 s）", "(b) Single-precision clock (+0.001 s every 1 ms)"), fontsize=11)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig20_4_1")
