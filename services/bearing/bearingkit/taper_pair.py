"""Tapered roller bearings in pairs and adjusted at mounting (round 64, plan section 十六).

Two identical single rows on one shaft: side by side (a pair, row distance s) or one at each end of the shaft (two
supports, span L). The shaft (the cones) moves as a rigid body against the housing (the cups): displacement u =
(u_x, u_y, u_z, β, γ), a point (x, y, z) of the shaft moving by (u_x + β z, u_y + γ z, u_z − β x − γ y). Row j sits
at z_j and faces σ_j = ±1 (σ = +1: the cone pushed towards +z closes the row; its pressure centre lies R tan α on
the −z side of the row). Each roller of row j at ψ, each slice at x along the roller (towards its large end), closes
along the cup normal by

    δ = σ_j (u_z − R(β cos ψ + γ sin ψ)) sin α − e/2 · sin α
        + ((u_x + β z_s) cos ψ + (u_y + γ z_s) sin ψ) cos α − 2 c(x),        z_s = z_j + σ_j x

with R = d_m/2 and e the axial end play of the arrangement (e > 0 play, e < 0 preload; shared equally by the rows).
Slices follow Palmgren's line contact law as in the single row (taper.py, both contacts in series, the cone side by
the roller's force balance), so q = k δ₊^(10/9), and the stored energy is Σ w k δ₊^(19/9)/(19/9): a convex function of
u whose gradient is the rows' resultant (the generalised forces P_x, P_y, P_z, P_β, P_γ). Equilibrium with the outside
load is the minimum of the energy less the work of that load, found by a quasi-Newton search and polished by Newton
steps on the exact gradient; a row may unload partly or wholly (no axial force is needed any more).

The outside load: forces F_x, F_y, F_z on the shaft and the generalised moments P_β = Σ z F_x, P_γ = Σ z F_y about the
origin (for supports A at z = −L/2 and B at +L/2 these are the reactions' moments), i.e. P_β = M_y and P_γ = −M_x.

No catalogue factors (the "induced axial force 0.5 F_r/Y" of handbooks needs a catalogue Y): the split of the axial
force between the rows comes from their stiffness and the adjustment. Low speed: no centrifugal force or rib friction.

Plain code: no AI, no network. N, mm, rad; end play in mm here (µm at the edges).
"""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq, minimize

from bearingkit import taper as TP
from bearingkit.roller import PALMGREN

PairError = ValueError
# facing σ of the rows at z = −s/2 and z = +s/2 (row A first). A row closes along (σ sin α, cos α) in (z, r), so its
# line of action crosses the axis at z_c − σ R tan α: a row facing +1 has its pressure centre on its −z side. The
# row at −s/2 facing +1 and the row at +s/2 facing −1 spread their pressure centres outwards: back to back (O). Face
# to face (X) is the other way round; its pressure centres meet between the rows.
ARRANGEMENTS = {"DB": (+1, -1), "DF": (-1, +1)}


class Pair:
    def __init__(self, b: TP.TaperBearing, arrangement: str, spacing: float, endplay: float = 0.0):
        if arrangement not in ARRANGEMENTS:
            raise PairError("the arrangement of a tapered pair is DB or DF")
        if not spacing > 0:
            raise PairError("give the distance between the two rows")
        self.b, self.arr, self.s, self.e = b, arrangement, float(spacing), float(endplay)
        self.sig = ARRANGEMENTS[arrangement]
        self.z = (-self.s / 2, self.s / 2)
        self.psi = 2 * np.pi * np.arange(b.Z) / b.Z
        self.x = b.cyl.x()
        self.w = b.L / b.k
        self.k = 1.0 / (PALMGREN * b.L**0.1 * b.kappa()) ** (10 / 9)  # q = k δ^(10/9)
        self.drop2 = 2 * b.cyl.drop(self.x)
        self.R = b.dm / 2
        self.sa, self.ca = math.sin(b.ao), math.cos(b.ao)

    # the closing of every slice and its derivative with respect to u (a linear map)
    def _row(self, j: int):
        s, c, z = self.sig[j], np.cos(self.psi)[:, None], np.sin(self.psi)[:, None]
        zs = self.z[j] + s * self.x[None, :]
        # dδ/du for u = (ux, uy, uz, β, γ): arrays (Z, k)
        one = np.ones((self.b.Z, self.b.k))
        G = [
            self.ca * c * one,
            self.ca * z * one,
            s * self.sa * one,
            -s * self.sa * self.R * c * one + self.ca * c * zs,
            -s * self.sa * self.R * z * one + self.ca * z * zs,
        ]
        d0 = -self.e / 2 * self.sa - self.drop2[None, :] * one
        return np.array(G), d0

    def state(self, u):
        """Per row: closing δ (Z × k), slice loads q, roller loads Q."""
        out = []
        for j in (0, 1):
            G, d0 = self._row(j)
            d = d0 + np.tensordot(u, G, axes=1)
            q = self.k * np.maximum(d, 0.0) ** (10 / 9)
            out.append({"G": G, "d": d, "q": q, "Q": q.sum(axis=1) * self.w})
        return out

    def energy(self, u, P):
        rows = self.state(u)
        e = sum(self.w * self.k * (np.maximum(r["d"], 0) ** (19 / 9)).sum() * 9 / 19 for r in rows)
        g = sum(self.w * np.tensordot(r["G"], r["q"], axes=([1, 2], [0, 1])) for r in rows)
        return e - float(np.dot(P, u)), g - P

    def forces(self, u):
        """The generalised forces the two rows carry (the gradient of the stored energy)."""
        rows = self.state(u)
        return sum(self.w * np.tensordot(r["G"], r["q"], axes=([1, 2], [0, 1])) for r in rows)

    def solve(self, P) -> np.ndarray:
        """Shaft displacement for the outside load P = (Fx, Fy, Fz, Pβ, Pγ)."""
        P = np.asarray(P, float)
        scale = max(np.abs(P[:3]).max(), np.abs(P[3:]).max() / self.R, self.preload_force(), 1.0)
        # displacement scale: the approach of one row under the load scale (lengths of a few µm)
        a = self.approach(scale)
        S = np.array([a, a, a, a / self.R, a / self.R])

        def fun(v):
            e, g = self.energy(v * S, P)
            return e / (scale * a), g * S / (scale * a)

        res = minimize(fun, np.zeros(5), jac=True, method="BFGS", options={"gtol": 1e-12, "maxiter": 2000})
        u = res.x * S
        for _ in range(30):  # Newton polish on the exact gradient (the Jacobian by central differences)
            r = self.forces(u) - P
            if np.abs(r[:3]).max() <= 1e-9 * scale and np.abs(r[3:]).max() <= 1e-9 * scale * self.R:
                break
            J = np.empty((5, 5))
            for i in range(5):
                h = np.zeros(5)
                h[i] = 1e-6 * S[i]
                J[:, i] = (self.forces(u + h) - self.forces(u - h)) / (2 * h[i])
            try:
                du = np.linalg.solve(J, -r)
            except np.linalg.LinAlgError:
                break
            u = u + du
        r = self.forces(u) - P
        if np.abs(r[:3]).max() > 1e-6 * scale or np.abs(r[3:]).max() > 1e-6 * scale * self.R:
            raise PairError(
                "the pair's load distribution did not converge (the load is too large for these rows, or nothing "
                "holds the shaft axially: check the arrangement and the end play)"
            )
        return u

    # the single row along its own axis (for the preload and the displacement scale)
    def axial_force(self, da: float) -> float:
        """Axial force of one row pushed da along its axis (no other load), N."""
        d = da * self.sa - self.drop2
        q = self.k * np.maximum(d, 0.0) ** (10 / 9)
        return float(q.sum() * self.w * self.b.Z * self.sa)

    def approach(self, F: float) -> float:
        if F <= 0:
            return 1e-4 * self.b.D
        hi = 1e-4 * self.b.D
        while self.axial_force(hi) < F:
            hi *= 2
        return brentq(lambda da: self.axial_force(da) - F, 0.0, hi, xtol=1e-15)

    def preload_force(self) -> float:
        """The axial force each row carries with no outside load (0 when there is end play)."""
        return self.axial_force(-self.e / 2) if self.e < 0 else 0.0


def endplay_for_preload(b: TP.TaperBearing, Fp: float) -> float:
    """The (negative) end play, mm, that gives the preload Fp in each row of an unloaded pair."""
    if Fp <= 0:
        return 0.0
    p = Pair(b, "DB", 1.0, 0.0)
    return -2 * p.approach(Fp)


def rows_of(p: Pair, u) -> list[dict]:
    """Each row as the single-row results look (taper.distribute's keys), for the checks and the drawings."""
    lam, mu = p.b.ratios()
    out = []
    for j, r in enumerate(p.state(u)):
        Q = r["Q"]
        c, s = np.cos(p.psi), np.sin(p.psi)
        out.append(
            {
                "row": j,
                "z": p.z[j],
                "facing": p.sig[j],
                "psi_deg": np.degrees(p.psi),
                "Q": Q,
                "Qi": lam * Q,
                "Qf": mu * Q,
                "q": r["q"],
                "x": p.x,
                "Qmax": float(Q.max()),
                "loaded": int(np.count_nonzero(Q > 0)),
                "Fa": float(p.sig[j] * Q.sum() * p.sa),
                "Fr": float(math.hypot((Q * c).sum() * p.ca, (Q * s).sum() * p.ca)),
                "da": float(p.sig[j] * u[2]),
                "dr": float(math.hypot(u[0], u[1])),
                "theta": float(math.hypot(u[3], u[4])),
            }
        )
    return out


def stiffness(p: Pair, P, u=None) -> dict:
    """Stiffness about the working point (N/µm; tilt N·m/mrad): the inverse of the compliance, the other
    displacements free."""
    u = p.solve(P) if u is None else u
    S = np.array([1e-5, 1e-5, 1e-5, 1e-5 / p.R, 1e-5 / p.R]) * p.b.D
    J = np.empty((5, 5))
    for i in range(5):
        h = np.zeros(5)
        h[i] = S[i]
        J[:, i] = (p.forces(u + h) - p.forces(u - h)) / (2 * h[i])
    C = np.linalg.inv(J)
    return {"axial": 1 / C[2, 2] / 1000, "radial": 1 / C[0, 0] / 1000, "tilt": 1 / C[3, 3] / 1e6}
