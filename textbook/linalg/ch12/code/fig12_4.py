"""图 12.4.1：“在 x = 1/2 处取值”的表示元。在 n 次多项式空间 𝒫ₙ 上取内积 ⟨p, q⟩ = ∫₀¹ pq dx，
泛函 p ↦ p(1/2) 由唯一的 u_n 表示：⟨u_n, p⟩ = p(1/2)。n = 2、8、32 时 u_n 越来越高、越来越窄，
‖u_n‖² = u_n(1/2) 随 n 无限增大——在全体平方可积函数中，这个泛函没有表示元（12.6 节）。"""
import numpy as np
from numpy.polynomial import legendre as Lg

from _fig import ACC, BLUE, MUTED, RED, T, figure, plt

x = np.linspace(0, 1, 2001)
fig, ax = plt.subplots(figsize=(7.5, 3.8))
for n, c in ((2, BLUE), (8, ACC), (32, RED)):
    u = sum((2 * k + 1) * Lg.legval(0.0, [0] * k + [1]) * Lg.legval(2 * x - 1, [0] * k + [1]) for k in range(n + 1))
    ax.plot(x, u, color=c, lw=1.6, label=f"n = {n}")
ax.axhline(0, color=MUTED, lw=0.6)
ax.axvline(0.5, color=MUTED, lw=0.6, ls=":")
ax.set_xlim(0, 1)
ax.set_xlabel("x"); ax.set_ylabel("$u_n(x)$")
ax.legend(frameon=False, fontsize=10)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("在 $\\mathcal{P}_n$ 中表示“取 p(1/2)”的多项式 $u_n$", "The polynomial $u_n$ in $\\mathcal{P}_n$ that represents p ↦ p(1/2)"), fontsize=11)
figure(fig, "fig12_4_1")
