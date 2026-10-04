"""图 6.6.1：用有限次采样证明安全——等距采样漏掉窄的危险窗口；利普希茨下界（锯齿）给出保证。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import K, clearance

s = 0.05
O2 = (0.176, 0.634)
g = lambda t: clearance(t, O2) - s
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
tt = np.linspace(0, 1, 2001)
gg = np.array([g(t) for t in tt]) * 1000
for ax, h in ((a1, 0.1), (a2, 0.025)):
    ax.plot(tt, gg, color=INK, lw=2, label=T("安全裕量 d(t) − s", "margin d(t) − s"))
    tk = np.arange(0, 1 + 1e-9, h)
    gk = np.array([g(t) for t in tk]) * 1000
    ax.plot(tk, gk, "o", color=BLUE, ms=4)
    lb = np.array([max(gk[i] - K * 1000 * abs(t - tk[i]) for i in range(len(tk)) if abs(t - tk[i]) <= h / 2 + 1e-12) for t in tt])
    ax.plot(tt, lb, color=ACC, lw=1, label=T("由采样保证的下界", "guaranteed lower bound"))
    ax.axhline(0, color=RED, lw=1)
    ax.set_ylim(-80, 160)
    ax.set_xlabel(T("时间 t / s", "time t / s"))
    ax.set_ylabel("mm")
    ax.set_title(T(f"步长 {h:g} s：", f"step {h:g} s: ") + (T("采样点都安全，但证明不了", "all samples safe, yet no proof") if h == 0.1 else T("有采样点落进危险窗口：发现碰撞", "samples fall in the danger window: collision found")), fontsize=10)
    ax.legend(fontsize=8.5, frameon=False, loc="upper right")
    clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig6_6_1")
