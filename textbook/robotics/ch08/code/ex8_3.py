"""算例 8.3.1～8.3.3：二次规划。

- 8.3.1 平面 2R 臂一个控制周期内的关节增量：min ½‖JΔ − e‖²，|Δ_i| ≤ 0.1 rad。
  有效集法逐步求解，KKT 四项残差，与“把超限分量截断”的做法比较，并与 scipy（SLSQP）核对；
- 8.3.2 算例 8.2.3 加上关节限位：序列二次规划（每步一个 QP，用有效集法解），限位处的乘子 μ 是限位挡块的力矩；
  与 scipy 的 trust-constr 核对；
- 8.3.3 单关节最小能量轨迹：min ∫a² dt，速度不超过 v_max；离散成 QP，用有效集法解，与连续问题的解析解和 scipy 比较，
  并验证乘子之和等于放宽限速时代价的下降率。
"""
import math
import warnings

import numpy as np
from scipy.optimize import Bounds, NonlinearConstraint, linprog, minimize

from _opt import L2R, L3R, d, jac, kkt_residuals, qp_active_set, tip, tip_hessians
from bookout import out, tex, vec

warnings.simplefilter("ignore")      # scipy 的 trust-constr 对拟牛顿更新给出的无害提醒

# ---------------------------------------------------------------- 算例 8.3.1：一个控制周期的关节增量
th = np.array([0.0, d(90)])                  # 与算例 8.1.1 相同的形态
pd = np.array([0.5, 0.4])
J = jac(th, L2R)
e = pd - tip(th, L2R)
dmax = 0.1                                   # 每周期关节增量上限，rad
Q = J.T @ J
c = -J.T @ e
A = np.vstack([np.eye(2), -np.eye(2)])       # Δ ≤ dmax，−Δ ≤ dmax
b = dmax * np.ones(4)
d_free = np.linalg.solve(J, e)               # 不加限制的解：末端一步到位
assert np.abs(d_free).max() > dmax
r1 = qp_active_set(Q, c, A, b, x0=np.zeros(2))
d_qp = r1["x"]
res1 = kkt_residuals(Q, c, A, b, None, None, d_qp, np.zeros(0), r1["mu"])
assert max(res1) < 1e-12
d_clip = np.clip(d_free, -dmax, dmax)        # 只把超限的分量截断
err_qp = float(np.linalg.norm(J @ d_qp - e))
err_clip = float(np.linalg.norm(J @ d_clip - e))
assert err_qp < err_clip
d_scale = d_free * dmax / np.abs(d_free).max()   # 整体按比例缩小
err_scale = float(np.linalg.norm(J @ d_scale - e))
sp = minimize(lambda x: 0.5 * x @ Q @ x + c @ x, np.zeros(2), jac=lambda x: Q @ x + c, method="SLSQP",
              constraints=[dict(type="ineq", fun=lambda x: b - A @ x, jac=lambda x: -A)], options={"ftol": 1e-15})
assert np.linalg.norm(sp.x - d_qp) < 1e-8
hist1 = [h[0] for h in r1["history"]]
act_names = ["Δ₁ ≤ 0.1", "Δ₂ ≤ 0.1", "−Δ₁ ≤ 0.1", "−Δ₂ ≤ 0.1"]
assert r1["active"] == [3] and r1["mu"][3] > 0
grad_qp = Q @ d_qp + c

# ---------------------------------------------------------------- 算例 8.3.2：加关节限位的扭簧手臂（序列二次规划）
L = L3R
thc = np.array([d(30), d(60), d(-60)])
Kw = np.diag([20.0, 10.0, 5.0])
pd3 = np.array([0.55, 0.45])
lo = np.array([d(-90), d(0), d(-80)])
hi = np.array([d(90), d(150), d(80)])
A3 = np.vstack([np.eye(3), -np.eye(3)])


def f3(x):
    return 0.5 * float((x - thc) @ Kw @ (x - thc))


x, lam, mu = thc.copy(), np.zeros(2), np.zeros(6)
sqp_steps = []
for k in range(30):
    Jx, H2 = jac(x, L), tip_hessians(x, L)
    HL = Kw + lam[0] * H2[0] + lam[1] * H2[1]
    Nx = np.linalg.svd(Jx)[2][2:].T
    assert (Nx.T @ HL @ Nx)[0, 0] > 0                     # QP 在线性化约束的切空间上严格凸
    b3 = np.r_[hi - x, x - lo]
    beq = tip(x, L) - pd3
    # 第一阶段：用线性规划找一个严格可行的起点（不等式右端收紧 5%）
    lp = linprog(np.zeros(3), A_ub=A3, b_ub=0.95 * b3, A_eq=Jx, b_eq=-beq, bounds=[(None, None)] * 3)
    assert lp.status == 0
    r = qp_active_set(HL, Kw @ (x - thc), A3, b3, Jx, -beq, x0=lp.x)
    x, lam, mu = x + r["x"], r["lam"], r["mu"]
    sqp_steps.append(float(np.linalg.norm(r["x"])))
    if sqp_steps[-1] < 1e-13:
        break
Js = jac(x, L)
stat = Kw @ (x - thc) + Js.T @ lam + A3.T @ mu
assert np.linalg.norm(stat) < 1e-12 and np.linalg.norm(tip(x, L) - pd3) < 1e-14
assert abs(x[2] - lo[2]) < 1e-14 and mu[5] > 0 and np.all(np.delete(mu, 5) < 1e-14)
F3 = -lam
tau_spring = -Kw @ (x - thc)                               # 扭簧对关节的力矩
assert np.allclose(tau_spring + Js.T @ F3 + np.r_[0, 0, mu[5]], 0, atol=1e-12)   # 力矩平衡：扭簧 + 手 + 挡块 = 0
rs = minimize(f3, thc, method="trust-constr", jac=lambda t: Kw @ (t - thc), bounds=Bounds(lo, hi),
              constraints=[NonlinearConstraint(lambda t: tip(t, L) - pd3, 0, 0, jac=lambda t: jac(t, L))],
              options={"gtol": 1e-12, "xtol": 1e-14, "maxiter": 5000})
assert np.linalg.norm(rs.x - x) < 1e-5 and abs(rs.fun - f3(x)) < 1e-6
# 无限位时的最优值（与程序 8.2.1 相同），这里重算一遍
x0, l0 = thc.copy(), np.zeros(2)
for _ in range(20):
    Jx, H2 = jac(x0, L), tip_hessians(x0, L)
    HL = Kw + l0[0] * H2[0] + l0[1] * H2[1]
    st = np.linalg.solve(np.block([[HL, Jx.T], [Jx, np.zeros((2, 2))]]), -np.r_[Kw @ (x0 - thc) + Jx.T @ l0, tip(x0, L) - pd3])
    x0, l0 = x0 + st[:3], l0 + st[3:]
f_nolim = f3(x0)
assert f3(x) > f_nolim

# ---------------------------------------------------------------- 算例 8.3.3：单关节最小能量轨迹
Tt, thf, vmax, N = 2.0, 2.0, 1.2, 100        # 时间 s、转角 rad、限速 rad/s、分段数
hh = Tt / N
Om = np.vstack([np.tril(np.ones((N, N)), -1) * hh, hh * np.ones(N)])   # 第 k 行：ω_k = h Σ_{j<k} a_j
thN = np.array([hh * hh * (N - j - 1) + hh * hh / 2 for j in range(N)])   # θ_N = Σ_j a_j h²(N − j − ½)
E = np.vstack([thN, hh * np.ones(N)])
ee = np.array([thf, 0.0])
Qt = hh * np.eye(N)                           # ½ Σ a_k² h = ½ aᵀ(hI)a
ct = np.zeros(N)
At = Om[1:N]
bt = vmax * np.ones(N - 1)
lp = linprog(np.zeros(N), A_ub=At, b_ub=0.9 * bt, A_eq=E, b_eq=ee, bounds=[(None, None)] * N)
rt = qp_active_set(Qt, ct, At, bt, E, ee, x0=lp.x)
a = rt["x"]
J_con = float(a @ Qt @ a)                     # ∫ a² dt
r0 = qp_active_set(Qt, ct, None, None, E, ee, x0=lp.x)
a0 = r0["x"]
J_free = float(a0 @ Qt @ a0)
v_free = float((Om @ a0).max())
assert abs(J_free - 12 * thf ** 2 / Tt ** 3) < 1e-3 and abs(v_free - 1.5 * thf / Tt) < 1e-3   # 三次多项式
t1 = 3 * (vmax * Tt - thf) / (2 * vmax)       # 解析解：加速段时长
J_an = 8 * vmax ** 2 / (3 * t1)
assert abs(J_con - J_an) / J_an < 1e-3
resk = kkt_residuals(Qt, ct, At, bt, E, ee, a, rt["lam"], rt["mu"])
assert max(resk) < 1e-10
n_act = len(rt["active"])
mu_sum = float(rt["mu"].sum())
dJ_an = 16 / 9 * vmax ** 2 * (2 * vmax * Tt - 3 * thf) / (vmax * Tt - thf) ** 2       # dJ*/dv_max（解析）
assert abs(mu_sum - (-dJ_an / 2)) / abs(dJ_an / 2) < 5e-3                             # Σμ = −d(½J*)/dv_max
st = minimize(lambda z: 0.5 * z @ Qt @ z, lp.x, jac=lambda z: Qt @ z, method="SLSQP",
              constraints=[dict(type="eq", fun=lambda z: E @ z - ee, jac=lambda z: E),
                           dict(type="ineq", fun=lambda z: bt - At @ z, jac=lambda z: -At)],
              options={"ftol": 1e-15, "maxiter": 1000})
assert np.abs(st.x - a).max() < 1e-8
act_t = [k * hh for k in np.array(rt["active"]) + 1]

out(
    J=tex(J, 3), e=vec(e, 3), d_free=vec(d_free, 4), d_qp=vec(d_qp, 4), d_clip=vec(d_clip, 4), d_scale=vec(d_scale, 4),
    mu4=float(r1["mu"][3]), grad_qp=vec(grad_qp, 4), err_free=0.0, err_qp=err_qp, err_clip=err_clip, err_scale=err_scale,
    n_it1=len(hist1) - 1, kkt1=max(res1), sp_err1=float(np.linalg.norm(sp.x - d_qp)),
    th3_deg=vec(np.degrees(x), 2), t31=math.degrees(x[0]), t32=math.degrees(x[1]), lam3=vec(lam, 3), F3=vec(F3, 3),
    mu3=float(mu[5]), f3=f3(x), f_nolim=f_nolim, sqp_it=len(sqp_steps), s1=sqp_steps[0], s2=sqp_steps[1],
    s3=sqp_steps[2], s4=sqp_steps[3], stat3=float(np.linalg.norm(stat)), rs_err=float(np.linalg.norm(rs.x - x)),
    tau_s=vec(tau_spring, 3),
    J_free=J_free, v_free=v_free, J_con=J_con, J_an=J_an, t1=t1, n_act=n_act, mu_sum=mu_sum, half_dJ=-dJ_an / 2,
    act_from=act_t[0], act_to=act_t[-1], kkt3=max(resk), n_it3=len(rt["history"]) - 1,
    st_err=float(np.abs(st.x - a).max()), J_rise=(J_con / J_free - 1) * 100,
)
