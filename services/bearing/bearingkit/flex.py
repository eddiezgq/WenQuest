"""The flexible bearing of a harmonic (strain wave) reducer (round 64, plan section 十八, H1).

A thin-walled deep groove ball bearing: the inner ring is pressed onto the wave generator's cam and takes its shape;
the outer ring sits in the flexspline and is bent by the balls; the deformation wave turns with the cam, so a point
of the outer ring is bent back and forth twice per turn of the cam relative to it, while the inner ring turns with
the cam and its bending is steady.

Model (plane, static, low speed):
- Cam: the radial deviation w(φ) of the inner ring from its round shape: cosine w = w₀ cos 2φ, an ellipse of
  semi-axes a, b (w = r_ellipse − d/2), or points (a trigonometric series fitted by least squares, up to the 24th
  harmonic). The inner ring raceway moves with the cam.
- Rings: thin circular rings of rectangular section, full width B, wall thickness at the groove bottom
  t_i = (d_m − D_w)/2 − d/2 and t_o = D/2 − (d_m + D_w)/2 − P_d/2; neutral radius R at the middle of the wall. The
  classical curved beam with the inextensional bending modes n ≥ 2, the uniform stretch (n = 0) and the rigid
  translation (n = 1). For a radial load per unit length q(θ) = Σ q_n cos nθ (outward positive):
      u_n = q_n R⁴ / (EI (n² − 1)²) (n ≥ 2),   u_0 = q_0 R² / (EA),   change of curvature Δκ_n = (n² − 1) u_n / R²,
  so an outward point load P at θ = 0 gives
      u(θ) = P R³/(π EI) S₂(θ) + P R/(2π EA),   Δκ(θ) = P R/(π EI) S₁(θ),   (0 ≤ θ ≤ 2π)
      S₁(θ) = Σ_{n≥2} cos nθ/(n² − 1) = 1/2 + cos θ/4 − (π − θ) sin θ/2,
      S₂(θ) = Σ_{n≥2} cos nθ/(n² − 1)² = θ² cos θ/8 − θ sin θ/4 − πθ cos θ/4 + π sin θ/4 + (π²/12 − 3/16) cos θ − 1/2.
  (Check: two opposite inward loads shorten the diameter by (π² − 8)/(4π) · P R³/EI and give the bending moments
  P R/π under the loads and P R (1/2 − 1/π) between them, the textbook ring results.)
- Balls: Z balls round the pitch circle at the cage phase ψ₀; ball j at φ_j. Its contact deflection
      δ_j = w(φ_j) − u_o(φ_j) − P_d/2,   Q_j = K_n δ_j^1.5 for δ_j > 0 (inner and outer Hertz contacts in series at
  0° contact angle, as the deep groove kernel; the raceway curvatures as made, not as bent).
- Outer load: the flexspline's reaction on the outer ring: two zones about the long axis (θ = 0 and π), each of
  half-angle β with uniform pressure and inward resultant F. Not worked out from the reducer's torque (that needs a
  formula not verified here): the user gives F and β, or leaves them blank (only the assembly bending is computed).
- Equilibrium: the ball loads minimise the complementary energy ½ QᵀCQ + Σ Q_j u_ext(φ_j) + (2/5) K^(−2/3) Σ Q_j^(5/3)
  − Σ Q_j (w(φ_j) − P_d/2) over Q ≥ 0 with the force balance of the outer ring (its translation the multipliers):
  convex, so the minimum is the solution; the loaded balls satisfy δ_j = (Q_j/K)^(2/3), the others δ_j ≤ 0.
- Stresses: bending stress at the raceway fibre, inner ring σ = +E (t_i/2) Δκ_i (its raceway is its outside), outer
  ring σ = −E (t_o/2) Δκ_o + N/A (raceway inside; N the hoop force). The cage phase is stepped through one ball
  pitch; the outer ring's alternating stress is half the range met round the ring over all phases, the mean the
  middle of it. Contact stresses from Hertz (as made).

No life or ratings (the standards' texts are not entered); limits are the user's. Not modelled: the flexspline and
its teeth, centrifugal force, the tangential creep of the balls, the groove's effect on the ring section.

Plain code: no AI, no network. N, mm, rad, MPa.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from bearingkit import ball as BL

FlexError = ValueError
NMODES = 4000  # modes summed for the zone loads (terms fall as 1/n³ or faster)
GRID = 720  # points round the ring for the stresses and the cam
POINTS_HARMONICS = 24  # highest harmonic fitted to a cam given by points


def S1(theta):
    """Σ_{n≥2} cos nθ / (n² − 1), closed form."""
    t = np.mod(np.asarray(theta, float), 2 * np.pi)
    return 0.5 + np.cos(t) / 4 - (np.pi - t) * np.sin(t) / 2


_N = np.arange(2, NMODES + 1)


def S2(theta):
    """Σ_{n≥2} cos nθ / (n² − 1)², closed form (the solution of f″ + f = −S₁ that is even about π with
    f(0) = π²/12 − 11/16; the tests compare it with the series)."""
    t = np.mod(np.asarray(theta, float), 2 * np.pi)
    c, s = np.cos(t), np.sin(t)
    return t * t * c / 8 - t * s / 4 - np.pi * t * c / 4 + np.pi * s / 4 - 3 * c / 16 + np.pi**2 * c / 12 - 0.5


@dataclass
class Ring:
    R: float  # neutral radius, mm
    t: float  # wall thickness, mm
    B: float  # width, mm
    E: float  # MPa

    @property
    def EI(self):
        return self.E * self.B * self.t**3 / 12

    @property
    def EA(self):
        return self.E * self.B * self.t

    def u_point(self, theta):
        """Radial displacement at θ per unit outward point load at 0 (mm/N), modes n ≠ 1."""
        return self.R**3 / (math.pi * self.EI) * S2(theta) + self.R / (2 * math.pi * self.EA)

    def dk_point(self, theta):
        """Change of curvature at θ per unit outward point load at 0 (1/mm per N)."""
        return self.R / (math.pi * self.EI) * S1(theta)

    def zones(self, F, beta, theta):
        """Displacement and change of curvature at θ from two uniform inward zones about 0 and π, half-angle β, each
        with inward resultant F; and the hoop force (N)."""
        if not F:
            z = np.zeros_like(np.asarray(theta, float))
            return z, z, 0.0
        p0 = F / (2 * self.R * math.sin(beta))  # N/mm along the neutral line
        n = _N[_N % 2 == 0]
        an = -(4 * p0 / math.pi) * np.sin(n * beta) / n  # Fourier coefficients of q = −p
        a0 = -2 * p0 * beta / math.pi
        c = np.cos(np.multiply.outer(np.asarray(theta, float), n))
        u = c @ (an * self.R**4 / (self.EI * (n**2 - 1.0) ** 2)) + a0 * self.R**2 / self.EA
        dk = c @ (an * self.R**2 / (self.EI * (n**2 - 1.0)))
        return u, dk, a0 * self.R


class Cam:
    """The inner ring's radial deviation w(φ) (mm) and its change of curvature."""

    def __init__(self, kind: str, r0: float, w0=None, a=None, b=None, points=None):
        self.kind, self.r0 = kind, r0
        phi = np.linspace(0, 2 * np.pi, GRID, endpoint=False)
        if kind == "cosine":
            if w0 is None or not w0 > 0:
                raise FlexError("give the cam's largest radial deformation w0")
            self.w0 = float(w0)
            self._w = lambda p: self.w0 * np.cos(2 * np.asarray(p, float))
        elif kind == "ellipse":
            if not (a and b and a >= b > 0):
                raise FlexError("give the cam ellipse's semi-axes a ≥ b > 0 (of the inner ring's bore)")
            self._w = lambda p: a * b / np.sqrt((b * np.cos(p)) ** 2 + (a * np.sin(p)) ** 2) - r0
        elif kind == "points":
            pts = sorted((float(x), float(y)) for x, y in (points or []))
            if len(pts) < 4 or pts[0][0] < 0 or pts[-1][0] >= 360:
                raise FlexError("give at least 4 cam points (angle 0° to below 360°, radial deviation in mm)")
            # a trigonometric series fitted by least squares (harmonics up to half the number of points, at most
            # POINTS_HARMONICS): the curvature needs the second derivative, which a piecewise curve would make rough
            xs, ys = np.radians([p[0] for p in pts]), np.array([p[1] for p in pts])
            m = min(len(pts) // 2 - 1, POINTS_HARMONICS)
            n = np.arange(1, m + 1)

            def basis(x):
                x = np.asarray(x, float)
                return np.concatenate(
                    [np.ones(x.shape + (1,)), np.cos(np.multiply.outer(x, n)), np.sin(np.multiply.outer(x, n))], axis=-1
                )

            cf = np.linalg.lstsq(basis(xs), ys, rcond=None)[0]
            self._w = lambda p: basis(p) @ cf
        else:
            raise FlexError("the cam is cosine, ellipse or points")
        wv = self._w(phi)
        self.coef = np.fft.rfft(wv) / GRID * 2  # w = Σ Re(c_n e^{inφ}); c_0 counted twice
        self.coef[0] /= 2
        self.max = float(wv.max())

    def w(self, phi):
        return self._w(phi)

    def dk(self, phi, R):
        """Change of curvature of a ring of neutral radius R forced to this shape (modes n ≥ 2)."""
        n = np.arange(len(self.coef))
        m = n >= 2
        c = self.coef[m] * (n[m] ** 2 - 1) / R**2
        return np.real(np.exp(1j * np.multiply.outer(np.asarray(phi, float), n[m])) @ c)

    def stretch(self):
        """Mean radial deviation (n = 0): a stretch of the inner ring if not zero."""
        return float(np.real(self.coef[0]))


def rings(d, D, B, Dw, dm, Pd, E):
    ti = (dm - Dw) / 2 - d / 2
    to = D / 2 - (dm + Dw) / 2 - Pd / 2
    if not (ti > 0 and to > 0):
        raise FlexError("the rings have no wall under the grooves: check d, D, the ball diameter and pitch diameter")
    return Ring(d / 2 + ti / 2, ti, B, E), Ring(D / 2 - to / 2, to, B, E)


def solve(bb: BL.BallBearing, cam: Cam, outer: Ring, phase: float, F=0.0, beta=None):
    """Ball loads at cage phase ψ₀ (rad): Q, δ, the outer ring's translation and the residuals."""
    Z = bb.Z
    phi = phase + 2 * np.pi * np.arange(Z) / Z
    K = bb.Kn(0.0)
    gap = cam.w(phi) - bb.Pd / 2  # what each ball must take up if the outer ring did not move
    C = outer.u_point(np.subtract.outer(phi, phi))
    uext, _dk, _N0 = outer.zones(F, beta, phi) if F else (np.zeros(Z), None, 0.0)
    rhs = gap - uext
    Qs = max(float(K * max(gap.max(), 1e-6) ** 1.5), 1.0)  # load scale

    def fun(x):
        Q = x * Qs
        Qp = np.maximum(Q, 0.0)
        e = 0.5 * Q @ C @ Q + 0.6 * K ** (-2 / 3) * np.sum(Qp ** (5 / 3)) - Q @ rhs
        g = C @ Q + K ** (-2 / 3) * Qp ** (2 / 3) - rhs
        return e / (Qs * Qs * C.max()), g * Qs / (Qs * Qs * C.max())

    cons = [
        {"type": "eq", "fun": lambda x: np.cos(phi) @ x, "jac": lambda x: np.cos(phi)},
        {"type": "eq", "fun": lambda x: np.sin(phi) @ x, "jac": lambda x: np.sin(phi)},
    ]
    x0 = np.maximum(gap, 0.0) ** 1.5 * K / Qs
    r = minimize(
        fun,
        x0,
        jac=True,
        method="SLSQP",
        bounds=[(0, None)] * Z,
        constraints=cons,
        options={"ftol": 1e-16, "maxiter": 1000},
    )
    Q = np.maximum(r.x * Qs, 0.0)
    cs, sn = np.cos(phi), np.sin(phi)
    t = _translation(C, Q, K, rhs, phi, np.flatnonzero(Q > 1e-9 * Qs))
    # polish: Newton on the loaded balls' δ_j = (Q_j/K)^(2/3) and the force balance, unknowns Q_loaded and (tx, ty)
    for _ in range(60):
        ia = np.flatnonzero(Q > 1e-12 * Qs)
        if not len(ia):
            break
        n = len(ia)
        delta = rhs - C @ Q - t[0] * cs - t[1] * sn
        res = np.concatenate([delta[ia] - (Q[ia] / K) ** (2 / 3), [-(cs @ Q), -(sn @ Q)]])
        if np.abs(res[:n]).max() <= 1e-12 * max(abs(gap).max(), 1e-9) and np.abs(res[n:]).max() <= 1e-12 * Qs:
            break
        J = np.zeros((n + 2, n + 2))
        J[:n, :n] = -C[np.ix_(ia, ia)] - np.diag((2 / 3) * K ** (-2 / 3) * Q[ia] ** (-1 / 3))
        J[:n, n], J[:n, n + 1] = -cs[ia], -sn[ia]
        J[n, :n], J[n + 1, :n] = -cs[ia], -sn[ia]
        try:
            dx = np.linalg.solve(J, -res)
        except np.linalg.LinAlgError:
            break
        Q[ia] = np.maximum(Q[ia] + dx[:n], 0.0)
        t = t + dx[n:]
    Q[Q <= 1e-12 * Qs] = 0.0
    u_o = C @ Q + uext + t[0] * cs + t[1] * sn
    delta = cam.w(phi) - u_o - bb.Pd / 2
    return {"phi": phi, "Q": Q, "delta": delta, "u_o": u_o, "t": t, "K": K}


def _translation(C, Q, K, rhs, phi, ia):
    """The outer ring's translation (tx, ty): least squares of δ_j = (Q_j/K)^(2/3) over the loaded balls."""
    if len(ia) < 2:
        return np.zeros(2)
    lhs = rhs[ia] - C[ia] @ Q - (Q[ia] / K) ** (2 / 3)
    M = np.column_stack([np.cos(phi[ia]), np.sin(phi[ia])])
    return np.linalg.lstsq(M, lhs, rcond=None)[0]


def analyse(g: dict, phases: int = 8) -> dict:
    """g: d, D, B, Dw, Z, dm, fi, fo, Pd, E, nu, cam {kind, w0 | a, b | points}, F, beta_deg."""
    bb = BL.bearing({k: g.get(k) for k in ("D", "Z", "dm", "fi", "fo", "Pd", "E", "nu")} | {"D": g["Dw"]})
    inner, outer = rings(g["d"], g["D"], g["B"], g["Dw"], g["dm"], bb.Pd, bb.E)
    c = g.get("cam") or {}
    cam = Cam(c.get("kind") or "cosine", g["d"] / 2, c.get("w0"), c.get("a"), c.get("b"), c.get("points"))
    F = float(g.get("F") or 0.0)
    beta = math.radians(g["beta_deg"]) if g.get("beta_deg") else None
    if F and not (beta and 0 < beta < math.pi / 2):
        raise FlexError("give the half-angle of the meshing zone (between 0° and 90°)")
    th = np.linspace(0, 2 * np.pi, GRID, endpoint=False)
    sig_i = bb.E * inner.t / 2 * cam.dk(th, inner.R) + bb.E * cam.stretch() / inner.R
    ue, dke, Ne = outer.zones(F, beta, th) if F else (0 * th, 0 * th, 0.0)
    runs, smin, smax = [], np.inf, -np.inf
    for k in range(phases):
        s = solve(bb, cam, outer, 2 * np.pi / bb.Z * k / phases, F, beta)
        dk = outer.dk_point(np.subtract.outer(th, s["phi"])) @ s["Q"] + dke
        N = (s["Q"].sum()) / (2 * np.pi) + Ne
        sig = -bb.E * outer.t / 2 * dk + N / (outer.B * outer.t)
        s["sig_o"] = sig
        s["u_ring"] = (
            outer.u_point(np.subtract.outer(th, s["phi"])) @ s["Q"]
            + ue
            + s["t"][0] * np.cos(th)
            + s["t"][1] * np.sin(th)
        )
        smin, smax = min(smin, sig.min()), max(smax, sig.max())
        cts = [BL.contacts(bb, q, 0.0) if q > 0 else None for q in s["Q"]]
        s["p_i"] = np.array([x["inner"].p_max if x else 0.0 for x in cts])
        s["p_o"] = np.array([x["outer"].p_max if x else 0.0 for x in cts])
        runs.append(s)
    worst = max(runs, key=lambda s: s["Q"].max())
    return {
        "inner": inner,
        "outer": outer,
        "cam": cam,
        "bearing": bb,
        "theta": th,
        "runs": runs,
        "worst": worst,
        "sig_i": sig_i,
        "sig_i_max": float(np.abs(sig_i).max()),
        "sig_o_max": float(smax),
        "sig_o_min": float(smin),
        "sig_o_amp": float((smax - smin) / 2),
        "sig_o_mean": float((smax + smin) / 2),
        "Qmax": float(max(s["Q"].max() for s in runs)),
        "p_i_max": float(max(s["p_i"].max() for s in runs)),
        "p_o_max": float(max(s["p_o"].max() for s in runs)),
        "loaded": int(min(np.count_nonzero(s["Q"] > 0) for s in runs)),
        "loaded_max": int(max(np.count_nonzero(s["Q"] > 0) for s in runs)),
        "gap_max": float(max(max(-s["delta"].min(), 0.0) for s in runs)),  # widest gap at an unloaded ball
        "stretch": cam.stretch(),
        "F": F,
    }
