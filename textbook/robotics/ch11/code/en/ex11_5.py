"""Section 11.5: closed chains and constraints.

(1) Four-bar linkage (frame 0.40, crank 0.15, coupler 0.35, rocker 0.30 m): the solution curves of the loop-closure
    equation (11.5.1) on the (θ1, θ3) torus. The type is decided by the Grashof condition (11.5.5); for each crank angle
    the rocker angles of the two assembly modes are found by geometric construction (intersecting two circles) and
    checked against Freudenstein's equation (11.5.2) and its closed-form solution (11.5.3); the swing of the rocker
    (checked by the law of cosines at the limit positions).
    With the frame changed to 0.58 m (Grashof condition not met), the range of the crank is found, and the two assembly
    modes join into one curve at the limit positions; at a limit position the Jacobian determinant of the constraints
    with respect to (θ2, θ3) is zero, while the Jacobian with respect to (θ1, θ2, θ3) still has rank 2.
(2) Delta (dimensions of the parts-library model): inverse kinematics (11.5.6), (11.5.7) and forward kinematics
    (intersection of three spheres, Eq. (11.5.8)) checked against each other; the active-arm angles with the moving
    platform at the model's rest position; the other solution of each leg; the other (upper) solution of the forward
    kinematics.
(3) Stewart platform 6-UPS: inverse kinematics (11.5.9), the six leg lengths with the moving platform translated and
    turned 10° about x.
(4) Pfaffian constraints: the no-side-slip constraint of a wheel (11.5.10) violates the integrability condition (11.5.12)
    a · (∇ × a) = 0 (curl computed numerically); of the three constraints (11.5.13) of the differential-drive AGV
    (parts library B-EDU-DIFF: wheel radius 0.05 m, track 0.26 m), φ − r(θR − θL)/b = const (11.5.14) is the integrable
    combination: in a simulation with random wheel speeds this quantity never changes;
    two wheel-speed programmes end with the same wheel angles and the same heading, but at different positions.
"""
import math

import numpy as np

from _ch11 import AGV_B, AGV_R, DELTA, FB, FB_NG, agv_drive, agv_programs, fourbar
from bookout import T, out

# ---------------------------------------------------------------- (1) four-bar linkage
def freud(l0, l1, l2, l3, t1, t3):
    """Residual of Freudenstein's equation: K1 cosθ3 − K2 cosθ1 + K3 − cos(θ1 − θ3)."""
    K1, K2, K3 = l0 / l1, l0 / l3, (l1 ** 2 - l2 ** 2 + l3 ** 2 + l0 ** 2) / (2 * l1 * l3)
    return K1 * math.cos(t3) - K2 * math.cos(t1) + K3 - math.cos(t1 - t3)


def closure(l0, l1, l2, l3, t1, t3):
    """Residual of the loop-closure equation (11.5.1): the distance from B to C must equal the coupler length."""
    B = np.array([l1 * math.cos(t1), l1 * math.sin(t1)])
    C = np.array([l0 + l3 * math.cos(t3), l3 * math.sin(t3)])
    return abs(np.linalg.norm(C - B) - l2)


L = FB
s_, l_ = min(L), max(L)
pq = sum(L) - s_ - l_
grashof = s_ + l_ <= pq
assert grashof
t1s = np.linspace(-math.pi, math.pi, 3601)
rocker = {1: [], -1: []}
for t1 in t1s:
    for mode in (1, -1):
        t3 = fourbar(*L, t1, mode)
        assert t3 is not None                          # the crank turns fully
        assert closure(*L, t1, t3) < 1e-12 and abs(freud(*L, t1, t3)) < 1e-12
        rocker[mode].append(t3)
r_up = np.degrees(np.unwrap(rocker[-1]))
swing = r_up.max() - r_up.min()
# the two assembly modes never meet in θ3: two separate closed curves on the torus
gap_modes = min(abs((a - b + math.pi) % (2 * math.pi) - math.pi) for a, b in zip(rocker[1], rocker[-1]))
assert gap_modes > 0.1
# limit positions: the rocker reaches the ends of its swing when coupler and crank are collinear; check by the law of cosines
l0, l1, l2, l3 = L


def rocker_at(dist):                                   # given the distance AC (l2 ± l1 when crank and coupler are collinear), ∠ADC from the law of cosines in triangle ACD; only the swing is checked here
    return math.acos((l3 ** 2 + l0 ** 2 - dist ** 2) / (2 * l3 * l0))


swing_check = math.degrees(abs(rocker_at(l2 + l1) - rocker_at(l2 - l1)))
assert abs(swing_check - swing) < 0.2

# closed-form solution (11.5.3) of Freudenstein's equation: the two assembly modes at θ1 = 60°
t1_60 = math.radians(60)
K1, K2, K3 = l0 / l1, l0 / l3, (l1 ** 2 - l2 ** 2 + l3 ** 2 + l0 ** 2) / (2 * l1 * l3)
Af, Bf, Cf = K1 - math.cos(t1_60), -math.sin(t1_60), K2 * math.cos(t1_60) - K3
rf = math.hypot(Af, Bf)
t3_open = math.atan2(Bf, Af) + math.acos(Cf / rf)
t3_cross = math.atan2(Bf, Af) - math.acos(Cf / rf)
assert abs(t3_open - fourbar(*L, t1_60, -1)) < 1e-12                         # geometric construction (two circles) agrees with the closed form
assert abs((t3_cross - fourbar(*L, t1_60, 1) + math.pi) % (2 * math.pi) - math.pi) < 1e-12
assert closure(*L, t1_60, t3_open) < 1e-12 and closure(*L, t1_60, t3_cross) < 1e-12

# Grashof condition not met: frame 0.58 m
Ln = FB_NG
assert min(Ln) + max(Ln) > sum(Ln) - min(Ln) - max(Ln)
ok = [fourbar(*Ln, t1, 1) is not None for t1 in t1s]
ok = np.array(ok)
crank_range = math.degrees((t1s[1] - t1s[0]) * ok.sum())
# at a limit position coupler and rocker lie in a straight line, |BD| = l2 + l3; the limiting crank angle follows from the law of cosines
cos_lim = (Ln[1] ** 2 + Ln[0] ** 2 - (Ln[2] + Ln[3]) ** 2) / (2 * Ln[1] * Ln[0])
t_lim = math.degrees(math.acos(cos_lim))
assert abs(crank_range - 2 * t_lim) < 0.3
# at a limit position the two assembly modes coincide: the curves join into one here
e_up, e_dn = fourbar(*Ln, math.radians(t_lim) - 1e-7, 1), fourbar(*Ln, math.radians(t_lim) - 1e-7, -1)
assert abs(e_up - e_dn) < 0.01


def jac_g(l0, l1, l2, l3, t1, t2, t3):
    """Jacobian (2×3) of the loop-closure equation (11.5.1) g = l1 e(θ1) + l2 e(θ2) − l3 e(θ3) − l0 e_x with respect to (θ1, θ2, θ3)."""
    return np.array([[-l1 * math.sin(t1), -l2 * math.sin(t2), l3 * math.sin(t3)],
                     [l1 * math.cos(t1), l2 * math.cos(t2), -l3 * math.cos(t3)]])


tl = math.radians(t_lim)
Bl = np.array([Ln[1] * math.cos(tl), Ln[1] * math.sin(tl)])
Dl = np.array([Ln[0], 0.0])
Cl = Bl + Ln[2] / (Ln[2] + Ln[3]) * (Dl - Bl)                               # coupler and rocker in a straight line: C lies on BD
t2l, t3l = math.atan2(*(Cl - Bl)[::-1]), math.atan2(*(Cl - Dl)[::-1])
gl = Ln[1] * np.array([math.cos(tl), math.sin(tl)]) + Ln[2] * np.array([math.cos(t2l), math.sin(t2l)]) \
    - Ln[3] * np.array([math.cos(t3l), math.sin(t3l)]) - np.array([Ln[0], 0])
assert np.abs(gl).max() < 1e-12
Jl = jac_g(*Ln, tl, t2l, t3l)
det23_lim = np.linalg.det(Jl[:, 1:])
rank_lim = np.linalg.matrix_rank(Jl, tol=1e-9)
assert abs(det23_lim) < 1e-12 and rank_lim == 2
# for comparison: at a general position (θ1 = 60°) the (θ2, θ3) determinant is non-zero
t3g = fourbar(*Ln, t1_60, -1)
Bg = np.array([Ln[1] * math.cos(t1_60), Ln[1] * math.sin(t1_60)])
Cg = np.array([Ln[0] + Ln[3] * math.cos(t3g), Ln[3] * math.sin(t3g)])
t2g = math.atan2(*(Cg - Bg)[::-1])
det23_gen = np.linalg.det(jac_g(*Ln, t1_60, t2g, t3g)[:, 1:])
assert abs(det23_gen) > 1e-3

# ---------------------------------------------------------------- (2) Delta
Rb, Rp, La, Lb = DELTA["Rb"], DELTA["Rp"], DELTA["La"], DELTA["Lb"]


def delta_ik(p, sign=1):
    """Inverse kinematics (11.5.7); sign = +1 gives the elbows-out solution (used by the parts-library model), −1 the other one."""
    th = []
    for k in range(3):
        ph = 2 * math.pi * k / 3
        er, et = np.array([math.cos(ph), math.sin(ph), 0]), np.array([-math.sin(ph), math.cos(ph), 0])
        q = p + Rp * er - Rb * er
        u, v, h = q @ er, q @ et, q[2]
        A, B, Cc = -2 * La * u, 2 * La * h, Lb ** 2 - La ** 2 - u * u - v * v - h * h
        r = math.hypot(A, B)
        if abs(Cc) > r:
            return None
        th.append(math.atan2(B, A) + sign * math.acos(Cc / r))
    return np.array(th)


def delta_fk(th, both=False):
    """Intersection of three spheres (11.5.8): centres c_k = elbow point − Rp e_rk, radius Lb; returns the lower point (both points if both=True)."""
    cs = []
    for k in range(3):
        ph = 2 * math.pi * k / 3
        er = np.array([math.cos(ph), math.sin(ph), 0])
        E = Rb * er + La * (math.cos(th[k]) * er - math.sin(th[k]) * np.array([0, 0, 1.0]))
        cs.append(E - Rp * er)
    c1, c2, c3 = cs
    ex = (c2 - c1) / np.linalg.norm(c2 - c1)
    i = ex @ (c3 - c1)
    ey = c3 - c1 - i * ex
    ey /= np.linalg.norm(ey)
    ez = np.cross(ex, ey)
    d, j = np.linalg.norm(c2 - c1), ey @ (c3 - c1)
    x = d / 2                                            # the three radii are equal
    y = (i * i + j * j - 2 * i * x) / (2 * j)
    z = math.sqrt(Lb ** 2 - x * x - y * y)
    cands = [c1 + x * ex + y * ey + s * z * ez for s in (1, -1)]
    if both:
        return sorted(cands, key=lambda v: v[2])
    return min(cands, key=lambda v: v[2])


p0 = np.array([0, 0, -0.42])
th0 = delta_ik(p0)
assert np.allclose(th0, 0.187523, atol=1e-6)
rng = np.random.default_rng(11)
nd = 0
for _ in range(500):
    p = np.array([rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), rng.uniform(-0.55, -0.32)])
    th = delta_ik(p)
    if th is None:
        continue
    assert np.allclose(delta_fk(th), p, atol=1e-9)
    nd += 1
assert nd > 400
p1 = np.array([0.1, 0.0, -0.45])
th1 = delta_ik(p1)
th1_in = delta_ik(p1, -1)                                  # the other, elbows-in solution: it closes too
assert np.allclose(delta_fk(th1_in), p1, atol=1e-9)
low, high = delta_fk(th1, both=True)
assert np.allclose(low, p1, atol=1e-9) and high[2] > 0     # the other intersection lies above the base and cannot be assembled

# Delta workspace: all three legs have a solution with active-arm angles within the model limits [−40°, 90°] (1 cm grid)
lo, hi = math.radians(-40), math.radians(90)
h_ = 0.01
gx = np.arange(-0.5, 0.5 + 1e-9, h_)
gz = np.arange(-0.8, -0.05 + 1e-9, h_)
X, Y, Z = np.meshgrid(gx, gx, gz, indexing="ij")
okw = np.ones(X.shape, bool)
for k in range(3):
    ph = 2 * math.pi * k / 3
    c_, s_k = math.cos(ph), math.sin(ph)
    qx, qy, qz = X + (Rp - Rb) * c_, Y + (Rp - Rb) * s_k, Z
    u_, v_ = qx * c_ + qy * s_k, -qx * s_k + qy * c_
    A_, B_, C_ = -2 * La * u_, 2 * La * qz, Lb ** 2 - La ** 2 - u_ ** 2 - v_ ** 2 - qz ** 2
    r_ = np.hypot(A_, B_)
    good = np.abs(C_) <= r_
    th_ = np.arctan2(B_, A_) + np.arccos(np.clip(C_ / np.where(r_ > 0, r_, 1), -1, 1))
    th_ = (th_ + math.pi) % (2 * math.pi) - math.pi
    okw &= good & (th_ >= lo) & (th_ <= hi)
V_delta = okw.sum() * h_ ** 3
iz = int(round((-0.42 - gz[0]) / h_))
rad_042 = np.hypot(X[:, :, iz], Y[:, :, iz])[okw[:, :, iz]].max()
zs_ok = gz[okw.any(axis=(0, 1))]
z_top, z_bot = zs_ok.max(), zs_ok.min()
assert okw[50, 50, iz]                                 # the rest position is in the workspace
# spot check: points of the workspace, inverse solution put back into the forward one
idx = np.argwhere(okw)
for i in rng.choice(len(idx), 200, replace=False):
    pp = np.array([X[tuple(idx[i])], Y[tuple(idx[i])], Z[tuple(idx[i])]])
    assert np.allclose(delta_fk(delta_ik(pp)), pp, atol=1e-9)

# ---------------------------------------------------------------- (3) inverse kinematics of the Stewart 6-UPS
ra, rb = 0.5, 0.3
aa = [ra * np.array([math.cos(t), math.sin(t), 0]) for t in np.radians([-10, 10, 110, 130, 230, 250])]
bb = [rb * np.array([math.cos(t), math.sin(t), 0]) for t in np.radians([-50, 50, 70, 170, 190, 290])]


def stewart_ik(p, R):
    return np.array([np.linalg.norm(p + R @ b - a) for a, b in zip(aa, bb)])


ps = np.array([0, 0, 0.6])
ang = math.radians(10)
Rx = np.array([[1, 0, 0], [0, math.cos(ang), -math.sin(ang)], [0, math.sin(ang), math.cos(ang)]])
legs0 = stewart_ik(ps, np.eye(3))
legs1 = stewart_ik(ps, Rx)
assert np.allclose(legs0, legs0[0])                   # symmetric layout: at the zero position the six legs are equally long

# ---------------------------------------------------------------- (4) Pfaffian constraints and integrability
def curl(a, q, h=1e-6):
    J = np.column_stack([(a(q + h * e) - a(q - h * e)) / (2 * h) for e in np.eye(3)])   # J[i, j] = ∂a_i/∂q_j
    return np.array([J[2, 1] - J[1, 2], J[0, 2] - J[2, 0], J[1, 0] - J[0, 1]])


a_car = lambda q: np.array([math.sin(q[2]), -math.cos(q[2]), 0.0])           # ẋ sinφ − ẏ cosφ = 0
vals = [a_car(q) @ curl(a_car, q) for q in rng.uniform(-2, 2, (20, 3))]
assert np.allclose(vals, -1.0, atol=1e-6)
# for comparison: the gradient of an integrable constraint g(x, y, φ) = x + 2y − φ = 0
a_hol = lambda q: np.array([1.0, 2.0, -1.0])
assert abs(a_hol(np.zeros(3)) @ curl(a_hol, np.zeros(3))) < 1e-9

r_w, b_w = AGV_R, AGV_B
qA, qB = agv_programs()
inv_a = qA[:, 2] - r_w * (qA[:, 3] - qA[:, 4]) / b_w          # the quantity of Eq. (11.5.14): must stay 0
inv_b = qB[:, 2] - r_w * (qB[:, 3] - qB[:, 4]) / b_w
qa, qb = qA[-1], qB[-1]
TR, TL = qa[3], qa[4]
# another set of random wheel speeds: it stays constant as well
rw = np.repeat(rng.uniform(-15, 15, (40, 2)), 50, axis=0)
qr = agv_drive(rw[:, 0], rw[:, 1])
assert np.abs(qr[:, 2] - r_w * (qr[:, 3] - qr[:, 4]) / b_w).max() < 1e-9
assert np.allclose(qa[3:], qb[3:], atol=1e-9)          # same wheel angles
assert np.allclose(qa[2], qb[2], atol=1e-9)            # same heading too (the integrable combination)
assert np.abs(inv_a).max() < 1e-9 and np.abs(inv_b).max() < 1e-9
gap_xy = np.linalg.norm(qa[:2] - qb[:2])
assert gap_xy > 0.1                                    # different positions (non-integrable)

inv_max = max(np.abs(inv_a).max(), np.abs(inv_b).max())
out(t3_open=math.degrees(t3_open), t3_cross=math.degrees(t3_cross), K1=K1, K2=K2, K3=K3,
    det23_lim=abs(det23_lim), det23_gen=abs(det23_gen), rank_lim=rank_lim,
    th1_in=np.degrees(th1_in).round(2).tolist(), th1_in_a=math.degrees(th1_in[0]), th1_in_b=math.degrees(th1_in[1]),
    fk_high_z=high[2], legs1_txt=T("、".join(f"{v:.4f}" for v in legs1), ", ".join(f"{v:.4f}" for v in legs1)), V_delta=V_delta, rad_042=rad_042, z_top=z_top, z_bot=z_bot, legs1=legs1.round(4).tolist(), inv_max=inv_max,
    swing=swing, gap_modes_deg=math.degrees(gap_modes), crank_range=crank_range, t_lim=t_lim, 
    th0=th0[0], th0_deg=math.degrees(th0[0]), nd=nd, th1=np.degrees(th1).round(3).tolist(), th1a=math.degrees(th1[0]), th1b=math.degrees(th1[1]),
    leg0=legs0[0], legs1_min=legs1.min(), legs1_max=legs1.max(),
    phi_end=math.degrees(qa[2]), TR=TR, TL=TL, xa=qa[0], ya=qa[1], xb=qb[0], yb=qb[1], gap_xy=gap_xy, s_l=s_ + l_, p_q=pq)
