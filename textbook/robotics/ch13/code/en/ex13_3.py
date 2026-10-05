"""Examples 13.3.1, 13.3.2 and Section 13.3.3: reading the standard DH parameter table of the UR5e published by Universal Robots.

Data: dh.params of the parts-library entry B-ARM-UR5E, copied from the UR5e column (a, d, α) of the Universal Robots
technical-support article "DH parameters for calculations of kinematics and dynamics".
13.3.1 Zero position: centre and orientation of the flange computed from the manufacturer's table.
13.3.2 Joint angles of Example 12.3.1: the end-effector from the manufacturer's table compared with Chapter 12 (product of
       exponentials, parts-library dimensions); the two end-effector frames differ only by Rot(x, 90°).
13.3.3 The DH table with the model dimensions compared item by item with the manufacturer's table: the maximum and mean of
       the difference reproduced with the same random joint angles as Program 12.3.1 of Chapter 12; then one parameter
       at a time is changed, to see how much each item contributes.
Also: the manufacturer's table rewritten in the "strict" form with a >= 0 (θ with offsets) and in Craig's modified DH form,
with a check that all three give the same end-effector.
"""
import math

import numpy as np

from _dh import Rx, clean, fk_mdh, fk_sdh, fk_space, inv, lines_to_sdh, ur_poe, ur_vendor, ur_vendor_raw
from bookout import out, tex, vec

pi = math.pi
vend = ur_vendor()                                   # [(a, α, d, θ offset)]
tab, S, M = ur_poe()
axes = [("R", np.asarray(w, float), np.asarray(q, float)) for w, q in tab]
model, F = lines_to_sdh(axes, M[:3, 3])               # DH table with the parts-library dimensions (the same as Example 13.2.2)
T6b = inv(F[-1]) @ M
assert np.allclose(T6b, Rx(pi / 2), atol=1e-12)

# ---------------------------------------------------------------- 13.3.1 zero position
T0 = fk_sdh(vend, np.zeros(6))
gap0 = float(np.linalg.norm(T0[:3, 3] - M[:3, 3])) * 1000     # difference from the flange centre at the zero position in Chapter 12 (mm)
assert 1.0 < gap0 < 1.2

# size of the orientation residual if α is the truncated seven-decimal value (as stored in the parts-library entry)
vraw = [(a, al, d, 0.0) for a, d, al in ur_vendor_raw()]
alpha_raw = vraw[0][1]
raw_err = float(np.abs(fk_sdh(vraw, np.radians([30.0, -60.0, 90.0, -120.0, -90.0, 45.0]))[:3, :3]
                       - fk_sdh(vend, np.radians([30.0, -60.0, 90.0, -120.0, -90.0, 45.0]))[:3, :3]).max())
assert 1e-9 < raw_err < 1e-6

# ---------------------------------------------------------------- 13.3.2 Example 12.3.1
q_ex = np.radians([30.0, -60.0, 90.0, -120.0, -90.0, 45.0])
Tv = fk_sdh(vend, q_ex)
Tp = fk_space(S, M, q_ex)                             # the result of Example 12.3.1 in Chapter 12
gap_ex = float(np.linalg.norm(Tv[:3, 3] - Tp[:3, 3])) * 1000
assert np.allclose(Tv[:3, :3] @ Rx(pi / 2)[:3, :3], Tp[:3, :3], atol=1e-3)   # orientation: differs only by Rot(x, 90°) (and tiny differences due to the parameters)
rot_err = float(np.abs(Tv[:3, :3] @ Rx(pi / 2)[:3, :3] - Tp[:3, :3]).max())

# ---------------------------------------------------------------- 13.3.3 model table and manufacturer's table
N = 10000
rng = np.random.default_rng(12)                       # the same random sequence as Program 12.3.1
for _ in range(N):
    rng.uniform(-pi, pi, 6)                           # Program 12.3.1 first checks the model with ten thousand sets of joint angles
Q = np.array([rng.uniform(-pi, pi, 6) for _ in range(N)])   # then the next ten thousand compare the manufacturer's DH
gaps = np.array([np.linalg.norm(fk_sdh(vend, q)[:3, 3] - fk_space(S, M, q)[:3, 3]) for q in Q]) * 1000
err_model = max(float(np.abs(fk_sdh(model, q) @ T6b - fk_space(S, M, q)).max()) for q in Q[:2000])
assert err_model < 1e-9

# item by item: change only one parameter from the model value to the manufacturer's value
names = [("d", 0, 2, "d_1"), ("a", 1, 0, "a_2"), ("a", 2, 0, "a_3"), ("d", 3, 2, "d_4"), ("d", 4, 2, "d_5"), ("d", 5, 2, "d_6")]
contrib, diffs = [], []
for kind, row, col, label in names:
    t = [list(r) for r in model]
    t[row][col] = vend[row][col]
    diffs.append((vend[row][col] - model[row][col]) * 1000)
    contrib.append(max(np.linalg.norm(fk_sdh(t, q)[:3, 3] - fk_sdh(model, q)[:3, 3]) for q in Q[:2000]) * 1000)
for (a1, al1, d1, _), (a2, al2, d2, _) in zip(model, vend):
    assert abs(al1 - al2) < 1e-6                      # same twist angles: the whole difference is in the lengths

# rows of Table 13.3.3
rows_cmp = []
for (kind, row, col, label), dmm, c in zip(names, diffs, contrib):
    dtxt = "0" if abs(dmm) < 0.05 else f"{dmm:+.1f}"
    rows_cmp.append(f"{label} & {model[row][col]:.3f} & {vend[row][col]:.4f} & {dtxt} & {c:.2f}")
rows_cmp = r" \\ ".join(rows_cmp)

# ---------------------------------------------------------------- the two other forms
strict = [list(r) for r in vend]                      # x_2, x_3 reversed: a positive, π appears in the θ offsets
strict[1][0], strict[1][3] = -strict[1][0], strict[1][3] + pi
strict[2][3] += pi
strict[2][0], strict[2][3] = -strict[2][0], strict[2][3] + pi
strict[3][3] += pi
craig = [((vend[i - 1][0], vend[i - 1][1]) if i else (0.0, 0.0)) + (vend[i][2], 0.0) for i in range(6)]
for q in Q[:500]:
    A = fk_sdh(vend, q)
    assert np.allclose(fk_sdh(strict, q), A, atol=1e-12)
    assert np.allclose(fk_mdh(craig, q), A, atol=1e-12)       # last row a_6 = α_6 = 0, so X_6 = I


def angle_s(x):
    k = round(x / (pi / 2))
    assert abs(x - k * pi / 2) < 1e-6
    return {0: "0", 1: r"\pi/2", -1: r"-\pi/2", 2: r"\pi", -2: r"-\pi", 4: r"2\pi"}[k]


def num_s(x, n=4):
    return "0" if abs(x) < 1e-12 else f"{x:.{n}f}".rstrip("0").rstrip(".")


def theta_s(i, off):
    off = (off + pi) % (2 * pi) - pi
    return rf"\theta_{i}" if abs(off) < 1e-9 else rf"\theta_{i} + {angle_s(abs(off))}"


v_rows = r" \\ ".join(f"{i} & {theta_s(i, th)} & {num_s(a)} & {num_s(d)} & {angle_s(al)}" for i, (a, al, d, th) in enumerate(vend, 1))
s_rows = r" \\ ".join(f"{i} & {theta_s(i, th)} & {num_s(a)} & {num_s(d)} & {angle_s(al)}" for i, (a, al, d, th) in enumerate(strict, 1))
c_rows = r" \\ ".join(f"{i} & {num_s(a)} & {angle_s(al)} & {num_s(d)} & \\theta_{i}" for i, (a, al, d, th) in enumerate(craig, 1))

out(alpha_raw=alpha_raw, raw_err=raw_err, gap0=gap0, v_d1=vend[0][2], v_a2=vend[1][0], v_a3=vend[2][0], v_d4=vend[3][2], v_d5=vend[4][2], v_d6=vend[5][2],
    v_rows=v_rows, s_rows=s_rows, c_rows=c_rows,
    T0=tex(clean(T0, 1e-12), 4), p0=vec(T0[:3, 3], 4),
    Tv=tex(clean(Tv, 1e-12), 4), pv=vec(Tv[:3, 3], 4), pp=vec(Tp[:3, 3], 4), gap_ex=gap_ex, rot_err=rot_err,
    N=N, gap_max=gaps.max(), gap_mean=gaps.mean(), gap_min=gaps.min(), err_model=err_model,
    rows_cmp=rows_cmp, contrib=[float(c) for c in contrib], diffs=[float(d) for d in diffs], big=float(max(contrib)),
    sum_abs=float(sum(abs(d) for d in diffs)))
