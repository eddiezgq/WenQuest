"""Thin-section ball bearings for robot joints (round 64, plan section 二十一, part 2): four-point contact (X),
angular contact (A, single or a pair) and radial deep groove (C), all with the same general model.

Each ring's groove is one or two circular arcs in the meridian plane (z axial, ρ radial). An arc has radius
r = f·D_w and a centre of curvature; the ball (diameter D_w, centre B) touches it where the line from the centre
through B meets the arc, and the contact closes by
    δ = |B − C| − (r − D_w/2)            (> 0: in contact, Hertz Q = K δ^1.5, K from the contact's curvatures).
  C (deep groove): one arc each, centres on the groove's middle plane.
  A (angular contact): one arc each, centres on the contact line at the free contact angle α₀ (the ball touching).
  X (four-point): two arcs each (a gothic arch), centres offset to ±z so that each diagonal (inner arc on one side,
    outer arc on the other) touches the ball at ±α₀.
Clearance: X and C have a radial play G_r (the inner ring's free radial movement from one side to the other; negative
is preload), the outer arcs moved outwards by G_r/2 (the clearance on the outer ring, as the drawings put it; the
balls are free, so where it goes does not change the results). A pair (back to back DB or face to
face DF, rows a distance s apart, the facings as for tapered pairs) has an axial end play e (negative: preload), each
row's inner arc moved back by e/2 along its facing.

The balls are free bodies (two unknowns each, their centre in their meridian plane): with four arcs a ball can carry
both diagonals, and a ball's position is what the arcs make it. Rigid rings; the inner ring moves
u = (u_x, u_y, u_z, β, γ) against the outer ring, an inner arc centre at (ψ, z, ρ) by
    Δρ = (u_x + β z) cos ψ + (u_y + γ z) sin ψ,     Δz = u_z − ρ (β cos ψ + γ sin ψ)
(as in crossed.py). The stored energy Σ K δ₊^2.5 · 2/5 is convex in (u, balls); equilibrium is its minimum less the
work of the load P = (F_x, F_y, F_z, P_β, P_γ) (P_β = M_y, P_γ = −M_x). For each u the balls settle on their own
(vectorised Newton, each ball a 2 × 2 convex problem); the reduced energy is convex in u, its gradient is the ring
force and its Hessian (the Schur complement) is the stiffness; the ring is found by a damped Newton search. A ball
touching nothing is held half way across its gap by a spring of 10⁻¹⁰ of the contact scale (it carries nothing either
way, and the spring's pull on a loaded ball is far below the tolerances).

K for each contact at the free contact angle (the curvature sums change little with the angle); the contact stress
and ellipse at the actual angle (Hertz, hertz.py). Low speed: no centrifugal force or gyroscopic moment.
Harris & Kotzalas, Rolling Bearing Analysis, 5th ed., vol. 1, ch. 2 (geometry, clearance) and ch. 7 (load
distribution); the four-point bearing as two diagonals of a gothic arch.

Plain code: no AI, no network. N, mm, rad (µm and degrees at the edges), MPa.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq

from bearingkit import hertz as H

ThinError = ValueError
SECTIONS = ("X", "A", "C")
ARRANGEMENTS = {"DB": (+1, -1), "DF": (-1, +1)}  # facings of the rows at −s/2 and +s/2 (as taper_pair)
EPS = 1e-10


class Thin:
    def __init__(
        self,
        Dw,
        Z,
        dm,
        fi,
        fo,
        section,
        alpha_deg=None,
        Gr=0.0,
        arrangement="single",
        spacing=None,
        endplay=0.0,
        E=206000.0,
        nu=0.3,
    ):
        if section not in SECTIONS:
            raise ThinError("the thin-section bearing is four-point contact X, angular contact A or radial C")
        if not (Dw and Z and dm and Dw > 0 and dm > Dw and Z >= 3 and Z == int(Z)):
            raise ThinError(
                "give the ball diameter, the number of balls (at least 3) and a pitch diameter above the ball diameter"
            )
        if not (fi and fo and 0.5 < fi < 0.6 and 0.5 < fo < 0.6):
            raise ThinError("groove radius ratios f_i, f_o are between 0.5 and 0.6")
        if Z * Dw >= math.pi * dm:
            raise ThinError("the balls do not fit round the pitch circle (Z·D ≥ π·d_m)")
        if section in ("X", "A") and (alpha_deg is None or not 10 <= alpha_deg <= 60):
            raise ThinError("give the contact angle of the thin-section bearing (between 10° and 60°)")
        if section != "A" and arrangement != "single":
            raise ThinError("only the angular contact thin-section bearing is used in pairs here")
        if arrangement not in ("single", "DB", "DF"):
            raise ThinError("the pair is back to back (DB) or face to face (DF)")
        if arrangement != "single" and not (spacing and spacing > 0):
            raise ThinError("give the distance between the two rows")
        self.Dw, self.Z, self.dm, self.fi, self.fo = float(Dw), int(Z), float(dm), float(fi), float(fo)
        self.section, self.arr = section, arrangement
        self.alpha = math.radians(alpha_deg) if section != "C" else 0.0
        self.Gr = float(Gr) if section != "A" else 0.0
        self.e = float(endplay) if arrangement != "single" else 0.0
        self.s = float(spacing) if arrangement != "single" else 0.0
        self.Es = H.e_star(E, nu, E, nu)
        self.E, self.nu = float(E), float(nu)
        rows = (
            [(0.0, 1)]
            if arrangement == "single"
            else list(zip((-self.s / 2, self.s / 2), ARRANGEMENTS[arrangement], strict=True))
        )
        self.rows = rows
        ri, ro, R = self.fi * self.Dw, self.fo * self.Dw, self.dm / 2
        ai, ao = ri - self.Dw / 2, ro - self.Dw / 2
        sa, ca = math.sin(self.alpha), math.cos(self.alpha)
        # the arcs of one row (row centre at z = 0, facing +1): (inner?, side σ, centre z, centre ρ, f)
        if section == "C":
            arcs = [(True, 0, 0.0, R + ai, self.fi), (False, 0, 0.0, R - ao, self.fo)]
        elif section == "A":
            arcs = [(True, 1, ai * sa, R + ai * ca, self.fi), (False, 1, -ao * sa, R - ao * ca, self.fo)]
        else:
            arcs = [
                (True, 1, ai * sa, R + ai * ca, self.fi),
                (True, -1, -ai * sa, R + ai * ca, self.fi),
                (False, 1, -ao * sa, R - ao * ca, self.fo),
                (False, -1, ao * sa, R - ao * ca, self.fo),
            ]
        m = len(arcs)
        nrow = len(rows)
        N = nrow * self.Z
        self.N, self.m = N, m
        psi1 = 2 * np.pi * np.arange(self.Z) / self.Z
        self.psi = np.tile(psi1, nrow)
        self.zrow = np.repeat([z for z, _ in rows], self.Z)
        self.face = np.repeat([f for _, f in rows], self.Z)
        self.inner = np.array([a[0] for a in arcs])
        self.side = np.array([a[1] for a in arcs], float)
        self.f = np.array([a[4] for a in arcs])
        self.r = self.f * self.Dw
        self.a0 = self.r - self.Dw / 2
        C0 = np.zeros((N, m, 2))
        for k, (inn, _sd, zc, rc, _f) in enumerate(arcs):
            zc_row = self.face * zc  # a row facing −1 is the mirror image
            dz = np.where(inn, -self.face * self.e / 2, 0.0)  # the end play: the inner arc moved back along the facing
            dr = 0.0 if inn else self.Gr / 2  # the clearance on the outer ring (as the drawings put it)
            C0[:, k, 0] = self.zrow + zc_row + dz
            C0[:, k, 1] = rc + dr
        self.C0 = C0
        self.side_z = self.side[None, :] * self.face[:, None]  # which way the arc's contact faces, per ball
        # the linear map u → movement of each inner arc centre, (N, m, 2, 5)
        J = np.zeros((N, m, 2, 5))
        c, s_ = np.cos(self.psi)[:, None], np.sin(self.psi)[:, None]
        zc, rc = C0[:, :, 0], C0[:, :, 1]
        one = np.ones((N, m))
        J[:, :, 0, 2] = one
        J[:, :, 0, 3] = -rc * c
        J[:, :, 0, 4] = -rc * s_
        J[:, :, 1, 0] = c * one
        J[:, :, 1, 1] = s_ * one
        J[:, :, 1, 3] = zc * c
        J[:, :, 1, 4] = zc * s_
        J[:, ~self.inner] = 0.0
        self.J = J
        self.Dm = J[:, self.inner].mean(axis=1)  # the mean movement of a ball's inner arc centres, (N, 2, 5)
        # Hertz stiffness of each contact at the free contact angle
        self.K = np.array(
            [
                H.stiffness(H.curvatures(self.Dw, self.dm, self.alpha, f, "inner" if inn else "outer"), self.Es)
                for (inn, _s, _z, _r, f) in arcs
            ]
        )
        self.B0 = np.stack([self.zrow, np.full(N, R)], axis=1)
        self.Bw = self.B0.copy()  # warm start of the balls
        self.Kn = 1.0 / ((1 / self.K[self.inner][0]) ** (2 / 3) + (1 / self.K[~self.inner][0]) ** (2 / 3)) ** 1.5
        self.A = ai + ao  # distance of the curvature centres of a diagonal with the ball seated
        d0 = max(-self.Gr / 2 * ca, -self.e / 2 * sa, 0.0)  # the closing a preload gives, roughly
        self._pre = self.Z * self.Kn * d0**1.5  # the force scale of the preload

    # ---- the contacts for a ring displacement and ball centres
    def _contacts(self, u, B):
        C = self.C0 + np.einsum("nmij,j->nmi", self.J, np.asarray(u, float))
        d = B[:, None, :] - C
        dist = np.linalg.norm(d, axis=2)
        dl = dist - self.a0[None, :]
        return d, dist, dl

    def _balls(self, u, B, need_h=True):
        d, dist, dl = self._contacts(u, B)
        dp = np.maximum(dl, 0.0)
        K = self.K[None, :]
        Q = K * dp**1.5
        nh = d / dist[:, :, None]
        e = (K * dp**2.5 * 0.4).sum(axis=1)
        gB = (Q[:, :, None] * nh).sum(axis=1)
        out = {"d": d, "dist": dist, "dl": dl, "Q": Q, "nh": nh, "e": e, "gB": gB}
        if need_h:
            nn = nh[:, :, :, None] * nh[:, :, None, :]
            I2 = np.eye(2)[None, None]
            Hc = K[:, :, None, None] * (
                1.5 * (dp**0.5)[:, :, None, None] * nn + (dp**1.5 / dist)[:, :, None, None] * (I2 - nn)
            )
            out["Hc"] = Hc
        return out

    def _anchor(self, u):
        """Where an idle ball is held: half way across its gap (half the inner arcs' mean movement), so the holding
        spring pulls on nothing while the ball floats."""
        return self.B0 + 0.5 * np.einsum("nij,j->ni", self.Dm, np.asarray(u, float))

    def _settle(self, u, B, scale):
        """The balls in equilibrium for this ring position (each on its own, Newton with backtracking)."""
        eps = EPS * scale["k"]
        B0 = self._anchor(u)
        for _ in range(80):
            b = self._balls(u, B)
            g = b["gB"] + eps * (B - B0)
            if np.abs(g).max() <= 1e-13 * scale["Q"]:
                break
            act = np.abs(g).max(axis=1) > 1e-13 * scale["Q"]  # the balls still moving
            Hb = b["Hc"].sum(axis=1) + eps * np.eye(2)[None]
            step = -np.linalg.solve(Hb, g[:, :, None])[:, :, 0] * act[:, None]
            e0 = b["e"] + 0.5 * eps * ((B - B0) ** 2).sum(axis=1)
            t = np.ones(self.N)
            for _k in range(30):
                Bn = B + t[:, None] * step
                bn = self._balls(u, Bn, need_h=False)
                en = bn["e"] + 0.5 * eps * ((Bn - B0) ** 2).sum(axis=1)
                gn = np.abs(bn["gB"] + eps * (Bn - B0)).max(axis=1)
                bad = act & (en > e0 + 1e-4 * t * (g * step).sum(axis=1)) & (gn >= 0.5 * np.abs(g).max(axis=1))
                if not bad.any():
                    break
                t = np.where(bad, t * 0.5, t)
            B = B + t[:, None] * step
            if np.abs(t[:, None] * step).max() <= 1e-15 * self.dm:
                break
        return B

    def _reduced(self, u, B, scale):
        """Ring force (gradient of the reduced energy), the stiffness (Schur complement) and the energy."""
        eps = EPS * scale["k"]
        b = self._balls(u, B)
        Ji = self.J
        F = -np.einsum("nmij,nmi->j", Ji, b["Q"][:, :, None] * b["nh"])
        Huu = np.einsum("nmia,nmij,nmjb->ab", Ji, b["Hc"], Ji)
        HuB = -np.einsum("nmia,nmij->naj", Ji, b["Hc"])  # (N, 5, 2)
        # the holding spring between the ball and its anchor (which moves with half the ring)
        D2 = 0.5 * self.Dm
        dB = B - self._anchor(u)
        F = F - eps * np.einsum("nia,ni->a", D2, dB)
        Huu = Huu + eps * np.einsum("nia,nib->ab", D2, D2)
        HuB = HuB - eps * np.transpose(D2, (0, 2, 1))
        Hb = b["Hc"].sum(axis=1) + eps * np.eye(2)[None]
        Hinv = np.linalg.inv(Hb)
        S = Huu - np.einsum("naj,njk,nbk->ab", HuB, Hinv, HuB)
        e = b["e"].sum() + 0.5 * eps * (dB**2).sum()
        return F, S, e, b

    def scales(self, P):
        P = np.asarray(P, float)
        R = self.dm / 2
        Qs = max(np.abs(P[:3]).max(), np.abs(P[3:]).max() / R, getattr(self, "_pre", 0.0), 1.0)
        q = Qs / max(self.Z / 4, 1.0)
        a = (q / self.Kn) ** (2 / 3) + abs(self.Gr) + abs(self.e)
        return {"Q": Qs, "a": a, "k": self.Kn * a**0.5, "S": np.array([a, a, a, a / R, a / R])}

    def solve(self, P):
        """Inner ring displacement u for the outside load P; the balls are kept in self.Bw."""
        P = np.asarray(P, float)
        sc = self.scales(P)
        Qs, Sv = sc["Q"], sc["S"]
        u = np.zeros(5)
        B = self.Bw.copy()
        B = self._settle(u, B, sc)
        F, S, e, _ = self._reduced(u, B, sc)
        lam = 0.0
        ok = False

        def resid(F_):
            r = F_ - P
            return max(np.abs(r[:3]).max() / Qs, np.abs(r[3:]).max() / (Qs * self.dm / 2))

        for _ in range(200):
            rn = resid(F)
            if rn <= 1e-11:
                ok = True
                break
            g = (F - P) * Sv / Qs
            Hs = S * Sv[:, None] * Sv[None, :] / Qs
            E0 = e - P @ u
            dmax = max(np.abs(np.diag(Hs)).max(), 1.0)
            while True:
                try:
                    step = -np.linalg.solve(Hs + lam * dmax * np.eye(5), g)
                    if not np.all(np.isfinite(step)):
                        raise np.linalg.LinAlgError
                except np.linalg.LinAlgError:
                    lam = max(lam * 10, 1e-8)
                    continue
                un = u + step * Sv
                Bn = self._settle(un, B.copy(), sc)
                Fn, Sn, en, _ = self._reduced(un, Bn, sc)
                if en - P @ un <= E0 or resid(Fn) < 0.5 * rn:
                    u, B, F, S, e = un, Bn, Fn, Sn, en
                    lam = lam / 10 if lam > 1e-10 else 0.0
                    break
                lam = max(lam * 10, 1e-8)
                if lam > 1e12:
                    break
            if lam > 1e12:
                break
        if not ok:
            r = F - P
            if np.abs(r[:3]).max() > 1e-6 * Qs or np.abs(r[3:]).max() > 1e-6 * Qs * self.dm / 2:
                raise ThinError(
                    "the thin-section bearing's load distribution did not converge (the load may be more than it "
                    "can carry, or nothing holds it in that direction)"
                )
        self.Bw = B
        self._last = (u.copy(), B.copy(), sc)
        return u

    def state(self, u, B=None, sc=None):
        """Every contact at u (the balls settled): loads, angles, ring force and stiffness."""
        if B is None:
            if getattr(self, "_last", None) is not None and np.allclose(self._last[0], u, rtol=0, atol=0):
                _, B, sc = self._last
            else:
                sc = sc or self.scales(np.zeros(5))
                B = self._settle(np.asarray(u, float), self.Bw.copy(), sc)
        F, S, e, b = self._reduced(u, B, sc)
        nh = b["nh"]
        # the contact angle of each contact, positive towards the side the arc faces (from the radial direction)
        side = np.where(self.side == 0, 1.0, self.side)
        sgn = (np.where(self.inner, 1.0, -1.0) * side)[None, :] * self.face[:, None]
        ang = np.arctan2(-nh[:, :, 0] * sgn, np.abs(nh[:, :, 1]))
        return {"F": F, "S": S, "Q": b["Q"], "delta": np.maximum(b["dl"], 0.0), "angle": ang, "B": B}

    def forces(self, u):
        return self.state(u)["F"]

    def stiffness(self, u) -> dict | None:
        S = self.state(u)["S"]
        try:
            Cm = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            return None
        if not np.all(np.isfinite(Cm)) or Cm[2, 2] <= 0 or Cm[0, 0] <= 0 or Cm[3, 3] <= 0:
            return None
        return {"axial": 1 / Cm[2, 2] / 1000, "radial": 1 / Cm[0, 0] / 1000, "tilt": 1 / Cm[3, 3] / 1e6}

    def preload_force(self) -> float:
        """With no outside load: X the axial force of each diagonal (all balls); A pair the axial force of each row;
        C the contact force of one ball (radial preload). 0 with clearance or end play."""
        if (self.section == "A" and (self.arr == "single" or self.e >= 0)) or (self.section != "A" and self.Gr >= 0):
            return 0.0
        if self.section == "A":  # by symmetry the ring stays put and each ball sits on its contact line
            A, sa, ca = self.A, math.sin(self.alpha), math.cos(self.alpha)
            vz, vr = A * sa - self.e / 2, A * ca
            dl = math.hypot(vz, vr) - A
            return float(self.Z * self.Kn * dl**1.5 * vz / math.hypot(vz, vr))
        u = self.solve(np.zeros(5))
        st = self.state(u)
        Q, ang = st["Q"], st["angle"]
        if self.section == "C":
            return float(Q[:, 0].max())
        if self.section == "X":
            return float((Q[:, 0] * np.sin(ang[:, 0])).sum())  # inner arc facing +z: one diagonal
        return float((Q[: self.Z, 0] * np.abs(np.sin(ang[: self.Z, 0]))).sum())

    def contacts(self, u) -> dict:
        """Per ball and arc: load, angle, Hertz stress and ellipse; the free-play limits of each arc."""
        st = self.state(u)
        Q, ang = st["Q"], st["angle"]
        p = np.zeros_like(Q)
        a = np.zeros_like(Q)
        for n, k in zip(*np.nonzero(Q > 0), strict=True):
            ring = "inner" if self.inner[k] else "outer"
            c = H.solve(float(Q[n, k]), H.curvatures(self.Dw, self.dm, float(abs(ang[n, k])), self.f[k], ring), self.Es)
            p[n, k], a[n, k] = c.p_max, c.a
        return {"Q": Q, "angle": ang, "p": p, "a": a, "B": st["B"], "F": st["F"], "S": st["S"]}

    def apex_angle(self, k: int) -> float:
        """Where arc k meets the other arc of its ring (the gothic arch's middle), as an angle at the arc's centre from
        the radial direction; 0 for one-arc grooves (the middle plane)."""
        if self.section != "X":
            return 0.0
        zoff = abs(self.C0[0, k, 0] - self.zrow[0])
        return math.asin(min(zoff / self.r[k], 1.0))

    def shoulder_angle(self, k: int, h: float) -> float:
        """The shoulder of arc k at height h above the groove bottom (the arch's middle for X), as an angle."""
        zoff = abs(self.C0[0, k, 0] - self.zrow[0]) if self.section == "X" else 0.0
        r = self.r[k]
        depth = math.sqrt(max(r * r - zoff * zoff, 0.0))  # arc centre to the groove bottom, radially
        c = (depth - h) / r
        if not -1 < c < 1:
            raise ThinError("the shoulder height is above zero and below the groove depth")
        return math.acos(c)

    def free_play(self) -> dict:
        """Closed-form free play from the geometry (Harris ch. 2): the radial play G_r and the axial play
        G_a = 2 (√(A² − (A cos α₀ − G_r/2)²) − A sin α₀) of a four-point (X) or deep groove (C, α₀ = 0; then the
        familiar G_a = 2 √(A² − (A − P_d/2)²))."""
        A, s, c = self.A, math.sin(self.alpha), math.cos(self.alpha)
        if self.section == "A" or self.Gr < 0:
            return {"radial": None, "axial": None}
        v = A * A - (A * c - self.Gr / 2) ** 2
        return {"radial": self.Gr, "axial": 2 * (math.sqrt(max(v, 0.0)) - A * s)}


def load(Fr=0.0, Fa=0.0, M=0.0):
    return np.array([Fr, 0.0, Fa, M, 0.0])


def make(spec: dict, setting: dict) -> Thin:
    """The bearing at the clearance or end play given, or the one that gives the preload given."""

    def at(v):
        kw = dict(spec)
        if spec["section"] == "A":
            kw["endplay"] = v
        else:
            kw["Gr"] = v
        return Thin(**kw)

    if setting.get("preload") is not None:
        Fp = float(setting["preload"])
        if Fp < 0:
            raise ThinError("give the preload of the thin-section bearing (N)")
        if spec["section"] == "C":
            raise ThinError("a radial thin-section bearing is set by its clearance, not a preload force")
        if spec["section"] == "A" and spec.get("arrangement", "single") == "single":
            raise ThinError("a single angular contact row has no preload of its own: pair it")
        if Fp == 0:
            return at(0.0)
        b0 = at(0.0)
        hi = -2 * (Fp / (b0.Z * max(math.sin(b0.alpha), 1e-9) * b0.Kn)) ** (2 / 3) / max(math.cos(b0.alpha), 0.2)
        while at(hi).preload_force() < Fp:
            hi *= 2
        v = brentq(lambda x: at(x).preload_force() - Fp, hi, 0.0, xtol=1e-13, rtol=1e-12)
        return at(v)
    return at(float(setting.get("play") or 0.0))


def setting_curve(spec: dict, P, v_from_um: float, v_to_um: float, n: int = 21) -> dict:
    out = {"e_um": [], "p_max": [], "loaded": [], "k_axial": [], "k_radial": [], "k_tilt": [], "preload": []}
    for v in np.linspace(v_from_um, v_to_um, n):
        b = make(spec, {"play": v / 1000})
        out["e_um"].append(float(v))
        out["preload"].append(b.preload_force())
        try:
            u = b.solve(P)
            c = b.contacts(u)
            st = b.stiffness(u) or {}
        except ThinError:
            for k in ("p_max", "loaded", "k_axial", "k_radial", "k_tilt"):
                out[k].append(None)
            continue
        out["p_max"].append(float(c["p"].max()))
        out["loaded"].append(int(np.count_nonzero(c["Q"].sum(axis=1) > 0)))
        out["k_axial"].append(st.get("axial"))
        out["k_radial"].append(st.get("radial"))
        out["k_tilt"].append(st.get("tilt"))
    return out
