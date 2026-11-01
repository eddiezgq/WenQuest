"""Angular contact ball bearings at speed, and in pairs (round 64, step 4, part 3).

1. Centrifugal force. At speed every ball is flung outwards with F_c = ½ m d_m ω_m² (m the ball mass, ω_m its
   orbital speed); the outer contact angle falls and the inner one rises, so the two contacts no longer share one
   line (Jones's quasi-static model; Harris & Kotzalas, Rolling Bearing Analysis, 5th ed., vol. 2, ch. 3). Per ball,
   with the outer groove centre at the origin, the inner groove centre at
       A = (A sin α₀ + δ_a + ℜ_i θ cos ψ,  A cos α₀ + δ_r cos ψ)        (axial, radial; A = (f_i + f_o − 1) D)
   and the ball centre at X, the contact deflections are δ_o = |X| − (f_o − ½)D, δ_i = |A − X| − (f_i − ½)D, the
   loads Q = K δ^1.5 (Hertz, each at its own contact angle), and the ball balances
       Q_i (A − X)/|A − X| − Q_o X/|X| + (0, F_c) = 0.
   At ω = 0 this is the static model of ball.py (the test checks that). The gyroscopic moment is taken as held by
   friction at the raceways (no gyroscopic spin), so it does not enter the force balance; ω_m is the pure-rolling
   cage speed at the outer contact angle (the cage speed is not known better without a raceway-control
   hypothesis, which this version does not make). Both simplifications are stated in the report.
2. Pairs. Two identical angular contact bearings on one shaft: back to back (DB, contact lines spread outwards),
   face to face (DF, contact lines meet inwards) or tandem (DT, both the same way). Rows at axial positions ±s/2;
   each faces +x or −x (σ_k = ±1). The shaft moves δ_a, δ_r and tilts θ; row k sees an axial approach
   σ_k δ_a + δ_p (the preload approach δ_p, found from the preload force, in DB/DF; DT has no preload), a radial
   δ_r + θ z_k and the tilt −σ_k θ (a rigid tilt moves a ball at radius r cos ψ axially by −θ r cos ψ). The pair
   balances F_a, F_r and M.

Plain code: no AI, no network. N, mm, rad, kg (ball density in kg/mm³), r/min.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq, fsolve, minimize

from bearingkit import ball as BB
from bearingkit import hertz as H

STEEL_DENSITY = 7.85e-6  # kg/mm³, a common value for bearing steel: the project can give its own


class SpeedError(ValueError):
    pass


class Row:
    """One angular contact ball bearing with its contact stiffness tabulated over the contact angle."""

    def __init__(self, b: BB.BallBearing, density: float = STEEL_DENSITY):
        self.b = b
        self.m = density * math.pi * b.D**3 / 6  # kg
        a = np.radians(np.linspace(0, 80, 161))
        self._a = a
        self._Ki = np.array([H.stiffness(H.curvatures(b.D, b.dm, x, b.fi, "inner"), b.Es) for x in a])
        self._Ko = np.array([H.stiffness(H.curvatures(b.D, b.dm, x, b.fo, "outer"), b.Es) for x in a])
        self.ri = (b.fi - 0.5) * b.D
        self.ro = (b.fo - 0.5) * b.D
        self.Ri = b.dm / 2 + (b.fi - 0.5) * b.D * math.cos(b.alpha0)

    def K(self, ring: str, alpha: float) -> float:
        return float(np.interp(abs(alpha), self._a, self._Ki if ring == "inner" else self._Ko))

    def Fc(self, n_rpm: float, alpha_o: float, outer_turns: bool = False) -> float:
        """Centrifugal force (N) on a ball: ½ m d_m ω_m², ω_m the pure-rolling cage speed."""
        w = n_rpm * 2 * math.pi / 60
        g = self.b.gamma(alpha_o)
        wm = w / 2 * ((1 + g) if outer_turns else (1 - g))
        return 0.5 * self.m * (self.b.dm * 1e-3) * wm * wm  # kg · m · (rad/s)² = N

    def ball(self, A1: float, A2: float, n_rpm: float, outer_turns: bool = False) -> dict:
        """Equilibrium of one ball for the inner groove centre at (A1, A2) relative to the outer one."""
        L = math.hypot(A1, A2)
        ri, ro = self.ri, self.ro
        a0 = math.atan2(A1, A2)
        if n_rpm <= 0:
            d = L - (ri + ro)
            if d <= 0:
                return {"Qi": 0.0, "Qo": 0.0, "ai": a0, "ao": a0, "di": 0.0, "do": 0.0, "Fc": 0.0}
            # static: one line, the deflection shared so that K_i δ_i^1.5 = K_o δ_o^1.5
            ki, ko = self.K("inner", a0), self.K("outer", a0)
            di = d / (1 + (ki / ko) ** (2 / 3))
            Q = ki * di**1.5
            return {"Qi": Q, "Qo": Q, "ai": a0, "ao": a0, "di": di, "do": d - di, "Fc": 0.0}
        Fc = self.Fc(n_rpm, a0, outer_turns)
        # without an inner contact the ball rests on the outer raceway under F_c alone
        do_free = (Fc / self.K("outer", 0.0)) ** (2 / 3)
        X_free = np.array([0.0, ro + do_free])
        if math.hypot(A1 - X_free[0], A2 - X_free[1]) <= ri:
            return {"Qi": 0.0, "Qo": Fc, "ai": a0, "ao": 0.0, "di": 0.0, "do": do_free, "Fc": Fc}
        scale = max(Fc, 1.0)

        def eqs(v):
            X = np.array(v)
            Lo = math.hypot(*X)
            vi = np.array([A1, A2]) - X
            Li = math.hypot(*vi)
            do, di = Lo - ro, Li - ri
            ao, ai = math.atan2(X[0], X[1]), math.atan2(vi[0], vi[1])
            Qo = self.K("outer", ao) * max(do, 0) ** 1.5
            Qi = self.K("inner", ai) * max(di, 0) ** 1.5
            f = Qi * vi / Li - Qo * X / Lo + np.array([0.0, self.Fc(n_rpm, ao, outer_turns)])
            return f / scale

        u = np.array([A1, A2]) / L
        X0 = u * (ro + max(L - ri - ro, 0) / 2)
        sol = fsolve(eqs, X0, full_output=True, xtol=1e-13)
        X = sol[0]
        if np.max(np.abs(eqs(X))) > 1e-7:
            # a start near the edge of contact can send Newton astray: find the ball by its potential energy
            # U = ⅖ K_o δ_o^2.5 + ⅖ K_i δ_i^2.5 − F_c x_r (convex), K fixed at the current angles, then polish
            Av = np.array([A1, A2])
            X = X0.copy()
            for _ in range(4):
                ko = self.K("outer", math.atan2(X[0], X[1]))
                ki = self.K("inner", math.atan2(*(Av - X)))
                fc = self.Fc(n_rpm, math.atan2(X[0], X[1]), outer_turns)

                def energy(v, ko=ko, ki=ki, fc=fc):
                    Xv = np.array(v)
                    lo, li = math.hypot(*Xv), math.hypot(*(Av - Xv))
                    do, di = max(lo - ro, 0.0), max(li - ri, 0.0)
                    e = 0.4 * ko * do**2.5 + 0.4 * ki * di**2.5 - fc * Xv[1]
                    g = ko * do**1.5 * Xv / lo - ki * di**1.5 * (Av - Xv) / li - np.array([0.0, fc])
                    return e, g

                X = minimize(energy, X, jac=True, method="BFGS", options={"gtol": 1e-10 * max(fc, 1.0)}).x
            sol = fsolve(eqs, X, full_output=True, xtol=1e-13)
            X = sol[0]
            if np.max(np.abs(eqs(X))) > 1e-6:
                raise SpeedError("a ball's equilibrium at speed did not converge")
        vi = np.array([A1, A2]) - X
        Lo, Li = math.hypot(*X), math.hypot(*vi)
        ao, ai = math.atan2(X[0], X[1]), math.atan2(vi[0], vi[1])
        do, di = Lo - ro, Li - ri
        return {
            "Qi": self.K("inner", ai) * max(di, 0) ** 1.5,
            "Qo": self.K("outer", ao) * max(do, 0) ** 1.5,
            "ai": ai,
            "ao": ao,
            "di": di,
            "do": do,
            "Fc": self.Fc(n_rpm, ao, outer_turns),
        }

    def balls(self, da: float, dr: float, th: float, n_rpm: float, psi: np.ndarray, outer_turns: bool = False):
        b = self.b
        A, a0 = b.A, b.alpha0
        out = [
            self.ball(
                A * math.sin(a0) + da + self.Ri * th * math.cos(p),
                A * math.cos(a0) + dr * math.cos(p),
                n_rpm,
                outer_turns,
            )
            for p in psi
        ]
        return {k: np.array([o[k] for o in out]) for k in out[0]}

    def forces(self, r: dict, psi: np.ndarray) -> tuple[float, float, float]:
        """Axial, radial and moment the balls put on the inner ring (as the load it carries)."""
        Fa = float(np.sum(r["Qi"] * np.sin(r["ai"])))
        Fr = float(np.sum(r["Qi"] * np.cos(r["ai"]) * np.cos(psi)))
        M = float(np.sum(r["Qi"] * np.sin(r["ai"]) * self.Ri * np.cos(psi)))
        return Fa, Fr, M


def _psi(b: BB.BallBearing, psi0_deg: float = 0.0) -> np.ndarray:
    return np.radians(psi0_deg) + 2 * np.pi * np.arange(b.Z) / b.Z


def single(
    row: Row, Fr: float, Fa: float, M: float = 0.0, n_rpm: float = 0.0, tilt: str = "fixed", outer_turns: bool = False
) -> dict:
    """One bearing at speed: δ_a, δ_r (and θ when the ring may tilt) so that the balls carry Fa, Fr (, M)."""
    if Fa < 0:
        raise SpeedError("give the axial force on the side the contact angle takes it (Fa ≥ 0)")
    psi = _psi(row.b)
    scale = max(Fr, Fa, abs(M) / row.b.dm, 1.0)
    free = tilt == "free"

    def eqs(v):
        da, dr, th = v[0], v[1], (v[2] if free else 0.0)
        fa, fr, m = row.forces(row.balls(da, dr, th, n_rpm, psi, outer_turns), psi)
        e = [(fa - Fa) / scale, (fr - Fr) / scale]
        return e + ([(m - M) / (scale * row.b.dm)] if free else [])

    # start from the static solution
    st = BB.distribute(row.b, Fr=Fr, Fa=Fa, M=M, tilt=tilt)
    v0 = [st["da"], st["dr"]] + ([st["theta"]] if free else [])
    sol = fsolve(eqs, v0, full_output=True, xtol=1e-12)
    v, ok = sol[0], sol[2] == 1
    if not ok or max(abs(e) for e in eqs(v)) > 1e-7:
        raise SpeedError("the load distribution at speed did not converge")
    th = v[2] if free else 0.0
    r = row.balls(v[0], v[1], th, n_rpm, psi, outer_turns)
    fa, fr, m = row.forces(r, psi)
    return {"psi_deg": np.degrees(psi), **r, "da": float(v[0]), "dr": float(v[1]), "theta": float(th), "M": m}


# facing σ of the rows at z = +s/2 and z = −s/2. A row facing +x (σ = +1) has its contact line meeting the axis on
# its −x side (the inner contact is axially behind the outer one), so back to back (pressure centres spread outwards)
# is (−1, +1) and face to face (−1 … meeting inwards) is (+1, −1)
ARRANGEMENTS = {"DB": (-1, +1), "DF": (+1, -1), "DT": (+1, +1)}


def preload_approach(row: Row, Fp: float) -> float:
    """Axial approach of one row carrying the preload Fp alone (at rest)."""
    if Fp <= 0:
        return 0.0
    psi = _psi(row.b)

    def f(da):
        return row.forces(row.balls(da, 0.0, 0.0, 0.0, psi), psi)[0] - Fp

    hi = 1e-4 * row.b.D
    while f(hi) < 0:
        hi *= 2
    return brentq(f, 0.0, hi, xtol=1e-15)


def pair(
    row: Row,
    arrangement: str,
    Fp: float,
    s: float,
    Fr: float,
    Fa: float,
    M: float = 0.0,
    n_rpm: float = 0.0,
    outer_turns: bool = False,
) -> dict:
    """Two identical rows at z = ±s/2 on one shaft. Fa positive along +x; the moment M about the pair centre."""
    if arrangement not in ARRANGEMENTS:
        raise SpeedError("the arrangement is DB, DF or DT")
    if arrangement == "DT" and Fa <= 0:
        raise SpeedError("a tandem pair takes axial force one way only: give Fa > 0")
    if not s > 0:
        raise SpeedError("give the distance between the two rows")
    sig = ARRANGEMENTS[arrangement]
    zs = (s / 2, -s / 2)
    dp = preload_approach(row, Fp) if arrangement != "DT" else 0.0
    psi = _psi(row.b)
    scale = max(Fr, abs(Fa), abs(M) / row.b.dm, Fp, 1.0)

    def rows(v):
        da, dr, th = v
        out = []
        for k in (0, 1):
            r = row.balls(sig[k] * da + dp, dr + th * zs[k], -sig[k] * th, n_rpm, psi, outer_turns)
            fa, fr, m = row.forces(r, psi)
            # a rigid tilt θ moves the row radially by θ z and its balls axially by −θ r cos ψ; the moment of the
            # row's axial forces about the pair centre is therefore −σ m
            out.append((r, sig[k] * fa, fr, -sig[k] * m + fr * zs[k]))
        return out

    def eqs(v):
        rr = rows(v)
        return [
            (sum(x[1] for x in rr) - Fa) / scale,
            (sum(x[2] for x in rr) - Fr) / scale,
            (sum(x[3] for x in rr) - M) / (scale * row.b.dm),
        ]

    v0 = [Fa / max(scale, 1) * 1e-3, 1e-3 * row.b.D if Fr > 0 else 0.0, 0.0]
    sol = fsolve(eqs, v0, full_output=True, xtol=1e-12)
    v = sol[0]  # judged by the residual: fsolve flags a start that is already the answer
    if max(abs(e) for e in eqs(v)) > 1e-7:
        raise SpeedError(
            "the pair's load distribution did not converge (too little preload for the load, or the load too large)"
        )
    rr = rows(v)
    return {
        "psi_deg": np.degrees(psi),
        "da": float(v[0]),
        "dr": float(v[1]),
        "theta": float(v[2]),
        "dp": dp,
        "rows": [{"z": zs[k], "facing": sig[k], **rr[k][0], "Fa": rr[k][1], "Fr": rr[k][2]} for k in (0, 1)],
    }


def stiffness(
    row: Row, arrangement: str, Fp: float, s: float, Fr: float, Fa: float, n_rpm: float = 0.0, outer_turns: bool = False
) -> dict:
    """Axial and radial stiffness of the pair (N/µm) by small load steps about the working point."""
    base = pair(row, arrangement, Fp, s, Fr, Fa, 0.0, n_rpm, outer_turns)
    dF = max(0.01 * max(Fr, abs(Fa), Fp), 1.0)
    ax = pair(row, arrangement, Fp, s, Fr, Fa + dF, 0.0, n_rpm, outer_turns)
    ra = pair(row, arrangement, Fp, s, Fr + dF, Fa, 0.0, n_rpm, outer_turns)
    return {"axial": dF / abs(ax["da"] - base["da"]) / 1000, "radial": dF / abs(ra["dr"] - base["dr"]) / 1000}
