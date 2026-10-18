"""Globoidal (roller gear) indexing cam (round 39, step 4): rib surfaces by envelope, pressure angle, rib thickness,
undercut, engagement and contact stress.

Frame (fixed): turret centre T at the origin, turret axis along y; the cam axis is the line x = C, y = 0, along z.
Roller i points outwards from the turret centre in the xz-plane, u_i = (cos φ_i, 0, sin φ_i), φ_i = h·φ(θ) + φ0 + 2πi/n;
it spans ρ ∈ [ρ1, ρ2] from T (ρ1 = R_p − b/2, ρ2 = R_p + b/2), radius r_r. The cam turns by θ about +z.

Velocities per unit cam speed of the roller-axis point A = ρ·u relative to the cam:
    v_rel = (−ρ φ_i′ sin φ_i,  C − ρ cos φ_i,  ρ φ_i′ cos φ_i)
Contact (the condition of meshing, Litvin & Fuentes ch. 6): the cylinder's normal n is perpendicular to the roller axis
and to v_rel at A, so n = ±(u × v_rel)/|u × v_rel| and the contact point is A + r_r·n (both flanks of each groove).
Pressure angle (n against the roller's direction of motion t = du/dφ):
    tan α = ρ φ′ / (C − ρ cos φ)     (the formula given for roller gear cams in Rothbart, Cam Design Handbook, and
                                      刘昌祺《自动机械凸轮机构实用设计手册》; checked here against the envelope itself)
Rib thickness between two neighbouring rollers, across the bisector at the foot of radius ρ on the roller axes
(d = ρ cos(π/n) from T): 2(d sin(π/n) − r_r)/cos(π/n) = 2ρ sin(π/n) − 2 r_r / cos(π/n).

Plain code: no AI, no network. Lengths mm, angles rad inside (degrees at the edge).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from camkit.analyze import _num
from camkit.program import Program

PASS, FAIL, UNKNOWN, NA, INFO = "pass", "fail", "unknown", "na", "info"
KEYS = ("C", "n", "Rp", "rr", "b", "L", "clearance", "phase_deg", "hand", "core")


class GloboidError(ValueError):
    pass


@dataclass
class Globoid:
    C: float  # centre distance, cam axis to turret axis, mm
    n: int  # rollers on the turret
    Rp: float  # turret pitch radius (middle of the roller's contact length), mm
    rr: float  # roller radius, mm
    b: float  # contact length of a roller, mm
    L: float  # cam length along its axis, mm
    clearance: float = 1.0  # roller tip to the groove bottom, mm
    phase: float = 0.0  # φ0, rad: roller 0 at θ = 0 (π/n puts two rollers astride the rib on the centre line)
    hand: int = 1  # +1 / −1: the turret turns one way or the other for a rising program

    @property
    def rho1(self) -> float:
        return self.Rp - self.b / 2

    @property
    def rho2(self) -> float:
        return self.Rp + self.b / 2

    @property
    def core(self) -> float:
        """Radius of the cam under the groove bottom (around its axis), at the middle of the cam."""
        return self.C - self.rho2 - self.clearance

    def check(self) -> None:
        if not (self.n >= 3 and self.n == int(self.n)):
            raise GloboidError("the turret has at least 3 rollers")
        for k in ("C", "Rp", "rr", "b", "L"):
            if not getattr(self, k) > 0:
                raise GloboidError(f"give the {NAMES[k]}")
        if self.rho1 <= self.rr:
            raise GloboidError("the rollers start too close to the turret centre: make the pitch radius larger")
        if self.core <= 0:
            raise GloboidError("the rollers reach the cam axis: make the centre distance larger or the rollers shorter")
        if self.L / 2 > 0.9 * self.rho1:
            raise GloboidError("the cam is too long for the turret: half its length must stay inside the arc the "
                               "rollers' inner ends describe (L/2 ≤ 0.9·(R_p − b/2))")
        if self.hand not in (1, -1):
            raise GloboidError("the hand is +1 or −1")


NAMES = {"C": "centre distance", "Rp": "turret pitch radius", "rr": "roller radius", "b": "roller contact length",
         "L": "cam length"}


def globoid(d: dict) -> Globoid:
    d = d or {}
    bad = set(d) - set(KEYS)
    if bad:
        raise GloboidError(f"unknown globoidal cam field: {sorted(bad)[0]}")
    g = Globoid(
        C=_num(d.get("C")) or 0.0,
        n=int(_num(d.get("n")) or 0),
        Rp=_num(d.get("Rp")) or 0.0,
        rr=_num(d.get("rr")) or 0.0,
        b=_num(d.get("b")) or 0.0,
        L=_num(d.get("L")) or 0.0,
        clearance=_num(d.get("clearance")) if _num(d.get("clearance")) is not None else 1.0,
        phase=math.radians(_num(d.get("phase_deg")) or 0.0),
        hand=int(d.get("hand", 1)),
    )
    g.check()
    return g


def roller_angles(g: Globoid, phi: np.ndarray) -> np.ndarray:
    """(n, m): the angle of every roller at every cam angle."""
    return g.hand * phi[None, :] + g.phase + 2 * math.pi * np.arange(g.n)[:, None] / g.n


def engaged(g: Globoid, ang: np.ndarray, rho: float | None = None) -> np.ndarray:
    """A roller can touch the cam while its axis points at the cam (cos φ > 0) and lies within the cam length."""
    r = g.rho2 if rho is None else rho
    a = np.angle(np.exp(1j * ang))
    return (np.cos(a) > 0) & (np.abs(r * np.sin(a)) <= g.L / 2 + g.rr)


def contact(g: Globoid, ang, dang, rho, side):
    """Contact point (fixed frame), unit normal (from the roller into the cam), unit roller-motion direction and
    pressure angle for rollers at angles ang (any shape) turning at dang = dφ_i/dθ, at distance rho from the turret
    centre, on flank side ±1."""
    c, s = np.cos(ang), np.sin(ang)
    u = np.stack([c, np.zeros_like(c), s])
    v = np.stack([-rho * dang * s, g.C - rho * c, rho * dang * c])
    nvec = np.cross(u, v, axis=0)
    nn = nvec / np.linalg.norm(nvec, axis=0)
    A = rho * u
    P = A + side * g.rr * nn
    t = np.stack([-s, np.zeros_like(s), c])
    alpha = np.arctan2(np.abs(rho * dang), g.C - rho * c)
    return P, side * nn, t, alpha


def cam_frame(g: Globoid, P: np.ndarray, theta) -> np.ndarray:
    ct, st = np.cos(theta), np.sin(theta)
    X, Y, Z = P[0] - g.C, P[1], P[2]
    return np.stack([ct * X + st * Y, -st * X + ct * Y, Z])


def fixed_frame(g: Globoid, Q: np.ndarray, theta) -> np.ndarray:
    ct, st = np.cos(theta), np.sin(theta)
    X = ct * Q[0] - st * Q[1]
    Y = st * Q[0] + ct * Q[1]
    return np.stack([X + g.C, Y, Q[2]])


def surfaces(g: Globoid, prog: Program, m: int = 720, k: int = 9):
    """Envelope (rib flank) points in the cam frame: for every roller and side, a (3, m, k) grid over the cam angle
    and along the roller, with a mask of where the roller is engaged. Returns a list of dicts."""
    th = np.linspace(0, 2 * math.pi, m, endpoint=False)
    phi, dphi, _, _ = prog.eval(th)
    ang = roller_angles(g, phi)
    rho = np.linspace(g.rho1, g.rho2, k)
    out = []
    for i in range(g.n):
        for side in (1, -1):
            a = ang[i][:, None] * np.ones((1, k))
            da = (g.hand * dphi)[:, None] * np.ones((1, k))
            rr = np.ones((m, 1)) * rho[None, :]
            P, nrm, _, alpha = contact(g, a, da, rr, side)
            Q = cam_frame(g, P, th[:, None])
            N = cam_frame_vec(nrm, th[:, None])
            on = engaged(g, ang[i])[:, None] & (np.abs(Q[2]) <= g.L / 2)
            out.append({"roller": i, "side": side, "Q": Q, "N": N, "alpha": alpha, "on": on, "theta": th, "rho": rho})
    return out


def cam_frame_vec(V, theta):
    ct, st = np.cos(theta), np.sin(theta)
    return np.stack([ct * V[0] + st * V[1], -st * V[0] + ct * V[1], V[2]])


def flank_curvature(sf: dict) -> np.ndarray:
    """Normal curvature of a flank across the contact line (perpendicular to the roller axis), (m, k); convex
    towards the roller > 0. From the first and second fundamental forms of the (θ, ρ) grid, central differences."""
    Q, N = sf["Q"], sf["N"]  # N points into the cam
    th, rho = sf["theta"], sf["rho"]
    dt, dr = th[1] - th[0], rho[1] - rho[0]
    St = (np.roll(Q, -1, axis=1) - np.roll(Q, 1, axis=1)) / (2 * dt)
    Stt = (np.roll(Q, -1, axis=1) - 2 * Q + np.roll(Q, 1, axis=1)) / dt**2
    Sr = np.gradient(Q, dr, axis=2)
    Srr = np.gradient(Sr, dr, axis=2)
    Str = np.gradient(St, dr, axis=2)
    n_out = -N
    E, F, Gm = (St * St).sum(0), (St * Sr).sum(0), (Sr * Sr).sum(0)
    L2, M2, N2 = (Stt * n_out).sum(0), (Str * n_out).sum(0), (Srr * n_out).sum(0)
    # direction in the tangent plane perpendicular to the contact line (the ρ direction): d = a·S_θ + c·S_ρ, d ⟂ S_ρ
    a = np.ones_like(E)
    c = -F / Gm
    num = L2 * a * a + 2 * M2 * a * c + N2 * c * c
    den = E * a * a + 2 * F * a * c + Gm * c * c
    return -num / den


def undercut(g: Globoid, prog: Program, pts: np.ndarray, m: int = 1440, tol: float = 1e-3) -> np.ndarray:
    """For cam-frame points pts (3, N): True where some roller, at some cam angle, passes through the point by more
    than tol (the point is cut away: undercut or interference)."""
    th = np.linspace(0, 2 * math.pi, m, endpoint=False)
    phi, _, _, _ = prog.eval(th)
    ang = roller_angles(g, phi)
    hit = np.zeros(pts.shape[1], dtype=bool)
    for j in range(m):
        P = fixed_frame(g, pts, th[j])
        for i in range(g.n):
            if not engaged(g, ang[i, j : j + 1])[0]:
                continue
            u = np.array([math.cos(ang[i, j]), 0.0, math.sin(ang[i, j])])
            along = u @ P
            radial = np.linalg.norm(P - np.outer(u, along), axis=0)
            inside = (along > g.rho1 + tol) & (along < g.rho2 - tol) & (radial < g.rr - tol)
            hit |= inside
    return hit


def thickness(g: Globoid) -> dict:
    """Rib thickness between neighbouring rollers at the roller's inner end (thinnest) and at the pitch radius."""
    def t(r):
        return 2 * r * math.sin(math.pi / g.n) - 2 * g.rr / math.cos(math.pi / g.n)
    return {"root": t(g.rho1), "pitch": t(g.Rp)}


def analyse(project: dict, m: int = 720) -> dict:
    """Checks and curves of a globoidal indexing cam."""
    prog = Program.from_dict(project.get("program") or {})
    if prog.unit != "rad":
        raise GloboidError("a globoidal cam turns the turret: its program is in angle")
    g = globoid(project.get("globoidal"))
    lim = project.get("limits") or {}
    th = np.linspace(0, 2 * math.pi, m, endpoint=False)
    phi, dphi, ddphi, _ = prog.eval(th)
    ang = roller_angles(g, phi)
    # pressure angle at the pitch radius of every engaged roller; the largest at each cam angle
    on = engaged(g, ang, g.Rp)
    alpha = np.arctan2(np.abs(g.Rp * g.hand * dphi)[None, :], g.C - g.Rp * np.cos(ang))
    alpha = np.where(on, alpha, np.nan)
    a_min = np.nanmin(alpha, axis=0)  # the roller in the best position carries the load
    a_max_all = float(np.nanmax(alpha))
    nin = on.sum(axis=0)
    tk = thickness(g)
    checks = []
    lim_a = _num(lim.get("phi_rise_deg"))
    worst = float(np.degrees(np.nanmax(a_min)))
    checks.append(_ck("pressure", "最大压力角（承载滚子）", "Largest pressure angle (loaded roller)", worst, lim_a,
                      UNKNOWN if lim_a is None else (PASS if worst <= lim_a else FAIL), "°",
                      "" if lim_a is not None else "give the allowed pressure angle",
                      deg=float(np.degrees(th[int(np.nanargmax(a_min))]))))
    checks.append(_ck("engage", "啮合连续（每个转角至少两个滚子在槽里）", "Two rollers always in grooves",
                      int(nin.min()), 2, PASS if nin.min() >= 2 else FAIL, ""))
    lim_t = _num(lim.get("rib_min"))
    checks.append(_ck("rib", "凸轮筋最薄处厚度", "Thinnest rib", tk["root"], lim_t,
                      FAIL if tk["root"] <= 0 else (INFO if lim_t is None else (PASS if tk["root"] >= lim_t else FAIL)),
                      "mm", "" if tk["root"] > 0 else "neighbouring rollers overlap: fewer or thinner rollers"))
    # undercut: sample contact points on every flank and see whether a roller cuts them away later
    sfs = surfaces(g, prog, m=180, k=5)
    pts = np.concatenate([s["Q"][:, s["on"]] for s in sfs], axis=1)
    hit = undercut(g, prog, pts, m=720)
    frac = float(hit.mean()) if hit.size else 0.0
    checks.append(_ck("undercut", "不根切、无干涉（接触点不被别的滚子切掉）", "No undercut or interference",
                      round(100 * frac, 3), 0, PASS if frac == 0 else FAIL, "%",
                      "" if frac == 0 else "part of the flank is cut away by a roller: check the motion law and sizes"))
    checks.append(_ck("core", "凸轮槽底到轴线的半径", "Groove bottom to cam axis", g.core, None, INFO, "mm"))
    status = FAIL if any(c["status"] == FAIL for c in checks) else (
        UNKNOWN if any(c["status"] == UNKNOWN for c in checks) else PASS)
    step = max(1, m // 360)
    idx = np.arange(0, m, step)
    return {
        "status": status,
        "checks": checks,
        "joints": prog.joints(),
        "curves": {
            "deg": np.degrees(th[idx]).round(3).tolist(),
            "phi_deg": np.degrees(phi[idx]).round(5).tolist(),
            "v": (dphi[idx]).round(6).tolist(),
            "a": (ddphi[idx]).round(6).tolist(),
            "alpha_deg": np.degrees(a_min[idx]).round(4).tolist(),
            "in_groove": nin[idx].tolist(),
        },
        "geometry": {"C": g.C, "n": g.n, "Rp": g.Rp, "rr": g.rr, "b": g.b, "L": g.L, "rho1": g.rho1, "rho2": g.rho2,
                     "core": g.core, "phase_deg": math.degrees(g.phase), "hand": g.hand, "rib": tk,
                     "alpha_all_deg": math.degrees(a_max_all)},
        "unit": "rad",
    }


def _ck(cid, zh, en, value, limit, status, unit, note="", deg=None):
    nz = (note.replace("give the allowed pressure angle", "请填许用压力角")
          .replace("neighbouring rollers overlap: fewer or thinner rollers", "相邻滚子重叠：减少滚子数或减小滚子半径")
          .replace("part of the flank is cut away by a roller: check the motion law and sizes",
                   "部分齿面被别的滚子切掉：请检查运动规律和尺寸"))
    return {"id": cid, "zh": zh, "en": en, "value": value, "limit": limit, "status": status, "unit": unit, "note": note,
            "note_zh": nz, "deg": deg}
