"""Examples of Section 7.3 (numerical solution of nonlinear equations).

Examples 7.3.1, 7.3.2: equilibrium angle of a link held by a torsion spring: f(θ) = k(θ_s − θ) − m𝔤 l_c cos θ = 0. Bisection (Example 7.3.1)
            compared with Newton's method (Example 7.3.2): bisection halves the error at each step; the error of Newton's method is
            e_{k+1} ≈ C e_k², C = |f''/(2f')| (Theorem 7.3.1).
Example 7.3.3: √2 by Newton's method (Heron's method).
Section 7.3.3: arctan x = 0: start 1.3 converges, 1.5 diverges; find the critical starting value.
Example 7.3.4: inverse kinematics of the 2R arm, target p_d = (0.45, 0.35) m: Newton's method from two starting guesses converges to
            the two solutions, checked against the analytic solution (law of cosines); the successive residuals show quadratic convergence.
Section 7.3.5: a singular starting guess (θ₂ = 0) and an out-of-reach target; the result of damped least squares.
Also: from a grid of starting guesses on [−π, π]², the shares that converge to each solution and that fail (data of Figure 7.3.3).
"""
import math

import numpy as np
from scipy.optimize import brentq

from _ode import G, L1, L2, LINK, fk2, ik2_analytic, jac2, link_params, newton2_batch, newton2_batch_ls, wrap
from bookout import out, tex, vec


def deg_pair(v, d=2):
    """Text of the form (a°, b°), with − as the minus sign."""
    return "(" + ", ".join(f"{x:.{d}f}°".replace("-", "−") for x in np.degrees(v)) + ")"


# ---------------------------------------------------------------- Example 7.3.1
Jo, lc, wn2 = link_params()
m = LINK["mk"]
k_s = 10.0                                   # torsion-spring stiffness, N·m/rad
th_s = math.pi / 3                           # angle at which the spring exerts no torque (60°)
mgl = m * G * lc                             # largest gravity torque, N·m
f = lambda t: k_s * (th_s - t) - mgl * math.cos(t)
df = lambda t: -k_s + mgl * math.sin(t)
d2f = lambda t: mgl * math.cos(t)
root = brentq(f, 0, th_s, xtol=1e-15, rtol=1e-15)
C = abs(d2f(root) / (2 * df(root)))

# bisection
a, b = 0.0, th_s
bis = []
while b - a > 1e-10:
    c = (a + b) / 2
    if f(a) * f(c) <= 0:
        b = c
    else:
        a = c
    bis.append(abs((a + b) / 2 - root))
n_bis = len(bis)
assert abs((a + b) / 2 - root) < 1e-10
n_bis_pred = math.ceil(math.log2(th_s / 1e-10))
assert n_bis == n_bis_pred

# Newton's method (Example 7.3.2)
t = 0.0
newt = [t]
while abs(f(t)) > 1e-15 and len(newt) < 20:
    t = t - f(t) / df(t)
    newt.append(t)
errs = [abs(x - root) for x in newt]
n_newt = len(newt) - 1
assert abs(newt[-1] - root) < 1e-14 and n_newt <= 6
ratios = [errs[i + 1] / errs[i] ** 2 for i in range(1, 3)]
assert abs(ratios[-1] - C) < 0.05 * C                       # e_{k+1}/e_k² → C

# ---------------------------------------------------------------- Example 7.3.3 √2
x = 1.0
heron = [x]
for _ in range(4):
    x = (x + 2 / x) / 2
    heron.append(x)
assert abs(heron[-1] - math.sqrt(2)) < 1e-11
heron_err = [abs(v - math.sqrt(2)) for v in heron]
s10_1 = (3 + 10 / 3) / 2
s10_2 = (s10_1 + 10 / s10_1) / 2
assert abs(s10_2 - math.sqrt(10)) < 1e-4

# ---------------------------------------------------------------- Section 7.3.3 arctan
def newton_atan(x0, n=8):
    xs = [x0]
    for _ in range(n):
        xs.append(xs[-1] - math.atan(xs[-1]) * (1 + xs[-1] ** 2))
    return xs


at13, at15 = newton_atan(1.3), newton_atan(1.5, 4)
assert abs(at13[-1]) < 1e-12 and abs(at15[-1]) > 10
# critical start: after one step it becomes exactly −x0, then jumps between ±x0: 2x = (1 + x²) arctan x
x_crit = brentq(lambda x: 2 * x - (1 + x * x) * math.atan(x), 1.0, 2.0, xtol=1e-15)

# ---------------------------------------------------------------- Example 7.3.4 2R arm
p_d = np.array([0.45, 0.35])
sols = ik2_analytic(p_d)
for s in sols:
    assert np.allclose(fk2(s), p_d, atol=1e-12)


def newton_ik(th0, p, n=12):
    th = np.array(th0, float)
    hist = [(th.copy(), float(np.linalg.norm(fk2(th) - p)))]
    for _ in range(n):
        r = fk2(th) - p
        if np.linalg.norm(r) < 1e-14:
            break
        th = th - np.linalg.solve(jac2(th), r)
        hist.append((th.copy(), float(np.linalg.norm(fk2(th) - p))))
    return hist


hA = newton_ik([0.0, 1.0], p_d)
hB = newton_ik([1.0, -1.0], p_d)
hC = newton_ik([0.0, -1.0], p_d, n=12)                     # this start does not converge: it wanders between the two solutions
resC = [r for _, r in hC]
assert min(resC) > 1e-3
thA, thB = hA[-1][0], hB[-1][0]
assert np.allclose(wrap(thA), sols[1], atol=1e-12) or np.allclose(wrap(thA), sols[0], atol=1e-12)
upA = thA[1] > 0
solA = sols[0] if upA else sols[1]
solB = sols[1] if upA else sols[0]
assert np.allclose(wrap(thA), solA, atol=1e-12) and np.allclose(wrap(thB), solB, atol=1e-12)
resA = [r for _, r in hA]
nA = len(hA) - 1
# check the Jacobian matrix by numerical differentiation
e = 1e-6
th_t = np.array([0.4, 1.1])
Jn = np.column_stack([(fk2(th_t + e * v) - fk2(th_t - e * v)) / (2 * e) for v in np.eye(2)])
assert np.allclose(Jn, jac2(th_t), atol=1e-8)
detJ = float(np.linalg.det(jac2(th_t)))
assert abs(detJ - L1 * L2 * math.sin(th_t[1])) < 1e-12        # det J = l1 l2 sin θ2

# ---------------------------------------------------------------- Section 7.3.5 singular start, out of reach
J_sing = jac2(np.array([0.3, 0.0]))
assert abs(np.linalg.det(J_sing)) < 1e-15
p_far = np.array([0.9, 0.3])
reach = L1 + L2
dist_far = float(np.linalg.norm(p_far))
assert dist_far > reach
hF = newton_ik([0.2, 0.5], p_far, n=40)
resF = [r for _, r in hF]
assert min(resF) > dist_far - reach - 1e-9                    # the residual cannot be smaller than the distance gap
# damped least squares: Δθ = −Jᵀ(JJᵀ + λ²I)⁻¹ r (Eq. (7.3.12))
lam = 0.2                                     # damping factor, m
th = np.array([0.2, 0.5])
for _ in range(100):
    J = jac2(th)
    r = fk2(th) - p_far
    th = th - J.T @ np.linalg.solve(J @ J.T + lam ** 2 * np.eye(2), r)
th_dls = th
res_dls = float(np.linalg.norm(fk2(th_dls) - p_far))
assert abs(res_dls - (dist_far - reach)) < 1e-12
assert abs(wrap(th_dls[1])) < 1e-9 and abs(wrap(th_dls[0]) - math.atan2(0.3, 0.9)) < 1e-9

# ---------------------------------------------------------------- grid of starting guesses (Figure 7.3.3)
N = 241
g = np.linspace(-math.pi, math.pi, N)
T1, T2 = np.meshgrid(g, g)
th0 = np.column_stack([T1.ravel(), T2.ravel()])
thf, ok, used = newton2_batch(th0, p_d)
up = ok & (wrap(thf[:, 1]) > 0)
down = ok & (wrap(thf[:, 1]) < 0)
frac_up, frac_down, frac_fail = up.mean() * 100, down.mean() * 100, (~ok).mean() * 100
med_iter = float(np.median(used[ok]))
assert 15 < frac_fail < 35 and abs(frac_up + frac_down + frac_fail - 100) < 1e-9
# most starts that fail fall into a back-and-forth cycle: look at one
i_fail = int(np.where(~ok & (np.abs(np.sin(th0[:, 1])) > 0.5))[0][0])
cyc = [th0[i_fail].copy()]
for _ in range(30):
    cyc.append(cyc[-1] - np.linalg.solve(jac2(cyc[-1]), fk2(cyc[-1]) - p_d))
cyc_res = [float(np.linalg.norm(fk2(c) - p_d)) for c in cyc[-4:]]
assert min(cyc_res) > 0.1
# with backtracking line search only the singular starts with sin θ₂ = 0 fail (the three grid rows θ₂ = 0, ±π)
thl, okl, usedl = newton2_batch_ls(th0, p_d)
sing = np.isclose(np.abs(wrap(th0[:, 1])), 0, atol=1e-12) | np.isclose(np.abs(th0[:, 1]), math.pi, atol=1e-12)
assert np.array_equal(~okl, sing)
frac_fail_ls = (~okl).mean() * 100
med_iter_ls = float(np.median(usedl[okl]))

out(
    s10_1=s10_1, s10_2=s10_2, s10=math.sqrt(10), lam=lam, k_s=k_s, mgl=mgl, root=root, root_deg=math.degrees(root), C=C, n_bis=n_bis, bis1=bis[0],
    **{f"nt{i}": newt[i] for i in range(len(newt))}, **{f"ne{i}": errs[i] for i in range(len(errs))}, n_newt=n_newt,
    r1=ratios[0], r2=ratios[1], f0=f(0.0), df0=df(0.0),
    **{f"he{i}": heron[i] for i in range(5)}, **{f"hee{i}": heron_err[i] for i in range(5)},
    at13_1=at13[1], at13_2=at13[2], at15_1=at15[1], at15_2=at15[2], at15_3=at15[3], x_crit=x_crit,
    solA=vec(solA, 4), solB=vec(solB, 4), solA_deg=deg_pair(solA), solB_deg=deg_pair(solB),
    **{f"rA{i}": resA[i] for i in range(len(resA))}, nA=nA, nB=len(hB) - 1, resC_min=min(resC), resC_last=resC[-1],
    **{f"thA{i}": vec(hA[i][0], 4) for i in range(min(4, len(hA)))},
    detJ=detJ, J_t=tex(jac2(th_t), 4), reach=reach, dist_far=dist_far, resF_min=min(resF), resF_last=resF[-1],
    th_dls=vec(th_dls, 4), th_dls_deg=deg_pair(wrap(th_dls)), res_dls=res_dls, gap_far=dist_far - reach,
    atan_far_deg=math.degrees(math.atan2(0.3, 0.9)),
    frac_up=frac_up, frac_down=frac_down, frac_fail=frac_fail, med_iter=med_iter, grid_n=N, frac_fail_ls=frac_fail_ls, med_iter_ls=med_iter_ls,
    cyc_res=cyc_res[-1], cyc0=deg_pair(th0[i_fail], 1), n_sing=int(sing.sum()),
)
