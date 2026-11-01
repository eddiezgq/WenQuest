"""Clearance chain (round 64, step 1): initial diametral clearance → mounted (interference fits) → operating
(temperature difference between the rings).

Fits by thick-walled cylinders (Lamé; Timoshenko & Goodier, Theory of Elasticity; the same approach as Harris &
Kotzalas vol. 1 ch. 2): the inner ring is a cylinder from its bore d to an equivalent outside diameter d_ie (the raceway
diameter is the usual choice), on a shaft with bore d_s (0 = solid); diametral interference I. Fit pressure p from
    I/2 = p (d/2) [ (d_ie² + d²)/(d_ie² − d²) + ν_r ] / E_r + p (d/2) [ (d² + d_s²)/(d² − d_s²) − ν_s ] / E_s
and the growth of the ring's outside (diametral)  Δ_i = 2 · 2 p a² b / (E_r (b² − a²)),  a = d/2, b = d_ie/2.
The outer ring in a housing (bore D, housing outside D_h; ∞ for a large housing) shrinks its inside by the mirror
formula. Temperature: each raceway grows by α_t ΔT times its diameter; the clearance changes by
α_t (ΔT_o d_o − ΔT_i d_i) (diametral; same steel, uniform ring temperatures, ΔT from the reference temperature).

Plain code: no AI, no network. mm, MPa, °C.
"""

from __future__ import annotations

import math


def fit_inner(interference: float, d: float, d_ie: float, d_s: float = 0.0, E_r: float = 206000.0,
              nu_r: float = 0.3, E_s: float = 206000.0, nu_s: float = 0.3) -> dict:
    """Inner ring pressed on a shaft: fit pressure p (MPa) and the growth of the raceway diameter (mm)."""
    if interference <= 0:
        return {"p": 0.0, "growth": 0.0}
    a, b, c = d / 2, d_ie / 2, d_s / 2
    ring = a * ((b * b + a * a) / (b * b - a * a) + nu_r) / E_r
    shaft = a * ((a * a + c * c) / (a * a - c * c) - nu_s) / E_s
    p = (interference / 2) / (ring + shaft)
    u_b = 2 * p * a * a * b / (E_r * (b * b - a * a))  # radial displacement of the ring's outside
    return {"p": p, "growth": 2 * u_b}


def fit_outer(interference: float, D: float, d_oe: float, D_h: float = math.inf, E_r: float = 206000.0,
              nu_r: float = 0.3, E_h: float = 206000.0, nu_h: float = 0.3) -> dict:
    """Outer ring pressed in a housing: fit pressure p (MPa) and the shrinkage of the raceway diameter (mm)."""
    if interference <= 0:
        return {"p": 0.0, "shrink": 0.0}
    a, b = d_oe / 2, D / 2  # ring from its raceway (inside, equivalent) to its outside
    ring = b * ((b * b + a * a) / (b * b - a * a) - nu_r) / E_r
    if math.isinf(D_h):
        house = b * (1 + nu_h) / E_h
    else:
        c = D_h / 2
        house = b * ((c * c + b * b) / (c * c - b * b) + nu_h) / E_h
    p = (interference / 2) / (ring + house)
    u_a = 2 * p * b * b * a / (E_r * (b * b - a * a))  # inward radial displacement of the ring's inside
    return {"p": p, "shrink": 2 * u_a}


def chain(Pd0: float, d_i: float, d_o: float, inner: dict | None = None, outer: dict | None = None,
          T_i: float = 20.0, T_o: float = 20.0, T_ref: float = 20.0, alpha_t: float = 11.5e-6) -> dict:
    """Initial → mounted → operating diametral clearance. inner/outer: the fit_inner/fit_outer arguments (or None).
    α_t defaults to a common value for bearing steel; give the real one."""
    gi = fit_inner(**inner)["growth"] if inner else 0.0
    so = fit_outer(**outer)["shrink"] if outer else 0.0
    mounted = Pd0 - gi - so
    thermal = alpha_t * ((T_o - T_ref) * d_o - (T_i - T_ref) * d_i)
    return {"initial": Pd0, "fit_inner": gi, "fit_outer": so, "mounted": mounted, "thermal": thermal,
            "operating": mounted + thermal}
