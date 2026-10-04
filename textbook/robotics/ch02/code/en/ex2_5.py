"""Examples of Section 2.5: least squares and the pseudoinverse.

Example 2.5.1: planar tool centre point (TCP) calibration. The tool-tip position t in the flange frame and the
               position c of the fixed pin in the base frame are both unknown; the robot touches the pin with the tool tip
               in 5 different orientations, recording the flange position p_i and angle φ_i. Each touch gives
               R(φ_i) t − c = −p_i. The data are "true values + 0.3 mm random error" (fixed random seed); the normal
               equations are solved and checked against three other methods: QR, SVD and the pseudoinverse.
Example 2.5.2: the planar 3R arm (dimensions of Chapter 12) at θ = (30°, 60°, −60°); the end-effector is to move at
               0.1 m/s along x; find the minimum-norm joint velocity J⁺v and compare it with another solution.
Example 2.5.3: fitting a line for a spring scale (the everyday example).
Also checked: the residual is orthogonal to the columns of A; cond(AᵀA) = cond(A)²; Penrose's four conditions; the
error with only 2 touches against 5 and 10 touches (Monte Carlo).
"""
import math

import numpy as np

from _la import L3R, d, jac, rot2
from bookout import out, tex, vec

t_true = np.array([0.120, 0.035])        # m, tool tip in the flange frame
c_true = np.array([0.650, 0.150])        # m, pin in the base frame
SIG = 0.0003                             # m, position error of each touch (standard deviation)


def poses(n):
    return np.radians(np.linspace(-40, 80, n))


def build(phis, ps):
    A = np.vstack([np.hstack([rot2(f), -np.eye(2)]) for f in phis])
    b = np.concatenate([-p for p in ps])
    return A, b


def measure(phis, rng):
    return [c_true - rot2(f) @ t_true + rng.normal(0, SIG, 2) for f in phis]


# ---------------------------------------------------------------- Example 2.5.1
rng = np.random.default_rng(20261001)
phis = poses(5)
ps = measure(phis, rng)
A, b = build(phis, ps)
AtA, Atb = A.T @ A, A.T @ b
x = np.linalg.solve(AtA, Atb)                                     # normal equations
r = b - A @ x
assert np.allclose(A.T @ r, 0, atol=1e-12)                        # residual orthogonal to every column
Q, Rq = np.linalg.qr(A)
x_qr = np.linalg.solve(Rq, Q.T @ b)
x_svd = np.linalg.lstsq(A, b, rcond=None)[0]
x_pinv = np.linalg.pinv(A) @ b
assert np.allclose(x, x_qr) and np.allclose(x, x_svd) and np.allclose(x, x_pinv)
t_hat, c_hat = x[:2], x[2:]
err_t = float(np.linalg.norm(t_hat - t_true)) * 1000              # mm
err_c = float(np.linalg.norm(c_hat - c_true)) * 1000
rms = float(np.sqrt((r ** 2).mean())) * 1000
condA = float(np.linalg.cond(A))
condAtA = float(np.linalg.cond(AtA))
assert abs(condAtA - condA ** 2) / condA ** 2 < 1e-8
# Pythagoras: sum of squared residuals for any x' = minimum + ‖A(x − x')‖²
xo = x + np.array([0.001, -0.002, 0.0005, 0.001])
assert abs(np.sum((b - A @ xo) ** 2) - (np.sum(r ** 2) + np.sum((A @ (x - xo)) ** 2))) < 1e-15

# only 2 touches: 4 equations, 4 unknowns, exactly solvable, all the error goes into the result
A2, b2 = build(phis[[0, 4]], [ps[0], ps[4]])
x2 = np.linalg.solve(A2, b2)
err_t2 = float(np.linalg.norm(x2[:2] - t_true)) * 1000

# Monte Carlo: RMS error of the estimate of t against the number of touches
mc = {}
rng_mc = np.random.default_rng(7)
for n in (2, 5, 10):
    e = []
    for _ in range(4000):
        ph = poses(n)
        Am, bm = build(ph, measure(ph, rng_mc))
        e.append(np.linalg.lstsq(Am, bm, rcond=None)[0][:2] - t_true)
    mc[n] = float(np.sqrt(np.mean(np.sum(np.array(e) ** 2, axis=1)))) * 1000
assert mc[2] > mc[5] > mc[10]

# ---------------------------------------------------------------- Example 2.5.3: spring scale
m = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])                     # kg
y = np.array([0.3, 10.2, 19.6, 30.4, 40.1, 49.6])                # mm
Al = np.column_stack([m, np.ones_like(m)])
kb = np.linalg.solve(Al.T @ Al, Al.T @ y)
assert np.allclose(kb, np.polyfit(m, y, 1))
rl = y - Al @ kb
assert abs(rl.sum()) < 1e-12 and abs(rl @ m) < 1e-12              # residuals sum to 0 and are orthogonal to m
sse = float(rl @ rl)

# ---------------------------------------------------------------- Example 2.5.2: minimum-norm solution for the redundant arm
th3 = [d(30), d(60), d(-60)]
J = jac(th3, L3R)
v = np.array([0.1, 0.0])
Jp = J.T @ np.linalg.inv(J @ J.T)
assert np.allclose(Jp, np.linalg.pinv(J))
thd = Jp @ v
assert np.allclose(J @ thd, v)
n = np.linalg.svd(J)[2][-1]                                       # null-space direction (Section 2.6)
assert np.allclose(J @ n, 0)
thd_other = thd + 0.2 * n
assert np.allclose(J @ thd_other, v) and np.linalg.norm(thd_other) > np.linalg.norm(thd)
assert abs(thd @ n) < 1e-12                                       # minimum-norm solution orthogonal to the null space
for M, Mp in ((J, Jp), (A, np.linalg.pinv(A))):                   # Penrose conditions
    assert np.allclose(M @ Mp @ M, M) and np.allclose(Mp @ M @ Mp, Mp)
    assert np.allclose((M @ Mp).T, M @ Mp) and np.allclose((Mp @ M).T, Mp @ M)

out(
    phis_deg=", ".join(f"{math.degrees(f):.0f}°" for f in phis),
    P=tex(np.array(ps) * 1000, 1), A_top=tex(A[:2], 4), AtA=tex(AtA, 4), Atb=tex(Atb * 1000, 1),
    t_hat=vec(t_hat * 1000, 2), c_hat=vec(c_hat * 1000, 2), err_t=err_t, err_c=err_c, rms=rms,
    condA=condA, condAtA=condAtA, err_t2=err_t2, mc2=mc[2], mc5=mc[5], mc10=mc[10],
    k=kb[0], b0=kb[1], sse=sse,
    J3=tex(J, 4), Jp=tex(Jp, 4), thd=vec(thd, 4), thd_norm=float(np.linalg.norm(thd)),
    thd_other=vec(thd_other, 4), other_norm=float(np.linalg.norm(thd_other)), n=vec(n, 4),
)
