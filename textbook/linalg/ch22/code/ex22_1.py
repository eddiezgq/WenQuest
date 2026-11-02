"""22.1 节：高斯消元的稳定性。(1) 主元很小：不选主元时 2 阶方程组的解全错，部分选主元后正确；
(2) 三种选主元策略（部分、车式、完全）的增长因子：威尔金森矩阵、随机矩阵、两点边值问题的多重打靶矩阵；
(3) 多重打靶矩阵：条件数只有 8 左右，部分选主元的增长因子随区间数指数增长，解的误差随之变大；完全选主元、QR 分解都没有问题；
(4) 对角占优与对称正定矩阵：不选主元也不增长；(5) 运算量：部分选主元比较 O(n²) 次，完全选主元比较 O(n³) 次。"""
import numpy as np

from _ge import lu, shooting, solve, wilkinson
from _num import sci
from bookout import out, tex, vec

rng = np.random.default_rng(22011)
# (1) 主元很小
eps = 1e-20
A = np.array([[eps, 1.0], [1.0, 1.0]])
b = np.array([1.0, 2.0])
xtrue = np.linalg.solve(np.array([[eps, 1.0], [1.0, 1.0]]), b)   # 部分选主元，可信
l21 = 1 / eps
u22 = 1 - l21                      # 舍入后就是 −10²⁰
x2 = (b[1] - l21 * b[0]) / u22
x1 = (b[0] - x2) / eps
xp, _ = solve(A, b, "none")
assert abs(xp[0] - x1) < 1e-12 and xp[0] == 0.0
out(x_np=vec([x1, x2], 4), x_true=vec(xtrue, 4), u22=sci(u22, 0), u22_exact=sci(1 - 1e20, 0))
# 不选主元的 L、U 相乘：(2,2) 元变成了 0
P, Q, L, U, g = lu(A, "none")
LU = L @ U
out(LU22=float(LU[1, 1]), g_none=sci(g, 0))

# (2) 三种策略的增长因子
res = {}
for name, M in (("w30", wilkinson(30)), ("sh40", shooting(40))):
    for piv in ("partial", "rook", "complete"):
        res[(name, piv)] = lu(M, piv)[4]
gr = {piv: [] for piv in ("partial", "rook", "complete")}
for trial in range(50):
    M = rng.standard_normal((100, 100))
    for piv in gr:
        gr[piv].append(lu(M, piv)[4])
out(w30_p=sci(res[("w30", "partial")], 1), w30_r=float(res[("w30", "rook")]), w30_c=float(res[("w30", "complete")]),
    sh_p=sci(res[("sh40", "partial")], 1), sh_r=float(res[("sh40", "rook")]), sh_c=float(res[("sh40", "complete")]),
    rnd_p=float(np.median(gr["partial"])), rnd_r=float(np.median(gr["rook"])), rnd_c=float(np.median(gr["complete"])),
    rnd_pmax=float(max(gr["partial"])), rnd_cmax=float(max(gr["complete"])))

# (3) 多重打靶矩阵：区间数 N 与增长因子、条件数、误差
rows = []
for N in (10, 20, 40, 60, 80):
    A = shooting(N)
    n = A.shape[0]
    x = rng.standard_normal(n)
    b = A @ x
    xp, gp = solve(A, b, "partial")
    xc, gc = solve(A, b, "complete")
    Qm, Rm = np.linalg.qr(A)
    xq = np.linalg.solve(Rm, Qm.T @ b)
    e = lambda y: float(np.linalg.norm(y - x) / np.linalg.norm(x))
    rows.append((N, gp, gc, np.linalg.cond(A), e(xp), e(xc), e(xq)))
for N, gp, gc, k, ep, ec, eq in rows:
    out(**{f"N{N}_gp": sci(gp, 1), f"N{N}_gc": float(gc), f"N{N}_k": float(k), f"N{N}_ep": sci(ep, 1), f"N{N}_ec": sci(ec, 1), f"N{N}_eq": sci(eq, 1)})
ev = np.linalg.eigvals(np.array([[-1 / 6, 1.0], [1.0, -1 / 6]]))
out(evM=", ".join(f"{z:.4g}" for z in sorted(ev.real)), growE=float(np.exp(max(ev.real) * 0.3)))

# (4) 列对角占优、对称正定：不选主元也不增长
n = 60
D = rng.standard_normal((n, n))
D += np.diag(np.abs(D).sum(axis=0) + 1.0)             # 按列严格对角占优
S = rng.standard_normal((n, n))
S = S @ S.T + n * np.eye(n)                           # 对称正定
out(g_dd=float(lu(D, "none")[4]), g_spd=float(lu(S, "none")[4]))
# (5) 比较次数
nn = 1000
out(cmp_p=sci(nn ** 2 / 2, 1), cmp_c=sci(nn ** 3 / 3, 1), flops=sci(2 * nn ** 3 / 3, 1))
