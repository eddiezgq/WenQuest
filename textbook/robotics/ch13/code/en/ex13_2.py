"""Examples 13.2.1, 13.2.2: setting up link frames step by step.

13.2.1 SCARA (parts-library model, joint axes in Table 12.3.2): two standard DH tables, both following the rules --
       Table A by the default rule "d = 0 for parallel axes" (generated automatically by the program following the steps
       of Section 13.2.2);
       Table B by engineering habit ({1} at the height of the upper arm, {3} on the tool mounting face, the lead-screw
       variable with an offset).
       Both tables give the same end-effector pose as the product of exponentials at the joint variables of Example
       12.3.2, and are checked against the model over ten thousand random sets of joint variables.
13.2.2 UR5e (the six axes of Table 12.1.1): set up {0}…{6} by the same steps and read off the origin of each frame;
       DH forward kinematics is checked against the product of exponentials and against the parts-library model over
       ten thousand random sets of joint angles.
A numerical illustration of Theorem 13.2.1: different choices of the intermediate frames give the same T_0n.
"""
import math

import numpy as np

from _dh import Model, clean, fk_sdh, fk_space, inv, lines_to_sdh, screw_prismatic, screw_revolute, ur_poe
from bookout import out, tex, vec

rng = np.random.default_rng(132)
N = 10000

# ---------------------------------------------------------------- SCARA
sc = Model("B-SCA-WQ4", "base", "tool")
axes_sc = sc.axes()                                   # [(type, direction, point on the axis)]
Ss = [screw_prismatic(w) if k == "P" else screw_revolute(w, q) for k, w, q in axes_sc]
Ms = sc.fk(np.zeros(4))
kinds = ["R", "R", "P", "R"]
tabA, FA = lines_to_sdh(axes_sc, Ms[:3, 3])           # Table A: default rule
offA = [0.0] * 4
pi = math.pi
tabB = [(0.35, 0.0, 0.4, 0.0), (0.25, pi, 0.0, 0.0), (0.0, pi, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)]   # Table B
offB = [0.0, 0.0, 0.158, 0.0]                          # lead screw: d_3 = θ_3 + 0.158 m
q_ex = np.array([math.radians(40), math.radians(-70), 0.12, math.radians(90)])     # Example 12.3.2
T_poe = fk_space(Ss, Ms, q_ex)
TA = fk_sdh(tabA, q_ex, kinds, offA)
TB = fk_sdh(tabB, q_ex, kinds, offB)
assert np.allclose(TA, T_poe, atol=1e-12) and np.allclose(TB, T_poe, atol=1e-12)
errA = errB = 0.0
for _ in range(N):
    q = np.r_[rng.uniform(-pi, pi, 2), rng.uniform(0, 0.15), rng.uniform(-pi, pi)]
    Tm = sc.fk(q)
    errA = max(errA, float(np.abs(fk_sdh(tabA, q, kinds, offA) - Tm).max()))
    errB = max(errB, float(np.abs(fk_sdh(tabB, q, kinds, offB) - Tm).max()))
assert errA < 1e-9 and errB < 1e-9
# origins of the frames of Table B (zero position)
FB = fk_sdh(tabB, np.zeros(4), kinds, offB, frames=True)
FA0 = fk_sdh(tabA, np.zeros(4), kinds, offA, frames=True)
assert all(np.allclose(F1, F2, atol=1e-12) for F1, F2 in zip(FA, FA0))   # frames set up automatically = frames computed from Table A


def rows_tex(tab, off, kinds):
    """LaTeX rows of a DH table: (a, α, d, θ); the joint variable is written as θ_i or d_i = θ_i + offset."""
    out_rows = []
    for i, ((a, al, d, th), k, o) in enumerate(zip(tab, kinds, off), 1):
        al_s = {0: "0", 1: r"\pi", -1: r"-\pi", 0.5: r"\pi/2", -0.5: r"-\pi/2"}[round(al / pi * 2) / 2]
        if k == "R":
            th_s = rf"\theta_{i}" + ("" if abs(th) < 1e-12 else f"{th:+.4f}")
            d_s = f"{d:.3f}".rstrip("0").rstrip(".") if abs(d) > 1e-12 else "0"
        else:
            th_s = "0"
            d_s = rf"\theta_{i}" + (f" + {o + d:.3f}" if abs(o + d) > 1e-12 else "")
        a_s = f"{a:.3f}".rstrip("0").rstrip(".") if abs(a) > 1e-12 else "0"
        out_rows.append(f"{i} & {a_s} & {al_s} & {d_s} & {th_s}")
    return r" \\ ".join(out_rows)


# ---------------------------------------------------------------- UR5e
tab, S_ur, M_ur = ur_poe()
axes_ur = [("R", np.asarray(w, float), np.asarray(q, float)) for w, q in tab]
tab_ur, F_ur = lines_to_sdh(axes_ur, M_ur[:3, 3])
ur = Model("B-ARM-UR5E", "base", "wrist_3_link", (0, 0.1, 0))
T6b = inv(F_ur[-1]) @ M_ur                               # fixed transformation from {6} to the {b} of Chapter 12
err_ur_poe = err_ur_model = 0.0
for _ in range(N):
    q = rng.uniform(-pi, pi, 6)
    A = fk_sdh(tab_ur, q) @ T6b
    err_ur_poe = max(err_ur_poe, float(np.abs(A - fk_space(S_ur, M_ur, q)).max()))
    err_ur_model = max(err_ur_model, float(np.abs(A - ur.fk(q)).max()))
assert err_ur_poe < 1e-9 and err_ur_model < 1e-9
origins = [clean(F[:3, 3]) for F in F_ur]

# Theorem 13.2.1: another choice of intermediate frame (origin of {2} shifted 0.05 m along z_2, x_2 reversed) leaves T_06 unchanged
alt = [list(r) for r in tab_ur]
# {2} shifted by c along z_2: d of row 2 increases by c, d of row 3 decreases by c; x_2 reversed: θ offset of row 2 +π and a changes sign, θ offset of row 3 +π
c = 0.05
alt[1][2] += c
alt[2][2] -= c
alt[1][3] += pi
alt[1][0] = -alt[1][0]
alt[2][3] += pi
for _ in range(100):
    q = rng.uniform(-pi, pi, 6)
    assert np.allclose(fk_sdh(alt, q), fk_sdh(tab_ur, q), atol=1e-12)

out(scA=rows_tex(tabA, offA, kinds), scB=rows_tex(tabB, offB, kinds), T_sc=tex(clean(TB, 1e-12), 4),
    errA=errA, errB=errB, N=N, oB1=vec(FB[1][:3, 3], 3), oB3=vec(FB[3][:3, 3], 3), oA1=vec(clean(FA0[1][:3, 3]), 3),
    oA3=vec(clean(FA0[3][:3, 3]), 3),
    **{f"o{i}": vec(o, 3) for i, o in enumerate(origins)},
    T6b=tex(clean(T6b), 0), err_ur_poe=err_ur_poe, err_ur_model=err_ur_model)
