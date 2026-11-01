"""Hertz point contact (round 64, step 1): ball on raceway.

Curvatures (convex > 0), per Harris & Kotzalas, Rolling Bearing Analysis, 5th ed., vol. 1, ch. 2 and 6 (and the
same definitions in Hamrock & Dowson, Ball Bearing Lubrication, 1981):
    ball:            ρI1 = ρI2 = 2/D
    inner raceway:   ρII1 = 2/D · γ/(1 − γ)   (rolling direction, convex)    ρII2 = −1/(f_i D)  (across, concave)
    outer raceway:   ρII1 = −2/D · γ/(1 + γ)  (rolling direction, concave)   ρII2 = −1/(f_o D)
    γ = D cos α / d_m
    Σρ = sum of the four, F(ρ) = [(ρI1 − ρI2) + (ρII1 − ρII2)] / Σρ
The contact ellipse (semi-axes a ≥ b, a across the rolling direction for a groove) follows from
    F(ρ) = [(κ² + 1) E(e) − 2 K(e)] / [(κ² − 1) E(e)],   κ = a/b,  e² = 1 − 1/κ²
with K, E the complete elliptic integrals of the first and second kind. Then (E* = 1 / Σ (1 − ν²)/E):
    a = (3 κ² E Q / (π Σρ E*))^(1/3),   b = (3 E Q / (π κ Σρ E*))^(1/3),   p_max = 3Q / (2π a b)
    δ = p_max · b · K / E*      (approach of distant points; Johnson, Contact Mechanics, 1985, §3.4)
For κ = 1 these reduce to Hertz's sphere formulas a³ = 3QR/(4E*), δ = a²/R (R = 2/Σρ).

Plain code: no AI, no network. Units: N, mm, MPa (N/mm²).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy.optimize import brentq
from scipy.special import ellipe, ellipk


@dataclass
class Contact:
    a: float  # semi-axis across the rolling direction, mm
    b: float  # semi-axis along the rolling direction, mm
    p_max: float  # MPa
    delta: float  # approach, mm
    kappa: float  # a / b
    sum_rho: float  # 1/mm
    F: float  # curvature difference


def e_star(E1: float, nu1: float, E2: float, nu2: float) -> float:
    return 1.0 / ((1 - nu1 * nu1) / E1 + (1 - nu2 * nu2) / E2)


def curvatures(D: float, dm: float, alpha: float, f: float, ring: str) -> tuple[float, float, float, float]:
    g = D * math.cos(alpha) / dm
    if ring == "inner":
        r21, r22 = 2 / D * g / (1 - g), -1 / (f * D)
    elif ring == "outer":
        r21, r22 = -2 / D * g / (1 + g), -1 / (f * D)
    else:
        raise ValueError("the ring is inner or outer")
    return 2 / D, 2 / D, r21, r22


def _F_of_kappa(k: float) -> float:
    m = 1 - 1 / (k * k)
    K, E = ellipk(m), ellipe(m)
    return ((k * k + 1) * E - 2 * K) / ((k * k - 1) * E)


def kappa_of_F(F: float) -> float:
    """Ellipticity a/b from the curvature difference (0 ≤ F < 1)."""
    if F < 1e-9:
        return 1.0
    if not F < 1:
        raise ValueError("the curvature difference must be below 1 (a line contact is not a point contact)")
    return brentq(lambda k: _F_of_kappa(k) - F, 1 + 1e-9, 1e4, xtol=1e-12, rtol=1e-14)


def solve(Q: float, rho: tuple[float, float, float, float], Es: float) -> Contact:
    """Contact of load Q (N) between two bodies with principal curvatures ρI1, ρI2, ρII1, ρII2 (1/mm), E* (MPa)."""
    r11, r12, r21, r22 = rho
    s = r11 + r12 + r21 + r22
    if not s > 0:
        raise ValueError("the bodies do not form a contact (curvature sum ≤ 0)")
    F = abs((r11 - r12) + (r21 - r22)) / s
    k = kappa_of_F(F)
    m = 1 - 1 / (k * k)
    K, E = (math.pi / 2, math.pi / 2) if k == 1.0 else (float(ellipk(m)), float(ellipe(m)))
    if Q <= 0:
        return Contact(0.0, 0.0, 0.0, 0.0, k, s, F)
    a = (3 * k * k * E * Q / (math.pi * s * Es)) ** (1 / 3)
    b = (3 * E * Q / (math.pi * k * s * Es)) ** (1 / 3)
    p = 3 * Q / (2 * math.pi * a * b)
    delta = p * b * K / Es
    return Contact(a, b, p, delta, k, s, F)


def stiffness(rho: tuple[float, float, float, float], Es: float) -> float:
    """K in Q = K δ^1.5 (N/mm^1.5) for these curvatures (δ ∝ Q^(2/3) in Hertz contact)."""
    c = solve(1.0, rho, Es)
    return 1.0 / c.delta**1.5
