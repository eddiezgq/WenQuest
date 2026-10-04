"""图 5.4.1：方程组 εx + y = 1，x + y = 2 的解 x 的误差随 ε 的变化（双对数坐标）：不选主元时 ε 越小误差越大，
部分选主元后误差保持在舍入误差的量级。"""
import numpy as np

from _fig import BLUE, RED, T, figure, plt

E = np.logspace(-1, -17, 81)
err_no, err_p = [], []
for e in E:
    exact = 1 / (1 - e)
    l = 1 / e
    y = (2 - l) / (1 - l)
    err_no.append(abs((1 - y) / e - exact) + 1e-18)
    xs = np.linalg.solve(np.array([[e, 1.0], [1.0, 1.0]]), np.array([1.0, 2.0]))
    err_p.append(max(abs(xs[0] - exact), 1e-17))
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.loglog(E, err_no, "o-", ms=3, color=RED, label=T("不选主元", "no pivoting"))
ax.loglog(E, err_p, "s", ms=3, color=BLUE, label=T("部分选主元（误差为 0 时画在 10⁻¹⁷）", "partial pivoting (zero error drawn at 10⁻¹⁷)"))
ax.invert_xaxis()
ax.set_xlabel("ε")
ax.set_ylabel(T("x 的误差", "error in x"))
ax.legend(frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig5_4_1")
