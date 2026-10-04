"""Example 1.3.1: the workspaces of a SCARA and a UR5e. Both are "robot arms", but with different structures they
reach regions of entirely different shapes.

SCARA (parts library B-SCA-WQ4): two horizontal arms a1, a2 turn about vertical axes; the joint limits come from the
model. The area the end can reach in the horizontal plane is computed in two ways:
  (1) grid + inverse solution: for each grid point, the inverse solution of the planar two-link arm decides whether a
      set of joint angles lies within the limits;
  (2) random joint angles: the end is computed by forward kinematics and the grid squares hit are counted.
The two must differ by less than 2%. The vertical stroke times the area gives the volume of the workspace.
UR5e (B-ARM-UR5E): every joint can turn ±360°; random joint angles give the largest distance from the flange centre
to the shoulder centre.
"""
import math

import numpy as np

from _ch1 import ALL8, dof_summary, entry, fk_point
from bookout import out

rng = np.random.default_rng(13)

# ---------------------------------------------------------------- SCARA
sc = entry("B-SCA-WQ4")
J = {j["name"]: j for j in sc["robot"]["joints"]}
a1 = J["J2"]["origin"]["xyz"][0]               # 0.35 m: joint 1 to joint 2
a2 = J["J3"]["origin"]["xyz"][0]               # 0.25 m: joint 2 to the lead screw
t1lo, t1hi = J["J1"]["limit"]["lower"], J["J1"]["limit"]["upper"]
t2lo, t2hi = J["J2"]["limit"]["lower"], J["J2"]["limit"]["upper"]
stroke = J["J3"]["limit"]["upper"] - J["J3"]["limit"]["lower"]
r_max = a1 + a2
r_min = math.sqrt(a1 ** 2 + a2 ** 2 + 2 * a1 * a2 * math.cos(t2hi))   # nearest to the axis with joint 2 at its limit


def reachable(x, y):
    """Inverse solution of the planar two-link arm: reachable if one set (θ1, θ2) lies within the limits."""
    r2 = x * x + y * y
    c2 = (r2 - a1 * a1 - a2 * a2) / (2 * a1 * a2)
    if c2 > 1 or c2 < math.cos(t2hi):
        return False
    for t2 in (math.acos(c2), -math.acos(c2)):
        t1 = math.atan2(y, x) - math.atan2(a2 * math.sin(t2), a1 + a2 * math.cos(t2))
        t1 = (t1 + math.pi) % (2 * math.pi) - math.pi
        if t1lo <= t1 <= t1hi and t2lo <= t2 <= t2hi:
            return True
    return False


h = 0.005                                       # grid spacing 5 mm
xs = np.arange(-r_max - h, r_max + h, h) + h / 2
grid = np.array([[reachable(x, y) for x in xs] for y in xs])
area_grid = grid.sum() * h * h

N = 400000
th1 = rng.uniform(t1lo, t1hi, N)
th2 = rng.uniform(t2lo, t2hi, N)
px = a1 * np.cos(th1) + a2 * np.cos(th1 + th2)
py = a1 * np.sin(th1) + a2 * np.sin(th1 + th2)
ix = np.floor((px - xs[0] + h / 2) / h).astype(int)
iy = np.floor((py - xs[0] + h / 2) / h).astype(int)
hit = np.zeros_like(grid)
hit[iy, ix] = True
area_mc = hit.sum() * h * h
assert abs(area_mc - area_grid) / area_grid < 0.02          # the two methods agree
# check one point with the model's forward kinematics: both kinematics (the hand-written two-link arm and the
# model's joint table) give the same end point
q = {"J1": 0.4, "J2": -0.9, "J3": 0.05, "J4": 0.0}
p_model = fk_point(sc, q, "tool")
p_hand = (a1 * math.cos(0.4) + a2 * math.cos(0.4 - 0.9), a1 * math.sin(0.4) + a2 * math.sin(0.4 - 0.9))
assert abs(p_model[0] - p_hand[0]) < 1e-9 and abs(p_model[1] - p_hand[1]) < 1e-9
annulus = math.pi * (r_max ** 2 - r_min ** 2)
vol_sc = area_grid * stroke

# ---------------------------------------------------------------- UR5e
ur = entry("B-ARM-UR5E")
names = [j["name"] for j in ur["robot"]["joints"]]
shoulder = fk_point(ur, {}, "upper_arm_link")            # a point on the shoulder (joint 2) axis
M = 20000
d_sh = []
for _ in range(M):
    qq = dict(zip(names, rng.uniform(-math.pi, math.pi, 6)))
    d_sh.append(np.linalg.norm(fk_point(ur, qq, "wrist_3_link", (0, 0.1, 0)) - shoulder))
d_sh = np.array(d_sh)
d_sh_max = d_sh.max()
out_pct = float((d_sh > 0.85).mean() * 100)          # share of samples farther than the 0.85 m datasheet reach
# upper bound: the sum of the lengths of the relative offsets from shoulder to flange (triangle inequality); the
# actual distance cannot exceed it
segs = [j["origin"]["xyz"] for j in ur["robot"]["joints"][2:]] + [(0, 0.1, 0)]
bound = sum(float(np.linalg.norm(s_)) for s_ in segs)
assert d_sh_max <= bound + 1e-9
vol_ur = 4 / 3 * math.pi * 0.85 ** 3                      # sphere whose radius is the 0.85 m datasheet reach

# ---------------------------------------------------------------- classes of the eight models
rows = [dof_summary(e) for e in ALL8]
n_fixed = sum(r["base"] == "fixed" for r in rows)
n_mobile = len(rows) - n_fixed

out(a1=a1, a2=a2, t1_deg=math.degrees(t1hi), t2_deg=math.degrees(t2hi), stroke=stroke, r_max=r_max, r_min=r_min,
    area_grid=area_grid, area_mc=area_mc, area_diff_pct=abs(area_mc - area_grid) / area_grid * 100, annulus=annulus,
    vol_sc=vol_sc, d_sh_max=d_sh_max, out_pct=out_pct, bound=bound, vol_ur=vol_ur, vol_ratio=vol_ur / vol_sc, N=N, M=M,
    n_fixed=n_fixed, n_mobile=n_mobile)
