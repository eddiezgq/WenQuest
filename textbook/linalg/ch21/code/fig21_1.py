"""图 21.1.1：(a) 投入产出模型的诺伊曼级数：订单一轮一轮向上游传导，三个车间的累计产出 d + Cd + … + Cᵏd 逼近 (I − C)⁻¹d；
(b) 误差按 ρ(C)ᵏ 衰减；盖尔范德公式：‖Aᵏ‖₂^{1/k} → ρ(A)，对 C 收敛很快，对 20.2 节的 B 很慢。"""
import numpy as np

from _fig import BLUE, GREEN, MUTED, RED, T, figure, plt

C = np.array([[0.10, 0.30, 0.05], [0.05, 0.10, 0.40], [0.02, 0.05, 0.10]])
d = np.array([50.0, 80.0, 300.0])
x = np.linalg.solve(np.eye(3) - C, d)
rho = max(abs(np.linalg.eigvals(C)))
K = 12
S, term, err = [], d.copy(), []
s = np.zeros(3)
for k in range(K + 1):
    s = s + term
    S.append(s.copy())
    err.append(np.max(np.abs(x - s)))
    term = C @ term
S = np.array(S)
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.5, 4.3))
names = [T("铸造", "casting"), T("机加工", "machining"), T("装配", "assembly")]
for i, col in enumerate((RED, GREEN, BLUE)):
    a1.plot(range(K + 1), S[:, i], "o-", color=col, ms=4, lw=1.4, label=names[i])
    a1.axhline(x[i], color=col, lw=0.8, ls="--")
a1.set_xlabel(T("传导的轮数 k", "rounds k"))
a1.set_ylabel(T("累计产出 / 万元", "cumulative output / 10⁴ yuan"))
a1.legend(frameon=False, fontsize=9, loc="lower right")
a1.set_title(T("(a) 部分和 d + Cd + … + Cᵏd\n（虚线为 (I − C)⁻¹d）", "(a) Partial sums d + Cd + … + Cᵏd\n(dashed: (I − C)⁻¹d)"), fontsize=10.5)
ks = np.arange(K + 1)
a2.semilogy(ks, err, "o-", color=RED, ms=4, lw=1.4, label=T("误差（最大分量）", "error (max entry)"))
a2.semilogy(ks, err[0] * rho ** ks, color=MUTED, lw=1, ls="--", label=f"∝ ρ(C)ᵏ = {rho:.3f}ᵏ")
a2.set_xlabel(T("传导的轮数 k", "rounds k"))
a2.set_ylabel(T("万元", "10⁴ yuan"))
a2.legend(frameon=False, fontsize=9)
a2.set_title(T("(b) 诺伊曼级数的误差按 ρᵏ 衰减", "(b) The Neumann-series error decays like ρᵏ"), fontsize=10.5)
B = np.array([[0.9, 1.0], [0.0, 0.9]])
kk = np.arange(1, 301)
gB = [np.linalg.norm(np.linalg.matrix_power(B, k), 2) ** (1 / k) for k in kk]
gC = [np.linalg.norm(np.linalg.matrix_power(C, k), 2) ** (1 / k) for k in kk]
a3.plot(kk, gB, color=BLUE, lw=1.8, label=r"$\|B^k\|_2^{1/k}$")
a3.plot(kk, gC, color=GREEN, lw=1.8, label=r"$\|C^k\|_2^{1/k}$")
a3.axhline(0.9, color=BLUE, lw=0.8, ls=":")
a3.axhline(rho, color=GREEN, lw=0.8, ls=":")
a3.text(300, 0.83, "ρ(B) = 0.9", color=BLUE, fontsize=9, ha="right")
a3.text(300, rho - 0.07, f"ρ(C) = {rho:.3f}", color=GREEN, fontsize=9, ha="right")
a3.set_ylim(0, 1.6)
a3.set_xlabel("k")
a3.legend(frameon=False, fontsize=10, loc="upper right")
a3.set_title(T("(c) 盖尔范德公式：‖Aᵏ‖^(1/k) → ρ(A)", "(c) Gelfand’s formula: ‖Aᵏ‖^(1/k) → ρ(A)"), fontsize=10.5)
for a in (a1, a2, a3):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig21_1_1")
