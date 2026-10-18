"""Disk and groove cams (第 39 轮): pitch curve, profile, curvature and pressure angle.

Frames: the cam turns about the origin O1. In the fixed frame a translating follower moves along x = e (offset e),
upward = rise; an oscillating follower turns about O2 = (a, 0) with arm length L, its roller centre at
F = (a − L cos ψ, −L sin ψ), ψ = ψ0 + s, so a rise moves the roller away from O1. The cam turns by σθ, σ = +1
counter-clockwise, −1 clockwise. In the cam frame P(θ) = R(−σθ) F(θ).

Everything is computed from vectors (no sign tables), with derivatives taken analytically from the motion program:
    P' = R[F' − σ J F],   P'' = R[F'' − 2σ J F' − F],   J = rotation by +90°.
Relative to the cam, the roller centre moves with velocity rel = F' − σ J F (fixed frame); the contact normal is
perpendicular to it, and the pressure angle φ is the angle between that normal and the direction the follower moves:
    tan φ = |rel · w| / |rel × w|.
Convex parts of the pitch curve have positive radius ρ. Roller profile radius = ρ − r_r (convex positive). Plain
code: no AI, no network.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, asin, pi, sqrt

import numpy as np

from camkit.program import Program

FOLLOWERS = ("translating", "oscillating")
CONTACTS = ("roller", "flat", "knife")


class GeometryError(ValueError):
    pass


@dataclass
class Mechanism:
    follower: str = "translating"
    contact: str = "roller"
    rb: float = 40.0  # base circle radius of the cam profile, mm
    rr: float = 0.0  # roller radius, mm (roller only)
    e: float = 0.0  # offset of a translating follower, mm (+x)
    a: float = 0.0  # centre distance O1-O2 of an oscillating follower, mm
    L: float = 0.0  # arm length of an oscillating follower, mm
    sigma: int = 1  # +1 cam turns counter-clockwise, -1 clockwise
    groove: bool = False  # form-closed groove cam (roller only)
    width: float = 0.0  # face width of the contact (roller or cam), mm; for contact stress

    def check(self) -> None:
        if self.follower not in FOLLOWERS:
            raise GeometryError("the follower is translating or oscillating")
        if self.contact not in CONTACTS:
            raise GeometryError("the contact is a roller, a flat face or a knife edge")
        if self.sigma not in (1, -1):
            raise GeometryError("the cam turns counter-clockwise (+1) or clockwise (-1)")
        if not self.rb > 0:
            raise GeometryError("the base circle radius is more than 0")
        if self.contact == "roller" and not self.rr > 0:
            raise GeometryError("give the roller radius")
        if self.groove and self.contact != "roller":
            raise GeometryError("a groove cam drives a roller")
        if self.follower == "oscillating":
            if not self.a > 0:
                raise GeometryError("an oscillating follower needs the centre distance")
            if self.contact != "flat":
                if not self.L > 0:
                    raise GeometryError("an oscillating roller or knife follower needs the arm length")
                rp = self.rp
                if not (abs(self.a - self.L) < rp < self.a + self.L):
                    raise GeometryError("with this centre distance and arm the roller cannot touch the base circle")
            elif not self.rb < self.a:
                raise GeometryError("the flat face cannot touch the base circle: the centre distance is too short")
        elif self.contact != "flat" and abs(self.e) >= self.rp:
            raise GeometryError("the offset is larger than the base circle (plus roller)")

    @property
    def r(self) -> float:
        return self.rr if self.contact == "roller" else 0.0

    @property
    def rp(self) -> float:
        """Prime circle: the base circle of the pitch curve."""
        return self.rb + self.r


def _J(v):
    return np.stack([-v[1], v[0]])


def _rot(v, ang):
    c, s = np.cos(ang), np.sin(ang)
    return np.stack([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def analyse(m: Mechanism, prog: Program, n: int = 3600) -> dict:
    """Geometry over one turn, sampled at n cam angles."""
    m.check()
    if (m.follower == "oscillating") != (prog.unit == "rad"):
        raise GeometryError("an oscillating follower's program is in angle (rad); a translating one's in mm")
    th = np.linspace(0, 2 * pi, n, endpoint=False)
    s, s1, s2, _ = prog.eval(th)
    sg = m.sigma
    if m.contact == "flat":
        return _flat(m, th, s, s1, s2)
    if m.follower == "translating":
        s0 = sqrt(m.rp**2 - m.e**2)
        F = np.stack([np.full_like(th, m.e), s0 + s])
        F1 = np.stack([np.zeros_like(th), s1])
        F2 = np.stack([np.zeros_like(th), s2])
        w = np.stack([np.zeros_like(th), np.ones_like(th)])
        psi0 = None
    else:
        psi0 = acos((m.a**2 + m.L**2 - m.rp**2) / (2 * m.a * m.L))
        psi = psi0 + s
        if np.any(psi <= 0) or np.any(psi >= pi):
            raise GeometryError("the arm would swing past the line of centres")
        u_perp = np.stack([np.sin(psi), -np.cos(psi)])  # direction of increasing ψ
        F = np.stack([m.a - m.L * np.cos(psi), -m.L * np.sin(psi)])
        F1 = m.L * s1 * u_perp
        F2 = m.L * s2 * u_perp + m.L * s1**2 * np.stack([np.cos(psi), np.sin(psi)])
        w = u_perp
    rel = F1 - sg * _J(F)
    P = _rot(F, -sg * th)
    P1 = _rot(rel, -sg * th)
    P2 = _rot(F2 - 2 * sg * _J(F1) - F, -sg * th)
    speed = np.hypot(P1[0], P1[1])
    if np.any(speed < 1e-9):
        raise GeometryError("the pitch curve has a point that does not move (degenerate geometry)")
    rho = -sg * speed**3 / _cross(P1, P2)  # convex > 0
    T = P1 / speed
    n_out = sg * _J(T)
    prof = P - m.r * n_out
    outer = P + m.r * n_out if m.groove else None
    phi = np.arctan2(np.abs(_dot(rel, w)), np.abs(_cross(rel, w)))
    phi_signed = np.sign(_dot(rel, w) * _cross(rel, w) * sg) * phi
    # normal at the contact in the fixed frame, pointing from the cam to the follower
    n_fixed = _rot(n_out, sg * th)
    out = {
        "theta": th,
        "s": s,
        "s1": s1,
        "s2": s2,
        "pitch": P,
        "profile": prof,
        "outer": outer,
        "rho_pitch": rho,
        "rho_profile": rho - m.r,
        "rho_outer": (rho + m.r) if m.groove else None,
        "phi": phi,
        "phi_signed": phi_signed,
        "normal": n_fixed,
        "F": F,
        "psi0": psi0,
    }
    if m.follower == "oscillating":
        out["lever"] = m.L * np.cos(phi)  # moment arm of the contact force about O2
    return out


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _flat(m: Mechanism, th, s, s1, s2):
    """Flat-faced follower: the profile is the envelope of the face lines (one line per cam angle)."""
    sg = m.sigma
    if m.follower == "translating":
        nf = np.stack([np.zeros_like(th), np.ones_like(th)])  # face normal, fixed frame
        d, d1 = m.rb + s, s1  # face line: nf · X = d
        nf1 = np.zeros_like(nf)
        psi0 = None
    else:
        psi0 = asin(m.rb / m.a)
        psi = psi0 + s
        # the face passes through O2 along the arm (−cos ψ, −sin ψ); distance from O1 to it is a sin ψ, which grows
        # with ψ (below 90°), so a rise moves the face away from the cam centre
        nf = np.stack([np.sin(psi), -np.cos(psi)])
        nf1 = np.stack([np.cos(psi), np.sin(psi)]) * s1
        d = nf[0] * m.a  # nf · O2
        d1 = nf1[0] * m.a
    # in the cam frame: n_c = R(−σθ) nf;  n_c' = R(−σθ)(nf' − σ J nf)
    nc = _rot(nf, -sg * th)
    nc1 = _rot(nf1 - sg * _J(nf), -sg * th)
    det = nc[0] * nc1[1] - nc[1] * nc1[0]
    if np.any(np.abs(det) < 1e-12):
        raise GeometryError("the face lines have no envelope here")
    X = np.stack([(d * nc1[1] - nc[1] * d1) / det, (nc[0] * d1 - d * nc1[0]) / det])
    Xf = _rot(X, sg * th)  # contact point, fixed frame
    # curvature of the envelope, numerically on the closed curve
    h = th[1] - th[0]
    X1 = (np.roll(X, -1, axis=1) - np.roll(X, 1, axis=1)) / (2 * h)
    X2 = (np.roll(X, -1, axis=1) - 2 * X + np.roll(X, 1, axis=1)) / h**2
    sp = np.hypot(X1[0], X1[1])
    with np.errstate(divide="ignore", invalid="ignore"):
        rho = np.where(sp > 1e-9, -sg * sp**3 / _cross(X1, X2), 0.0)
    if m.follower == "translating":
        phi = np.zeros_like(th)
        along = Xf[0]  # contact position along the face
        lever = None
    else:
        O2 = np.array([[m.a], [0.0]])
        r = Xf - O2
        vel = _J(r)  # velocity direction of the face point
        vn = np.hypot(vel[0], vel[1])
        phi = np.arccos(np.clip(np.abs(_dot(nf, vel)) / np.where(vn > 0, vn, 1), 0, 1))
        along = np.hypot(r[0], r[1])
        lever = along
    out = {
        "theta": th,
        "s": s,
        "s1": s1,
        "s2": s2,
        "pitch": None,
        "profile": X,
        "outer": None,
        "rho_pitch": None,
        "rho_profile": rho,
        "rho_outer": None,
        "phi": phi,
        "phi_signed": phi,
        "normal": nf,
        "F": Xf,
        "psi0": psi0,
        "face_contact": along,
    }
    if lever is not None:
        out["lever"] = lever
    if m.follower == "translating":
        out["rho_numeric"] = rho  # kept to check the closed form
        out["rho_profile"] = m.rb + s + s2  # ρ = r_b + s + s'' (Norton; 孙桓《机械原理》)
    return out
