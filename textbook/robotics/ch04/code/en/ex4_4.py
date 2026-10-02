"""Examples of Section 4.4.

Example 4.4.1: 120° about (1,1,1)/√3 -- Rodrigues' formula gives a matrix of only 0s and 1s, exactly the result of
method A in Example 4.2.2.
Example 4.4.2: the logarithm map -- exponential coordinates from the matrix of Example 4.3.1, agreeing with the
eigenvector method.
Example 4.4.3: the special case of an angle of π.
Also: the vector form, the matrix form and the matrix exponential (series) agree; how many series terms are enough.
"""
import math

import numpy as np
from scipy.linalg import expm

from _rot import is_rotation, rot_axis, rot_x, rot_z, skew
from bookout import out, tex, vec

d = math.radians


def rodrigues_vector(w, t, v):
    """Eq. (4.4.2): the vector form."""
    return v * math.cos(t) + np.cross(w, v) * math.sin(t) + w * (w @ v) * (1 - math.cos(t))


def exp_series(A, n):
    """The series of the matrix exponential, first n terms: I + A + A²/2! + ..."""
    S, term = np.eye(3), np.eye(3)
    for k in range(1, n):
        term = term @ A / k
        S = S + term
    return S


def log_so3(R):
    """Logarithm map: (ŵ, θ) from R, θ ∈ [0, π]. The three cases are handled separately."""
    c = float(np.clip((np.trace(R) - 1) / 2, -1, 1))
    t = math.acos(c)
    if t < 1e-9:
        return None, 0.0
    if math.pi - t < 1e-6:
        # R = 2ŵŵᵀ − I: take the column of (R + I)/2 with the largest diagonal entry
        B = (R + np.eye(3)) / 2
        j = int(np.argmax(np.diag(B)))
        w = B[:, j] / math.sqrt(B[j, j])
        return w / np.linalg.norm(w), math.pi
    W = (R - R.T) / (2 * math.sin(t))
    return np.array([W[2, 1], W[0, 2], W[1, 0]]), t


# [ŵ]² = ŵŵᵀ − I, [ŵ]³ = −[ŵ]
w0 = np.array([0.6, 0.0, 0.8])
K = skew(w0)
assert np.allclose(K @ K, np.outer(w0, w0) - np.eye(3)) and np.allclose(K @ K @ K, -K)

# Example 4.4.1
w1 = np.ones(3) / math.sqrt(3)
t1 = d(120)
R1 = rot_axis(w1, t1)
assert np.allclose(R1, np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]]))
assert np.allclose(R1, rot_z(d(90)) @ rot_x(d(90)))        # method A
for v in np.eye(3):                                          # the three forms agree
    assert np.allclose(rodrigues_vector(w1, t1, v), R1 @ v)
assert np.allclose(expm(skew(w1) * t1), R1)

# the series: error against number of terms (Figure 4.4.2 uses the same numbers)
A = skew(w1) * t1
errors = [float(np.abs(exp_series(A, n) - R1).max()) for n in range(1, 31)]
n_needed = next(n for n, e in zip(range(1, 31), errors) if e < 1e-12)

# Example 4.4.2: the logarithm map
R2 = rot_z(d(30)) @ rot_x(d(45))
w2, t2 = log_so3(R2)
assert is_rotation(R2) and np.allclose(rot_axis(w2, t2), R2)
vals, vecs = np.linalg.eig(R2)
w_eig = np.real(vecs[:, int(np.argmin(abs(vals - 1)))])
assert np.allclose(abs(w_eig @ w2), 1)                       # agrees with the eigenvector method of Section 4.3 (same line)
W2 = (R2 - R2.T) / 2

# Example 4.4.3: angle π
w3 = np.array([0.6, 0.8, 0.0])
R3 = rot_axis(w3, math.pi)
assert np.allclose(R3, 2 * np.outer(w3, w3) - np.eye(3))
w3_back, t3 = log_so3(R3)
assert abs(t3 - math.pi) < 1e-12 and np.allclose(abs(w3_back @ w3), 1)
assert np.allclose(R3 - R3.T, 0)                             # here R − Rᵀ = 0 and the general formula fails

out(R1=tex(R1), sin120=math.sin(t1), w2=vec(w2), t2_deg=math.degrees(t2), t2=t2, expc2=vec(w2 * t2), sin_t2=math.sin(t2),
    W2=tex(W2), R3=tex(R3), half_RI=tex((R3 + np.eye(3)) / 2), n_needed=n_needed,
    err5=errors[4], err10=errors[9], err20=errors[19], _errors=errors)
