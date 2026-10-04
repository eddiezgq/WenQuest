"""Section 11.4: workspace.

(1) Planar 3R arm (0.425, 0.392, 0.1 m): the analytic reachable and dexterous workspaces (Theorems 11.4.1, 11.4.2),
    checked numerically with 1900 distances × 720 orientations; on the boundary det J = L1 L2 sinθ2 = 0.
(2) UR5e (dimensions of the parts-library model): reachable and dexterous workspaces of the flange centre.
    Joint 1 turns through a full circle, so the workspace is symmetric about the vertical base axis and a grid (2 cm)
    on the (ρ, z) half-plane suffices; at each grid point take K flange-normal directions (Fibonacci sphere grid)
    and decide with the analytic inverse kinematics whether a solution exists (_ch11.ur_reachable).
    Reachable = at least one direction solvable; dexterous = all directions solvable. Volume V = Σ 2πρ Δρ Δz.
    K = 100 and K = 400 are compared for convergence.
    Also computed: the region reachable with the flange facing down (a = −z), and some analytic boundaries: the radius
    d4 − d6 of the unreachable inner cylinder and the inner radius d4 + d6 of the dexterous region.
    A random batch of solvable grid points is checked by substituting the inverse solutions back into forward kinematics.
(3) SCARA (parts-library model): area of the horizontal reachable region (limits of joints 1 and 2), times the screw
    stroke for the volume; joint 4 turns ±360°, so for its own task space R³ × S¹ the dexterous workspace equals the
    reachable workspace.
"""
import math

import numpy as np

from _ch11 import (D4, D6, H1, L1u, L2u, SC_L1, SC_L2, SC_STROKE, frame_from_z, scara_limits, scara_reach_xy, sphere_dirs,
                   ur_fk_dh, ur_ik, ur_reachable)
from bookout import out

# ---------------------------------------------------------------- (1) planar 3R arm
L1, L2, L3 = 0.425, 0.392, 0.1
r_out = L1 + L2 + L3
r_in = max(0.0, abs(L1 - L2) - L3)
dex_out = L1 + L2 - L3
dex_gap = (L3 - abs(L1 - L2), L3 + abs(L1 - L2))           # ring cut out of the dexterous region: L3 − |L1 − L2| < r < L3 + |L1 − L2|
assert dex_gap[0] > 0


def reach2(r):
    return (r >= abs(L1 - L2) - 1e-12) & (r <= L1 + L2 + 1e-12)


rs = np.linspace(0.0005, 0.95, 1900)
phis = np.linspace(0, 2 * np.pi, 720, endpoint=False)
P = rs[:, None]                                            # points on the x-axis (the problem is symmetric about the origin)
wx = P - L3 * np.cos(phis)[None, :]
wy = -L3 * np.sin(phis)[None, :]
ok = reach2(np.hypot(wx, wy))
num_reach = ok.any(1)
num_dex = ok.all(1)
ana_reach = rs <= r_out
ana_dex = (rs <= dex_out) & ((rs <= dex_gap[0]) | (rs >= dex_gap[1]))
mism_reach = int((num_reach != ana_reach).sum())
mism_dex = int((num_dex != ana_dex).sum())
assert mism_reach <= 2 and mism_dex <= 4                  # differ only by one grid step on the boundary
A_reach = math.pi * r_out ** 2
A_dex = math.pi * (dex_gap[0] ** 2 + dex_out ** 2 - dex_gap[1] ** 2)
# boundary of the 2R arm and det J = 0: θ2 = 0 (stretched) gives the outer circle, θ2 = π (folded back) the inner circle
for t2, rr in ((0.0, L1 + L2), (math.pi, abs(L1 - L2))):
    assert abs(math.hypot(L1 + L2 * math.cos(t2), L2 * math.sin(t2)) - rr) < 1e-12
    assert abs(L1 * L2 * math.sin(t2)) < 1e-12

# ---------------------------------------------------------------- (2) UR5e
h = 0.02
rho = np.arange(h / 2, 1.06, h)
zz = np.arange(-0.88, 1.16, h) + h / 2
RR, ZZ = np.meshgrid(rho, zz, indexing="ij")
pts = np.stack([RR.ravel(), np.zeros(RR.size), ZZ.ravel()], 1)
w_cell = 2 * np.pi * pts[:, 0] * h * h


def scan(K):
    cnt = np.zeros(len(pts), int)
    for d in sphere_dirs(K):
        cnt += ur_reachable(pts, np.repeat(d[None], len(pts), 0))
    return cnt


cnt = scan(100)
reach, dex = cnt > 0, cnt == 100
V_reach, V_dex = w_cell[reach].sum(), w_cell[dex].sum()
cnt4 = scan(400)
V_reach4, V_dex4 = w_cell[cnt4 > 0].sum(), w_cell[cnt4 == 400].sum()
assert abs(V_reach4 - V_reach) / V_reach < 0.01 and abs(V_dex4 - V_dex) / V_dex < 0.03
down = ur_reachable(pts, np.repeat(np.array([[0, 0, -1.0]]), len(pts), 0))
V_down = w_cell[down].sum()
# compare with the estimate of Chapter 1, "a ball of radius 0.85 m"
V_ball = 4 / 3 * math.pi * 0.85 ** 3
# analytic boundaries: the flange centre is at least d4 − d6 from the base axis; at least d4 + d6 when dexterous
rho_min_reach = pts[reach, 0].min() - h / 2
rho_min_dex = pts[dex, 0].min() - h / 2
assert abs(rho_min_reach - (D4 - D6)) < h and abs(rho_min_dex - (D4 + D6)) < h
dist = np.hypot(pts[:, 0], pts[:, 2] - H1)                # distance to the shoulder centre (height where the joint 2 axis meets the base axis)
d_reach_max, d_dex_max = dist[reach].max() + h / 2, dist[dex].max() + h / 2
# spot check: at solvable grid points, substitute the inverse solutions back into forward kinematics
rng = np.random.default_rng(5)
idx = rng.choice(np.where(reach)[0], 300, replace=False)
dirs = sphere_dirs(100)
nchk = 0
for i in idx:
    for d in dirs[rng.choice(100, 5, replace=False)]:
        Tg = np.eye(4)
        Tg[:3, :3] = frame_from_z(d)[0]
        Tg[:3, 3] = pts[i]
        for q in ur_ik(Tg):
            assert np.allclose(ur_fk_dh(q), Tg, atol=1e-8)
            nchk += 1
assert nchk > 1000

# ---------------------------------------------------------------- (3) SCARA
lim = scara_limits()
hs = 0.0025
g = np.arange(-0.65, 0.65, hs) + hs / 2
X, Y = np.meshgrid(g, g)
okxy = scara_reach_xy(X, Y, lim["J1"], lim["J2"])
A_sc = okxy.sum() * hs * hs
V_sc = A_sc * SC_STROKE
r_sc = np.hypot(X, Y)[okxy]
r_sc_min = math.sqrt(SC_L1 ** 2 + SC_L2 ** 2 + 2 * SC_L1 * SC_L2 * math.cos(lim["J2"][1]))
assert abs(r_sc.min() - r_sc_min) < 2 * hs
A_ring = math.pi * ((SC_L1 + SC_L2) ** 2 - r_sc_min ** 2)
assert A_sc < A_ring

out(r_out=r_out, dex_out=dex_out, gap0=dex_gap[0], gap1=dex_gap[1], A_reach=A_reach, A_dex=A_dex, dex_ratio=100 * A_dex / A_reach,
    mism_reach=mism_reach, mism_dex=mism_dex,
    V_reach=V_reach, V_dex=V_dex, V_reach4=V_reach4, V_dex4=V_dex4, V_down=V_down, V_ball=V_ball,
    dex_pct=100 * V_dex / V_reach, down_pct=100 * V_down / V_reach,
    rho_in=D4 - D6, rho_dex=D4 + D6, d_reach_max=d_reach_max, d_dex_max=d_dex_max, nchk=nchk, ncell=len(pts),
    A_sc=A_sc, V_sc=V_sc, r_sc_min=r_sc_min, A_ring=A_ring, sc_t1=math.degrees(lim["J1"][1]), sc_t2=math.degrees(lim["J2"][1]),
    rho_max_reach=pts[reach, 0].max() + h / 2, L12=L1u + L2u, ratio_ur_sc=V_reach / V_sc, d_dex_max_mm=0)
