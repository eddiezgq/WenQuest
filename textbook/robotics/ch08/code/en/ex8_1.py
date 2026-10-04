"""Examples 8.1.1–8.1.4: the inverse kinematics of the planar 2R arm as unconstrained optimization, f(θ) = ½‖p(θ) − p_d‖².

- 8.1.1 the gradient at the starting point (Eq. (8.1.5)) and the directional derivative, checked by difference quotients;
- 8.1.2 the Hessian matrix at the solution, its eigenvalues, the condition number and the stable step-size limit of
  gradient descent (Theorem 8.1.6);
- 8.1.3 iteration counts of gradient descent (several fixed steps, Armijo line search) and of Newton's method, compared
  with the analytic inverse solution and with SciPy's BFGS; and a check that the factor by which the error of gradient
  descent shrinks per step in the later stage equals max|1 − αλ_i| predicted from the eigenvalues of the Hessian matrix;
- 8.1.4 Newton's method from another starting point converges to a saddle point; safeguarded Newton's method converges
  to the minimizer.
"""
import math

import numpy as np
from scipy.optimize import minimize

from _opt import L2R, d, gradient_descent, ik_closed_2r, jac, newton, tip, tip_hessians
from bookout import out, tex, vec

L = L2R
pd = np.array([0.5, 0.4])                    # target point, m


def f(th):
    r = tip(th, L) - pd
    return 0.5 * float(r @ r)


def grad(th):
    return jac(th, L).T @ (tip(th, L) - pd)


def hess(th):
    J, r, H2 = jac(th, L), tip(th, L) - pd, tip_hessians(th, L)
    return J.T @ J + r[0] * H2[0] + r[1] * H2[1]


# ---------------------------------------------------------------- Example 8.1.1: the gradient at the starting point
th0 = np.array([0.0, d(90)])
p0 = tip(th0, L)
r0 = p0 - pd
J0 = jac(th0, L)
g0 = grad(th0)
h = 1e-6
g_fd = np.array([(f(th0 + h * e) - f(th0 - h * e)) / (2 * h) for e in np.eye(2)])
assert np.allclose(g0, g_fd, atol=1e-9)                                  # the gradient formula agrees with the difference quotients
u = np.array([1.0, 1.0]) / math.sqrt(2)                                  # direction in which both joints turn by equal amounts
Du = float(g0 @ u)
Du_fd = (f(th0 + h * u) - f(th0 - h * u)) / (2 * h)
assert abs(Du - Du_fd) < 1e-9                                            # directional derivative = ∇f · u (Theorem 8.1.1)
ud = -g0 / np.linalg.norm(g0)
assert abs(float(g0 @ ud) + np.linalg.norm(g0)) < 1e-15                  # rate of change along the steepest-descent direction = −‖∇f‖

# ---------------------------------------------------------------- Example 8.1.2: the Hessian matrix at the solution
ts = ik_closed_2r(pd, L, +1)                                             # analytic inverse solution (the elbow-down branch)
assert np.linalg.norm(tip(ts, L) - pd) < 1e-14
Hs = hess(ts)
Js = jac(ts, L)
assert np.allclose(Hs, Js.T @ Js, atol=1e-14)                            # where the residual is zero, Hessian matrix = JᵀJ
H_fd = np.array([(grad(ts + h * e) - grad(ts - h * e)) / (2 * h) for e in np.eye(2)])
assert np.allclose(Hs, H_fd, atol=1e-8)
lam = np.linalg.eigvalsh(Hs)
kappa = lam[1] / lam[0]
alpha_max = 2 / lam[1]
alpha_best = 2 / (lam[0] + lam[1])
rate_best = (kappa - 1) / (kappa + 1)
assert lam[0] > 0                                                        # second-order sufficient condition: positive definite, strict local minimizer

# ---------------------------------------------------------------- Example 8.1.3: iteration counts of the methods
tol = 1e-8                                                               # stopping criterion: ‖∇f‖ < 10⁻⁸
runs = {}
for a in (1.0, 3.0):
    x, path, _ = gradient_descent(f, grad, th0, alpha=a, tol=tol)
    runs[a] = (x, path)
    assert np.linalg.norm(x - ts) < 1e-6
x4, path4, _ = gradient_descent(f, grad, th0, alpha=4.0, tol=tol, kmax=2000)
assert np.linalg.norm(grad(x4)) > 1e-3                                   # α = 4 exceeds the limit 2/λ_max: no convergence
xa, patha, nfa = gradient_descent(f, grad, th0, tol=tol, alpha0=8.0)     # Armijo backtracking, trial step starting at 8
assert np.linalg.norm(xa - ts) < 1e-6
xn, pathn = newton(grad, hess, th0, tol=1e-12)
assert np.linalg.norm(xn - ts) < 1e-13
errn = [float(np.linalg.norm(q - ts)) for q in pathn]
# quadratic convergence: e_{k+1} / e_k² tends to a constant
ratios = [errn[k + 1] / errn[k] ** 2 for k in range(len(errn) - 2)]
assert errn[3] < 1e-5 and errn[-1] < 1e-12

# factor by which the gradient-descent error shrinks per step in the later stage, compared with max|1 − αλ_i| (Theorem 8.1.6)
x3, path3 = runs[3.0]
e3 = np.linalg.norm(path3 - ts, axis=1)
obs_rate = float(np.exp(np.mean(np.log(e3[41:61] / e3[40:60]))))
pred_rate = float(max(abs(1 - 3.0 * lam[0]), abs(1 - 3.0 * lam[1])))
assert abs(obs_rate - pred_rate) < 5e-3

# SciPy's BFGS (a quasi-Newton method) as an independent check
res = minimize(f, th0, jac=grad, method="BFGS", options={"gtol": tol})
assert res.success and np.linalg.norm(res.x - ts) < 1e-6

# ---------------------------------------------------------------- Example 8.1.4: Newton's method converges to a saddle point
th_b = np.array([0.0, 0.3])
Hb = hess(th_b)
lam_b = np.linalg.eigvalsh(Hb)
assert lam_b[0] < 0                                                      # the Hessian matrix is indefinite at the starting point
xs, paths = newton(grad, hess, th_b, tol=1e-12)
assert abs(xs[1]) < 1e-9                                                 # θ2 = 0: the arm is straight and points at the target
assert np.linalg.norm(grad(xs)) < 1e-12
lam_s = np.linalg.eigvalsh(hess(xs))
assert lam_s[0] < 0 < lam_s[1]                                           # saddle point
Hsad = hess(xs)
assert Hsad[0, 0] > 0 and Hsad[1, 1] > 0                                 # both diagonal entries positive: turning one joint alone cannot descend
v_neg = np.linalg.eigh(Hsad)[1][:, 0]
assert v_neg[0] * v_neg[1] < 0                                           # descent direction: bend joint 2 while turning joint 1 the opposite way
dist_s = float(np.linalg.norm(tip(xs, L) - pd))
assert abs(dist_s - (sum(L) - np.linalg.norm(pd))) < 1e-12               # distance from the straight arm to the target = L1 + L2 − |p_d|
xg, pathg = newton(grad, hess, th_b, tol=1e-12, f=f, safeguard=True)
assert np.linalg.norm(xg - ts) < 1e-10                                   # with the safeguards it converges to the minimizer

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
