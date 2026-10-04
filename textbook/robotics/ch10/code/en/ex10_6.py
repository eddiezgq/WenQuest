"""Examples 10.6.1–10.6.3: rotating reference frame, the theorem of composition of accelerations a_abs = a_rel + a_tr + 2Ω × v_rel.

Ground frame {s} (fixed frame); turntable frame {p} (moving frame), origin at the centre of the table, turning with the
table about the vertical axis.
Example 10.6.1: the table turns steadily at Ω = 0.5 rad/s (anticlockwise seen from above); an AGV starts at the centre and
  drives outwards at a constant v_rel = 0.4 m/s along a radius drawn on the table. At t = 2.5 s (1.0 m from the centre) find
  the transport, Coriolis and absolute accelerations and the reading of the accelerometer on the AGV (x forward, y left).
  Three checks: (1) the composition theorem; (2) numerical second derivative in ground coordinates; (3) the polar-coordinate
  formula (10.3.9) of Section 10.3. Also computed term by term in the matrix form (10.6.10).
Example 10.6.2: at the same instant the table is speeding up at Ω̇ = 0.2 rad/s² and the AGV is accelerating along the
  radius at 0.3 m/s²; find each term and the total acceleration.
Example 10.6.3: the Earth's rotation: an AGV in Shanghai (latitude 31.2° N) drives due north at 1.0 m/s; the horizontal
  component of its Coriolis acceleration.
"""
import math

import numpy as np

from _kin import d1, d2, rotz, skew
from bookout import out

Om, vr = 0.5, 0.4
t1 = 2.5
z = np.array([0, 0, 1.0])


def pos_s(t, Om0=Om, Omd=0.0, vr0=vr, ar=0.0):
    """Position of the AGV in the ground frame {s}: table angle ψ = Om0 t + Omd t²/2; the AGV is at (ρ, 0, 0) in {p}, ρ = vr0 t + ar t²/2."""
    psi = Om0 * t + 0.5 * Omd * t * t
    rho = vr0 * t + 0.5 * ar * t * t
    return rotz(psi) @ np.array([rho, 0, 0])


rho1 = vr * t1
psi1 = Om * t1
R = rotz(psi1)
r_p = np.array([rho1, 0, 0])              # position of the AGV in {p}
v_rel_p = np.array([vr, 0, 0])            # relative velocity (components in {p})
a_rel_p = np.zeros(3)
Om_s = Om * z
# composition theorem (components in {s})
r_s = R @ r_p
v_rel = R @ v_rel_p
v_tr = np.cross(Om_s, r_s)
v_abs = v_tr + v_rel
a_tr = np.cross(Om_s, np.cross(Om_s, r_s))           # table turns steadily, O′ fixed: only the centripetal term
a_C = 2 * np.cross(Om_s, v_rel)
a_abs = R @ a_rel_p + a_tr + a_C
# (2) numerical differentiation
assert np.allclose(d1(pos_s, t1, 1e-5), v_abs, atol=1e-9)
assert np.allclose(d2(pos_s, t1, 1e-3), a_abs, atol=1e-6)
# (3) polar-coordinate formula (10.3.9): ρ̇ = vr, φ̇ = Ω, ρ̈ = φ̈ = 0
a_rho = 0 - rho1 * Om ** 2
a_phi = rho1 * 0 + 2 * vr * Om
er, ep = R @ np.array([1.0, 0, 0]), R @ np.array([0, 1.0, 0])
assert np.allclose(a_rho * er + a_phi * ep, a_abs, atol=1e-14)
# matrix form (10.6.10): r̈_s = p̈ + ([Ω̇] + [Ω]²) R r_p + 2[Ω] R ṙ_p + R r̈_p
A = skew(Om_s) @ skew(Om_s) @ R @ r_p + 2 * skew(Om_s) @ R @ v_rel_p + R @ a_rel_p
assert np.allclose(A, a_abs, atol=1e-15)
# accelerometer reading: x of the AGV body {b} points outwards along the radius (same as e_ρ), y to the left (same as e_φ); in the horizontal plane specific force = acceleration
imu = np.array([a_abs @ er, a_abs @ ep])

# ---------------------------------------------------------------- Example 10.6.2
Omd, ar = 0.2, 0.3
# the state at t1 is that of Example 10.6.1 (ψ1, Ω, ρ1 = 1.0 m, v_rel = 0.4 m/s); now Ω̇ = 0.2 rad/s² and the AGV accelerates along the radius at 0.3 m/s²


def f2(t):
    tau = t - t1
    psi = psi1 + Om * tau + 0.5 * Omd * tau * tau
    rho = rho1 + vr * tau + 0.5 * ar * tau * tau
    return rotz(psi) @ np.array([rho, 0, 0])


R2 = R
r2 = r_s
a_euler = np.cross(Omd * z, r2)
a_cent2 = np.cross(Om_s, np.cross(Om_s, r2))
a_C2 = 2 * np.cross(Om_s, R2 @ np.array([vr, 0, 0]))
a_rel2 = R2 @ np.array([ar, 0, 0])
a_abs2 = a_rel2 + a_euler + a_cent2 + a_C2
assert np.allclose(d2(f2, t1, 1e-3), a_abs2, atol=1e-6)
er2, ep2 = R2 @ np.array([1.0, 0, 0]), R2 @ np.array([0, 1.0, 0])
imu2 = np.array([a_abs2 @ er2, a_abs2 @ ep2])

# ---------------------------------------------------------------- Example 10.6.3
w_E = 2 * math.pi / 86164.0905             # rotation rate of the Earth relative to the stars, rad/s (sidereal day 86164.0905 s)
lat = math.radians(31.2)
v_n = 1.0
aC_h = 2 * w_E * v_n * math.sin(lat)       # magnitude of the horizontal component (a_C points west)
aC_v = 2 * w_E * v_n * 0.0                 # vertical component is 0 when moving north
# in local (east, north, up) coordinates: Ω = ω_E (0, cos λ, sin λ), v = (0, 1, 0)
Om_E = w_E * np.array([0, math.cos(lat), math.sin(lat)])
aC_vec = -2 * np.cross(Om_E, np.array([0, v_n, 0]))  # deflection seen when there is no sideways force = −a_C (see Section 10.6.8)
assert abs(abs(aC_vec[0]) - aC_h) < 1e-18 and abs(aC_vec[2]) < 1e-18

out(Om=Om, vr=vr, t1=t1, rho1=rho1, psi1_deg=math.degrees(psi1),
    v_tr=float(np.linalg.norm(v_tr)), v_abs=float(np.linalg.norm(v_abs)),
    a_tr=float(np.linalg.norm(a_tr)), a_C=float(np.linalg.norm(a_C)), a_abs=float(np.linalg.norm(a_abs)),
    a_ang=math.degrees(math.atan2(imu[1], -imu[0])),
    imu_x=imu[0], imu_y=imu[1],
    Omd=Omd, ar=ar, a_euler=float(np.linalg.norm(a_euler)), imu2_x=imu2[0], imu2_y=imu2[1],
    a_abs2=float(np.linalg.norm(a_abs2)),
    w_E=w_E, lat_deg=31.2, aC_h=aC_h, aC_h_g=aC_h / 9.81, aC_h_um=aC_h * 1e6)
