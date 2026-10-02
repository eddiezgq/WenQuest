"""8.2 节：等式约束优化与拉格朗日乘子。

- 菜园（8.2.2～8.2.4 节）：靠墙用 20 m 篱笆围矩形，面积最大；乘子 = 多 1 m 篱笆多出的面积（式 (8.2.7)）；
- 算例 8.2.1 冗余 3R 臂的加权最小范数关节速度（式 (8.2.9)）：W = I 时与算例 2.5.2 相同；KKT 方程组 (8.2.8) 与闭式公式核对；
- 算例 8.2.2 关节装有扭簧的 3R 臂，手把末端拉到 p_d：min ½(θ − θ_c)ᵀK(θ − θ_c) s.t. p(θ) = p_d。
  用拉格朗日-牛顿法 (8.2.10) 求解，与 scipy 的 trust-constr 比较；验证 −λ 就是手施加的力：
  (a) 静力平衡 τ + JᵀF = 0（式 (8.2.13)）；(b) 最优值对 p_d 的导数（差商）等于 F；(c) 约化黑塞矩阵为正（定理 8.2.4）；
- 算例 8.2.3 晾衣绳上的衣架：乘子就是绳的拉力。
"""
import math
import warnings

import numpy as np
from scipy.optimize import NonlinearConstraint, minimize

from _opt import L3R, d, jac, tip, tip_hessians
from bookout import out, tex, vec

# ---------------------------------------------------------------- 菜园
Lf = 20.0                                   # 篱笆总长，m
# x 为垂直于墙的两条边的边长，y 为平行于墙的边长；约束 2x + y = 20。
# 拉格朗日条件 −y + 2λ = 0、−x + λ = 0 给出 λ = x、y = 2x，代入约束得 x = 5 m、y = 10 m。
x_g = Lf / 4
y_g = Lf / 2
lam_g = x_g
S_g = x_g * y_g
S_more = (Lf + 0.01) / 4 * (Lf + 0.01) / 2   # 多 1 cm 篱笆
dS_dL = (S_more - S_g) / 0.01
assert abs(dS_dL - lam_g) < 0.01                                    # 乘子 = 最优值对篱笆长度的变化率
xs = np.linspace(0.1, 9.9, 9801)
assert abs(max(xs * (Lf - 2 * xs)) - S_g) < 1e-6                   # 穷举核对

# ---------------------------------------------------------------- 算例 8.2.1：加权最小范数关节速度
L = L3R
thc = np.array([d(30), d(60), d(-60)])      # 与算例 2.5.2 相同的形态
J = jac(thc, L)
v = np.array([0.1, 0.0])                     # 末端速度，m/s
Kw = np.diag([20.0, 10.0, 5.0])             # 权重（算例 8.2.2 中是扭簧刚度，N·m/rad）


def weighted_min_norm(W):
    Wi = np.linalg.inv(W)
    return Wi @ J.T @ np.linalg.solve(J @ Wi @ J.T, v)


def kkt_solve(W):
    K = np.block([[W, J.T], [J, np.zeros((2, 2))]])
    sol = np.linalg.solve(K, np.r_[np.zeros(3), v])
    return sol[:3], sol[3:]


thd_I = weighted_min_norm(np.eye(3))
assert np.allclose(thd_I, np.linalg.pinv(J) @ v, atol=1e-14)                  # W = I：伪逆解（算例 2.5.2）
thd_W = weighted_min_norm(Kw)
thd_kkt, lam_kkt = kkt_solve(Kw)
assert np.allclose(thd_W, thd_kkt, atol=1e-14)                                # 闭式公式与 KKT 方程组一致
assert np.allclose(J @ thd_W, v, atol=1e-14)
assert np.allclose(Kw @ thd_W + J.T @ lam_kkt, 0, atol=1e-14)                 # 驻点条件
lam_formula = -np.linalg.solve(J @ np.linalg.inv(Kw) @ J.T, v)
assert np.allclose(lam_kkt, lam_formula, atol=1e-13)
cost_I = 0.5 * thd_I @ Kw @ thd_I
cost_W = 0.5 * thd_W @ Kw @ thd_W
assert cost_W < cost_I                                                        # 加权解的加权代价更小

# ---------------------------------------------------------------- 算例 8.2.2：带扭簧的手臂被拉到 p_d
pd = np.array([0.55, 0.45])
p_c = tip(thc, L)


def f(th):
    e = th - thc
    return 0.5 * float(e @ Kw @ e)


def h(th):
    return tip(th, L) - pd


x, lam = thc.copy(), np.zeros(2)
hist = []
for k in range(20):
    Jx, H2 = jac(x, L), tip_hessians(x, L)
    gL = Kw @ (x - thc) + Jx.T @ lam
    HL = Kw + lam[0] * H2[0] + lam[1] * H2[1]
    KKT = np.block([[HL, Jx.T], [Jx, np.zeros((2, 2))]])
    step = np.linalg.solve(KKT, -np.r_[gL, h(x)])
    x, lam = x + step[:3], lam + step[3:]
    resid = float(np.linalg.norm(np.r_[Kw @ (x - thc) + jac(x, L).T @ lam, h(x)]))
    hist.append(resid)
    if resid < 1e-14:
        break
it_ln = len(hist)
Js = jac(x, L)
F = -lam                                                                      # 手施加在末端的力，N
assert np.allclose(Kw @ (x - thc), Js.T @ F, atol=1e-12)                      # (a) 扭簧力矩 = Jᵀ F
# (b) 最优值对 p_d 的导数：把 p_d 沿 x、y 各挪 1 μm，重新求解
def solve_for(target, x0, l0):
    xx, ll = x0.copy(), l0.copy()
    for _ in range(30):
        Jx, H2 = jac(xx, L), tip_hessians(xx, L)
        HL = Kw + ll[0] * H2[0] + ll[1] * H2[1]
        st = np.linalg.solve(np.block([[HL, Jx.T], [Jx, np.zeros((2, 2))]]),
                             -np.r_[Kw @ (xx - thc) + Jx.T @ ll, tip(xx, L) - target])
        xx, ll = xx + st[:3], ll + st[3:]
        if np.linalg.norm(st) < 1e-15:
            break
    return xx, ll


dd = 1e-6
grad_fstar = np.array([(f(solve_for(pd + dd * e, x, lam)[0]) - f(solve_for(pd - dd * e, x, lam)[0])) / (2 * dd) for e in np.eye(2)])
assert np.allclose(grad_fstar, F, rtol=1e-6)
# (c) 二阶条件：拉格朗日函数的黑塞矩阵在切空间（J 的零空间）上为正
H2 = tip_hessians(x, L)
HL = Kw + lam[0] * H2[0] + lam[1] * H2[1]
N = np.linalg.svd(Js)[2][2:].T                                                # J 的零空间（一维）
red = float((N.T @ HL @ N)[0, 0])
assert red > 0
lam_HL = np.linalg.eigvalsh(HL)
# scipy 独立核对（trust-constr 会对线性约束的拟牛顿更新给出无害的提醒，这里不显示）
warnings.simplefilter("ignore")
res = minimize(f, thc, method="trust-constr", jac=lambda t: Kw @ (t - thc),
               constraints=[NonlinearConstraint(h, 0, 0, jac=lambda t: jac(t, L))],
               options={"gtol": 1e-12, "xtol": 1e-14})
assert np.linalg.norm(res.x - x) < 1e-6 and np.allclose(res.v[0], lam, rtol=1e-6)
tau = -Kw @ (x - thc)                                                         # 扭簧作用在关节上的力矩，N·m（与 Jᵀ F 相抵）
assert np.allclose(tau + Js.T @ F, 0, atol=1e-12)
# 末端的顺从各向异性：在自然形态 θ_c 处，小位移时 K δθ = Jᵀ F（由式 (8.2.13)），δp ≈ J K⁻¹ Jᵀ F
Cc = J @ np.linalg.inv(Kw) @ J.T                                              # 柔度矩阵，m/N
comp_down = Cc @ np.array([0.0, -1.0])                                        # 竖直向下 1 N 的力引起的末端位移
assert comp_down[0] > 0 and comp_down[1] < 0                                  # 下降的同时向右偏
eps = 1e-3                                                                    # 用小力 1 mN 的完整非线性求解核对
_, l_small = solve_for(p_c + eps * comp_down, thc, np.zeros(2))
assert np.allclose(-l_small, [0.0, -eps], atol=1e-2 * eps)                    # 把末端拉到这一位移所需的力就是向下 1 mN

# ---------------------------------------------------------------- 算例 8.2.3：晾衣绳上的衣架
A_h, B_h = np.array([0.0, 2.0]), np.array([2.0, 2.4])     # 两个挂钩，m
ell, G = 2.6, 20.0                                         # 绳长 m，衣服重 N


def hh(P):
    return np.linalg.norm(P - A_h) + np.linalg.norm(P - B_h) - ell


Pz, lz = np.array([1.0, 1.2]), G / 2                         # 初值：拉力取重量的一半（绳竖直时的值）
for _ in range(50):
    ua, ub = (Pz - A_h) / np.linalg.norm(Pz - A_h), (Pz - B_h) / np.linalg.norm(Pz - B_h)
    gh = ua + ub
    Hh = (np.eye(2) - np.outer(ua, ua)) / np.linalg.norm(Pz - A_h) + (np.eye(2) - np.outer(ub, ub)) / np.linalg.norm(Pz - B_h)
    K2 = np.block([[lz * Hh, gh[:, None]], [gh[None, :], np.zeros((1, 1))]])
    st2 = np.linalg.solve(K2, -np.r_[np.array([0.0, G]) + lz * gh, hh(Pz)])
    Pz, lz = Pz + st2[:2], lz + st2[2]
    if np.linalg.norm(st2) < 1e-14:
        break
sin_a = (B_h[0] - A_h[0]) / ell                             # 两段绳与竖直方向夹角相等：sin α = 跨距 / 绳长
T_rope = G / (2 * math.sqrt(1 - sin_a ** 2))
assert abs(lz - T_rope) < 1e-9                              # 乘子就是绳的拉力
ua, ub = (Pz - A_h) / np.linalg.norm(Pz - A_h), (Pz - B_h) / np.linalg.norm(Pz - B_h)
assert abs(abs(ua[0]) - sin_a) < 1e-12 and abs(abs(ub[0]) - sin_a) < 1e-12      # 两段绳与竖直方向夹角相等
alpha_deg = math.degrees(math.asin(sin_a))

out(
    P_h=vec(Pz, 3), T_rope=T_rope, alpha_deg=alpha_deg,
    x_g=x_g, y_g=y_g, lam_g=lam_g, S_g=S_g, dS_dL=dS_dL,
    J=tex(J, 4), thd_I=vec(thd_I, 4), thd_W=vec(thd_W, 4), lam_v=vec(lam_kkt, 4),
    cost_I=cost_I, cost_W=cost_W,
    pc=vec(p_c, 4), pd=vec(pd, 2), th_deg=vec(np.degrees(x), 2), th1=math.degrees(x[0]), th2=math.degrees(x[1]),
    th3=math.degrees(x[2]), lam=vec(lam, 3), F=vec(F, 3), Fx=F[0], Fy=F[1], Fnorm=float(np.linalg.norm(F)), fstar=f(x),
    tau=vec(tau, 3), grad_fstar=vec(grad_fstar, 3), it_ln=it_ln,
    r1=hist[0], r2=hist[1], r3=hist[2], r4=hist[3], red=red, lHmin=lam_HL[0],
    scipy_err=float(np.linalg.norm(res.x - x)), scipy_lam=vec(res.v[0], 3),
    disp=vec(pd - p_c, 4), comp_down=vec(comp_down * 1000, 1), disp_norm=float(np.linalg.norm(pd - p_c)), work=float(F @ (pd - p_c)),
)
