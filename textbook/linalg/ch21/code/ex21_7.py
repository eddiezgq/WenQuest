"""21.7 节：矩阵微积分。(1) 常用公式与有限差分的比较：∇(aᵀx)、∇(xᵀAx)、∇‖Ax − b‖²、∂tr(AX)/∂X、∂ln det X/∂X、∂det X/∂X；
(2) 最小二乘的梯度与梯度下降（实验 21.7 的数据）：AGV 测距传感器标定 d ≈ a·r + c，步长 η < 1/λ_max(AᵀA) 才收敛，
收敛快慢由 κ(AᵀA) 决定，读数先去均值后快得多；(3) 三连杆平面机械臂的可操作度 w(q) = √det(J Jᵀ) 的梯度：
解析公式与有限差分一致；在零空间里沿梯度运动，末端不动而 w 增大，远离奇异位形。"""
import math

import numpy as np

from _num import sci
from bookout import out, tex, vec

rng = np.random.default_rng(21071)


def num_grad(f, X, h=1e-6):
    X = np.asarray(X, float)
    g = np.zeros_like(X)
    for idx in np.ndindex(X.shape):
        E = np.zeros_like(X)
        E[idx] = h
        g[idx] = (f(X + E) - f(X - E)) / (2 * h)
    return g


rel = lambda a, b: float(np.linalg.norm(a - b) / np.linalg.norm(b))
n = 4
a = rng.standard_normal(n)
A = rng.standard_normal((n, n))
x = rng.standard_normal(n)
Am = rng.standard_normal((6, n))
bm = rng.standard_normal(6)
X = rng.standard_normal((n, n)) + n * np.eye(n)          # 行列式为正
checks = {
    "lin": (num_grad(lambda v: a @ v, x), a),
    "quad": (num_grad(lambda v: v @ A @ v, x), (A + A.T) @ x),
    "ls": (num_grad(lambda v: np.sum((Am @ v - bm) ** 2), x), 2 * Am.T @ (Am @ x - bm)),
    "tr": (num_grad(lambda M: np.trace(A @ M), X), A.T),
    "logdet": (num_grad(lambda M: math.log(np.linalg.det(M)), X), np.linalg.inv(X).T),
    "det": (num_grad(lambda M: np.linalg.det(M), X), np.linalg.det(X) * np.linalg.inv(X).T),
    "trq": (num_grad(lambda M: np.trace(M.T @ A @ M), X), (A + A.T) @ X),
}
for k, (g_num, g_formula) in checks.items():
    e = rel(g_num, g_formula)
    assert e < 1e-6, k
    out(**{f"c_{k}": sci(e, 1)})
# 布局约定：∂(Ax)/∂x 的雅可比矩阵（分子布局）就是 A
Jn = np.column_stack([num_grad(lambda v: (A @ v)[i], x) for i in range(n)]).T
assert np.allclose(Jn, A, atol=1e-6)

# (2) 测距传感器标定：真实距离 d（激光跟踪仪测得），原始读数 r（单位 mm 的计数），模型 d = a r + c
d = np.linspace(0.3, 3.0, 12)
r = (d - 0.031) / 0.00098 + np.random.default_rng(7).normal(0, 4.0, d.size)   # 读数（计数），与图 21.7.1 相同
D = np.column_stack([r, np.ones_like(r)])
theta = np.linalg.lstsq(D, d, rcond=None)[0]
H = D.T @ D
lam = np.linalg.eigvalsh(H)
eta_max = 1 / lam[-1]
out(a_fit=float(theta[0] * 1000), c_fit=float(theta[1] * 1000), lam_min=sci(float(lam[0]), 2), lam_max=sci(float(lam[-1]), 2),
    kH=sci(float(lam[-1] / lam[0]), 1), eta_max=sci(float(eta_max), 2), rmean=float(r.mean()))


def gd(Dm, y, eta, steps):
    th = np.zeros(2)
    for _ in range(steps):
        th = th - eta * 2 * Dm.T @ (Dm @ th - y)
    return th


f0 = lambda th, Dm=D: float(np.sum((Dm @ th - d) ** 2))
fstar = f0(theta)
# 固定步长的最优值 η = 1/(λ_min + λ_max)，误差每步乘以 (κ − 1)/(κ + 1)
eta = 1 / (lam[0] + lam[-1])
rate = (lam[-1] - lam[0]) / (lam[-1] + lam[0])
th_ok = gd(D, d, eta, 10000)
th_bad = gd(D, d, 1.05 * eta_max, 200)
out(err_c_ok=float(abs(th_ok[1] - theta[1]) * 1000), f_bad=sci(f0(th_bad), 1), rate=float(rate),
    steps_e3=sci(float(math.log(1e-3) / math.log(rate)), 1))
# 读数去均值、除以标准差后：AᵀA = n I，κ = 1，一步就到
rs = (r - r.mean()) / r.std()
Ds = np.column_stack([rs, np.ones_like(rs)])
lams = np.linalg.eigvalsh(Ds.T @ Ds)
ths = gd(Ds, d, 1 / (lams[0] + lams[-1]), 1)
thstar = np.linalg.lstsq(Ds, d, rcond=None)[0]
assert np.allclose(ths, thstar)
Dsc = np.column_stack([r / r.std(), np.ones_like(r)])
lsc = np.linalg.eigvalsh(Dsc.T @ Dsc)
out(kHs=float(lams[-1] / lams[0]), nsamp=int(d.size), kHsc=float(lsc[-1] / lsc[0]), rate_sc=float((lsc[-1] - lsc[0]) / (lsc[-1] + lsc[0])))

# (3) 三连杆平面机械臂的可操作度
L = np.array([0.40, 0.35, 0.25])


def fk(q):
    c = np.cumsum(q)
    return np.array([np.sum(L * np.cos(c)), np.sum(L * np.sin(c))])


def jac(q):
    c = np.cumsum(q)
    J = np.zeros((2, 3))
    for j in range(3):
        J[0, j] = -np.sum(L[j:] * np.sin(c[j:]))
        J[1, j] = np.sum(L[j:] * np.cos(c[j:]))
    return J


def djac(q, k):
    """∂J/∂q_k：第 j 列只与 c_j, …, c_3 有关，而 ∂c_i/∂q_k = 1（i ≥ k）。"""
    c = np.cumsum(q)
    Jk = np.zeros((2, 3))
    for j in range(3):
        m = max(j, k)
        Jk[0, j] = -np.sum(L[m:] * np.cos(c[m:]))
        Jk[1, j] = -np.sum(L[m:] * np.sin(c[m:]))
    return Jk


def manip(q):
    J = jac(q)
    return math.sqrt(np.linalg.det(J @ J.T))


def grad_w(q):
    J = jac(q)
    M = J @ J.T
    w = math.sqrt(np.linalg.det(M))
    Mi = np.linalg.inv(M)
    return np.array([0.5 * w * np.trace(Mi @ (djac(q, k) @ J.T + J @ djac(q, k).T)) for k in range(3)])


q0 = np.radians([45.0, 5.0, 170.0])                     # 腕部几乎折回：接近奇异
g_an = grad_w(q0)
g_fd = num_grad(manip, q0)
assert rel(g_fd, g_an) < 1e-6
out(q0=vec(np.degrees(q0), 0), w0=float(manip(q0)), g_an=vec(g_an, 4), g_rel=sci(rel(g_fd, g_an), 1))
# 零空间运动：q̇ = (I − J⁺J) ∇w，末端保持不动
q = q0.copy()
p0 = fk(q0)
for _ in range(400):
    J = jac(q)
    Jp = np.linalg.pinv(J)
    N = np.eye(3) - Jp @ J
    g = N @ grad_w(q)
    dq = g / max(1e-12, np.linalg.norm(g)) * math.radians(0.5)       # 每步在零空间里沿梯度方向转 0.5°
    dq += Jp @ (p0 - fk(q + dq) + J @ dq)            # 一步牛顿校正，抵消末端的漂移
    q = q + dq
out(q1=vec(np.degrees(q), 1), w1=float(manip(q)), drift=sci(float(1000 * np.linalg.norm(fk(q) - p0)), 1), p0=vec(p0, 3),
    sig0=vec(np.linalg.svd(jac(q0), compute_uv=False), 3), sig1=vec(np.linalg.svd(jac(q), compute_uv=False), 3))
