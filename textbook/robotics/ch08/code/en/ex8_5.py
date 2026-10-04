"""Examples 8.5.1–8.5.3: nonlinear least squares.

- 8.5.1 Position inverse kinematics for the flange centre of the UR5e (joints 1 to 3 unknown, wrist joints fixed):
  gradient descent, Newton's method, the Gauss-Newton method and the LM method solve the same problem and are compared
  with SciPy's least_squares (MINPACK's LM); then, starting from the singular fully extended configuration, Gauss-Newton
  and LM are compared;
- 8.5.2 Kinematic calibration of a planar 3R arm: 6 parameters (3 link lengths, 3 zero-position offsets), laser-tracker
  measurements at 12 configurations; solved by Gauss-Newton and LM and checked against SciPy; the end-effector errors
  before and after calibration are compared at 50 test configurations;
- 8.5.3 Indoor positioning (UWB): the position of a phone from its distances to 4 anchors;
- data for Figure 8.5.2: for the planar 2R arm at theta = (30 deg, 30 deg), the Gauss-Newton step increases F (negative
  gain ratio), while the LM step (damping parameter mu = 0.02) is accepted; ||Delta(mu)|| decreases monotonically with
  mu, and as mu -> infinity the direction of Delta tends to the negative gradient (Theorem 8.5.2).
"""
import math

import numpy as np
from scipy.optimize import least_squares

from _opt import (L2R, L3R, arm_points, d, gauss_newton, gradient_descent, jac, levenberg_marquardt, newton, tip,
                  ur5e_flange, ur5e_flange_jac)
from bookout import out, tex, vec

# ---------------------------------------------------------------- Example 8.5.1: position inverse kinematics of the UR5e
wrist = np.array([d(-90), d(-90), 0.0])        # joints 4 to 6 fixed
th_true = np.array([d(40), d(-70), d(100)])
pd = ur5e_flange(np.r_[th_true, wrist])        # target: computed from known joint angles, so it can be checked


def res(x):
    return ur5e_flange(np.r_[x, wrist]) - pd


def jr(x):
    return ur5e_flange_jac(np.r_[x, wrist])[:, :3]


h = 1e-6
Jn = np.array([(res(th_true + h * e) - res(th_true - h * e)) / (2 * h) for e in np.eye(3)]).T
assert np.abs(Jn - jr(th_true)).max() < 1e-9                       # analytic Jacobian agrees with difference quotients


def F(x):
    r = res(x)
    return 0.5 * float(r @ r)


def gF(x):
    return jr(x).T @ res(x)


def hF(x):                                                          # full Hessian JᵀJ + Σ r_i ∇²r_i (∇²r_i from difference quotients of J)
    J, r = jr(x), res(x)
    S = np.zeros((3, 3))
    for j in range(3):
        e = np.zeros(3)
        e[j] = 1e-6
        dJ = (jr(x + e) - jr(x - e)) / 2e-6                          # ∂J/∂x_j
        S[:, j] = dJ.T @ r
    return J.T @ J + (S + S.T) / 2


x0 = np.array([0.0, d(-90), d(90)])
xg, pg, Fg = gauss_newton(res, jr, x0)
xl, pl, Fl, ll = levenberg_marquardt(res, jr, x0)
xd, pdd, nfd = gradient_descent(F, gF, x0, tol=1e-10, alpha0=8.0)
xn, pn = newton(gF, hF, x0, tol=1e-12, f=F, safeguard=True)
sp = least_squares(res, x0, jac=jr, method="lm", xtol=1e-15, ftol=1e-15, gtol=1e-15)
for xx in (xg, xl, xd, xn, sp.x):
    assert np.linalg.norm(xx - th_true) < 1e-5
err_g = [math.sqrt(2 * v) for v in Fg]                               # ‖r‖, m
assert err_g[5] < 1e-8 and err_g[5] / err_g[4] ** 2 < 10 and err_g[4] / err_g[3] ** 2 < 10   # zero-residual problem: quadratic convergence at the end
k_gd, k_n, k_gn, k_lm = len(pdd) - 1, len(pn) - 1, len(pg) - 1, len(pl) - 1
assert k_gd > 5 * k_gn
cond_sol = float(np.linalg.cond(jr(th_true)))

# starting from the singular fully extended configuration
xs0 = np.zeros(3)
sv0 = np.linalg.svd(jr(xs0), compute_uv=False)
xgs, pgs, Fgs = gauss_newton(res, jr, xs0)
xls, pls, Fls, lls = levenberg_marquardt(res, jr, xs0)
step_gn1 = float(np.degrees(np.abs(pgs[1] - pgs[0]).max()))         # largest joint rotation in the first Gauss-Newton step, deg
step_lm1 = float(np.degrees(np.abs(pls[1] - pls[0]).max()))
wrap = lambda a: (np.degrees(a) + 180) % 360 - 180
assert np.allclose(wrap(xgs), np.degrees(th_true), atol=1e-6)      # equal to the true solution once wrapped to (-180, 180] deg
assert np.linalg.norm(xls - th_true) < 1e-6                         # LM converges directly to the true solution, without winding round
assert step_gn1 > 3 * step_lm1 and step_gn1 > 360       # the first Gauss-Newton step already turns a joint more than a full turn

# ---------------------------------------------------------------- data for Figure 8.5.2: Gauss-Newton and LM steps of the planar 2R arm at θ = (30°, 30°)
pd2 = np.array([0.5, 0.4])
th2 = np.array([d(30), d(30)])
r2 = tip(th2, L2R) - pd2
J2 = jac(th2, L2R)
F2 = lambda dx: 0.5 * float((tip(th2 + dx, L2R) - pd2) @ (tip(th2 + dx, L2R) - pd2))
Lm2 = lambda dx: 0.5 * float((r2 + J2 @ dx) @ (r2 + J2 @ dx))
d_gn2 = -np.linalg.solve(J2.T @ J2, J2.T @ r2)
F0_2, Fgn_2 = F2(np.zeros(2)), F2(d_gn2)
rho_gn2 = (F0_2 - Fgn_2) / (Lm2(np.zeros(2)) - Lm2(d_gn2))
assert Fgn_2 > F0_2 and rho_gn2 < 0                                  # the Gauss-Newton step actually increases F
lam_k = 0.02                                                       # damping parameter μ, m²
d_lm2 = -np.linalg.solve(J2.T @ J2 + lam_k * np.eye(2), J2.T @ r2)
pred_lm2 = 0.5 * float(d_lm2 @ (lam_k * d_lm2 - J2.T @ r2))            # Eq. (8.5.8)
assert abs(pred_lm2 - (Lm2(np.zeros(2)) - Lm2(d_lm2))) < 1e-15
rho_lm2 = (F0_2 - F2(d_lm2)) / pred_lm2
assert 0 < rho_lm2 and F2(d_lm2) < F0_2
# properties: ‖Δ(μ)‖ decreases monotonically with μ; as μ → ∞ the direction tends to the negative gradient
lams = np.geomspace(1e-6, 1e4, 200)
norms = [np.linalg.norm(np.linalg.solve(J2.T @ J2 + l * np.eye(2), -J2.T @ r2)) for l in lams]
assert all(a > b for a, b in zip(norms, norms[1:]))
d_big = np.linalg.solve(J2.T @ J2 + 1e6 * np.eye(2), -J2.T @ r2)
g2 = J2.T @ r2
assert float(-g2 @ d_big) / (np.linalg.norm(g2) * np.linalg.norm(d_big)) > 1 - 1e-9
ang_gn2 = math.degrees(math.acos(float(-g2 @ d_gn2) / (np.linalg.norm(g2) * np.linalg.norm(d_gn2))))

# ---------------------------------------------------------------- Example 8.5.2: kinematic calibration of a planar 3R arm
rng = np.random.default_rng(8)
Nm = 12
TH = np.radians(rng.uniform([-90, -150, -150], [90, 150, 150], size=(Nm, 3)))
phi_true = np.r_[0.4262, 0.3911, 0.1013, np.radians([0.3, -0.5, 0.8])]
phi_nom = np.r_[L3R, 0.0, 0.0, 0.0]
sig = 5e-5                                                          # measurement noise 0.05 mm


def model(phi, th):
    return tip(th + phi[3:], phi[:3])


meas = np.array([model(phi_true, t) for t in TH]) + sig * rng.standard_normal((Nm, 2))


def rc(phi):
    return np.concatenate([model(phi, t) - m for t, m in zip(TH, meas)])


def jc(phi):
    rows = []
    for t in TH:
        th = t + phi[3:]
        a = np.cumsum(th)
        dL = np.array([[math.cos(a[i]), math.sin(a[i])] for i in range(3)]).T     # ∂p/∂L_i
        rows.append(np.hstack([dL, jac(th, phi[:3])]))                              # ∂p/∂β_i = ∂p/∂θ_i
    return np.vstack(rows)


Jcn = np.array([(rc(phi_nom + 1e-7 * e) - rc(phi_nom - 1e-7 * e)) / 2e-7 for e in np.eye(6)]).T
assert np.abs(Jcn - jc(phi_nom)).max() < 1e-8
pg_c, path_gc, F_gc = gauss_newton(rc, jc, phi_nom)
pl_c, path_lc, F_lc, _ = levenberg_marquardt(rc, jc, phi_nom)
sp_c = least_squares(rc, phi_nom, jac=jc, method="lm", xtol=1e-15, ftol=1e-15, gtol=1e-15)
assert np.linalg.norm(pg_c - pl_c) < 1e-10 and np.linalg.norm(pg_c - sp_c.x) < 1e-10
rms_before = math.sqrt(2 * F_gc[0] / (2 * Nm))
rms_after = math.sqrt(2 * F_gc[-1] / (2 * Nm))
assert rms_after < 2 * sig
dL_mm = (pg_c[:3] - phi_true[:3]) * 1000
dB_deg = np.degrees(pg_c[3:] - phi_true[3:])
assert np.abs(dL_mm).max() < 0.2 and np.abs(dB_deg).max() < 0.05
THv = np.radians(rng.uniform([-90, -150, -150], [90, 150, 150], size=(50, 3)))   # test configurations (not used in the calibration)
ev_nom = np.array([np.linalg.norm(model(phi_nom, t) - model(phi_true, t)) for t in THv]) * 1000
ev_cal = np.array([np.linalg.norm(model(pg_c, t) - model(phi_true, t)) for t in THv]) * 1000
assert ev_cal.max() < 0.2
cond_c = float(np.linalg.cond(jc(pg_c)))

# ---------------------------------------------------------------- Example 8.5.3: indoor positioning
anchors = np.array([[0.0, 0.0, 2.5], [6.0, 0.0, 2.5], [6.0, 4.0, 2.5], [0.0, 4.0, 0.3]])   # anchors, m
phone = np.array([3.6, 1.2, 1.0])
rng2 = np.random.default_rng(3)
rho = np.linalg.norm(anchors - phone, axis=1) + 0.05 * rng2.standard_normal(4)              # ranges, error about 5 cm


def ru(x):
    return np.linalg.norm(anchors - x, axis=1) - rho


def ju(x):
    return (x - anchors) / np.linalg.norm(anchors - x, axis=1)[:, None]   # row i: unit vector from anchor i to x


xu0 = np.array([3.0, 2.0, 1.2])                                  # start at the centre of the room
xu, pu, Fu = gauss_newton(ru, ju, xu0)
spu = least_squares(ru, xu0, jac=ju, method="lm", xtol=1e-15, ftol=1e-15, gtol=1e-15)
assert np.linalg.norm(xu - spu.x) < 1e-9
pos_err_cm = float(np.linalg.norm(xu - phone) * 100)
assert pos_err_cm < 15

out(
    F0_2=F0_2, Fgn_2=Fgn_2, rho_gn2=rho_gn2, d_gn2=vec(d_gn2, 3), d_lm2=vec(d_lm2, 3), rho_lm2=rho_lm2, F_lm2=F2(d_lm2),
    nd_lm2=float(np.linalg.norm(d_lm2)), ang_gn2=ang_gn2,
    wrist=vec(np.degrees(wrist), 0), th_true=vec(np.degrees(th_true), 0), pd=vec(pd, 4), x0=vec(np.degrees(x0), 0),
    k_gd=k_gd, nf_gd=nfd, k_n=k_n, k_gn=k_gn, k_lm=k_lm, sp_nfev=int(sp.nfev),
    eg0=err_g[0], eg1=err_g[1], eg2=err_g[2], eg3=err_g[3], eg4=err_g[4], cond_sol=cond_sol,
    sv0=vec(sv0, 4), sv0min=float(sv0[-1]), xgs=vec(np.degrees(xgs), 1), xls=vec(np.degrees(xls), 2),
    step_gn1=step_gn1, step_lm1=step_lm1, k_gns=len(pgs) - 1, k_lms=len(pls) - 1,
    TH_rows=Nm, phi_true_L=vec(phi_true[:3] * 1000, 1), phi_true_b=vec(np.degrees(phi_true[3:]), 1),
    L_hat=vec(pg_c[:3] * 1000, 2), b_hat=vec(np.degrees(pg_c[3:]), 3), dL_mm=vec(dL_mm, 3), dB_deg=vec(dB_deg, 4),
    k_gc=len(path_gc) - 1, k_lc=len(path_lc) - 1, sp_c_nfev=int(sp_c.nfev),
    rms_before=rms_before * 1000, rms_after=rms_after * 1000, ev_nom_max=float(ev_nom.max()), ev_nom_mean=float(ev_nom.mean()),
    ev_cal_max=float(ev_cal.max()), ev_cal_mean=float(ev_cal.mean()), cond_c=cond_c,
    phone=vec(phone, 2), rho=vec(rho, 3), xu=vec(xu, 3), k_u=len(pu) - 1, pos_err_cm=pos_err_cm,
)
