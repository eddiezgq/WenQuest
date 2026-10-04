"""Examples 10.4.1, 10.4.2: spherical coordinates and a pan-tilt gimbal camera.

Gimbal frame {g}: origin at the optical centre of the camera (the intersection of the two axes), z vertically up; the
camera is mounted on the workshop ceiling, H = 3.0 m above the floor.
The AGV runs steadily along the line x = v t, y = d, z = −H, with v = 1.0 m/s and d = 0.5 m (the horizontal distance
of the line from the point directly below the camera).
Example 10.4.1: the spherical coordinates (r, θ, φ) of the target at t = −1 s; ṙ, θ̇, φ̇ from the velocity by
  Eq. (10.4.12); the three velocity components by Eq. (10.4.8); the terms of the acceleration by Eqs. (10.4.9)-(10.4.11),
  checking that they add up to zero (the AGV moves uniformly in a straight line). Checked by numerical differentiation.
Example 10.4.2: over the whole pass, the largest pan rate |φ̇|max = v/d and the largest angular acceleration
  3√3 v²/(8d²); the lower bound on d when the gimbal's pan rate is limited to 90°/s.
"""
import math

import numpy as np

from _kin import d1, d2, sph_basis, to_sph
from bookout import out

H, v, d = 3.0, 1.0, 0.5


def target(t):
    return np.array([v * t, d, -H])


def sph(t):
    return np.array(to_sph(target(t)))


t1 = -1.0
p = target(t1)
vel = np.array([v, 0.0, 0.0])
r, th, ph = to_sph(p)
er, et, ep = sph_basis(th, ph)
# Eq. (10.4.12): rates of the spherical coordinates from the velocity
rdot = er @ vel
thdot = (et @ vel) / r
phdot = (ep @ vel) / (r * math.sin(th))
num = d1(sph, t1, 1e-5)
assert np.allclose(num, [rdot, thdot, phdot], atol=1e-8)
# second derivatives (numerical)
rdd, thdd, phdd = d2(sph, t1, 2e-3)
# analytic: φ = atan2(d, vt), φ̇ = −v d/(v²t² + d²), φ̈ = 2 v³ d t/(v²t² + d²)²
assert abs(phdot - (-v * d / (v * v * t1 * t1 + d * d))) < 1e-12
phdd_an = 2 * v ** 3 * d * t1 / (v * v * t1 * t1 + d * d) ** 2
assert abs(phdd - phdd_an) < 1e-5
phdd = phdd_an
# velocity components (Eq. (10.4.8))
v_r, v_th, v_ph = rdot, r * thdot, r * math.sin(th) * phdot
assert abs(math.sqrt(v_r ** 2 + v_th ** 2 + v_ph ** 2) - v) < 1e-12
# terms of the acceleration (Eqs. (10.4.9)-(10.4.11))
s, c = math.sin(th), math.cos(th)
ar_terms = [rdd, -r * thdot ** 2, -r * s * s * phdot ** 2]
at_terms = [r * thdd, 2 * rdot * thdot, -r * s * c * phdot ** 2]
ap_terms = [r * s * phdd, 2 * rdot * phdot * s, 2 * r * thdot * phdot * c]
a_r, a_t, a_p = sum(ar_terms), sum(at_terms), sum(ap_terms)
assert max(abs(a_r), abs(a_t), abs(a_p)) < 1e-6          # the error level of numerical second derivatives; uniform straight-line motion has a = 0
# angular velocity of the gimbal, ω = φ̇ e_z + θ̇ e_φ (Eq. (10.4.6))
omega = phdot * np.array([0, 0, 1.0]) + thdot * ep

# ---------------------------------------------------------------- Example 10.4.2
ts = np.linspace(-6, 6, 120001)
phd = np.array([-v * d / (v * v * t * t + d * d) for t in ts])
thd = np.array([d1(lambda tt: to_sph(target(tt))[1], t, 1e-6) for t in ts[::100]])
phd_max = float(np.max(np.abs(phd)))
assert abs(phd_max - v / d) < 1e-9
phdd_max = 3 * math.sqrt(3) / 8 * v * v / (d * d)
t_star = d / (math.sqrt(3) * v)
assert abs(abs(2 * v ** 3 * d * t_star / (v * v * t_star ** 2 + d * d) ** 2) - phdd_max) < 1e-12
lim = math.radians(90)
d_min = v / lim

out(H=H, v=v, d=d, t1=t1, r=r, th_deg=math.degrees(th), ph_deg=math.degrees(ph), elev_deg=math.degrees(th) - 90,
    rdot=rdot, thdot=thdot, phdot=phdot, thdot_deg=math.degrees(thdot), phdot_deg=math.degrees(phdot),
    v_r=v_r, v_th=v_th, v_ph=v_ph,
    rdd=rdd, thdd=thdd, phdd=phdd,
    ar1=ar_terms[0], ar2=ar_terms[1], ar3=ar_terms[2],
    at1=at_terms[0], at2=at_terms[1], at3=at_terms[2],
    ap1=ap_terms[0], ap2=ap_terms[1], ap3=ap_terms[2],
    om_x=omega[0], om_y=omega[1], om_z=omega[2], om_mag=float(np.linalg.norm(omega)),
    phd_max=phd_max, phd_max_deg=math.degrees(phd_max), thd_max_deg=math.degrees(float(np.max(np.abs(thd)))),
    phdd_max=phdd_max, t_star=t_star, d_min=d_min,
    phd_max_d01_deg=math.degrees(v / 0.1))
