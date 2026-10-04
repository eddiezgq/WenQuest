"""Examples 5.4.1 and 5.4.2: the frame tree.

5.4.1 The UR5e itself is a chain of frames: for each link the model file records T_parent,child(θ) = Trans(xyz)·Rot_rpy·Rot(axis, θ).
      At the joint angles θ_A = (0°, −90°, 90°, −90°, −90°, 0°), multiplying along the chain gives the flange pose T_sb,
      checked by three mutually independent algorithms:
      (1) the numbers in the model's joint table entry.json (rpy written as 1.570796, rounded); (2) the node matrices of
      the web 3D model default.glb; (3) the product of exponentials formula of Chapter 12. Also explains why (1) differs
      from the other two by less than 10⁻⁶ (rotation matrix entries) and by about 10⁻⁷ m (flange position).
5.4.2 The frame tree of the workstation (root: the worktable {w}): find the pose T_ct of the tool as seen by the camera.
      (1) the general tree path algorithm; (2) the hand-written chain T_cw T_ws T_sb T_bt. Then the loop check T_wc T_ct T_tw = I.
      When joint 1 turns, only the subtree below joint 1 moves: T_wc is unchanged, T_ct changes.
"""
import math

import numpy as np

from _frames import (DEG, FrameTree, T, T_bt, T_wc, T_ws, UR_LINKS, clean, inv, rot_z, texm, ur_edges_from_table, ur_entry,
                     ur_fk_glb, ur_fk_poe, ur_fk_table, vecm)
from bookout import T as TT, out

thA = np.array([0, -90, 90, -90, -90, 0]) * DEG

# ---------------------------------------------------------------- Example 5.4.1
edges = ur_edges_from_table(thA)
T1, T2, T3 = ur_fk_table(thA), ur_fk_glb(thA), ur_fk_poe(thA)
d12, d23 = np.abs(T1 - T2).max(), np.abs(T2 - T3).max()
d12_p = np.linalg.norm(T1[:3, 3] - T2[:3, 3])                       # position difference, m
d12_R = np.abs(T1[:3, :3] - T2[:3, :3]).max()                      # orientation difference (rotation matrix entries), dimensionless
assert d23 < 1e-12            # web model and product of exponentials: identical (up to rounding)
assert d12 < 1e-6             # joint table: 1.570796 differs from π/2 by 3.3e-7 rad, times an arm length of about 1 m
rpy_file = ur_entry()["robot"]["joints"][1]["origin"]["rpy"][1]          # π/2 as recorded in the model file
rpy_err = abs(rpy_file - math.pi / 2)

# the position part of each edge (link offsets at the zero position) listed as Table 5.4.1
names = ["base"] + UR_LINKS + ["b"]
labels = [TT("基座连杆", "base link")] + [TT(f"连杆 {i}", f"link {i}") for i in range(1, 7)] + [TT("法兰 {b}", "flange {b}")]
rows = []
for (child, parent, Tm), lab in zip(edges, labels):
    rows.append(f"{lab} & {vecm(clean(Tm[:3, 3]), 3)}")

# position of each link frame origin in {s} (used by Figure 5.4.2)
M = np.eye(4)
origins = []
for _, _, Tm in edges:
    M = M @ Tm
    origins.append(M[:3, 3].copy())
assert np.allclose(M, T1)

# ---------------------------------------------------------------- Example 5.4.2 the frame tree of the workstation
tree = FrameTree("w")
tree.add("s", "w", T_ws())
for child, parent, Tm in edges:
    tree.add(child, parent, Tm)
tree.add("t", "b", T_bt())
tree.add("c", "w", T_wc())

Tct = tree.T("c", "t")
Tct_hand = inv(T_wc()) @ T_ws() @ T3 @ T_bt()
assert np.allclose(Tct, Tct_hand, atol=1e-6)
path = tree.path("c", "t")
n_up = sum(1 for _, _, d in path if d == "up")
n_down = len(path) - n_up
loop = T_wc() @ Tct @ tree.T("t", "w")
assert np.allclose(loop, np.eye(4), atol=1e-14)
Twt = tree.T_root("t")
assert np.allclose(Twt, tree.T("w", "t"), atol=1e-14)

# turn joint 1: only the subtree below it moves
before_wc, before_ct = tree.T("w", "c"), Tct.copy()
th2 = thA.copy()
th2[0] = 30 * DEG
for child, parent, Tm in ur_edges_from_table(th2):
    tree.set(child, Tm)
assert np.allclose(tree.T("w", "c"), before_wc)
assert not np.allclose(tree.T("c", "t"), before_ct)
assert np.allclose(tree.T("w", "s"), T_ws())

out(
    TsbA=texm(clean(T3), 4), d12=d12, d12_p=d12_p, d12_R=d12_R, d23=d23, rpy_err=rpy_err, rpy_file=rpy_file, rows=r" \\ ".join(rows),
    Tct=texm(clean(Tct), 4), pct=vecm(Tct[:3, 3], 4), dist_ct=np.linalg.norm(Tct[:3, 3]),
    n_up=n_up, n_down=n_down, n_edges=len(path),
    Twt=texm(clean(Twt), 4), pwt=vecm(Twt[:3, 3], 4),
    origins=[o.tolist() for o in origins],
)
