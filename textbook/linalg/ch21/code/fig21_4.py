"""图 21.4.1：特征值的扰动。(a) 根为 1, 2, …, 6 的多项式的友矩阵，加 200 个 ‖E‖₂ = 10⁻¹⁰ 的随机扰动：
每个特征值的最大移动与一阶估计 ε/|yᴴx| 相符，中间几个根的条件数上万；对称矩阵的特征值移动不超过 ε（虚线）；
(b) 8 个相同的一阶环节串联，A = −I + N 只有一个 8 阶若尔当块；在角上加 ε，8 个特征值落在以 −1 为圆心、半径 ε^{1/8} 的圆上。"""
import math

import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(21042)
n = 6
p = np.poly(np.arange(1, n + 1))
Cm = np.zeros((n, n))
Cm[0, :] = -p[1:]
Cm[1:, :-1] = np.eye(n - 1)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))
w, X = np.linalg.eig(Cm)
Y = np.linalg.inv(X).conj().T
order = np.argsort(w.real)
kap = [1 / abs(np.vdot(Y[:, i] / np.linalg.norm(Y[:, i]), X[:, i] / np.linalg.norm(X[:, i]))) for i in order]
eps = 1e-10
sh = np.zeros(n)
for _ in range(200):
    E = rng.standard_normal((n, n))
    E *= eps / np.linalg.norm(E, 2)
    z = np.linalg.eigvals(Cm + E)
    for j, i in enumerate(order):
        sh[j] = max(sh[j], np.min(np.abs(z - w[i])))
xs = np.arange(1, n + 1)
a1.bar(xs - 0.2, np.array(kap) * eps, width=0.38, color=MUTED, label=T("一阶估计 ε/|yᴴx|", "first-order estimate ε/|yᴴx|"))
a1.bar(xs + 0.2, sh, width=0.38, color=RED, label=T("200 次随机扰动中的最大移动", "largest shift in 200 random trials"))
a1.axhline(eps, color=BLUE, lw=1.2, ls="--", label=T("对称矩阵的界 ‖E‖₂ = ε", "bound for symmetric matrices ‖E‖₂ = ε"))
a1.set_yscale("log")
a1.set_xticks(xs)
a1.set_xlabel(T("特征值（多项式的根）", "eigenvalue (root of the polynomial)"))
a1.set_ylabel(T("特征值的移动", "eigenvalue shift"))
a1.legend(frameon=False, fontsize=8.5, loc="upper left")
a1.set_ylim(1e-11, 1e-3)
a1.set_title(T("(a) 根为 1, …, 6 的友矩阵，‖E‖₂ = ε = 10⁻¹⁰", "(a) Companion matrix with roots 1, …, 6, ‖E‖₂ = ε = 10⁻¹⁰"), fontsize=10)
for sp in ("top", "right"):
    a1.spines[sp].set_visible(False)
m = 8
A = -np.eye(m) + np.diag(np.ones(m - 1), -1)
u = np.linspace(0, 2 * math.pi, 361)
for e_, col in ((1e-8, BLUE), (1e-4, GREEN), (1e-2, RED)):
    P = A.copy()
    P[0, m - 1] = e_
    z = np.linalg.eigvals(P)
    rr = e_ ** (1 / m)
    a2.plot(-1 + rr * np.cos(u), rr * np.sin(u), color=col, lw=0.8, ls="--")
    a2.plot(z.real, z.imag, "o", color=col, ms=6, label="ε = 10" + {-8: "⁻⁸", -4: "⁻⁴", -2: "⁻²"}[int(round(math.log10(e_)))] + T("，", ", ") + f"ε^(1/8) = {rr:.2f}")
a2.plot([-1], [0], "x", color=INK, ms=9, mew=2)
a2.set_aspect("equal")
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xlim(-1.8, -0.2)
a2.set_ylim(-0.7, 0.7)
a2.set_xlabel(T("实部 / s⁻¹", "real part / s⁻¹"))
a2.legend(frameon=False, fontsize=8.5, loc="upper right")
a2.set_title(T("(b) 8 个一阶环节串联：ε 的扰动使特征值移动 ε^(1/8)", "(b) Eight first-order stages in series: ε moves eigenvalues by ε^(1/8)"), fontsize=10)
fig.tight_layout()
figure(fig, "fig21_4_1")
