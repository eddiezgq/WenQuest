"""Section 7.2.7: integrating the orientation from gyroscope readings (Lie group integration).

Coning motion R(t) = Rot(ẑ, a t) Rot(x̂, b t), a = 2 rad/s, b = 3 rad/s; the body angular velocity has the closed form ω_b(t) = (b, a sin bt, a cos bt),
so the true orientation is known exactly. Five methods integrate Ṙ = R[ω_b]:
  Euler (matrix entries)    R_{k+1} = R_k (I + h[ω_b(t_k)])
  RK4 (matrix entries)      classical fourth-order Runge–Kutta on the 9 entries
  Lie–Euler                 R_{k+1} = R_k exp(h[ω_b(t_k)])
  Lie midpoint              R_{k+1} = R_k exp(h[ω_b(t_k + h/2)])
  fourth-order Magnus       R_{k+1} = R_k exp(Ω), Ω = h(ω₁ + ω₂)/2 + (√3/12)h² ω₁ × ω₂ (Eqs. (7.2.16), (7.2.17))
Measures the orientation error angle and the orthogonality error ‖RᵀR − I‖ at t = 2 s; halving the step gives the order of each method. Then the orthogonality error after 100 s.
"""
import math

import numpy as np

from _ode import CONE, S3, angle_between, cone_R, cone_wb, lie_integrate as integrate, orth
from bookout import out

# check the closed form of ω_b by numerical differentiation: [ω_b] = Rᵀ Ṙ
for t in (0.3, 1.7):
    e = 1e-6
    Rd = (cone_R(t + e) - cone_R(t - e)) / (2 * e)
    W = cone_R(t).T @ Rd
    assert np.allclose(W, -W.T, atol=1e-8)
    assert np.allclose([W[2, 1], W[0, 2], W[1, 0]], cone_wb(t), atol=1e-8)

T = 2.0
R_true = cone_R(T)
hs = [0.02, 0.01, 0.005]
meths = ["euler", "rk4", "lie", "mid", "mag4"]
err, ort, order = {}, {}, {}
for m in meths:
    Rs = [integrate(m, T, h) for h in hs]
    err[m] = [math.degrees(angle_between(R, R_true)) for R in Rs]
    ort[m] = [orth(R) for R in Rs]
    order[m] = [math.log2(err[m][i] / err[m][i + 1]) for i in range(2)]
expect = {"euler": 1, "rk4": 4, "lie": 1, "mid": 2, "mag4": 4}
for m, p in expect.items():
    assert all(abs(o - p) < 0.2 for o in order[m]), (m, order[m])
for m in ("lie", "mid", "mag4"):
    assert max(ort[m]) < 1e-13                               # Lie group methods: always a rotation matrix (up to rounding error)
assert ort["euler"][0] > 1e-2                                # Euler leaves SO(3)
# Euler: each step has det(I + h[ω]) = 1 + h²|ω|², so the determinant keeps growing
det_eu = float(np.linalg.det(integrate("euler", T, 0.01)))
w2 = CONE["a"] ** 2 + CONE["b"] ** 2                          # |ω_b|² is constant
det_pred = (1 + 0.01 ** 2 * w2) ** 200                       # each step multiplies the determinant by 1 + h²|ω|², 200 steps in all
assert abs(det_eu - det_pred) < 1e-12

# long run: after 100 s the orthogonality error of RK4 keeps growing, the Lie group methods stay at rounding level
T_long = 100.0
ort_rk4_long = orth(integrate("rk4", T_long, 0.01))
ort_mag_long = orth(integrate("mag4", T_long, 0.01))
assert ort_rk4_long > 10 * ort["rk4"][1] and ort_mag_long < 1e-12

vals = {}
for m in meths:
    for i in range(3):
        vals[f"err_{m}{i}"] = err[m][i]
        vals[f"ort_{m}{i}"] = ort[m][i]
    for i in range(2):
        vals[f"p_{m}{i}"] = order[m][i]
out(a=CONE["a"], b=CONE["b"], wnorm=math.sqrt(w2), det_eu=det_eu, ort_rk4_long=ort_rk4_long, ort_mag_long=ort_mag_long,
    s3_12=S3 / 12, **vals)
