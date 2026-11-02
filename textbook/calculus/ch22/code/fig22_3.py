"""图 22.3.1：RE 40 启动、30 ms 突加负载：转速与电流（上），自适应休恩–欧拉法每一步的步长（下，对数坐标）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

V, R, L, k, J = 48.0, 1.13, 0.33e-3, 60.3e-3, 137e-7
TL = lambda t: 0.15 if t >= 0.03 else 0.0
f = lambda t, y: np.array([(V - R * y[0] - k * y[1]) / L, (k * y[0] - TL(t)) / J])
TT, tol = 0.06, 1e-5
t, y, h = 0.0, np.zeros(2), 1e-6
ts, ys, hs, rj = [0.0], [y.copy()], [], []
scale = np.array([40.0, 800.0])
while t < TT - 1e-15:
    h = min(h, TT - t)
    k1 = f(t, y); k2 = f(t + h, y + h * k1)
    yh = y + h / 2 * (k1 + k2); err = np.max(np.abs(h / 2 * (k2 - k1)) / scale)
    if err <= tol:
        t += h; y = yh; ts.append(t); ys.append(y.copy()); hs.append(h)
    else:
        rj.append((t, h))
    h *= min(4.0, max(0.2, 0.9 * math.sqrt(tol / max(err, 1e-300))))
ts, ys, hs = np.array(ts), np.array(ys), np.array(hs)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 5.6), sharex=True, gridspec_kw=dict(height_ratios=[1.2, 1]))
a1.plot(ts * 1000, ys[:, 1], color=BLUE, lw=2, label=T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
b = a1.twinx()
b.plot(ts * 1000, ys[:, 0], color=RED, lw=1.6, label=T("电流 i / A", "current i / A"))
b.set_ylabel(T("电流 / A", "current / A"), color=RED); b.spines["top"].set_visible(False)
a1.set_ylabel(T("转速 / (rad/s)", "speed / (rad/s)"), color=BLUE)
a1.axvline(30, color=MUTED, ls=":", lw=1)
a1.text(30.5, 200, T("突加负载 0.15 N·m", "load step 0.15 N·m"), fontsize=9, color=MUTED)
a1.set_title(T("RE 40 启动与突加负载（计入电感）", "RE 40 start and load step (with inductance)"), fontsize=10)
clean(a1, zero=False)
a2.semilogy(ts[1:] * 1000, hs * 1e6, ".", color=INK, ms=3)
if rj:
    a2.semilogy([r[0] * 1000 for r in rj], [r[1] * 1e6 for r in rj], "x", color=RED, ms=6, label=T("被拒绝的步", "rejected steps"))
a2.axvline(30, color=MUTED, ls=":", lw=1)
a2.set_xlabel(T("时间 t / ms", "time t / ms")); a2.set_ylabel(T("步长 h / μs", "step h / μs"))
a2.set_title(T(f"自适应步长（tol = 10⁻⁵）：共 {len(hs)} 步；变化快处步子小，平稳处步子大",
               f"Adaptive step (tol = 10⁻⁵): {len(hs)} steps; small where things change fast"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower right"); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig22_3_1")
