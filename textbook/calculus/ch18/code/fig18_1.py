"""图 18.1.1：左：f(x) = x² 在 [0, 1] 上 6 等分的达布上和（外接矩形）与下和（内接矩形），积分被夹在中间；
右：AGV 制动时速度单调减小，每隔 0.1 s 采样，左端点矩形是距离的上界，右端点矩形是下界。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.1))
x = np.linspace(0, 1, 300)
n = 6
for k in range(n):
    xa, xb = k / n, (k + 1) / n
    a1.add_patch(plt.Rectangle((xa, 0), 1 / n, xb ** 2, fc=RED, alpha=0.18, ec=RED, lw=0.8))
    a1.add_patch(plt.Rectangle((xa, 0), 1 / n, xa ** 2, fc=BLUE, alpha=0.35, ec=BLUE, lw=0.8))
a1.plot(x, x * x, color=INK, lw=2)
a1.plot([], [], color=RED, lw=6, alpha=0.3, label=T("上和 U(P)：每段取上确界", "upper sum U(P): sup on each piece"))
a1.plot([], [], color=BLUE, lw=6, alpha=0.5, label=T("下和 L(P)：每段取下确界", "lower sum L(P): inf on each piece"))
a1.legend(fontsize=9, frameon=False, loc="upper left")
a1.set_title(T("L(P) ≤ 积分 ≤ U(P)", "L(P) ≤ integral ≤ U(P)"), fontsize=10)
a1.set_xlabel("x")
clean(a1)
T_, v0, dt = 1.2, 1.5, 0.1
t = np.linspace(0, T_, 300)
v = lambda s: v0 * np.clip(1 - s / T_, 0, None) ** 1.5
for k in range(round(T_ / dt)):
    ta = k * dt
    a2.add_patch(plt.Rectangle((ta, 0), dt, v(ta), fc=RED, alpha=0.18, ec=RED, lw=0.6))
    a2.add_patch(plt.Rectangle((ta, 0), dt, v(ta + dt), fc=BLUE, alpha=0.35, ec=BLUE, lw=0.6))
a2.plot(t, v(t), color=INK, lw=2, label=T("制动速度 v(t)（单调减小）", "braking speed v(t) (decreasing)"))
a2.set_xlabel("t / s")
a2.set_ylabel("v / (m/s)")
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("制动距离：0.6465 m ≤ s ≤ 0.7965 m（Δt = 0.1 s）", "Braking distance: 0.6465 m ≤ s ≤ 0.7965 m (Δt = 0.1 s)"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig18_1_1")
