"""8.2 节的计算：

算例 8.2.1  用欧拉法解算例 8.1.1 的网球：步长 h 取 0.1 s 到 0.0005 s，落地点与参考解（RK4，h = 10⁻⁴ s）相差多少？
            误差与 h 成正比吗（图 8.2.1）？
算例 8.2.2  弹簧振子（m = 1.0 kg，k = 100 N/m，由 x = 0.10 m 静止释放）用欧拉法计算，步长 h = 0.01 s。
            每走一步，能量变为原来的 1 + (ωh)² 倍；三个周期后振幅变为多少（图 8.2.2）？
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d
from _ode import run
from _ball import landing

# ---- 算例 8.2.1
Xref = landing(1e-4, "rk4")
hs = np.array([0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005])
err = np.array([abs(landing(h, "euler") - Xref) for h in hs])
slope = np.polyfit(np.log(hs), np.log(err), 1)[0]
out(Xref=Xref, e01=err[0], e001=err[3], e0001=err[6], slope=slope, h_1cm_ms=1000 * 0.01 / (err[3] / 0.01))

# ---- 算例 8.2.2
mS, kS, A = 1.0, 100.0, 0.10
w = math.sqrt(kS / mS); Tp = 2 * math.pi / w; h = 0.01
fS = lambda t, y: np.array([y[1], -kS / mS * y[0]])
n = int(round(3 * Tp / h))
tE, YE = run(fS, np.array([A, 0.0]), h, n, "euler")
E = 0.5 * kS * YE[:, 0] ** 2 + 0.5 * mS * YE[:, 1] ** 2
out(w=w, Tp=Tp, h=h, wh=w * h, grow=1 + (w * h) ** 2, steps_per=Tp / h, amp3=math.sqrt(2 * E[-1] / kS), E_ratio3=E[-1] / E[0],
    E_ratio1=(1 + (w * h) ** 2) ** (Tp / h))

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 2.8))
tt = np.linspace(0, 3 * Tp, 600)
ax.plot(tt, A * np.cos(w * tt), color=d.MUTED, lw=1.4, ls="--", label=T("精确解", "exact"))
ax.plot(tE, YE[:, 0], color=d.VR, lw=1.8, label=T("欧拉法，h = 0.01 s", "Euler, h = 0.01 s"))
ax.set_xlabel("t / s"); ax.set_ylabel("x / m"); ax.set_ylim(-0.25, 0.38); ax.legend(frameon=False, fontsize=8.5, loc="upper left", ncol=2); d.spines(ax)
figure(fig, "fig8_2_2")

fig, ax = plt.subplots(figsize=(4.6, 3.1))
ax.loglog(hs, err, "o-", color=d.VR, lw=1.8)
ax.loglog(hs, err[3] * hs / hs[3], color=d.MUTED, ls="--", lw=1, label=T("与 h 成正比", "∝ h"))
ax.set_xlabel(T("步长 h / s", "step h / s")); ax.set_ylabel(T("落地点误差 / m", "landing error / m")); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig8_2_1")
