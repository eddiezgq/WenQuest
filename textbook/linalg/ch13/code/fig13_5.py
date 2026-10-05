"""图 13.5.1：矩阵的幂。(a) 工作站可用率（正常的概率）从 1 出发，按 0.5ᵏ 的速度趋于 λ = 1 的特征向量给出的 0.8；
(b) 采样 PD 控制的关节角 θₖ（T = 0.05 s，从 θ₀ = 1 出发）：四组增益；(c) 对应的特征值与单位圆，模大于 1 的发散。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a0, a1, a2) = plt.subplots(1, 3, figsize=(13.0, 4.0), gridspec_kw={"width_ratios": [1, 1.4, 1]})
P = np.array([[0.9, 0.4], [0.1, 0.6]])
x = np.array([1.0, 0]); h = [1.0]
for _ in range(12):
    x = P @ x; h.append(x[0])
a0.plot(range(13), h, "o-", color=BLUE, ms=4)
a0.axhline(0.8, color=MUTED, ls="--", lw=1)
a0.text(6, 0.81, T("稳态 0.8", "steady state 0.8"), color=MUTED, fontsize=10)
a0.set_xlabel(T("班次 k", "shift k")); a0.set_ylabel(T("正常的概率", "probability of running"))
a0.set_ylim(0.75, 1.02)
a0.set_title(T("(a) 工作站的可用率", "(a) Availability of a work cell"), fontsize=11)
Tt = 0.05
cases = [((100, 10), BLUE, "K_p=100, K_d=10"), ((100, 20), GREEN, "K_p=100, K_d=20"), ((400, 40), ACC, "K_p=400, K_d=40"), ((100, 4), RED, "K_p=100, K_d=4")]
for (kp, kd), c, lab in cases:
    A = np.array([[1, Tt], [-kp * Tt, 1 - kd * Tt]])
    x = np.array([1.0, 0]); th = [1.0]
    for _ in range(40):
        x = A @ x; th.append(x[0])
    a1.plot(np.arange(41) * Tt, th, "o-", color=c, ms=2.5, lw=1.2, label=f"${lab.replace('K_p', 'K_p').replace(', ', ',\\ ')}$")
    ev = np.linalg.eigvals(A)
    a2.plot(ev.real, ev.imag, "o", color=c, ms=7, mfc="none" if kd == 20 else c)
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_ylim(-2.8, 2.8); a1.set_xlabel(T("时间 / s", "time / s")); a1.set_ylabel("$\\theta_k$")
a1.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2)
a1.set_title(T("(b) 采样 PD 控制的关节角", "(b) Joint angle under sampled PD control"), fontsize=11)
t = np.linspace(0, 2 * np.pi, 300)
a2.plot(np.cos(t), np.sin(t), color=MUTED, lw=1)
a2.axhline(0, color=MUTED, lw=0.6); a2.axvline(0, color=MUTED, lw=0.6)
a2.set_aspect("equal"); a2.set_xlim(-1.3, 1.3); a2.set_ylim(-1.3, 1.3)
a2.text(-1.25, 1.12, T("单位圆", "unit circle"), color=MUTED, fontsize=9)
a2.set_title(T("(c) 特征值", "(c) Eigenvalues"), fontsize=11)
for ax in (a0, a1):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig13_5_1")
