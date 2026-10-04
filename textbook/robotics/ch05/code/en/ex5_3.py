"""Examples 5.3.1–5.3.3: composition and inversion of homogeneous transformations.

With the UR5e at joint angles (0°, −90°, 90°, −70°, −90°, 0°), the controller gives the pose T_sb of the flange frame {b}
(computed here with the product of exponentials formula of Chapter 12 and checked one by one against the 3D model in the
parts library). The tool frame {t} of the gripper relative to {b} is T_bt.
5.3.1 Composition: T_st = T_sb T_bt, compared with the point-by-point method "first write the origin and the three axes
      of {t} in {b}, then convert them to {s}".
5.3.2 Inversion: T_ts by Theorem 5.3.2, compared with general matrix inversion; check that T_st T_ts = I.
5.3.3 Premultiplication and postmultiplication: 20 mm forward along the tool's own z axis vs 20 mm down along the base
      z axis; 90° about the tool z axis vs 90° about the base z axis.
"""
import math

import numpy as np

from _frames import DEG, T, T_bt, clean, hom, inv, is_se3, rot_z, texm, trans, ur_fk_glb, ur_fk_poe, vecm
from bookout import out

theta = np.array([0, -90, 90, -70, -90, 0]) * DEG
Tsb = ur_fk_poe(theta)
assert np.allclose(Tsb, ur_fk_glb(theta), atol=1e-12)      # agrees with the algorithm of the web 3D model
Tbt = T_bt()

# ---------------------------------------------------------------- Example 5.3.1 composition
Tst = Tsb @ Tbt
# point by point: the origin and three axes of {t} are first written in {b}, then converted to {s} with T_sb
# (the origin as a point, the axes as free vectors)
o_s = (Tsb @ hom(Tbt[:3, 3]))[:3]
axes_s = Tsb[:3, :3] @ Tbt[:3, :3]
assert np.allclose(o_s, Tst[:3, 3]) and np.allclose(axes_s, Tst[:3, :3])
assert is_se3(Tst)
# the order cannot be swapped
assert not np.allclose(Tbt @ Tsb, Tst)
wrong = Tbt @ Tsb

# ---------------------------------------------------------------- Example 5.3.2 inversion
Tts = inv(Tst)
Tts_num = np.linalg.inv(Tst)
assert np.allclose(Tts, Tts_num, atol=1e-14)
assert np.allclose(Tst @ Tts, np.eye(4), atol=1e-15) and np.allclose(Tts @ Tst, np.eye(4), atol=1e-15)
neg_p = -Tst[:3, 3]                                     # common mistake: only negating p
assert np.linalg.norm(neg_p - Tts[:3, 3]) > 0.1
# convert a point from {s} to {t} and back
q_s = np.array([-0.45, -0.10, 0.02])                    # a feature point of a part on the table (in {s})
q_t = (Tts @ hom(q_s))[:3]
assert np.allclose((Tst @ hom(q_t))[:3], q_s)

# ---------------------------------------------------------------- Example 5.3.3 premultiplication and postmultiplication
step = 0.02
Tst_A = Tst @ trans(0, 0, step)          # 20 mm forward along the z axis of {t} itself (postmultiply)
Tst_B = trans(0, 0, -step) @ Tst         # 20 mm down along the z axis of {s} (premultiply)
dA = Tst_A[:3, 3] - Tst[:3, 3]
dB = Tst_B[:3, 3] - Tst[:3, 3]
assert np.allclose(dA, step * Tst[:3, 2]) and np.allclose(dB, [0, 0, -step])
tilt = math.degrees(math.acos(-Tst[2, 2]))                # angle of the tool z axis from the vertical downward direction
gap = np.linalg.norm(dA - dB)

Rz90 = T(rot_z(math.pi / 2))
Tst_C = Tst @ Rz90                        # 90° about the tool's own z axis (postmultiply): the TCP does not move
Tst_D = Rz90 @ Tst                        # 90° about the base z axis (premultiply): the TCP swings 90° about the base vertical axis
assert np.allclose(Tst_C[:3, 3], Tst[:3, 3])
swing = np.linalg.norm(Tst_D[:3, 3] - Tst[:3, 3])
r_axis = math.hypot(Tst[0, 3], Tst[1, 3])
assert abs(swing - math.sqrt(2) * r_axis) < 1e-12        # chord = √2 × distance to the z_s axis
# Are the orientations after the two rotations the same? Only if the tool z axis is parallel to z_s; here it is not
assert not np.allclose(Tst_C[:3, :3], Tst_D[:3, :3])

out(
    Tsb=texm(clean(Tsb), 4), Tbt=texm(clean(Tbt), 2), Tst=texm(clean(Tst), 4), wrong=texm(clean(wrong), 4),
    Tts=texm(clean(Tts), 4), pst=vecm(Tst[:3, 3], 4), pts=vecm(Tts[:3, 3], 4), negp=vecm(neg_p, 4),
    pst_norm=np.linalg.norm(Tst[:3, 3]), pts_norm=np.linalg.norm(Tts[:3, 3]),
    qt=vecm(q_t, 4), dA=vecm(dA, 4), dB=vecm(dB, 4), tilt=tilt, gap_mm=gap * 1000,
    pD=vecm(Tst_D[:3, 3], 4), swing=swing, r_axis=r_axis,
    zt=vecm(clean(Tst[:3, 2]), 4),
)
