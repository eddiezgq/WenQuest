"""21.3 节：格什戈林圆盘定理。(1) 算例：三个互不相交的圆盘，各含一个特征值；行圆盘与列圆盘；
(2) 机械臂三个关节电机的六节点热模型（每个电机两节点，同 16.1 节的 _motor.py；相邻关节的外壳经连杆导热）：
行圆盘碰到原点，证不出稳定；对角相似变换 D⁻¹AD 把圆盘推离原点，不求特征值就证明了稳定，并给出最慢时间常数的上界；
(3) 用缩放把一个圆盘缩小，把特征值“围”得更紧。"""
import numpy as np

from _thermal import model
from bookout import out, tex, vec


def discs(A):
    c = np.diag(A)
    r = np.sum(np.abs(A), axis=1) - np.abs(c)
    return c, r


# (1) 算例 21.3.1
A = np.array([[10.0, 1.0, -0.5], [0.4, 4.0, 0.8], [0.6, 0.2, -2.0]])
c, r = discs(A)
cc, rc = discs(A.T)
ev = np.sort(np.linalg.eigvals(A).real)
assert np.all(np.abs(np.linalg.eigvals(A).imag) < 1e-12)
for lam in np.linalg.eigvals(A):
    assert np.any(np.abs(lam - c) <= r + 1e-12)
out(A=tex(A, 1), c=vec(c, 0), r=vec(r, 1), rc=vec(rc, 1), ev=vec(ev, 4))
# 缩放：D = diag(1, 1, δ)，D⁻¹AD 第 3 行的元素除以 δ（半径变大），其余行中第 3 列的元素乘 δ（半径变小）
for name, dl in (("a", 0.25), ("b", 0.1)):
    D = np.diag([1, 1, dl])
    c2, r2 = discs(np.linalg.inv(D) @ A @ D)
    out(**{f"r_{name}": vec(r2, 3)})
    if name == "a":
        out(ra1=float(r2[0]), ra2=float(r2[1]))

# (2) 三个关节电机的热模型：节点顺序 (w₁, h₁, w₂, h₂, w₃, h₃)
Cap, G, Ath = model()
c, r = discs(Ath)
right = c + r
evt = np.sort(np.linalg.eigvals(Ath).real)
out(cw=float(c[0]), rw=float(r[0]), ch1=float(c[1]), rh1=float(r[1]), ch2=float(c[3]), rh2=float(r[3]), right_max=float(np.max(right)))
assert abs(right[0]) < 1e-15
# 缩放：D = diag(1, s, 1, s, 1, s)，s < 1 把绕组行的半径乘 s，外壳行的半径中绕组那一项除以 s
best = None
for s in np.linspace(0.5, 1.0, 501):
    D = np.diag([1, s] * 3)
    c2, r2 = discs(np.linalg.inv(D) @ Ath @ D)
    m = np.max(c2 + r2)
    if best is None or m < best[1]:
        best = (s, m, c2, r2)
s_best, m_best = best[0], best[1]
s9 = 0.9
D9 = np.diag([1, s9] * 3)
c9, r9 = discs(np.linalg.inv(D9) @ Ath @ D9)
out(s9=s9, right9=float(np.max(c9 + r9)), rw9=float(r9[0]), rh9=float(r9[3]), s_best=float(s_best), right_best=float(m_best),
    tau_bound=float(-1 / m_best), tau_bound_min=float(-1 / m_best / 60))
out(evt=", ".join(f"{-1/x:.0f}" for x in evt[::-1]), tau_slow=float(-1 / evt[-1]), tau_slow_min=float(-1 / evt[-1] / 60), lam_slow=float(evt[-1]),
    lam_fast=float(evt[0]))
# 对称化：C^{1/2} A C^{-1/2} = −C^{-1/2} G C^{-1/2} 对称，特征值为实数
S = np.diag(Cap ** 0.5) @ Ath @ np.diag(Cap ** -0.5)
assert np.allclose(S, S.T)
# 严格对角占优 ⇒ 可逆：(G 加上一个外部热导) 例
out(dd_rows=", ".join("{:.2f}".format(abs(G[i, i]) - (np.sum(np.abs(G[i])) - abs(G[i, i]))) for i in range(6)))
