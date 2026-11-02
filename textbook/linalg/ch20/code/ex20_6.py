"""20.6 节：病态问题。希尔伯特矩阵 Hₙ 的条件数（用 50 位精度计算）与双精度下解 Hₙx = Hₙ1 的误差；
它来自用 1, t, t², … 在 [0, 1] 上做最小二乘拟合；机械臂关节轨迹的多项式拟合：单项式、缩放后的单项式、勒让德多项式三种基；
威尔金森多项式：x¹⁹ 的系数改动 2⁻²³，根就跑到复平面上。"""
import math

import mpmath as mp
import numpy as np
import scipy.linalg as sla

from _num import sci
from bookout import out, vec

mp.mp.dps = 50
# (1) 希尔伯特矩阵
kap = {}
for n in range(2, 15):
    H = mp.matrix(n, n)
    for i in range(n):
        for j in range(n):
            H[i, j] = mp.mpf(1) / (i + j + 1)
    s = mp.svd_r(H, compute_uv=False)
    kap[n] = float(max(s) / min(s))
out(**{f"kH{n}": sci(kap[n], 1) for n in (4, 6, 8, 10, 12, 14)})
out(rate=float(np.polyfit(list(kap), np.log(list(kap.values())), 1)[0]), growth=float(np.exp(np.polyfit(list(kap), np.log(list(kap.values())), 1)[0])))
for n in (6, 10, 12, 14):
    H = sla.hilbert(n)
    x = np.ones(n)
    b = H @ x
    xh = np.linalg.solve(H, b)
    out(**{f"fe{n}": sci(np.linalg.norm(xh - x) / np.linalg.norm(x), 0), f"res{n}": sci(np.linalg.norm(b - H @ xh) / np.linalg.norm(b) + 1e-30, 0)})
# H₄ 的元素就是 ∫₀¹ tⁱ⁺ʲ dt
out(H4=r"\begin{pmatrix} 1 & \tfrac12 & \tfrac13 & \tfrac14 \\ \tfrac12 & \tfrac13 & \tfrac14 & \tfrac15 \\ \tfrac13 & \tfrac14 & \tfrac15 & \tfrac16 \\ \tfrac14 & \tfrac15 & \tfrac16 & \tfrac17 \end{pmatrix}")

# (2) 关节轨迹拟合：t ∈ [0, 10] s，每 50 ms 一个采样（201 个点），用 15 次多项式拟合
t = np.linspace(0, 10, 201)
tau = t / 10
q = 1.2 * (10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5) + 0.02 * np.sin(2 * math.pi * 0.25 * t)     # rad：最小加加速度轨迹 + 小振动
deg = 15
bases = {
    "mono": np.vander(t, deg + 1, increasing=True),                    # 1, t, …, t¹⁵（t 以秒计）
    "scaled": np.vander(2 * t / 10 - 1, deg + 1, increasing=True),     # 先把 t 缩放到 [−1, 1]
    "leg": np.polynomial.legendre.legvander(2 * t / 10 - 1, deg),      # 勒让德多项式
}
rng = np.random.default_rng(2006)
noise = 1e-6 * rng.standard_normal(t.size)                             # 编码器量化级别的扰动：1 μrad
for name, V in bases.items():
    c, _, rk, _ = np.linalg.lstsq(V, q, rcond=None)
    c2, *_ = np.linalg.lstsq(V, q + noise, rcond=None)
    out(**{f"k_{name}": sci(np.linalg.cond(V), 1), f"rank_{name}": int(rk),
           f"fit_{name}": float(1e3 * np.sqrt(np.mean((V @ c - q) ** 2))),                         # mrad
           f"dc_{name}": sci(np.linalg.norm(c2 - c) / np.linalg.norm(c), 0),
           f"dq_{name}": sci(np.max(np.abs(V @ c2 - V @ c)), 0)})

# (3) 威尔金森多项式 p(x) = (x − 1)(x − 2)…(x − 20)
coeffs = [mp.mpf(1)]
for r in range(1, 21):
    coeffs = [a - r * b for a, b in zip(coeffs + [0], [0] + coeffs)]
assert coeffs[1] == -210
pert = list(coeffs)
pert[1] = pert[1] - mp.mpf(2) ** -23
roots = mp.polyroots(pert, maxsteps=200, extraprec=200)
roots = sorted(roots, key=lambda z: (float(mp.re(z)), float(mp.im(z))))
cplx = [z for z in roots if abs(mp.im(z)) > 1e-10]
far = max(roots, key=lambda z: abs(mp.im(z)))
reals = [float(mp.re(z)) for z in roots if abs(mp.im(z)) <= 1e-10]
cre = sorted(float(mp.re(z)) for z in cplx)
moved = [abs(r - round(r)) for r in reals]
out(n_cplx=len(cplx), far_re=float(mp.re(far)), far_im=float(abs(mp.im(far))), d2=sci(2.0 ** -23, 2),
    n_real=len(reals), r_lo=reals[8], r_hi=reals[-1], cre_lo=cre[0], cre_hi=cre[-1], move8=sci(max(moved[:8]) + 1e-30, 0))
# 根 j 对 x¹⁹ 系数的灵敏度：∂r/∂a = −j¹⁹ / p′(j)
sens = {j: float(mp.mpf(j) ** 19 / abs(mp.fprod(j - k for k in range(1, 21) if k != j))) for j in range(1, 21)}
jmax = max(sens, key=sens.get)
out(jmax=jmax, smax=sci(sens[jmax], 1), s1=sci(sens[1], 0), s20=sci(sens[20], 1))
# 双精度下 numpy 直接从展开的系数求根（系数本身已经有舍入误差）
r_np = np.sort_complex(np.roots([float(a) for a in coeffs]))
out(np_err=float(np.max(np.abs(r_np - np.arange(1, 21)))))
