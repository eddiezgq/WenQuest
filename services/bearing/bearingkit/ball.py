"""Radial ball bearings (deep groove and angular contact): geometry and the static internal load distribution
(round 64, step 1). Harris & Kotzalas, Rolling Bearing Analysis, 5th ed., vol. 1 ch. 2 (geometry) and ch. 7
(distribution of internal loading); the same model is the basis of ISO 16281.

Geometry: Z balls of diameter D on pitch diameter d_m; groove radii r_i = f_i D, r_o = f_o D; the distance between
the groove curvature centres A = (f_i + f_o − 1) D. Free (unloaded) contact angle of a deep groove bearing from its
diametral clearance P_d:  cos α₀ = 1 − P_d / (2A); an angular contact bearing is given α₀ directly.

Static equilibrium, rigid rings, low speed (no centrifugal force or gyroscopic moment), outer ring fixed: the inner
ring moves δ_a axially, δ_r radially and tilts θ (moment). At azimuth ψ the curvature centres are apart by
    s(ψ) = √[(A sin α₀ + δ_a + ℜ_i θ cos ψ)² + (A cos α₀ + δ_r cos ψ)²],   ℜ_i = d_m/2 + (f_i − 0.5) D cos α₀,
the contact deflection is δ(ψ) = s − A (no load where ≤ 0), the ball load Q = K_n δ^1.5 (K_n from the inner and
outer Hertz contacts in series, at the ball's own contact angle), sin α(ψ) = (A sin α₀ + δ_a + ℜ_i θ cos ψ) / s.
Equilibrium: F_a = Σ Q sin α, F_r = Σ Q cos α cos ψ, M = Σ Q sin α ℜ_i cos ψ.

Plain code: no AI, no network. N, mm, rad (degrees at the edge), MPa.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import fsolve

from bearingkit import hertz as H


class BallError(ValueError):
    pass


@dataclass
class BallBearing:
    D: float  # ball diameter, mm
    Z: int  # number of balls
    dm: float  # pitch diameter, mm
    fi: float  # inner groove radius / D
    fo: float  # outer groove radius / D
    Pd: float = 0.0  # diametral clearance (deep groove), mm; negative = preload
    alpha0_deg: float | None = None  # angular contact: free contact angle; None = from the clearance
    E: float = 206000.0  # MPa, ball and rings (steel, a common value: override with the real material)
    nu: float = 0.3
    E_ball: float | None = None
    nu_ball: float | None = None
    extra: dict = field(default_factory=dict)

    def check(self) -> None:
        if not (self.D > 0 and self.dm > self.D and self.Z >= 3 and self.Z == int(self.Z)):
            raise BallError("give the ball diameter, the number of balls (at least 3) and a pitch diameter above it")
        if not (0.5 < self.fi < 0.6 and 0.5 < self.fo < 0.6):
            raise BallError("groove radius ratios f_i, f_o are between 0.5 and 0.6")
        if self.alpha0_deg is None and self.Pd < 0:
            raise BallError("a deep groove bearing with preload: give the contact angle instead")
        # balls must fit round the pitch circle: Z·D < π·d_m
        if self.Z * self.D >= math.pi * self.dm:
            raise BallError("the balls do not fit round the pitch circle (Z·D ≥ π·d_m)")

    @property
    def A(self) -> float:
        return (self.fi + self.fo - 1) * self.D

    @property
    def alpha0(self) -> float:
        if self.alpha0_deg is not None:
            return math.radians(self.alpha0_deg)
        c = 1 - self.Pd / (2 * self.A)
        return math.acos(max(-1.0, min(1.0, c)))

    @property
    def Es(self) -> float:
        Eb = self.E_ball or self.E
        nb = self.nu_ball if self.nu_ball is not None else self.nu
        return H.e_star(Eb, nb, self.E, self.nu)

    def gamma(self, alpha: float) -> float:
        return self.D * math.cos(alpha) / self.dm

    def Kn(self, alpha: float) -> float:
        """Q = K_n δ^1.5 for one ball, inner and outer contacts in series, at contact angle α."""
        Ki = H.stiffness(H.curvatures(self.D, self.dm, alpha, self.fi, "inner"), self.Es)
        Ko = H.stiffness(H.curvatures(self.D, self.dm, alpha, self.fo, "outer"), self.Es)
        return 1.0 / ((1 / Ki) ** (2 / 3) + (1 / Ko) ** (2 / 3)) ** 1.5

    def raceways(self) -> dict:
        """Raceway (groove bottom) diameters: inner d_i = d_m − D, outer d_o = d_m + D at zero clearance; the
        clearance is shared out on the outer one (P_d = d_o − d_i − 2D)."""
        return {"inner": self.dm - self.D, "outer": self.dm + self.D + max(self.Pd, 0.0)}


def bearing(d: dict) -> BallBearing:
    b = BallBearing(**{k: d[k] for k in ("D", "Z", "dm", "fi", "fo") if k in d},
                    Pd=float(d.get("Pd") or 0.0), alpha0_deg=d.get("alpha0_deg"),
                    E=float(d.get("E") or 206000.0), nu=float(d.get("nu") or 0.3))
    b.Z = int(b.Z)
    b.check()
    return b


def _balls(b: BallBearing, x, psi):
    """Ball loads, contact angles and deflections for inner-ring displacement x = (δ_a, δ_r, θ)."""
    da, dr, th = x
    a0 = b.alpha0
    Ri = b.dm / 2 + (b.fi - 0.5) * b.D * math.cos(a0)
    ax = b.A * math.sin(a0) + da + Ri * th * np.cos(psi)
    rd = b.A * math.cos(a0) + dr * np.cos(psi)
    s = np.hypot(ax, rd)
    dl = np.maximum(s - b.A, 0.0)
    alpha = np.arctan2(ax, rd)
    Kn = np.array([b.Kn(a) for a in alpha])
    Q = Kn * dl**1.5
    return Q, alpha, dl, Ri


def distribute(b: BallBearing, Fr: float = 0.0, Fa: float = 0.0, M: float = 0.0, psi0_deg: float = 0.0) -> dict:
    """Ball loads under radial force Fr (N, along ψ = 0), axial force Fa (N, pushing the contact angle side) and
    moment M (N·mm). The first ball at ψ0. Returns per-ball loads, angles, deflections and the displacements."""
    if Fa < 0:
        raise BallError("give the axial force on the side the contact angle takes it (Fa ≥ 0)")
    psi = np.radians(psi0_deg) + 2 * np.pi * np.arange(b.Z) / b.Z
    scale = max(Fr, Fa, abs(M) / max(b.dm, 1e-9), 1.0)

    def eqs(x):
        Q, al, _, Ri = _balls(b, x, psi)
        return [(np.sum(Q * np.sin(al)) - Fa) / scale, (np.sum(Q * np.cos(al) * np.cos(psi)) - Fr) / scale,
                (np.sum(Q * np.sin(al) * Ri * np.cos(psi)) - M) / (scale * b.dm)]

    # a starting point: with clearance and no axial load the ring first takes up half the clearance
    g = 1e-3 * b.D
    x0 = [g if Fa > 0 else 0.0, max(b.Pd / 2, 0) + g if Fr > 0 else 0.0, 0.0]
    if Fa == 0 and M == 0:  # only radial: solve δ_r alone (δ_a = θ = 0 by symmetry when α₀ = 0)
        sol = fsolve(lambda v: [eqs([0.0, v[0], 0.0])[1]], [x0[1]], full_output=True, xtol=1e-13)
        x = np.array([0.0, sol[0][0], 0.0])
        ok = sol[2] == 1
        if b.alpha0 > 1e-9:  # an angular contact bearing under radial load alone pushes itself axially: solve all
            sol = fsolve(eqs, [g, x[1], 0.0], full_output=True, xtol=1e-13)
            x, ok = sol[0], sol[2] == 1
    else:
        sol = fsolve(eqs, x0, full_output=True, xtol=1e-13)
        x, ok = sol[0], sol[2] == 1
    res = np.max(np.abs(eqs(x)))
    if not ok or res > 1e-8:
        raise BallError("the load distribution did not converge (the load may be more than the bearing can carry "
                        "with this clearance, or there is no axial support for the moment)")
    Q, al, dl, _ = _balls(b, x, psi)
    return {"psi_deg": np.degrees(psi), "Q": Q, "alpha_deg": np.degrees(al), "delta": dl,
            "da": float(x[0]), "dr": float(x[1]), "theta": float(x[2]), "Qmax": float(Q.max()),
            "loaded": int(np.count_nonzero(Q > 0))}


def contacts(b: BallBearing, Q: float, alpha: float) -> dict:
    """Hertz contact at the inner and outer raceways for ball load Q at contact angle α."""
    out = {}
    for ring, f in (("inner", b.fi), ("outer", b.fo)):
        c = H.solve(Q, H.curvatures(b.D, b.dm, alpha, f, ring), b.Es)
        out[ring] = c
    return out


def frequencies(b: BallBearing, n_rpm: float, alpha_deg: float | None = None, outer_turns: bool = False) -> dict:
    """Fault frequencies (Hz) at shaft speed n (r/min), one ring fixed: cage (FTF), ball pass outer (BPFO) and inner
    (BPFI), ball spin (BSF). Pure rolling kinematics (Harris & Kotzalas vol. 1 ch. 8)."""
    a = math.radians(alpha_deg) if alpha_deg is not None else b.alpha0
    g = b.gamma(a)
    fr = n_rpm / 60
    if outer_turns:
        ftf = fr / 2 * (1 + g)
        rel_out, rel_in = fr - ftf, ftf
    else:
        ftf = fr / 2 * (1 - g)
        rel_out, rel_in = ftf, fr - ftf
    return {"FTF": ftf, "BPFO": b.Z * rel_out, "BPFI": b.Z * rel_in,
            "BSF": b.dm / (2 * b.D) * fr * (1 - g * g), "shaft": fr}
