"""Tapered roller bearings (round 64, step 4, part 2): one row, the cone rib, line contact by slices.

Geometry in the axial plane (x along the bearing axis towards the large end of the rollers, r radial): the cup
raceway makes the angle α_o with the axis (the contact angle), the cone raceway α_i < α_o, the roller axis
α_m = (α_o + α_i)/2; rollers of mean diameter D_w and effective length l_we, Z of them on the pitch diameter d_m.

Roller equilibrium (low speed: no centrifugal force or gyroscopic moment; Harris & Kotzalas, Rolling Bearing
Analysis, 5th ed., vol. 1, ch. 7). The cup pushes on the roller along n_o = (sin α_o, −cos α_o), the cone along
n_i = (−sin α_i, cos α_i), the cone rib on the large end along the roller axis n_f = −(cos α_f, sin α_f) (α_f the
direction of the rib's push; α_f = α_m for a rib face square to the roller axis). Q_o n_o + Q_i n_i + Q_f n_f = 0
gives Q_i and Q_f in proportion to Q_o (the same as Lamy's theorem for three concurrent forces).

Bearing (cup fixed, cone displaced δ_a axially and δ_r radially, tilted θ): along the cup normal, slice j of the
roller at ψ closes by
    δ_j(ψ) = δ_a sin α_o + δ_r cos α_o cos ψ + θ x_j cos ψ − 2 c(x_j)
(mounted with zero end play: the end play or preload of a pair comes in part 3). Each slice follows Palmgren's line
contact deflection (steel) at both raceways; the cone contact carries Q_i = λ Q_o and its approach projects onto the
cup normal by cos(α_o − α_i), so q_o,j = (δ_j / (3.84·10⁻⁵ l^0.1 (1 + λ^0.9 cos(α_o − α_i))))^(10/9).
Equilibrium on the cup: F_a = Σ Q_o sin α_o, F_r = Σ Q_o cos α_o cos ψ.
Stresses: Hertz line contact with the mean roller diameter, 1/R = (2/D_w)/(1 ∓ γ), γ = D_w cos α / d_m (cone −, cup +).
The rib: the roller end, a sphere of radius R_end, against the rib face taken as flat (Hertz sphere on a plane:
p = (6 Q E*² / (π³ R²))^(1/3)); a simplification the report states.

Plain code: no AI, no network. N, mm, rad (degrees at the edge), MPa.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import brentq, fsolve

from bearingkit import hertz as H
from bearingkit.roller import PALMGREN, CylBearing

TaperError = ValueError


@dataclass
class TaperBearing:
    D: float  # mean roller diameter
    L: float  # effective contact length
    Z: int
    dm: float
    alpha_o_deg: float  # cup angle (contact angle)
    alpha_i_deg: float  # cone angle
    alpha_f_deg: float | None = None  # direction of the rib's push; None: square to the roller axis
    R_end: float | None = None  # roller end sphere radius
    E: float = 206000.0
    nu: float = 0.3
    profile: dict = field(default_factory=lambda: {"kind": "straight"})
    k: int = 41

    def __post_init__(self):
        if not (0 < self.alpha_i_deg < self.alpha_o_deg < 45):
            raise TaperError("the cone angle is above 0 and below the cup angle, the cup angle below 45°")
        # the crown and the slices are those of a cylindrical roller of the same length and mean diameter
        self.cyl = CylBearing(
            D=self.D, L=self.L, Z=self.Z, dm=self.dm, E=self.E, nu=self.nu, profile=self.profile, k=self.k
        )
        self.cyl.check()

    @property
    def ao(self):
        return math.radians(self.alpha_o_deg)

    @property
    def ai(self):
        return math.radians(self.alpha_i_deg)

    @property
    def af(self):
        return math.radians(self.alpha_f_deg) if self.alpha_f_deg is not None else (self.ao + self.ai) / 2

    @property
    def Es(self):
        return H.e_star(self.E, self.nu, self.E, self.nu)

    def ratios(self) -> tuple[float, float]:
        """λ = Q_i / Q_o and μ = Q_f / Q_o from the roller's equilibrium."""
        no = np.array([math.sin(self.ao), -math.cos(self.ao)])
        ni = np.array([-math.sin(self.ai), math.cos(self.ai)])
        nf = -np.array([math.cos(self.af), math.sin(self.af)])
        lam, mu = np.linalg.solve(np.column_stack([ni, nf]), -no)
        if lam <= 0 or mu < 0:
            raise TaperError("the rib cannot hold the roller with these angles")
        return float(lam), float(mu)

    def kappa(self) -> float:
        lam, _ = self.ratios()
        return 1 + lam**0.9 * math.cos(self.ao - self.ai)

    def radius(self, ring: str) -> float:
        a = self.ai if ring == "inner" else self.ao
        g = self.D * math.cos(a) / self.dm
        return 1 / ((2 / self.D) / (1 - g)) if ring == "inner" else 1 / ((2 / self.D) / (1 + g))


def bearing(d: dict) -> TaperBearing:
    return TaperBearing(
        D=float(d["D"]),
        L=float(d["L"]),
        Z=int(d["Z"]),
        dm=float(d["dm"]),
        alpha_o_deg=float(d["alpha_o_deg"]),
        alpha_i_deg=float(d["alpha_i_deg"]),
        alpha_f_deg=None if d.get("alpha_f_deg") in (None, "") else float(d["alpha_f_deg"]),
        R_end=None if d.get("R_end") in (None, "") else float(d["R_end"]),
        E=float(d.get("E") or 206000.0),
        nu=float(d.get("nu") or 0.3),
        profile=d.get("profile") or {"kind": "straight"},
        k=int(d.get("k") or 41),
    )


def _state(b: TaperBearing, da: float, dr: float, theta: float, psi: np.ndarray):
    x = b.cyl.x()
    c = np.cos(psi)[:, None]
    closing = da * math.sin(b.ao) + dr * math.cos(b.ao) * c + theta * x[None, :] * c - 2 * b.cyl.drop(x)[None, :]
    q = (np.maximum(closing, 0.0) / (PALMGREN * b.L**0.1 * b.kappa())) ** (10 / 9)
    Q = q.sum(axis=1) * (b.L / b.k)
    return q, Q, x


def distribute(b: TaperBearing, Fr: float, Fa: float, theta: float = 0.0, psi0_deg: float = 0.0) -> dict:
    """Cup contact loads under radial force Fr (N, along ψ = 0) and axial force Fa (N, towards the cup's thrust
    side). A single row needs axial force: radial load alone pushes the cone out of the cup."""
    if Fa <= 0:
        raise TaperError(
            "a single tapered roller bearing needs an axial force (radial load alone pushes the cone "
            "out): give the axial force, or pair it (part 3)"
        )
    psi = np.radians(psi0_deg) + 2 * np.pi * np.arange(b.Z) / b.Z
    sa, ca = math.sin(b.ao), math.cos(b.ao)

    def fa_only(da):
        _, Q, _ = _state(b, da, 0.0, theta, psi)
        return float(np.sum(Q)) * sa - Fa

    hi = 1e-4 * b.D
    while fa_only(hi) < 0:
        hi *= 2
    da0 = brentq(fa_only, 0.0, hi, xtol=1e-15)
    scale = max(Fr, Fa)

    def eqs(v):
        _, Q, _ = _state(b, v[0], v[1], theta, psi)
        return [(np.sum(Q) * sa - Fa) / scale, (np.sum(Q * np.cos(psi)) * ca - Fr) / scale]

    if Fr > 0:
        sol = fsolve(eqs, [da0, 0.3 * da0 * sa / ca], full_output=True, xtol=1e-13)
        v, ok = sol[0], sol[2] == 1
        if not ok or max(abs(e) for e in eqs(v)) > 1e-8:
            raise TaperError(
                "the load distribution did not converge (the radial load may be too large for this "
                "axial force on a single row)"
            )
        da, dr = float(v[0]), float(v[1])
    else:
        da, dr = da0, 0.0
    q, Q, x = _state(b, da, dr, theta, psi)
    lam, mu = b.ratios()
    w = b.L / b.k
    return {
        "psi_deg": np.degrees(psi),
        "Q": Q,
        "Qi": lam * Q,
        "Qf": mu * Q,
        "q": q,
        "x": x,
        "da": da,
        "dr": dr,
        "theta": theta,
        "Qmax": float(Q.max()),
        "loaded": int(np.count_nonzero(Q > 0)),
        "M": float(np.sum((q * x[None, :]).sum(axis=1) * w * np.cos(psi))),
    }


def stresses(b: TaperBearing, q: np.ndarray) -> dict:
    """Hertz line-contact pressure (MPa) per slice: the cup carries q, the cone λ q."""
    lam, _ = b.ratios()
    out = {}
    for ring, qq in (("inner", lam * q), ("outer", q)):
        R = b.radius(ring)
        out[ring] = {"p": np.sqrt(np.maximum(qq, 0) * b.Es / (math.pi * R))}
    return out


def rib_stress(b: TaperBearing, Qf: float) -> float | None:
    """Roller end (sphere R_end) on the rib taken as flat: Hertz sphere on a plane."""
    if not b.R_end or Qf <= 0:
        return None
    return (6 * Qf * b.Es**2 / (math.pi**3 * b.R_end**2)) ** (1 / 3)


def frequencies(b: TaperBearing, n_rpm: float, outer_turns: bool = False) -> dict:
    g, fr = b.D * math.cos(b.ao) / b.dm, n_rpm / 60
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
