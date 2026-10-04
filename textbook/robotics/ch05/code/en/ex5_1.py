"""Examples 5.1.1 and 5.1.2: the coordinates of one point in two frames with different origins.

5.1.1 Worktable frame {w} and UR5e base frame {s}: the origin of {s} is at (0.30, 0.40, 0) m in {w}, turned 180° about z.
      The centre P of the part is at (0.80, 0.45, 0.02) m in {w}; find its coordinates in {s}.
      Method 1: Theorem 5.1.1, p_s = R_wsᵀ (p_w − p_ws); method 2: geometric reasoning axis by axis (x_s = −x_w, y_s = −y_w).
5.1.2 Workshop map {m} and AGV frame {v}: the AGV is at (12.0, 5.0) m with heading 30°. Shelf station Q is at (14.5, 8.0) m.
      Method 1: Theorem 5.1.1; method 2: first find the distance and the bearing, then subtract the heading (polar coordinates).
The two methods must agree; also check that the distance to an origin and the distance between two points do not depend
on the frame, and that a free vector is transformed by R alone.
"""
import math

import numpy as np

from _frames import rot_z
from bookout import out

# ---------------------------------------------------------------- Example 5.1.1
p_ws = np.array([0.30, 0.40, 0.0])          # origin of {s} in {w}, m
R_ws = rot_z(math.pi)                        # {s} turned 180° about z relative to {w}
p_w = np.array([0.80, 0.45, 0.02])          # centre P of the part in {w}, m

p_s = R_ws.T @ (p_w - p_ws)                  # p_s solved from Theorem 5.1.1
d = p_w - p_ws
p_s_geo = np.array([-d[0], -d[1], d[2]])     # x_s opposite to x_w, y_s opposite to y_w, z the same
assert np.allclose(p_s, p_s_geo, atol=1e-15)
assert np.allclose(p_ws + R_ws @ p_s, p_w)   # substitute back into Eq. (5.1.2)

# A position vector depends on the origin: |O_w P| differs from |O_s P|; but the distance from O_s to P comes out the same in both frames
dist_s = np.linalg.norm(p_s)
dist_s_from_w = np.linalg.norm(p_w - p_ws)
assert abs(dist_s - dist_s_from_w) < 1e-15
dist_w = np.linalg.norm(p_w)

# A second point: the locating pin Q on the tray is at (0.80, 0.25, 0.02) m in {w}; the distance between two points does not depend on the frame
q_w = np.array([0.80, 0.25, 0.02])
q_s = R_ws.T @ (q_w - p_ws)
assert abs(np.linalg.norm(p_w - q_w) - np.linalg.norm(p_s - q_s)) < 1e-15

# ---------------------------------------------------------------- Example 5.1.2 (planar)
p_mv = np.array([12.0, 5.0])                 # origin of the AGV frame {v} in the map {m}, m
psi = math.radians(30)                       # heading: x_v turned 30° anticlockwise from x_m
c, s = math.cos(psi), math.sin(psi)
R_mv = np.array([[c, -s], [s, c]])
q_m = np.array([14.5, 8.0])                  # shelf station Q in {m}

q_v = R_mv.T @ (q_m - p_mv)                  # method 1
dq = q_m - p_mv
rng = math.hypot(*dq)                        # method 2: distance and bearing
bearing_m = math.atan2(dq[1], dq[0])         # bearing as seen on the map
bearing_v = bearing_m - psi                  # bearing relative to the front of the AGV
q_v_polar = rng * np.array([math.cos(bearing_v), math.sin(bearing_v)])
assert np.allclose(q_v, q_v_polar, atol=1e-13)

# Free vector: the AGV drives forward at 1.0 m/s; the velocity in {m} is R_mv (1, 0), and converting it back to {v} uses R only, with no origin subtracted
v_v = np.array([1.0, 0.0])
v_m = R_mv @ v_v
assert np.allclose(R_mv.T @ v_m, v_v)
wrong = R_mv.T @ (v_m - p_mv)               # treating the velocity as a point by mistake gives an absurd result
assert np.linalg.norm(wrong) > 10

out(
    ps_x=p_s[0], ps_y=p_s[1], ps_z=p_s[2], dx=d[0], dy=d[1],
    dist_s=dist_s, dist_w=dist_w, qs_x=q_s[0], qs_y=q_s[1], dist_pq=np.linalg.norm(p_w - q_w),
    c30=c, s30=s, qv_x=q_v[0], qv_y=q_v[1], rng=rng,
    bear_m_deg=math.degrees(bearing_m), bear_v_deg=math.degrees(bearing_v),
    vm_x=v_m[0], vm_y=v_m[1], wrong_x=wrong[0], wrong_y=wrong[1],
)
