"""Forces at speed (第 39 轮): inertia, spring and load on the follower; contact force, cam torque, contact stress,
and the speed at which a force-closed follower would leave the cam (jump).

Translating follower, along its axis (N), positive = pressing the follower onto the cam:
    F_ax = m · s''ω² · 1e-3 + k (s + δ0) + F_w            (m kg, s'' mm/rad², ω rad/s, k N/mm, δ0 mm)
Oscillating follower, about its pivot (N·mm):
    M = J · s''ω² · 1e3 + k_t (s + ψ_pre) + M_w            (J kg·m², s'' rad/rad², k_t N·mm/rad)
A force-closed follower stays on the cam while F_ax > 0 (M > 0). Contact force along the normal: F_n = F_ax / cos φ
(translating roller), M / lever (oscillating). Cam torque from power balance, friction neglected: T = F_ax · s'
(N·mm). Hertz line contact between the roller (or flat face) and the profile:
    σ_H = sqrt( F_n (1/ρ1 + 1/ρ2) / (π b ((1 − ν1²)/E1 + (1 − ν2²)/E2)) ),  concave profile radius negative.
Gravity and guide friction are not included (say so in the report). Plain code: no AI, no network.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np


@dataclass
class Loads:
    rpm: float | None = None  # cam speed
    mass: float | None = None  # translating: equivalent mass, kg
    inertia: float | None = None  # oscillating: moment of inertia about the pivot, kg·m²
    k: float = 0.0  # spring rate: N/mm (translating) or N·mm/rad (oscillating)
    preload: float = 0.0  # spring preload deflection at s = 0: mm or rad
    load: float = 0.0  # constant working load pressing on the cam: N or N·mm


@dataclass
class Material:
    E1: float | None = None  # roller (or flat face) Young's modulus, MPa
    nu1: float | None = None
    E2: float | None = None  # cam
    nu2: float | None = None


def omega(rpm: float) -> float:
    return rpm * 2 * pi / 60


def forces(follower: str, geo: dict, loads: Loads) -> dict | None:
    """Follower force (N) or moment (N·mm) pressing on the cam, contact force and torque at the given speed. None
    when the speed or the mass is not given (unknown, not zero)."""
    w = omega(loads.rpm) if loads.rpm else None
    inertia_term = loads.mass if follower == "translating" else loads.inertia
    if w is None or inertia_term is None:
        return None
    s, s1, s2, phi = geo["s"], geo["s1"], geo["s2"], geo["phi"]
    if follower == "translating":
        f = loads.mass * s2 * w**2 * 1e-3 + loads.k * (s + loads.preload) + loads.load
        cos = np.cos(phi)
        fn = np.abs(f) / np.where(cos > 1e-9, cos, np.nan)
    else:
        f = loads.inertia * s2 * w**2 * 1e3 + loads.k * (s + loads.preload) + loads.load
        lever = geo["lever"]
        fn = np.abs(f) / np.where(lever > 1e-9, lever, np.nan)
    torque = f * s1
    return {"force": f, "contact": fn, "torque": torque, "omega": w}


def jump_speed(follower: str, geo: dict, loads: Loads) -> float | None:
    """The cam speed (r/min) above which a force-closed follower leaves the cam somewhere in the turn; inf when it
    never does (no deceleration); None when the mass is not given."""
    inertia_term = loads.mass if follower == "translating" else loads.inertia
    if inertia_term is None:
        return None
    s, s2 = geo["s"], geo["s2"]
    hold = loads.k * (s + loads.preload) + loads.load
    if np.any(hold < 0):
        return 0.0  # the spring pulls the follower off even at rest
    scale = 1e-3 if follower == "translating" else 1e3
    dec = s2 < 0
    if not np.any(dec):
        return float("inf")
    w2 = hold[dec] / (inertia_term * scale * -s2[dec])
    return float(sqrt(max(0.0, np.min(w2))) * 60 / (2 * pi))


def hertz(fn, rho_roller: float | None, rho_profile, width: float | None, mat: Material):
    """Contact stress (MPa) along the turn; None when the width or the materials are not given. ρ in mm; a flat
    face has rho_roller None (infinite)."""
    if not width or None in (mat.E1, mat.nu1, mat.E2, mat.nu2):
        return None
    inv = (0.0 if rho_roller is None else 1.0 / rho_roller) + 1.0 / np.where(
        np.abs(rho_profile) > 1e-9, rho_profile, np.nan
    )
    elastic = (1 - mat.nu1**2) / mat.E1 + (1 - mat.nu2**2) / mat.E2
    with np.errstate(invalid="ignore"):
        return np.sqrt(np.clip(fn * inv, 0, None) / (pi * width * elastic))
