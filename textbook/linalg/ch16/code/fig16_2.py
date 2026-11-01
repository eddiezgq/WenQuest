"""图 16.2.1：矩阵指数的两个应用。(a) PD 控制的关节（K_p = 100、K_d = 4），每 T = 0.05 s 取一点：
欧拉法 x_{k+1} = (I + AT)x_k 越摆越大，精确离散化 x_{k+1} = e^{AT}x_k 与连续系统的解完全重合；
(b) 电机以 80 W 过载（程序 16.2.1）：两节点模型的绕组温升 13.6 min 达到 100 K；把电机当成一个热容、一个热阻估计，要 24.6 min，严重高估了允许时间。"""
import numpy as np
import scipy.linalg as sl

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _motor import A as AM, B as BM

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
Ac = np.array([[0.0, 1], [-100, -4]])
Tt = 0.05
tc = np.linspace(0, 3, 600)
a1.plot(tc, [(sl.expm(Ac * t) @ [1.0, 0])[0] for t in tc], color=INK, lw=1.4, label=T("连续系统", "continuous"))
for M, col, mk, lab in ((np.eye(2) + Ac * Tt, RED, "s", T("欧拉法 I + AT", "Euler I + AT")), (sl.expm(Ac * Tt), BLUE, "o", T("精确 exp(AT)", "exact exp(AT)"))):
    x, th = np.array([1.0, 0]), []
    for _ in range(61):
        th.append(x[0]); x = M @ x
    a1.plot(np.arange(61) * Tt, th, mk, color=col, ms=4, label=lab)
a1.set_ylim(-2.2, 2.2); a1.axhline(0, color=MUTED, lw=0.6)
a1.set_xlabel(T("t / s", "t / s")); a1.set_ylabel(T("关节角 θ", "joint angle θ"))
a1.legend(frameon=False, fontsize=9, loc="lower left")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) PD 关节：欧拉法与精确离散化", "(a) PD joint: Euler vs exact discretization"), fontsize=11)
P = 80.0
tt = np.linspace(0, 3000, 600)
xw = [(np.linalg.solve(AM, (sl.expm(AM * t) - np.eye(2)) @ BM * P))[0] for t in tt]
a2.plot(tt / 60, xw, color=RED, lw=2, label=T("两节点模型（矩阵指数）", "two-node model (matrix exponential)"))
tau1 = 550 * 1.5
a2.plot(tt / 60, 120 * (1 - np.exp(-tt / tau1)), color=MUTED, lw=1.6, ls="--", label=T("单一时间常数的估计", "single time-constant estimate"))
a2.axhline(100, color=ACC, lw=1)
a2.text(1, 103, T("绕组温升上限 100 K", "winding limit 100 K"), color=ACC, fontsize=9)
for tm, col in ((13.57, RED), (24.64, MUTED)):
    a2.axvline(tm, color=col, lw=0.8, ls=":")
    a2.text(tm + 0.4, 20, f"{tm:.1f} min", color=col, fontsize=9)
a2.set_xlabel(T("t / min", "t / min")); a2.set_ylabel(T("绕组温升 / K", "winding rise / K"))
a2.set_ylim(0, 125); a2.legend(frameon=False, fontsize=9, loc="lower right")
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 80 W 过载：多久到上限", "(b) 80 W overload: time to the limit"), fontsize=11)
fig.tight_layout()
figure(fig, "fig16_2_1")
