"""Examples of Section 4.5.

Example 4.5.1: ZYX Euler angles (yaw ψ, pitch θ, roll φ) from a rotation matrix, composed back again as a check.
Example 4.5.2: gimbal lock -- near 90° pitch a small change of orientation makes roll and yaw jump a long way; at
exactly 90° pitch only ψ − φ is determined.
"""
import math

import numpy as np

from _rot import is_rotation, rot_axis, rot_x, rot_y, rot_z
from bookout import out, tex

d, deg = math.radians, math.degrees


def wrap(a):
    """Bring an angle into (−180°, 180°]."""
    a = (a + 180.0) % 360.0 - 180.0
    return 180.0 if a == -180.0 else a


def zyx(psi, th, phi):
    """Eq. (4.5.3): R = Rot(z,ψ) Rot(y,θ) Rot(x,φ)."""
    return rot_z(psi) @ rot_y(th) @ rot_x(phi)


def zyx_angles(R):
    """Eq. (4.5.4): the solution with cos θ ≥ 0."""
    th = math.atan2(-R[2, 0], math.hypot(R[0, 0], R[1, 0]))
    psi = math.atan2(R[1, 0], R[0, 0])
    phi = math.atan2(R[2, 1], R[2, 2])
    return psi, th, phi


# Theorem 4.5.1: fixed axes x→y→z give the same as body axes z→y→x
a, b, c = d(20), d(-35), d(50)
fixed = rot_z(c) @ rot_y(b) @ rot_x(a)           # about fixed axes x(a), y(b), z(c) in turn: premultiply
body = np.eye(3)
for M in (rot_z(c), rot_y(b), rot_x(a)):          # about body axes z(c), y(b), x(a) in turn: postmultiply
    body = body @ M
assert np.allclose(fixed, body)

# Example 4.5.1: the "fixed axes" result of Example 4.2.3, Rot(x,45°) Rot(z,30°)
R = rot_x(d(45)) @ rot_z(d(30))
psi, th, phi = zyx_angles(R)
assert is_rotation(R) and np.allclose(zyx(psi, th, phi), R)
# the other solution: θ' = π − θ, ψ' = ψ + π, φ' = φ + π
assert np.allclose(zyx(psi + math.pi, math.pi - th, phi + math.pi), R)

# Example 4.5.2: pitch 89.9°, then a further 0.1° about the fixed x axis
R0 = zyx(d(10), d(89.9), d(20))
R1 = rot_axis([1, 0, 0], d(0.1)) @ R0
a0, a1 = zyx_angles(R0), zyx_angles(R1)
change = float(np.degrees(np.arccos(np.clip((np.trace(R0.T @ R1) - 1) / 2, -1, 1))))
jump_psi, jump_phi = deg(a1[0] - a0[0]), deg(a1[2] - a0[2])
assert abs(change - 0.1) < 1e-9 and abs(jump_psi) > 10 * change

# pitch exactly 90°: only ψ − φ is determined
L1, L2 = zyx(d(40), d(90), d(10)), zyx(d(70), d(90), d(40))
assert np.allclose(L1, L2)

# data for Figure 4.5.2: pitch swept from 80° to 89.99°, the yaw jump caused by the same 0.1° disturbance
pitches = list(np.linspace(80, 89.99, 120))
jumps = []
for p in pitches:
    A0 = zyx(d(10), d(p), d(20))
    A1 = rot_axis([1, 0, 0], d(0.1)) @ A0
    jumps.append(abs(deg(zyx_angles(A1)[0] - zyx_angles(A0)[0])))

out(R=tex(R), psi=deg(psi), th=deg(th), phi=deg(phi), psi2=wrap(deg(psi + math.pi)), th2=wrap(deg(math.pi - th)), phi2=wrap(deg(phi + math.pi)),
    r31=R[2, 0], r21=R[1, 0], r11=R[0, 0], r32=R[2, 1], r33=R[2, 2],
    psi0=deg(a0[0]), phi0=deg(a0[2]), psi1=deg(a1[0]), phi1=deg(a1[2]), jump_psi=jump_psi, jump_phi=jump_phi,
    L=tex(L1), _pitches=pitches, _jumps=jumps)
