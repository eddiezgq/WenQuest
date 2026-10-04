"""Example 10.1.1: an AGV turns on a circular arc; how does a part at rest on the workshop floor move in the AGV frame {b}?

Floor frame {s}: the AGV starts at the origin facing +x and turns left at v = 0.5 m/s on a circle of radius R0 = 2.0 m,
centre C = (0, 2.0) m. AGV frame {b}: origin at the centre of the vehicle body, x forward, y to the left, moving with
the AGV. The part P is at rest in {s} at (2.0, 0.5) m.
Converting at every instant by p_b = R_sb^T (p_s − p_sb) (Eq. (5.1.3)), we check that in {b} the part moves on a circle
about the point (0, R0), with radius |CP| and speed Ω|CP|; its velocity in {b} is found in two ways (numerical
differentiation, and the formula ṗ_b = −Ω ẑ × p_b − (v, 0, 0)), and the two agree.
Also given: the two readings of P in two coordinate systems of the same reference frame (the floor): Cartesian and polar.
"""
import math

import numpy as np

from _kin import d1, rotz, skew
from bookout import out

v, R0 = 0.5, 2.0                       # AGV speed m/s, turning radius m
Om = v / R0                            # angular velocity of the vehicle body rad/s
C = np.array([0.0, R0, 0.0])           # centre of the circle, {s}
P = np.array([2.0, 0.5, 0.0])          # the part, {s}


def agv(t):
    """Position p_sb(t) and orientation R_sb(t) of the AGV in {s}."""
    psi = Om * t
    return C + R0 * np.array([math.sin(psi), -math.cos(psi), 0.0]), rotz(psi)


def p_b(t):
    o, R = agv(t)
    return R.T @ (P - o)                # Eq. (5.1.3)


t1 = 6.0
pb1 = p_b(t1)
cb = np.array([0.0, R0, 0.0])          # position of the centre in {b} (does not change with time)
d = float(np.linalg.norm(P - C))
for t in np.linspace(0, 20, 81):       # in {b} the part always stays at distance d from (0, R0)
    assert abs(np.linalg.norm(p_b(t) - cb) - d) < 1e-12
    o, R = agv(t)
    assert abs(np.linalg.norm(R.T @ (C - o) - cb)) < 1e-12

vb_num = d1(p_b, t1, 1e-5)
vb_formula = -skew([0, 0, Om]) @ pb1 - np.array([v, 0, 0])
assert np.allclose(vb_num, vb_formula, atol=1e-9)
speed_b = float(np.linalg.norm(vb_formula))
assert abs(speed_b - Om * d) < 1e-12

# two coordinate systems in the same reference frame: Cartesian (x, y) and polar (ρ, φ)
rho = math.hypot(P[0], P[1])
phi = math.atan2(P[1], P[0])
assert abs(rho * math.cos(phi) - P[0]) < 1e-12 and abs(rho * math.sin(phi) - P[1]) < 1e-12

o1, _ = agv(t1)
out(v=v, R0=R0, Om=Om, t1=t1, psi1_deg=math.degrees(Om * t1),
    ox1=o1[0], oy1=o1[1], pbx=pb1[0], pby=pb1[1], d=d, speed_b=speed_b,
    vbx=vb_formula[0], vby=vb_formula[1],
    rho=rho, phi_deg=math.degrees(phi), period=2 * math.pi / Om)
