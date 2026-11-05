"""Crossed roller bearings (round 64, plan section 十九, X1).

Cylindrical rollers in a V-shaped raceway, every other one turned through 90°: roller j faces σ_j = +1 or −1
(alternating). In the meridian plane (r, z) the contact normal of a roller runs from the inner raceway through the
roller centre to the outer raceway at the contact angle α to the radial direction: n = (cos α, σ sin α); the roller
axis is across it, a = (−σ sin α, cos α). So one set of rollers carries axial force one way and the other set the
other way, and together with the radial force and the tilting moment one bearing carries everything.

Rigid rings. The inner ring moves u = (u_x, u_y, u_z, β, γ) relative to the outer ring: a point (x, y, z) of it by
(u_x + β z, u_y + γ z, u_z − β x − γ y) (as in taper_pair.py). A slice of roller j at azimuth ψ_j, at s along the
roller axis from its centre, sits at r = R₀ + s a_r, z = s a_z (R₀ = d_m/2) and closes along n by
    δ = ((u_x + β z) cos ψ + (u_y + γ z) sin ψ) cos α + σ (u_z − r (β cos ψ + γ sin ψ)) sin α − (G_r/2) cos α − 2 c(s)
with G_r the radial clearance (the inner ring's free radial play; negative = preload) and c(s) the crown drop (the
same profiles as the cylindrical roller bearing). Each slice is a piece of line contact, both contacts in series:
Palmgren's law q = k δ₊^(10/9), k = (2 · 3.84·10⁻⁵ l^0.1)^(−10/9). The stored energy Σ w k δ₊^(19/9) · 9/19 is a
convex function of u whose gradient is the rows' resultant; equilibrium with the outside load is its minimum less
the load's work (quasi-Newton, then Newton on the exact gradient), as for the tapered pair (taper_pair.py). Rollers
may unload partly or wholly.

Contact stress of a slice (Hertz line contact): p = √(q E*/(π R)) with 1/R = 2/D_w + cos α/r_i on the inner
raceway (a cone: its curvature across the roller is cos α / r) and 2/D_w − cos α/r_o on the outer one,
r_i,o = (d_m ∓ D_w cos α)/2.

Plain code: no AI, no network. N, mm, rad (µm and degrees at the edges), MPa.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq, minimize

from bearingkit import hertz as H
from bearingkit import roller as RL

CrossedError = ValueError


class Crossed:
    def __init__(self, Dw, L, Z, dm, alpha_deg, Gr=0.0, E=206000.0, nu=0.3, profile=None, k=31):
        if not (Dw > 0 and L > 0 and dm > Dw and Z >= 4 and Z == int(Z)):
            raise CrossedError(
                "give the roller diameter and length, the number of rollers (at least 4) and a pitch diameter "
                "above the roller diameter"
            )
        if alpha_deg is None or not 20 <= alpha_deg <= 70:
            raise CrossedError("give the contact angle of the crossed roller bearing (between 20° and 70°)")
        if Z * Dw >= math.pi * dm:
            raise CrossedError("the rollers do not fit round the pitch circle (Z·Dw ≥ π·dm)")
        try:
            self.cyl = RL.bearing({"D": Dw, "L": L, "Z": Z, "dm": dm, "E": E, "nu": nu, "profile": profile, "k": k})
        except RL.RollerError as e:
            raise CrossedError(str(e)) from e
        self.Dw, self.L, self.Z, self.dm, self.Gr = float(Dw), float(L), int(Z), float(dm), float(Gr)
        self.a = math.radians(alpha_deg)
        self.sa, self.ca = math.sin(self.a), math.cos(self.a)
        self.psi = 2 * np.pi * np.arange(self.Z) / self.Z
        self.sig = np.where(np.arange(self.Z) % 2 == 0, 1.0, -1.0)
        self.s = self.cyl.x()  # slice positions along the roller axis
        self.w = self.L / self.cyl.k
        self.k = (2 * RL.PALMGREN * self.L**0.1) ** (-10 / 9)
        self.drop2 = 2 * self.cyl.drop(self.s)
        self.R0 = self.dm / 2
        self.Es = H.e_star(E, nu, E, nu)
        # the linear map u → closing, arrays (5, Z, k), and the closing at u = 0
        c, sn = np.cos(self.psi)[:, None], np.sin(self.psi)[:, None]
        sg = self.sig[:, None]
        r = self.R0 + self.s[None, :] * (-sg * self.sa)
        z = self.s[None, :] * self.ca * np.ones_like(sg)
        one = np.ones((self.Z, len(self.s)))
        self.G = np.array(
            [
                self.ca * c * one,
                self.ca * sn * one,
                sg * self.sa * one,
                self.ca * c * z - sg * self.sa * r * c,
                self.ca * sn * z - sg * self.sa * r * sn,
            ]
        )
        self.d0 = -(self.Gr / 2) * self.ca - self.drop2[None, :] * one

    def closing(self, u):
        return self.d0 + np.tensordot(np.asarray(u, float), self.G, axes=1)

    def energy(self, u, P):
        d = self.closing(u)
        dp = np.maximum(d, 0.0)
        q = self.k * dp ** (10 / 9)
        e = self.w * self.k * (dp ** (19 / 9)).sum() * 9 / 19
        g = self.w * np.tensordot(self.G, q, axes=([1, 2], [0, 1]))
        return e - float(np.dot(P, u)), g - P

    def forces(self, u):
        q = self.k * np.maximum(self.closing(u), 0.0) ** (10 / 9)
        return self.w * np.tensordot(self.G, q, axes=([1, 2], [0, 1]))

    # one roller pushed along its normal (for the preload and the scales)
    def roller_force(self, dn: float) -> float:
        d = dn - self.drop2
        return float(self.w * self.k * (np.maximum(d, 0.0) ** (10 / 9)).sum())

    def approach(self, Q: float) -> float:
        if Q <= 0:
            return 1e-4 * self.dm
        hi = 1e-4 * self.dm
        while self.roller_force(hi) < Q:
            hi *= 2
        return brentq(lambda x: self.roller_force(x) - Q, 0.0, hi, xtol=1e-15)

    def preload_force(self) -> float:
        """Axial force each set of rollers carries with no outside load (0 with clearance), N."""
        if self.Gr >= 0:
            return 0.0
        Q = self.roller_force(-self.Gr / 2 * self.ca)
        return float(Q * self.sa * np.count_nonzero(self.sig > 0))

    def solve(self, P) -> np.ndarray:
        """Inner ring displacement for the outside load P = (Fx, Fy, Fz, Pβ, Pγ) (Pβ = Σ z Fx = M_y, Pγ = −M_x)."""
        P = np.asarray(P, float)
        Qs = max(np.abs(P[:3]).max(), np.abs(P[3:]).max() / self.R0, self.preload_force(), 1.0)
        a = self.approach(Qs / max(self.Z / 4, 1.0))
        S = np.array([a, a, a, a / self.R0, a / self.R0])

        def fun(v):
            e, g = self.energy(v * S, P)
            return e / (Qs * a), g * S / (Qs * a)

        res = minimize(fun, np.zeros(5), jac=True, method="BFGS", options={"gtol": 1e-12, "maxiter": 3000})
        u = res.x * S
        for _ in range(40):
            r = self.forces(u) - P
            if np.abs(r[:3]).max() <= 1e-10 * Qs and np.abs(r[3:]).max() <= 1e-10 * Qs * self.R0:
                break
            J = self.jacobian(u, S)
            try:
                u = u + np.linalg.solve(J, -r)
            except np.linalg.LinAlgError:
                break
        r = self.forces(u) - P
        if np.abs(r[:3]).max() > 1e-6 * Qs or np.abs(r[3:]).max() > 1e-6 * Qs * self.R0:
            raise CrossedError(
                "the crossed roller bearing's load distribution did not converge (the load is too large for these "
                "rollers)"
            )
        return u

    def jacobian(self, u, S=None):
        S = S if S is not None else np.array([1, 1, 1, 1 / self.R0, 1 / self.R0]) * 1e-4 * self.Dw
        J = np.empty((5, 5))
        for i in range(5):
            h = np.zeros(5)
            h[i] = 1e-6 * S[i]
            J[:, i] = (self.forces(u + h) - self.forces(u - h)) / (2 * h[i])
        return J

    def rollers(self, u) -> dict:
        d = self.closing(u)
        q = self.k * np.maximum(d, 0.0) ** (10 / 9)
        Q = q.sum(axis=1) * self.w
        ri = (self.dm - self.Dw * self.ca) / 2
        ro = (self.dm + self.Dw * self.ca) / 2
        Ri = 1 / (2 / self.Dw + self.ca / ri)
        Ro = 1 / (2 / self.Dw - self.ca / ro)
        p_i = np.sqrt(q * self.Es / (math.pi * Ri))
        p_o = np.sqrt(q * self.Es / (math.pi * Ro))
        return {
            "psi_deg": np.degrees(self.psi),
            "facing": self.sig,
            "Q": Q,
            "q": q,
            "s": self.s,
            "p_i": p_i,
            "p_o": p_o,
            "Qmax": float(Q.max()),
            "loaded": int(np.count_nonzero(Q > 0)),
            "Fa_plus": float((Q * self.sa)[self.sig > 0].sum()),
            "Fa_minus": float((Q * self.sa)[self.sig < 0].sum()),
            "p_max_inner": float(p_i.max()),
            "p_max_outer": float(p_o.max()),
            "loaded_plus": int(np.count_nonzero(Q[self.sig > 0] > 0)),
            "loaded_minus": int(np.count_nonzero(Q[self.sig < 0] > 0)),
        }

    def stiffness(self, u) -> dict:
        """Stiffness about the working point (axial and radial N/µm, tilt N·m/mrad): the inverse of the compliance,
        the other displacements free."""
        C = np.linalg.inv(self.jacobian(u))
        return {"axial": 1 / C[2, 2] / 1000, "radial": 1 / C[0, 0] / 1000, "tilt": 1 / C[3, 3] / 1e6}


def clearance_for_preload(b: Crossed, Fp: float) -> float:
    """The radial clearance (negative, mm) that gives each set of rollers the axial preload Fp."""
    if Fp <= 0:
        return 0.0
    n = int(np.count_nonzero(b.sig > 0))
    dn = b.approach(Fp / (n * b.sa))
    return -2 * dn / b.ca


def load(Fr=0.0, Fa=0.0, M=0.0):
    """The outside load vector for a radial force along x, an axial force along z and a tilting moment that turns
    about y (the moment the radial force at an axial offset gives): P = (Fr, 0, Fa, M, 0), N and N·mm."""
    return np.array([Fr, 0.0, Fa, M, 0.0])


def setting_curve(make, P, g_from_um, g_to_um, n=21) -> dict:
    """Clearance swept from g_from to g_to (µm): the largest contact stress, loaded rollers, stiffness, preload."""
    out = {"g_um": [], "p_max": [], "loaded": [], "k_axial": [], "k_radial": [], "k_tilt": [], "preload": []}
    for gv in np.linspace(g_from_um, g_to_um, n):
        b = make(gv / 1000)
        out["g_um"].append(float(gv))
        out["preload"].append(b.preload_force())
        try:
            u = b.solve(P)
        except CrossedError:
            for k in ("p_max", "loaded", "k_axial", "k_radial", "k_tilt"):
                out[k].append(None)
            continue
        r = b.rollers(u)
        st = b.stiffness(u)
        out["p_max"].append(max(r["p_max_inner"], r["p_max_outer"]))
        out["loaded"].append(r["loaded"])
        out["k_axial"].append(st["axial"])
        out["k_radial"].append(st["radial"])
        out["k_tilt"].append(st["tilt"])
    return out
