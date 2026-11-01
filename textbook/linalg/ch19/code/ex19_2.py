"""19.2 节：主成分分析。算例 19.2.1 噪声与振动两项（标准化）的主成分；投影方差与残差平方和之和不变；
200 件减速器六项检测的主成分（相关矩阵）：特征值、方差解释比、载荷；得分互不相关；
不标准化（直接用协方差矩阵）时，结果随单位改变。"""
import numpy as np

from _num import fix_sign
from _qc import ITEMS, N_I, SHORT, X_I
from bookout import out, tex, vec

X = X_I
m = X.mean(axis=0)
Xc = X - m
s = Xc.std(axis=0, ddof=1)
Z = Xc / s
R = Z.T @ Z / (N_I - 1)

# 算例 19.2.1：噪声与振动两项
R2 = R[np.ix_([2, 4], [2, 4])]
w2, V2 = np.linalg.eigh(R2)
w2, V2 = w2[::-1], fix_sign(V2[:, ::-1])
out(R2=tex(R2, 3), r2=float(R2[0, 1]), ev2=vec(w2, 3), V2=tex(V2, 3), w2_1=float(w2[0]), w2_2=float(w2[1]),
    ratio2=float(100 * w2[0] / w2.sum()))
# 投影方差 + 残差平方和/(N−1) = 总方差（勾股定理），对每个方向都成立
Z2 = Z[:, [2, 4]]
for deg in (0, 30, 45, 60, 90, 135):
    u = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg))])
    proj = Z2 @ u
    resid = Z2 - np.outer(proj, u)
    assert abs(np.var(proj, ddof=1) + np.sum(resid ** 2) / (N_I - 1) - np.trace(R2)) < 1e-10
var0 = float(np.var(Z2[:, 0], ddof=1))
out(var_axis=var0)

# 六项检测的主成分（相关矩阵）
w, V = np.linalg.eigh(R)
w, V = w[::-1], fix_sign(V[:, ::-1])
ratio = w / w.sum()
out(w=vec(w, 3), ratio=vec(100 * ratio, 1), cum=vec(100 * np.cumsum(ratio), 1),
    w1=float(w[0]), w2=float(w[1]), w3=float(w[2]),
    c1=float(100 * ratio[0]), c2=float(100 * ratio[:2].sum()), c3=float(100 * ratio[:3].sum()),
    V3=tex(V[:, :3], 2), trR=float(np.trace(R)))
# 载荷中绝对值最大的几项
for k in range(3):
    big = [SHORT[i] for i in np.argsort(-np.abs(V[:, k]))[:3]]
    out(**{f"big{k + 1}": "、".join(big)})
# 得分 T = Z V 的协方差是对角矩阵 Λ
Tsc = Z @ V
C = Tsc.T @ Tsc / (N_I - 1)
out(offdiag=float(np.max(np.abs(C - np.diag(np.diag(C))))))
assert np.allclose(np.diag(C), w)
# 前 k 个主成分的残差：∑‖z − ẑ‖²/(N−1) = λ_{k+1} + … + λ_p（定理 19.2.2）
for k in (1, 2, 3):
    Vk = V[:, :k]
    E = Z - Z @ Vk @ Vk.T
    assert abs(np.sum(E ** 2) / (N_I - 1) - w[k:].sum()) < 1e-10
# 樊畿不等式：随便取一个二维子空间，投影方差之和不超过 λ₁ + λ₂
rng = np.random.default_rng(19)
Q, _ = np.linalg.qr(rng.standard_normal((6, 2)))
out(rand2=float(np.trace(Q.T @ R @ Q)), top2=float(w[:2].sum()))

# 不标准化：直接用协方差矩阵，直径（μm）方差最大，第一主成分几乎就是“直径”
Sx = Xc.T @ Xc / (N_I - 1)
ws, Vs = np.linalg.eigh(Sx)
ws, Vs = ws[::-1], fix_sign(Vs[:, ::-1])
out(ws=vec(ws, 2), vs1=vec(Vs[:, 0], 2), cs1=float(100 * ws[0] / ws.sum()))
# 把直径和跳动的单位改成 mm：它们的方差缩小 10⁶ 倍，第一主成分变成“温升 + 噪声”
scale = np.array([1e-3, 1e-3, 1, 1, 1, 1])
Sm = (Xc * scale).T @ (Xc * scale) / (N_I - 1)
wm, Vm = np.linalg.eigh(Sm)
wm, Vm = wm[::-1], fix_sign(Vm[:, ::-1])
out(vm1=vec(Vm[:, 0], 2), cm1=float(100 * wm[0] / wm.sum()))
out(items=ITEMS)
