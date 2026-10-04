"""Examples 10.2.1 and 10.2.2: position, velocity and acceleration in Cartesian coordinates.

Example 10.2.1: a SCARA dispenses sealant; the tool tip moves on the ellipse x = xc + a cos ωt, y = yc + b sin ωt, z = z0
  ({s} is the SCARA base frame). The velocity and acceleration at t = 0.5 s are found from Eq. (10.2.10) and checked by
  numerically differentiating the positions with the central difference quotients (10.2.11); the largest and smallest
  speeds over one loop are found; we check that the acceleration always points to the centre, a = −ω²(r − r_c).
Example 10.2.2: the gripper releases a part while moving horizontally at 0.6 m/s; the part falls 0.25 m into a tote.
  The landing point is found by integrating a = (0, 0, −g) twice, and checked by numerical integration with the
  classical fourth-order Runge–Kutta method (7.2.6).
"""
import math

import numpy as np

from _kin import d1, d2
from bookout import out

# ---------------------------------------------------------------- Example 10.2.1
xc, yc, z0 = 0.40, 0.05, 0.10           # centre and height of the ellipse, m
a, b = 0.12, 0.08                       # semi-major and semi-minor axes, m
Tp = 4.0                                # time for one loop, s
w = 2 * math.pi / Tp                    # rad/s


def r(t):
    return np.array([xc + a * math.cos(w * t), yc + b * math.sin(w * t), z0])


def v(t):                               # Eq. (10.2.10): differentiate each component
    return np.array([-a * w * math.sin(w * t), b * w * math.cos(w * t), 0.0])


def acc(t):                             # Eq. (10.2.10)
    return np.array([-a * w * w * math.cos(w * t), -b * w * w * math.sin(w * t), 0.0])


t1 = 0.5
r1, v1, a1 = r(t1), v(t1), acc(t1)
v_num = d1(r, t1, 1e-3)                 # sampling interval of 1 ms
a_num = d2(r, t1, 1e-3)
assert np.allclose(v_num, v1, atol=1e-6) and np.allclose(a_num, a1, atol=1e-5)
err_v = float(np.max(np.abs(v_num - v1)))
err_a = float(np.max(np.abs(a_num - a1)))
for t in np.linspace(0, Tp, 41):        # the acceleration points to the centre
    assert np.allclose(acc(t), -w * w * (r(t) - np.array([xc, yc, z0])), atol=1e-14)
speeds = [np.linalg.norm(v(t)) for t in np.linspace(0, Tp, 4001)]
vmax, vmin = max(speeds), min(speeds)
assert abs(vmax - a * w) < 1e-9 and abs(vmin - b * w) < 1e-9
amax = a * w * w
# angle between velocity and acceleration (speeding up or slowing down at this instant)
cosang = float(v1 @ a1 / np.linalg.norm(v1) / np.linalg.norm(a1))
dspeed = float(v1 @ a1 / np.linalg.norm(v1))      # rate of change of the speed, d|v|/dt = v·a/|v|
assert abs(dspeed - d1(lambda t: np.linalg.norm(v(t)), t1, 1e-5)) < 1e-8

# ---------------------------------------------------------------- Example 10.2.2
g = 9.81
vx0, h = 0.6, 0.25                      # horizontal velocity at release m/s, height of fall m
t_land = math.sqrt(2 * h / g)
x_land = vx0 * t_land
vz_land = -g * t_land


def f(t, s):                            # state s = (x, z, ẋ, ż), ṡ = (ẋ, ż, 0, −g)
    return np.array([s[2], s[3], 0.0, -g])


def rk4(s, t, hstep):
    k1 = f(t, s)
    k2 = f(t + hstep / 2, s + hstep / 2 * k1)
    k3 = f(t + hstep / 2, s + hstep / 2 * k2)
    k4 = f(t + hstep, s + hstep * k3)
    return s + hstep / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


N = 100
s = np.array([0.0, h, vx0, 0.0])
for k in range(N):
    s = rk4(s, k * t_land / N, t_land / N)
assert abs(s[0] - x_land) < 1e-12 and abs(s[1]) < 1e-12 and abs(s[3] - vz_land) < 1e-12

out(xc=xc, yc=yc, z0=z0, a=a, b=b, Tp=Tp, w=w, t1=t1,
    x1=r1[0], y1=r1[1], vx1=v1[0], vy1=v1[1], ax1=a1[0], ay1=a1[1],
    speed1=float(np.linalg.norm(v1)), acc1=float(np.linalg.norm(a1)),
    err_v=err_v, err_a=err_a, vmax=vmax, vmin=vmin, amax=amax, amin=b * w * w,
    ang_va=math.degrees(math.acos(cosang)), dspeed=dspeed,
    g=g, vx0=vx0, h=h, t_land=t_land, x_land=x_land, x_land_mm=x_land * 1000, vz_land=vz_land,
    v_land=math.hypot(vx0, vz_land))
