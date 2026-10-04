"""Section 11.3: configuration space and task space.

(1) Example 11.3.1: the C-space of a planar 2R arm (upper arm 0.425 m, forearm 0.392 m, as on the UR5e) is the torus T².
    From θa = (150°, −60°) to θb = (−120°, 60°): going in a straight line as on an ordinary plane, joint 1 turns −270°;
    taking the shortest path on the torus, joint 1 turns +90°.
    The obstacle is a post of centre (0.45, 0.35) m and radius 0.10 m (a circle seen from above). Both paths are checked for collision.
(2) Configuration-space obstacle: check for collision on a 1° grid and find the fraction of configurations occupied by the obstacle.
(3) Forward kinematics is not one-to-one: the same end-effector position has an elbow-up and an elbow-down pair of joint
    angles; both are checked with forward kinematics.
(4) SO(3) cannot be described globally and without singularities by three numbers: the Jacobian (9 × 3) of the map from
    ZYX Euler angles to rotation matrices drops to rank 2 at a pitch of 90°.
(5) The hour and minute hands of a clock: the C-space is T², but the gearing couples the two hands, so they can only move
    along one closed curve on the torus; this curve meets the diagonal "hands overlap" in 11 points, i.e. the hands
    overlap 11 times in 12 hours.
"""
import math

import numpy as np

from _ch11 import L1, L2, OBS_C, OBS_R, collide, fk2, wrap
from bookout import out

# ---------------------------------------------------------------- (1) shortest path on the torus
ta, tb = np.radians([150.0, -60.0]), np.radians([-120.0, 60.0])
d_naive = tb - ta
d_torus = wrap(tb - ta)
s = np.linspace(0, 1, 2001)
hit_naive = collide(ta[0] + s * d_naive[0], ta[1] + s * d_naive[1])
hit_torus = collide(ta[0] + s * d_torus[0], ta[1] + s * d_torus[1])
assert not collide(*ta) and not collide(*tb)
assert hit_naive.any() and not hit_torus.any()
# both paths end in the same configuration: same end-effector position
assert np.allclose(fk2(*(ta + d_naive))[1], fk2(*(ta + d_torus))[1], atol=1e-12)
# how far joint 1 has turned when the obstacle is first hit
k_hit = int(np.argmax(hit_naive))
th1_hit = math.degrees(ta[0] + s[k_hit] * d_naive[0])

# ---------------------------------------------------------------- (2) configuration-space obstacle
g = np.radians(np.arange(-180, 180, 1.0))
T1, T2 = np.meshgrid(g, g, indexing="ij")
C = collide(T1, T2)
frac = C.mean()
# another algorithm: random sampling
rng = np.random.default_rng(7)
U = rng.uniform(-np.pi, np.pi, (200000, 2))
frac_mc = collide(U[:, 0], U[:, 1]).mean()
assert abs(frac - frac_mc) < 0.003

# ---------------------------------------------------------------- (3) elbow up, elbow down
p = np.array([0.55, -0.25])
c2 = (p @ p - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
sols = []
for sg in (1, -1):
    t2 = sg * math.acos(c2)
    t1 = math.atan2(p[1], p[0]) - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
    assert np.allclose(fk2(t1, t2)[1], p, atol=1e-12)
    sols.append((math.degrees(t1), math.degrees(t2)))
(up1, up2), (dn1, dn2) = sols[1], sols[0]            # θ2 < 0 is elbow up (with anticlockwise positive the elbow is above)


# ---------------------------------------------------------------- (4) singularity of ZYX Euler angles
def R_zyx(a):
    ps, th, ph = a
    Rz = np.array([[math.cos(ps), -math.sin(ps), 0], [math.sin(ps), math.cos(ps), 0], [0, 0, 1]])
    Ry = np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(ph), -math.sin(ph)], [0, math.sin(ph), math.cos(ph)]])
    return Rz @ Ry @ Rx


def jac_rank(a, h=1e-6):
    J = np.column_stack([(R_zyx(a + h * e) - R_zyx(a - h * e)).ravel() / (2 * h) for e in np.eye(3)])
    return np.linalg.matrix_rank(J, tol=1e-6)


rank_gen = jac_rank(np.array([0.3, 0.4, 0.5]))
rank_sing = jac_rank(np.array([0.3, math.pi / 2, 0.5]))
assert rank_gen == 3 and rank_sing == 2

# ---------------------------------------------------------------- (5) the two hands of a clock
t = np.linspace(0, 720, 720 * 2000 + 1)              # minutes, 12 hours
a_h = np.radians(0.5 * t) % (2 * np.pi)              # the hour hand turns 0.5° per minute
a_m = np.radians(6.0 * t) % (2 * np.pi)              # the minute hand turns 6° per minute
diff = wrap(a_m - a_h)
crossings = int(((diff[:-1] < 0) & (diff[1:] >= 0)).sum())
# analytically: 6t − 0.5t = 360k, t = 720k/11, k = 0, 1, …, 10 (t = 720 and t = 0 are the same instant)
assert crossings == 11
t_first = 720 / 11

out(d1_naive=math.degrees(d_naive[0]), d1_torus=math.degrees(d_torus[0]), d2=math.degrees(d_torus[1]), th1_hit=th1_hit,
    frac_pct=100 * frac, frac_mc_pct=100 * frac_mc, up1=up1, up2=up2, dn1=dn1, dn2=dn2,
    rank_gen=rank_gen, rank_sing=rank_sing, crossings=crossings, t_first=t_first, t_first_s=(t_first - 65) * 60)
