"""算例 8.1.1～8.1.4：把平面 2R 臂的逆运动学写成无约束优化 f(θ) = ½‖p(θ) − p_d‖²。

- 8.1.1 起点处的梯度（式 (8.1.5)）与方向导数，并用差商核对；
- 8.1.2 解处的黑塞矩阵、特征值、条件数和梯度下降的稳定步长上限（定理 8.1.6）；
- 8.1.3 梯度下降（几种固定步长、阿米霍线搜索）与牛顿法的迭代次数，与解析逆解和 scipy 的 BFGS 比较；
  并验证：梯度下降后期每步误差缩小的倍数，等于由黑塞矩阵特征值预测的 max|1 − αλ_i|；
- 8.1.4 牛顿法从另一个起点出发收敛到鞍点；加保护的牛顿法收敛到极小点。
"""
import math

import numpy as np
from scipy.optimize import minimize

from _opt import L2R, d, gradient_descent, ik_closed_2r, jac, newton, tip, tip_hessians
from bookout import out, tex, vec

L = L2R
pd = np.array([0.5, 0.4])                    # 目标点，m


def f(th):
    r = tip(th, L) - pd
    return 0.5 * float(r @ r)


def grad(th):
    return jac(th, L).T @ (tip(th, L) - pd)


def hess(th):
    J, r, H2 = jac(th, L), tip(th, L) - pd, tip_hessians(th, L)
    return J.T @ J + r[0] * H2[0] + r[1] * H2[1]


# ---------------------------------------------------------------- 算例 8.1.1：起点处的梯度
th0 = np.array([0.0, d(90)])
p0 = tip(th0, L)
r0 = p0 - pd
J0 = jac(th0, L)
g0 = grad(th0)
h = 1e-6
g_fd = np.array([(f(th0 + h * e) - f(th0 - h * e)) / (2 * h) for e in np.eye(2)])
assert np.allclose(g0, g_fd, atol=1e-9)                                  # 梯度公式与差商一致
u = np.array([1.0, 1.0]) / math.sqrt(2)                                  # 两个关节同时等量转动的方向
Du = float(g0 @ u)
Du_fd = (f(th0 + h * u) - f(th0 - h * u)) / (2 * h)
assert abs(Du - Du_fd) < 1e-9                                            # 方向导数 = ∇f · u（定理 8.1.1）
ud = -g0 / np.linalg.norm(g0)
assert abs(float(g0 @ ud) + np.linalg.norm(g0)) < 1e-15                  # 最速下降方向上的变化率 = −‖∇f‖

# ---------------------------------------------------------------- 算例 8.1.2：解处的黑塞矩阵
ts = ik_closed_2r(pd, L, +1)                                             # 解析逆解（肘部向下的一支）
assert np.linalg.norm(tip(ts, L) - pd) < 1e-14
Hs = hess(ts)
Js = jac(ts, L)
assert np.allclose(Hs, Js.T @ Js, atol=1e-14)                            # 残差为零处，黑塞矩阵 = JᵀJ
H_fd = np.array([(grad(ts + h * e) - grad(ts - h * e)) / (2 * h) for e in np.eye(2)])
assert np.allclose(Hs, H_fd, atol=1e-8)
lam = np.linalg.eigvalsh(Hs)
kappa = lam[1] / lam[0]
alpha_max = 2 / lam[1]
alpha_best = 2 / (lam[0] + lam[1])
rate_best = (kappa - 1) / (kappa + 1)
assert lam[0] > 0                                                        # 二阶充分条件：正定，严格局部极小

# ---------------------------------------------------------------- 算例 8.1.3：几种方法的迭代次数
tol = 1e-8                                                               # 停止条件：‖∇f‖ < 10⁻⁸
runs = {}
for a in (1.0, 3.0):
    x, path, _ = gradient_descent(f, grad, th0, alpha=a, tol=tol)
    runs[a] = (x, path)
    assert np.linalg.norm(x - ts) < 1e-6
x4, path4, _ = gradient_descent(f, grad, th0, alpha=4.0, tol=tol, kmax=2000)
assert np.linalg.norm(grad(x4)) > 1e-3                                   # α = 4 超过上限 2/λ_max：不收敛
xa, patha, nfa = gradient_descent(f, grad, th0, tol=tol, alpha0=8.0)     # 阿米霍回溯，试探步长从 8 开始
assert np.linalg.norm(xa - ts) < 1e-6
xn, pathn = newton(grad, hess, th0, tol=1e-12)
assert np.linalg.norm(xn - ts) < 1e-13
errn = [float(np.linalg.norm(q - ts)) for q in pathn]
# 二次收敛：e_{k+1} / e_k² 趋于常数
ratios = [errn[k + 1] / errn[k] ** 2 for k in range(len(errn) - 2)]
assert errn[3] < 1e-5 and errn[-1] < 1e-12

# 梯度下降后期误差每步缩小的倍数，与 max|1 − αλ_i| 比较（定理 8.1.6）
x3, path3 = runs[3.0]
e3 = np.linalg.norm(path3 - ts, axis=1)
obs_rate = float(np.exp(np.mean(np.log(e3[41:61] / e3[40:60]))))
pred_rate = float(max(abs(1 - 3.0 * lam[0]), abs(1 - 3.0 * lam[1])))
assert abs(obs_rate - pred_rate) < 5e-3

# scipy 的 BFGS（拟牛顿法）作为独立核对
res = minimize(f, th0, jac=grad, method="BFGS", options={"gtol": tol})
assert res.success and np.linalg.norm(res.x - ts) < 1e-6

# ---------------------------------------------------------------- 算例 8.1.4：牛顿法收敛到鞍点
th_b = np.array([0.0, 0.3])
Hb = hess(th_b)
lam_b = np.linalg.eigvalsh(Hb)
assert lam_b[0] < 0                                                      # 起点处黑塞矩阵不定
xs, paths = newton(grad, hess, th_b, tol=1e-12)
assert abs(xs[1]) < 1e-9                                                 # θ2 = 0：手臂伸直指向目标
assert np.linalg.norm(grad(xs)) < 1e-12
lam_s = np.linalg.eigvalsh(hess(xs))
assert lam_s[0] < 0 < lam_s[1]                                           # 鞍点
Hsad = hess(xs)
assert Hsad[0, 0] > 0 and Hsad[1, 1] > 0                                 # 对角元都为正：单独转一个关节不能下降
v_neg = np.linalg.eigh(Hsad)[1][:, 0]
assert v_neg[0] * v_neg[1] < 0                                           # 下降方向：弯关节 2 的同时关节 1 反向转
dist_s = float(np.linalg.norm(tip(xs, L) - pd))
assert abs(dist_s - (sum(L) - np.linalg.norm(pd))) < 1e-12               # 伸直的臂到目标的距离 = L1 + L2 − |p_d|
xg, pathg = newton(grad, hess, th_b, tol=1e-12, f=f, safeguard=True)
assert np.linalg.norm(xg - ts) < 1e-10                                   # 加保护后收敛到极小点

out(
    pd=vec(pd, 2), th0=vec(np.degrees(th0), 0), p0=vec(p0, 3), r0=vec(r0, 3), J0=tex(J0, 3), g0=vec(g0, 4),
    g0x=g0[0], g0y=g0[1], gnorm0=float(np.linalg.norm(g0)), Du=Du, ud=vec(ud, 4),
    ts_deg=vec(np.degrees(ts), 2), ts1=math.degrees(ts[0]), ts2=math.degrees(ts[1]),
    Hs=tex(Hs, 4), lmin=lam[0], lmax=lam[1], kappa=kappa, alpha_max=alpha_max, alpha_best=alpha_best,
    rate_best=rate_best, k1=len(runs[1.0][1]) - 1, k3=len(path3) - 1, ka=len(patha) - 1, nfa=nfa,
    kn=len(pathn) - 1, e0=errn[0],
    e1=errn[1], e2=errn[2], e3=errn[3], e4=errn[4], ratio2=ratios[1], ratio3=ratios[2],
    f4=f(x4), g4=float(np.linalg.norm(grad(x4))),
    obs_rate=obs_rate, pred_rate=pred_rate, bfgs_nit=int(res.nit), bfgs_err=float(np.linalg.norm(res.x - ts)),
    lam_b=vec(lam_b, 4), xs_deg=vec(np.degrees(xs), 2), lam_s=vec(lam_s, 4), dist_s=dist_s, kg=len(pathg) - 1,
    ks=len(paths) - 1,
)
