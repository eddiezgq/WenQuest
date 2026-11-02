"""23.2 节：秩亏与截断 SVD。UR5e 运动学标定的线性化：在名义参数处，50 个位姿的末端位置（150 个测量）对 24 个 DH 参数的雅可比矩阵 J。
(1) J 的奇异值：前 18 个在 0.4～13 之间，后 6 个是差分误差量级——J 数值上秩为 18，有 6 个参数组合“看不见”；
(2) 带列主元的 QR 分解挑出 18 个可辨识的参数，剩下 6 个是哪些（末关节零点 θ₀₆ 与扭角 α₆ 不影响法兰中心的位置；
三个平行关节轴的 d₂、d₃、d₄ 只有和可辨识；等等）；
(3) 线性化的标定问题 J δp ≈ y − f(p₀)：保留前 k 个奇异值的截断 SVD 解的范数和残差；保留全部 24 个时修正量大得荒谬；
(4) 最小范数解与“只估计 18 个参数”的解给出相同的预测（在另外 30 个验证位姿上，与真实位置比较）。"""
import numpy as np
from scipy.linalg import qr

from _num import sci
from _ur5e import NAMES, NOMINAL, TEXNAMES, fk_all, jac, measure, poses, true_params
from bookout import T, out

Q = poses(50)
pt = true_params()
y = measure(pt, Q)
J = jac(NOMINAL, Q)
U, s, Vt = np.linalg.svd(J, full_matrices=False)
rank = int(np.sum(s > s[0] * 1e-6))
out(s_big=", ".join(f"{x:.2f}" for x in s[:3]), s18=float(s[17]), s19=sci(float(s[18]), 1), rank=rank,
    m=J.shape[0], n=J.shape[1], kJ18=float(s[0] / s[17]))
# 列主元 QR
_, R, piv = qr(J, pivoting=True, mode="economic")
dropped = [TEXNAMES[i] for i in piv[rank:]]
out(dropped=T("\\text{、}", ",\\ ").join(dropped), rdiag18=float(abs(R[17, 17])), rdiag19=sci(float(abs(R[18, 18])), 1))
# 零空间：SVD 给出的 v₁₉…v₂₄ 是这个 6 维子空间的任意一组基；按几何分析写出一组稀疏的基，验证它与 SVD 的零空间相同
k = {nm: i for i, nm in enumerate(NAMES)}
d6 = NOMINAL[k["d6"]]


def comb(**w):
    v = np.zeros(24)
    for nm, val in w.items():
        v[k[nm]] = val
    return v


B = np.array([comb(θ06=1), comb(α6=1), comb(d2=1, d3=-1), comb(d3=1, d4=-1),
              comb(θ05=1, a5=d6), comb(α5=1, d5=-d6)]).T          # θ₀₆；α₆；d₂ − d₃；d₃ − d₄；θ₀₅ 与 a₅；α₅ 与 d₅
Qb = np.linalg.qr(B)[0]
out(null_res=sci(float(max(np.linalg.norm(J @ b) / np.linalg.norm(b) for b in B.T)), 1),
    null_cos=float(np.min(np.linalg.svd(Vt[rank:] @ Qb, compute_uv=False))), d6_mm=float(d6 * 1000))
# (3) 截断 SVD
r0 = y - fk_all(NOMINAL, Q)
c = U.T @ r0
rows = []
for k in (6, 12, 18, 20, 22):
    dp = Vt[:k].T @ (c[:k] / s[:k])
    res = np.linalg.norm(J @ dp - r0) / np.sqrt(len(r0))
    rows.append((k, np.linalg.norm(dp), res))
    out(**{f"t{k}_norm": sci(float(np.linalg.norm(dp)), 1), f"t{k}_res": float(res * 1000)})
out(res0=float(np.linalg.norm(r0) / np.sqrt(len(r0)) * 1000))
# (4) 验证：另取 30 个位姿
Qv = poses(30, seed=23064)
yv = fk_all(pt, Qv)                                  # 验证用真实位置（相当于用精度高得多的测量）
dp18 = Vt[:18].T @ (c[:18] / s[:18])
sub = piv[:rank]
dsub = np.linalg.lstsq(J[:, sub], r0, rcond=None)[0]
dp_sub = np.zeros(24)
dp_sub[sub] = dsub
ev = lambda p: float(np.sqrt(np.mean((fk_all(p, Qv) - yv) ** 2)) * 1000)
out(v_nom=ev(NOMINAL), v_tsvd=ev(NOMINAL + dp18), v_sub=ev(NOMINAL + dp_sub), dp_diff=sci(float(np.linalg.norm(dp18 - dp_sub)), 1),
    kJsub=float(np.linalg.cond(J[:, sub])))
