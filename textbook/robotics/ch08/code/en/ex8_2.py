"""Section 8.2: equality-constrained optimization and Lagrange multipliers.

- The garden (Sections 8.2.2–8.2.4): the largest rectangle fenced against a wall with 20 m of fence; multiplier = the
  extra area given by 1 m more fence (Eq. (8.2.7));
- Example 8.2.1: weighted minimum-norm joint velocities of the redundant 3R arm (Eq. (8.2.9)); for W = I the same as
  Example 2.5.2; the KKT system (8.2.8) checked against the closed-form formula;
- Example 8.2.2: a 3R arm with torsion springs in its joints, its end-effector pulled to p_d by a hand:
  min ½(θ − θ_c)ᵀK(θ − θ_c) s.t. p(θ) = p_d. Solved by the Lagrange–Newton method (8.2.10) and compared with SciPy's
  trust-constr; checks that −λ is the force applied by the hand:
  (a) static equilibrium τ + JᵀF = 0 (Eq. (8.2.13)); (b) the derivative of the optimal value with respect to p_d
  (difference quotients) equals F; (c) the reduced Hessian matrix is positive (Theorem 8.2.4);
- Example 8.2.3: a hanger on a clothes line: the multiplier is the tension of the line.
"""
import math
import warnings

import numpy as np
from scipy.optimize import NonlinearConstraint, minimize

from _opt import L3R, d, jac, tip, tip_hessians
from bookout import out, tex, vec

# ---------------------------------------------------------------- the garden
Lf = 20.0                                   # total length of fence, m
# x is the length of the two sides perpendicular to the wall, y that of the side parallel to it; constraint 2x + y = 20.
# The Lagrange conditions −y + 2λ = 0, −x + λ = 0 give λ = x, y = 2x; the constraint then gives x = 5 m, y = 10 m.
x_g = Lf / 4
y_g = Lf / 2
lam_g = x_g
S_g = x_g * y_g
S_more = (Lf + 0.01) / 4 * (Lf + 0.01) / 2   # 1 cm more fence
dS_dL = (S_more - S_g) / 0.01
assert abs(dS_dL - lam_g) < 0.01                                    # multiplier = rate of change of the optimal value with the length of fence
xs = np.linspace(0.1, 9.9, 9801)
assert abs(max(xs * (Lf - 2 * xs)) - S_g) < 1e-6                   # check by exhaustive search

# ---------------------------------------------------------------- Example 8.2.1: weighted minimum-norm joint velocities
L = L3R
thc = np.array([d(30), d(60), d(-60)])      # the same configuration as in Example 2.5.2
J = jac(thc, L)
v = np.array([0.1, 0.0])                     # end-effector velocity, m/s
Kw = np.diag([20.0, 10.0, 5.0])             # weights (the spring stiffnesses in Example 8.2.2, N·m/rad)


def weighted_min_norm(W):
    Wi = np.linalg.inv(W)
    return Wi @ J.T @ np.linalg.solve(J @ Wi @ J.T, v)


def kkt_solve(W):
    K = np.block([[W, J.T], [J, np.zeros((2, 2))]])
    sol = np.linalg.solve(K, np.r_[np.zeros(3), v])
    return sol[:3], sol[3:]


thd_I = weighted_min_norm(np.eye(3))
assert np.allclose(thd_I, np.linalg.pinv(J) @ v, atol=1e-14)                  # W = I: the pseudoinverse solution (Example 2.5.2)
thd_W = weighted_min_norm(Kw)
thd_kkt, lam_kkt = kkt_solve(Kw)
assert np.allclose(thd_W, thd_kkt, atol=1e-14)                                # the closed-form formula agrees with the KKT system
assert np.allclose(J @ thd_W, v, atol=1e-14)
assert np.allclose(Kw @ thd_W + J.T @ lam_kkt, 0, atol=1e-14)                 # stationarity condition
lam_formula = -np.linalg.solve(J @ np.linalg.inv(Kw) @ J.T, v)
assert np.allclose(lam_kkt, lam_formula, atol=1e-13)
cost_I = 0.5 * thd_I @ Kw @ thd_I
cost_W = 0.5 * thd_W @ Kw @ thd_W
assert cost_W < cost_I                                                        # the weighted solution has the smaller weighted cost

# ---------------------------------------------------------------- Example 8.2.2: the arm with springs pulled to p_d
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
F = -lam                                                                      # force applied by the hand to the end-effector, N
assert np.allclose(Kw @ (x - thc), Js.T @ F, atol=1e-12)                      # (a) spring torques = Jᵀ F
# (b) derivative of the optimal value with respect to p_d: move p_d by 1 μm along x and along y and solve again
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
# (c) second-order condition: the Hessian matrix of the Lagrangian is positive on the tangent space (the null space of J)
H2 = tip_hessians(x, L)
HL = Kw + lam[0] * H2[0] + lam[1] * H2[1]
N = np.linalg.svd(Js)[2][2:].T                                                # null space of J (one-dimensional)
red = float((N.T @ HL @ N)[0, 0])
assert red > 0
lam_HL = np.linalg.eigvalsh(HL)
# independent check with SciPy (trust-constr gives a harmless warning about quasi-Newton updates for linear constraints; not shown here)
warnings.simplefilter("ignore")
res = minimize(f, thc, method="trust-constr", jac=lambda t: Kw @ (t - thc),
               constraints=[NonlinearConstraint(h, 0, 0, jac=lambda t: jac(t, L))],
               options={"gtol": 1e-12, "xtol": 1e-14})
assert np.linalg.norm(res.x - x) < 1e-6 and np.allclose(res.v[0], lam, rtol=1e-6)
tau = -Kw @ (x - thc)                                                         # torques exerted by the springs on the joints, N·m (cancelling Jᵀ F)
assert np.allclose(tau + Js.T @ F, 0, atol=1e-12)
# anisotropic compliance of the end-effector: in the natural configuration θ_c, for small displacements K δθ = Jᵀ F (from Eq. (8.2.13)), δp ≈ J K⁻¹ Jᵀ F
Cc = J @ np.linalg.inv(Kw) @ J.T                                              # compliance matrix, m/N
comp_down = Cc @ np.array([0.0, -1.0])                                        # end-effector displacement caused by a force of 1 N vertically downwards
assert comp_down[0] > 0 and comp_down[1] < 0                                  # it moves to the right while going down
eps = 1e-3                                                                    # check by a full nonlinear solution with a small force of 1 mN
_, l_small = solve_for(p_c + eps * comp_down, thc, np.zeros(2))
assert np.allclose(-l_small, [0.0, -eps], atol=1e-2 * eps)                    # the force needed to pull the end-effector through this displacement is 1 mN downwards

# ---------------------------------------------------------------- Example 8.2.3: a hanger on a clothes line
A_h, B_h = np.array([0.0, 2.0]), np.array([2.0, 2.4])     # the two hooks, m
ell, G = 2.6, 20.0                                         # length of the line in m, weight of the clothes in N


def hh(P):
    return np.linalg.norm(P - A_h) + np.linalg.norm(P - B_h) - ell


Pz, lz = np.array([1.0, 1.2]), G / 2                         # initial value: tension equal to half the weight (its value when the line is vertical)
for _ in range(50):
    ua, ub = (Pz - A_h) / np.linalg.norm(Pz - A_h), (Pz - B_h) / np.linalg.norm(Pz - B_h)
    gh = ua + ub
    Hh = (np.eye(2) - np.outer(ua, ua)) / np.linalg.norm(Pz - A_h) + (np.eye(2) - np.outer(ub, ub)) / np.linalg.norm(Pz - B_h)
    K2 = np.block([[lz * Hh, gh[:, None]], [gh[None, :], np.zeros((1, 1))]])
    st2 = np.linalg.solve(K2, -np.r_[np.array([0.0, G]) + lz * gh, hh(Pz)])
    Pz, lz = Pz + st2[:2], lz + st2[2]
    if np.linalg.norm(st2) < 1e-14:
        break
sin_a = (B_h[0] - A_h[0]) / ell                             # the two parts of the line make equal angles with the vertical: sin α = span / length of line
T_rope = G / (2 * math.sqrt(1 - sin_a ** 2))
assert abs(lz - T_rope) < 1e-9                              # the multiplier is the tension of the line
ua, ub = (Pz - A_h) / np.linalg.norm(Pz - A_h), (Pz - B_h) / np.linalg.norm(Pz - B_h)
assert abs(abs(ua[0]) - sin_a) < 1e-12 and abs(abs(ub[0]) - sin_a) < 1e-12      # the two parts of the line make equal angles with the vertical
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
