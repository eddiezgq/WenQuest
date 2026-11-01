"""Cylindrical roller bearings (round 64, step 4): line contact by slices, roller crowning, misalignment.

Geometry: Z rollers of diameter D_w and effective contact length l_we on pitch diameter d_m, diametral clearance P_d.
Raceways d_i = d_m − D_w, d_o = d_m + D_w + P_d. Radial load only (types NU / N: the flanges guide, they carry no
design axial load here).

Slicing (Harris & Kotzalas, Rolling Bearing Analysis, 5th ed., vol. 1, ch. 7, "the slicing technique"): the
effective length is cut into k slices of width w. At azimuth ψ the inner ring has moved δ_r radially and is tilted
by the misalignment θ (about the axis across the load), so slice j at axial position x_j closes by
    δ_j(ψ) = δ_r cos ψ − P_d/2 + θ x_j cos ψ − 2 c(x_j)
where c(x) is the crown drop of the roller profile (the same drop meets both raceways). Each slice behaves as a piece
of a uniformly loaded roller: Palmgren's line-contact deflection of one roller–raceway contact
    δ = 3.84·10⁻⁵ Q^0.9 / l^0.8          (mm, N; steel; Palmgren, Ball and Roller Bearing Engineering, 1959,
                                          as given by Harris & Kotzalas)
gives, with load q per unit length (Q = q l) and two contacts in series, q_j = (δ_j / (2·3.84·10⁻⁵ l^0.1))^(10/9).
The slices do not influence each other, so the stress concentration at a loaded roller end is not captured: the
check says so instead of showing a number for it.
Stress of a slice (Hertz line contact; Johnson, Contact Mechanics, §4.2):  p = √(q E* / (π R)),  half-width
b = √(4 q R / (π E*)), with 1/R = (2/D_w)/(1 − γ) on the inner raceway and (2/D_w)/(1 + γ) on the outer, γ = D_w/d_m.

Crown profiles c(x) (x from the roller centre, |x| ≤ l_we/2):
    straight;  arc of radius R_c: c = R_c − √(R_c² − x²);  flat middle of length L_f, then an arc of radius R_c from
    its ends;  a table of (x, drop) points, linearly interpolated (a measured or designed profile).

Plain code: no AI, no network. N, mm, rad (arcmin at the edge), MPa.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import brentq

from bearingkit import hertz as H

PALMGREN = 3.84e-5  # mm / (N^0.9 mm^-0.8), steel


class RollerError(ValueError):
    pass


@dataclass
class CylBearing:
    D: float  # roller diameter, mm
    L: float  # effective contact length, mm
    Z: int
    dm: float
    Pd: float = 0.0
    E: float = 206000.0
    nu: float = 0.3
    profile: dict = field(default_factory=lambda: {"kind": "straight"})
    k: int = 41  # slices

    def check(self) -> None:
        if not (self.D > 0 and self.L > 0 and self.dm > self.D and self.Z >= 3 and self.Z == int(self.Z)):
            raise RollerError(
                "give the roller diameter and length, the number of rollers (at least 3) and a pitch "
                "diameter above the roller diameter"
            )
        if self.Pd < 0:
            raise RollerError("the clearance of a cylindrical roller bearing is 0 or more")
        if self.Z * self.D >= math.pi * self.dm:
            raise RollerError("the rollers do not fit round the pitch circle (Z·D ≥ π·d_m)")
        kind = self.profile.get("kind", "straight")
        if kind not in ("straight", "arc", "partial", "table"):
            raise RollerError("the roller profile is straight, arc, partial or table")
        if kind in ("arc", "partial") and not (_f(self.profile.get("R")) or 0) > self.L / 2:
            raise RollerError("give the crown radius (more than half the roller length)")
        if kind == "partial" and not 0 <= (_f(self.profile.get("flat")) or 0) < self.L:
            raise RollerError("the flat middle is shorter than the roller")
        if kind == "table" and len(self.profile.get("points") or []) < 2:
            raise RollerError("give at least two points of the crown profile")

    @property
    def Es(self) -> float:
        return H.e_star(self.E, self.nu, self.E, self.nu)

    @property
    def gamma(self) -> float:
        return self.D / self.dm

    def x(self) -> np.ndarray:
        w = self.L / self.k
        return -self.L / 2 + w * (np.arange(self.k) + 0.5)

    def drop(self, x: np.ndarray) -> np.ndarray:
        p = self.profile
        kind = p.get("kind", "straight")
        ax = np.abs(x)
        if kind == "straight":
            return np.zeros_like(ax)
        if kind == "arc":
            R = float(p["R"])
            return R - np.sqrt(R * R - ax * ax)
        if kind == "partial":
            R, h = float(p["R"]), float(p.get("flat") or 0) / 2
            u = np.maximum(ax - h, 0.0)
            return R - np.sqrt(R * R - u * u)
        pts = sorted((float(a), float(b)) for a, b in p["points"])
        xs, ds = [a for a, _ in pts], [b for _, b in pts]
        return np.interp(ax, xs, ds)

    def radius(self, ring: str) -> float:
        g = self.gamma
        return 1 / ((2 / self.D) / (1 - g)) if ring == "inner" else 1 / ((2 / self.D) / (1 + g))


def _f(v):
    return None if v in (None, "") else float(v)


def bearing(d: dict) -> CylBearing:
    b = CylBearing(
        D=float(d["D"]),
        L=float(d["L"]),
        Z=int(d["Z"]),
        dm=float(d["dm"]),
        Pd=float(d.get("Pd") or 0.0),
        E=float(d.get("E") or 206000.0),
        nu=float(d.get("nu") or 0.3),
        profile=d.get("profile") or {"kind": "straight"},
        k=int(d.get("k") or 41),
    )
    b.check()
    return b


def slice_loads(b: CylBearing, closing: np.ndarray) -> np.ndarray:
    """Load per unit length (N/mm) of each slice for the given closings (mm), two contacts in series."""
    return (np.maximum(closing, 0.0) / (2 * PALMGREN * b.L**0.1)) ** (10 / 9)


def _state(b: CylBearing, dr: float, theta: float, psi: np.ndarray):
    x = b.x()
    c = np.cos(psi)[:, None]
    closing = dr * c - b.Pd / 2 + theta * x[None, :] * c - 2 * b.drop(x)[None, :]
    q = slice_loads(b, closing)
    w = b.L / b.k
    Q = q.sum(axis=1) * w
    return q, Q, x


def distribute(b: CylBearing, Fr: float, theta: float = 0.0, psi0_deg: float = 0.0) -> dict:
    """Roller loads under radial force Fr (N, along ψ = 0) with the inner ring tilted by θ (rad) about the axis
    across the load. Returns the slice loads q[ψ, x] (N/mm), roller loads, δ_r and the moment on the shaft."""
    if Fr <= 0:
        raise RollerError("give a radial force (cylindrical roller bearings carry radial load)")
    psi = np.radians(psi0_deg) + 2 * np.pi * np.arange(b.Z) / b.Z

    def f(dr):
        _, Q, _ = _state(b, dr, theta, psi)
        return float(np.sum(Q * np.cos(psi))) - Fr

    lo = b.Pd / 2 - abs(theta) * b.L / 2  # below this no slice is closed
    hi = b.Pd / 2 + 1e-3 * b.D
    n = 0
    while f(hi) < 0:
        lo, hi = hi, hi + 2 * (hi - lo)
        n += 1
        if n > 80:
            raise RollerError("the load distribution did not converge")
    dr = brentq(f, lo, hi, xtol=1e-15, rtol=1e-14)
    q, Q, x = _state(b, dr, theta, psi)
    w = b.L / b.k
    M = float(np.sum((q * x[None, :]).sum(axis=1) * w * np.cos(psi)))  # moment of the roller loads about the centre
    return {
        "psi_deg": np.degrees(psi),
        "Q": Q,
        "q": q,
        "x": x,
        "dr": dr,
        "theta": theta,
        "Qmax": float(Q.max()),
        "loaded": int(np.count_nonzero(Q > 0)),
        "M": M,
    }


def stresses(b: CylBearing, q: np.ndarray) -> dict:
    """Hertz line-contact pressure (MPa) and half-width (mm) of each slice, inner and outer raceway."""
    out = {}
    for ring in ("inner", "outer"):
        R = b.radius(ring)
        out[ring] = {
            "p": np.sqrt(np.maximum(q, 0) * b.Es / (math.pi * R)),
            "b": np.sqrt(4 * np.maximum(q, 0) * R / (math.pi * b.Es)),
        }
    return out


def film(q: float, R: float, Es: float, eta0: float, alpha_p: float, u_mm_s: float) -> dict:
    """Minimum film thickness (mm) of a line contact, Dowson & Higginson (Elasto-hydrodynamic Lubrication, 1977):
    h_min = 2.65 U^0.70 G^0.54 W^−0.13 R, U = η₀u/(E′R), G = α E′, W = q/(E′R), E′ = 2E* (q per unit length)."""
    Ep = 2 * Es * 1e6
    Rm, u = R * 1e-3, u_mm_s * 1e-3
    U = eta0 * u / (Ep * Rm)
    G = alpha_p * Ep
    W = (q * 1e3) / (Ep * Rm)  # N/mm → N/m
    h = 2.65 * U**0.70 * G**0.54 * W**-0.13 * Rm
    return {"h_min": h * 1e3, "U": U, "G": G, "W": W}


def frequencies(b: CylBearing, n_rpm: float, outer_turns: bool = False) -> dict:
    g, fr = b.gamma, n_rpm / 60
    if outer_turns:
        ftf = fr / 2 * (1 + g)
        rel_out, rel_in = fr - ftf, ftf
    else:
        ftf = fr / 2 * (1 - g)
        rel_out, rel_in = ftf, fr - ftf
    return {
        "FTF": ftf,
        "BPFO": b.Z * rel_out,
        "BPFI": b.Z * rel_in,
        "BSF": b.dm / (2 * b.D) * fr * (1 - g * g),
        "shaft": fr,
    }
