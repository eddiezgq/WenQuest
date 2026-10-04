"""Section 11.2: degrees of freedom and Grübler's formula.

For a set of mechanisms, the degrees of freedom are found in two ways, with Grübler's formula (11.2.2) and from "the rank
of the constraints":
- formula: count the links N (ground included), the joints J and the degrees of freedom f_i of the joints;
- rank: at a position where the mechanism is assembled, take the twists of the moving links and the joint rates as
  unknowns; each joint gives 6 linear equations V_b − V_a − S_j θ̇_j = 0 (_ch11.mobility), and the degrees of freedom
  = number of unknowns − rank. This is the true (instantaneous) number of degrees of freedom.
Where the two disagree are the exceptions to the formula: passive degrees of freedom (the rods of the Delta spinning
about their own axes), overconstraint (planar mechanisms counted as spatial, a parallelogram with a third crank, the
Bennett linkage) and singular positions (the collinear position of a parallelogram linkage).
Single-loop mechanisms are also checked with the velocity loop-closure equation Σ S_i θ̇_i = 0 of a single loop:
degrees of freedom = n − rank(S_1 … S_n) (Eq. (11.2.6)).
"""
import math

import numpy as np

from _ch11 import (exp6, grubler, joint_P, joint_R, joint_S, joint_U, mobility, screw_revolute, tinv, ur_screws)
from _fig11 import circ_int
from bookout import T, out

z = np.array([0, 0, 1.0])
xh = np.array([1.0, 0, 0])


def P3(p):
    return np.array([p[0], p[1], 0.0])


rows = []          # (name, N, J, Σf, formula m, true m)


def record(name, m_body, n_moving, joints, f_list, extra=None):
    nu, ne, rank, m_true, N = mobility(n_moving, joints)
    m_formula = grubler(m_body, n_moving + 1, f_list)
    rows.append((name, n_moving + 1, len(f_list), sum(f_list), m_formula, m_true))
    return m_formula, m_true, N


# ---------------------------------------------------------------- planar mechanisms (all axes along z)
# four-bar linkage: ground 0.40, crank 0.15, coupler 0.35, rocker 0.30 (Grashof condition met, the crank turns fully)
A, D = np.array([0.0, 0.0]), np.array([0.40, 0.0])
t1 = math.radians(60)
B = A + 0.15 * np.array([math.cos(t1), math.sin(t1)])
Cc = circ_int(B, 0.35, D, 0.30, 1)
j4 = [(0, 1, joint_R(z, P3(A))), (1, 2, joint_R(z, P3(B))), (2, 3, joint_R(z, P3(Cc))), (3, 0, joint_R(z, P3(D)))]
g4_planar, m4, _ = record(T("平面四杆机构", "Planar four-bar linkage"), 3, 3, j4, [1, 1, 1, 1])
g4_spatial = grubler(6, 4, [1, 1, 1, 1])
assert g4_planar == 1 and m4 == 1 and g4_spatial == -2

# slider-crank: crank 0.10, connecting rod 0.30, slider along x
t1 = math.radians(60)
B = 0.1 * np.array([math.cos(t1), math.sin(t1)])
xs = B[0] + math.sqrt(0.3 ** 2 - B[1] ** 2)
jsc = [(0, 1, joint_R(z, P3(A))), (1, 2, joint_R(z, P3(B))), (2, 3, joint_R(z, P3((xs, 0)))), (3, 0, joint_P(xh))]
gsc, msc, _ = record(T("曲柄滑块机构", "Slider-crank mechanism"), 3, 3, jsc, [1, 1, 1, 1])
assert gsc == 1 and msc == 1

# planar five-bar: the two ground points 0.30 apart, the four links 0.20, 0.30, 0.30, 0.20 long
A5, E5 = np.array([0.0, 0.0]), np.array([0.30, 0.0])
B5 = A5 + 0.2 * np.array([math.cos(math.radians(110)), math.sin(math.radians(110))])
D5 = E5 + 0.2 * np.array([math.cos(math.radians(70)), math.sin(math.radians(70))])
C5 = circ_int(B5, 0.3, D5, 0.3, -1)
j5 = [(0, 1, joint_R(z, P3(A5))), (1, 2, joint_R(z, P3(B5))), (2, 3, joint_R(z, P3(C5))), (3, 4, joint_R(z, P3(D5))), (4, 0, joint_R(z, P3(E5)))]
g5, m5, _ = record(T("平面五杆机构", "Planar five-bar linkage"), 3, 4, j5, [1] * 5)
assert g5 == 2 and m5 == 2

# parallelogram linkage with a third crank: three pivots on the ground at (0,0), (0.3,0), (0.6,0), three cranks 0.25 long, the coupler joining the three ends
tp = math.radians(60)
e = 0.25 * np.array([math.cos(tp), math.sin(tp)])
G = [np.array([0.0, 0]), np.array([0.3, 0]), np.array([0.6, 0])]
jpp = [(0, 1, joint_R(z, P3(G[0]))), (0, 2, joint_R(z, P3(G[1]))), (0, 3, joint_R(z, P3(G[2]))),
       (1, 4, joint_R(z, P3(G[0] + e))), (2, 4, joint_R(z, P3(G[1] + e))), (3, 4, joint_R(z, P3(G[2] + e)))]
gpp, mpp, _ = record(T("平行四边形加一根曲柄", "Parallelogram with an extra crank"), 3, 4, jpp, [1] * 6)
assert gpp == 0 and mpp == 1
# if the third crank is slightly longer (0.26, its pin on the coupler also moved out by 1 cm, so it still fits in the original position), the mechanism jams: once the geometric condition is broken, the overconstrained mechanism cannot move
jbad = list(jpp)
e2 = 0.26 * np.array([math.cos(tp), math.sin(tp)])
# the three cranks are still parallel here, and the instantaneous mobility from the rank is still 1; but in a real motion the length constraint of the third crank is violated:
jbad[5] = (3, 4, joint_R(z, P3(G[2] + e2)))
_, _, _, m_jam, _ = mobility(4, jbad)
assert m_jam == 1
d_ang = 0.5                                         # crank 1 turns a further 0.5 rad, the coupler translates with it
shift = 0.25 * np.array([math.cos(tp + d_ang), math.sin(tp + d_ang)]) - e
jam_err = abs(np.linalg.norm(G[2] + e2 + shift - G[2]) - 0.26)     # change of length the third crank would need (m)
assert jam_err > 1e-3

# scissor lift (one stage): two bars of length 2a pinned at their midpoints; at the bottom one fixed pin and one slider, the same at the top
a, phi = 0.6, math.radians(35)
c, s = math.cos(phi), math.sin(phi)
# links: 1 bar A, 2 bar B, 3 platform, 4 lower slider, 5 upper slider
jsl = [(0, 1, joint_R(z, P3((0, 0)))), (0, 4, joint_P(xh)), (4, 2, joint_R(z, P3((2 * a * c, 0)))),
       (1, 2, joint_R(z, P3((a * c, a * s)))), (2, 3, joint_R(z, P3((0, 2 * a * s)))), (3, 5, joint_P(xh)),
       (5, 1, joint_R(z, P3((2 * a * c, 2 * a * s))))]
gsl, msl, _ = record(T("剪叉式升降台（一级）", "Scissor lift (one stage)"), 3, 5, jsl, [1] * 7)
assert gsl == 1 and msl == 1

# ---------------------------------------------------------------- spatial mechanisms
# UR5e: open chain, 6 revolute joints (screw axes of Table 12.1.1, zero position)
S_ur, _ = ur_screws()
jur = [(i, i + 1, S.reshape(6, 1)) for i, S in enumerate(S_ur)]
gur, mur, _ = record(T("UR5e（开链）", "UR5e (open chain)"), 6, 6, jur, [1] * 6)
assert gur == 6 and mur == 6

# Delta: dimensions of the parts-library model. Active arm 0.22 m, passive rods 0.5 m, base radius 0.15 m, moving-platform radius 0.04 m;
# the two rods of each parallelogram are w = 0.06 m apart. With the moving platform at (0, 0, −0.42) m the active-arm angle is the model's 0.187523 rad.
Rb, Rp, La, Lb, w = 0.15, 0.04, 0.22, 0.5, 0.06
pz = np.array([0, 0, -0.42])


def delta_angle(p, k):
    """Active-arm angle of leg k with the centre of the moving platform at p (inverse kinematics, Section 11.5, Eq. (11.5.6))."""
    ph = 2 * math.pi * k / 3
    er, et = np.array([math.cos(ph), math.sin(ph), 0]), np.array([-math.sin(ph), math.cos(ph), 0])
    q = p + Rp * er - Rb * er              # midpoint of the spherical joints relative to the centre of the active-arm axis
    u, v, h = q @ er, q @ et, q[2]
    # |(La cosθ − u, −v, −La sinθ − h)| = Lb  ⇒  A cosθ + B sinθ = C
    Aa, Bb = -2 * La * u, 2 * La * h
    Cc_ = Lb ** 2 - La ** 2 - u * u - v * v - h * h
    r = math.hypot(Aa, Bb)
    base = math.atan2(Bb, Aa)
    return base + math.acos(Cc_ / r)       # the branch with the elbow pointing outwards


th_rest = delta_angle(pz, 0)
assert abs(th_rest - 0.187523) < 1e-6


def delta_joints(p, th, rod_end="S"):
    """Joint table of the Delta. Link numbers: 1–3 active arms, 4–9 passive rods (two per leg), 10 moving platform."""
    js = []
    for k in range(3):
        ph = 2 * math.pi * k / 3
        er, et = np.array([math.cos(ph), math.sin(ph), 0]), np.array([-math.sin(ph), math.cos(ph), 0])
        Bk = Rb * er
        Ek = Bk + La * (math.cos(th[k]) * er - math.sin(th[k]) * np.array([0, 0, 1.0]))
        Pk = p + Rp * er
        js.append((0, 1 + k, joint_R(et, Bk)))                  # the axis of the active arm is tangential
        for sgn, rod in ((1, 4 + 2 * k), (-1, 5 + 2 * k)):
            e1, e2 = Ek + sgn * w / 2 * et, Pk + sgn * w / 2 * et
            js.append((1 + k, rod, joint_S(e1)))
            if rod_end == "S":
                js.append((rod, 10, joint_S(e2)))
            else:                                               # a universal joint replaces the spherical joint at one end, removing the idle spin of the rod
                d = (e2 - e1) / np.linalg.norm(e2 - e1)
                n1 = np.cross(d, et)
                n1 /= np.linalg.norm(n1)
                js.append((rod, 10, joint_U(et, n1, e2)))
    return js


th3 = [th_rest] * 3
jd = delta_joints(pz, th3, "S")
fd = [1] * 3 + [3] * 12
gd, md, Nd = record(T("Delta（杆两端为球关节）", "Delta (spherical joints at both rod ends)"), 6, 10, jd, fd)
# twists of the moving platform: the 6 platform components of each null-space basis vector span a 3-dimensional space of pure translations
Vp = Nd[6 * 9:6 * 10, :]
rank_p = np.linalg.matrix_rank(Vp, tol=1e-9)
assert rank_p == 3 and np.allclose(Vp[:3, :], 0, atol=1e-9)
# idle spin of the rods: the angular velocity of each rod along its own direction is arbitrary, 6 in all
jd2 = delta_joints(pz, th3, "U")
fd2 = [1] * 3 + [3, 2] * 6
gd2, md2, _ = record(T("Delta（杆一端改为万向节）", "Delta (universal joint at one rod end)"), 6, 10, jd2, fd2)
assert (gd, md) == (9, 9) and (gd2, md2) == (3, 3)

# Stewart platform 6-UPS: six points on the base and on the moving platform (three pairs, symmetric)
ra, rb = 0.5, 0.3
aa = [ra * np.array([math.cos(t), math.sin(t), 0]) for t in np.radians([-10, 10, 110, 130, 230, 250])]
bb = [rb * np.array([math.cos(t), math.sin(t), 0]) + np.array([0, 0, 0.6]) for t in np.radians([-50, 50, 70, 170, 190, 290])]
jst = []
for i in range(6):
    d = (bb[i] - aa[i]) / np.linalg.norm(bb[i] - aa[i])
    u1 = np.cross(d, z)
    u1 /= np.linalg.norm(u1)
    u2 = np.cross(d, u1)
    low, up = 1 + i, 7 + i
    jst += [(0, low, joint_U(u1, u2, aa[i])), (low, up, joint_P(d)), (up, 13, joint_S(bb[i]))]
gst, mst, _ = record(T("Stewart 平台 6-UPS", "Stewart platform 6-UPS"), 6, 13, jst, [2, 1, 3] * 6)
assert gst == 6 and mst == 6

# Bennett linkage: spatial single loop of four revolute joints. DH parameters a1 = a3 = a, α1 = α3 = α; a2 = a4 = b, α2 = α4 = β, a/sinα = b/sinβ
aB, alB, beB = 0.3, math.radians(30), math.radians(60)
bB = aB * math.sin(beB) / math.sin(alB)
KB = math.sin((beB + alB) / 2) / math.sin((beB - alB) / 2)


def dhA(th, a_, al):
    ct, st, ca, sa = math.cos(th), math.sin(th), math.cos(al), math.sin(al)
    return np.array([[ct, -st * ca, st * sa, a_ * ct], [st, ct * ca, -ct * sa, a_ * st], [0, sa, ca, 0], [0, 0, 0, 1]])


def bennett(t1_):
    """Given θ1, find the four joint angles from Bennett's relations tan(θ1/2) tan(θ2/2) = K, θ3 = −θ1, θ4 = −θ2, and return the loop-closure error."""
    t2_ = 2 * math.atan(KB / math.tan(t1_ / 2))
    th = [t1_, t2_, -t1_, -t2_]
    Tl = dhA(th[0], aB, alB) @ dhA(th[1], bB, beB) @ dhA(th[2], aB, alB) @ dhA(th[3], bB, beB)
    return th, np.abs(Tl - np.eye(4)).max()


closure = max(bennett(t)[1] for t in np.linspace(0.2, 3.0, 15))
assert closure < 1e-12
# at θ1 = 1 rad: screws of the four joint axes (the DH z-axes) in the ground frame
thB, _ = bennett(1.0)
Tcur, SB = np.eye(4), []
for k in range(4):
    SB.append(screw_revolute(Tcur[:3, 2], Tcur[:3, 3]))
    Tcur = Tcur @ dhA(thB[k], [aB, bB][k % 2], [alB, beB][k % 2])
jB = [(0, 1, SB[1].reshape(6, 1)), (1, 2, SB[2].reshape(6, 1)), (2, 3, SB[3].reshape(6, 1)), (3, 0, SB[0].reshape(6, 1))]
gB, mB, _ = record(T("本内特机构（4R 空间单回路）", "Bennett linkage (spatial 4R loop)"), 6, 3, jB, [1] * 4)
rank_B = np.linalg.matrix_rank(np.column_stack(SB), tol=1e-9)
assert gB == -2 and mB == 1 and rank_B == 3
# for comparison: four arbitrary lines in space as joint axes give a single loop of rank 4 and 0 degrees of freedom
rng = np.random.default_rng(3)
Sr = [screw_revolute(v / np.linalg.norm(v), q) for v, q in zip(rng.normal(size=(4, 3)), rng.normal(size=(4, 3)))]
rank_r = np.linalg.matrix_rank(np.column_stack(Sr), tol=1e-9)
assert rank_r == 4

# ---------------------------------------------------------------- single-loop formula (11.2.6) and singular positions
# four-bar linkage: the four planar revolute screws have rank 3, n − rank = 1
rank4 = np.linalg.matrix_rank(np.column_stack([j[2][:, 0] for j in j4]), tol=1e-9)
assert 4 - rank4 == m4
# parallelogram linkage (ground 0.4, crank 0.2, coupler 0.4, rocker 0.2) turned to the collinear position: all four pins on the x-axis
col = [P3((0, 0)), P3((0.2, 0)), P3((0.6, 0)), P3((0.4, 0))]
rank_col = np.linalg.matrix_rank(np.column_stack([screw_revolute(z, q) for q in col]), tol=1e-9)
m_col = 4 - rank_col
assert m_col == 2
# still 1 at a general position (crank at 1 rad)
q2 = P3(0.2 * np.array([math.cos(1.0), math.sin(1.0)]))
gen = [P3((0, 0)), q2, q2 + P3((0.4, 0)), P3((0.4, 0))]
assert 4 - np.linalg.matrix_rank(np.column_stack([screw_revolute(z, q) for q in gen]), tol=1e-9) == 1

table = "\n".join(f"| {n} | {N} | {J} | {sf} | {str(g).replace('-', '−')} | {m} |" for n, N, J, sf, g, m in rows)
out(table=table, jam_err_mm=jam_err * 1000, g4s=g4_spatial, delta_th=th_rest, delta_th_deg=math.degrees(th_rest), bB=bB, KB=KB,
    rank_B=rank_B, rank_r=rank_r, rank_col=rank_col, m_col=m_col, gd=gd, gd2=gd2, gst=gst, gB=gB)
