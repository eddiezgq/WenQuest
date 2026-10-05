"""11.5 节：用 QR 解最小二乘。10.4 节的例子：Rx̂ = Qᵀb 给出 x̂ = (5, −3)；残差的长度等于 Qᵀb 中“多出来”的分量。
病态的比较：在 [0, 1] 上以单项式为基拟合多项式，构造已知精确最小二乘解的问题，比较正规方程、豪斯霍尔德 QR、SVD（lstsq）的相对误差：
正规方程的误差随条件数的平方增长，QR 与 SVD 随条件数增长。"""
import numpy as np

from _frac import fvec
from _num import sci
from bookout import out, tex, vec

A = np.array([[1.0, 0], [1, 1], [1, 2]])
b = np.array([6.0, 0, 0])
Qf, Rf = np.linalg.qr(A, mode="complete")
s = np.sign(np.diag(Rf[:2]))
Qf[:, :2] *= s; Rf[:2] *= s[:, None]
if Qf[0, 2] < 0:
    Qf[:, 2] *= -1
c = Qf.T @ b
xh = np.linalg.solve(Rf[:2], c[:2])
out(Q=tex(Qf[:, :2], 4), R=tex(Rf[:2], 4), c=vec(c, 4), xh=fvec(xh), res=float(abs(c[2])), sqrt6=float(np.sqrt(6)))
# 病态：在 t ∈ [0, 1] 上用单项式 1, t, …, t^d 拟合（例如把一段关节轨迹拟合成多项式），构造已知精确最小二乘解的问题
t = np.linspace(0.0, 1.0, 40)
rng = np.random.default_rng(115)
rows = []
for d in range(2, 15, 2):
    V = np.vander(t, d + 1, increasing=True)
    Qc, _ = np.linalg.qr(V, mode="complete")
    x_true = rng.normal(size=d + 1)
    r = Qc[:, d + 1:] @ rng.normal(size=V.shape[0] - d - 1) * 1e-8      # 与列空间正交的小残差，最小二乘解恰为 x_true
    bb = V @ x_true + r
    xn = np.linalg.solve(V.T @ V, V.T @ bb)
    Qr, Rr = np.linalg.qr(V)
    xq = np.linalg.solve(Rr, Qr.T @ bb)
    xs = np.linalg.lstsq(V, bb, rcond=None)[0]
    rel = lambda z: float(np.linalg.norm(z - x_true) / np.linalg.norm(x_true))
    rows.append((d, float(np.linalg.cond(V)), rel(xn), rel(xq), rel(xs)))
out(rows=[[d, k, en, eq, es] for d, k, en, eq, es in rows])
for d, k, en, eq, es in rows:
    out(**{f"k{d}": sci(k, 0), f"n{d}": sci(en, 0), f"q{d}": sci(eq, 0), f"s{d}": sci(es, 0)})
