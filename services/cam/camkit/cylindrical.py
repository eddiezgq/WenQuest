"""Cylindrical (barrel) cam (round 39, step 8; plan section 十三): a groove around a cylinder drives a roller along the
cam axis (translating follower) or swings an arm (oscillating follower, pivot axis square to the cam axis). Groove
flanks by the condition of meshing, pressure angle, undercut, flank curvature, contact stress, torque, roller sliding.

Frame (fixed): cam axis along z, the cam turns by σθ about +z. The roller axis is along x (radial at the middle of its
travel); the roller spans x ∈ [x1, x2] = [R_p − b/2, R_p + b/2] and its axis passes through c = (0, c_y, c_z):
    translating:  c = (0, 0, s(θ) − h/2)                      (the groove centred on the cam length)
    oscillating:  the arm (length L) turns about the line (t, −L, 0), t ∈ ℝ (axis x), by ψ = s(θ) − ψ_mid:
                  c = (0, L(cos ψ − 1), L sin ψ)
Roller surface: P(x, φ) = (x, c_y + ρ(x) cos φ, c_z + ρ(x) sin φ), ρ = r_r (cylinder) or r_r·x/R_p (cone, apex on the
cam axis). Outward normal n ∝ (−ρ′, cos φ, sin φ). Velocity of a roller point relative to the cam, per unit θ:
    v_rel = v_follower − σ ẑ × P,   v_follower = s′ ẑ (translating) or ψ′ x̂ × (P − O), O = (0, −L, 0) (oscillating)
Meshing (Litvin & Fuentes, Gear Geometry and Applied Theory, ch. 6): n · v_rel = 0, linear here in cos φ and sin φ:
    A cos φ + B sin φ = D,  A = −σ(x + ρρ′) − ψ′ c_z,  B = s′ (translating) or ψ′ (c_y + L),  D = σ ρ′ c_y
(translating: c_y = c_z = 0, ψ′ → 0 in A). Two roots: the two flanks of the groove. For a cylindrical roller and a
translating follower this gives tan α = s′ / x, the pressure angle of a barrel cam at radius x (Norton, Cam Design and
Manufacturing Handbook, ch. on barrel cams), largest at the groove bottom.

Pressure angle: between the contact force projected on the plane square to the roller axis (the part along the roller
axis is thrust on the roller pin) and the direction the roller centre moves. Plain code: no AI, no network. Lengths mm,
angles rad inside (degrees at the edge), forces N, torques N·mm inside (N·m at the edge).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from camkit import dynamics as Y
from camkit.globoidal import flank_curvature
from camkit.program import Program

PASS, FAIL, UNKNOWN, NA, INFO = "pass", "fail", "unknown", "na", "info"
KEYS = ("follower", "roller", "Rp", "rr", "b", "gap", "bottom", "length", "arm", "psi_mid_deg", "sigma")
NAMES = {"Rp": "pitch radius", "rr": "roller radius", "b": "roller length", "length": "cam length", "arm": "arm length"}


class CylError(ValueError):
    pass


def _num(v):
    if v in (None, ""):
        return None
    x = float(v)
    if not math.isfinite(x):
        raise CylError("numbers must be finite")
    return x


@dataclass
class Cyl:
    follower: str  # translating | oscillating
    roller: str  # cylinder | cone (apex on the cam axis)
    Rp: float  # pitch radius: the middle of the roller's length, mm
    rr: float  # roller radius (at the pitch radius for a cone), mm
    b: float  # roller length in the groove, mm
    length: float  # cam length along its axis, mm
    gap: float = 0.0  # groove width minus roller diameter (side clearance), mm
    bottom: float = 1.0  # roller tip to groove bottom, mm
    arm: float = 0.0  # oscillating: pivot to roller axis, mm
    psi_mid: float | None = None  # oscillating: the program's ψ that puts the arm square (rad); None = middle of swing
    sigma: int = 1  # cam turns +1 counter-clockwise / −1 clockwise seen from +z

    @property
    def x1(self) -> float:
        return self.Rp - self.b / 2

    @property
    def x2(self) -> float:
        return self.Rp + self.b / 2

    @property
    def k(self) -> float:
        """ρ′: the cone's radius grows by k per mm along its axis (0 for a cylinder)."""
        return self.rr / self.Rp if self.roller == "cone" else 0.0

    def rho(self, x):
        return (
            self.k * np.asarray(x, dtype=float) if self.roller == "cone" else self.rr + 0 * np.asarray(x, dtype=float)
        )

    @property
    def core(self) -> float:
        """Groove bottom radius."""
        return self.x1 - self.bottom

    def check(self, unit: str) -> None:
        if self.follower not in ("translating", "oscillating"):
            raise CylError("the follower of a cylindrical cam is translating or oscillating")
        if self.roller not in ("cylinder", "cone"):
            raise CylError("the roller is a cylinder or a cone")
        if (self.follower == "translating") != (unit == "mm"):
            raise CylError("a translating follower's program is in mm, an oscillating one's in angle")
        need = ("Rp", "rr", "b", "length") + (("arm",) if self.follower == "oscillating" else ())
        for k in need:
            if not getattr(self, k) > 0:
                raise CylError(f"give the {NAMES[k]}")
        if self.b >= self.Rp:
            raise CylError("the roller is longer than the pitch radius: the groove would reach the cam axis")
        if self.core <= 0:
            raise CylError("the groove reaches the cam axis: make the pitch radius larger or the roller shorter")
        if self.gap < 0 or self.bottom < 0:
            raise CylError("the side clearance and the bottom clearance are not negative")
        if self.sigma not in (1, -1):
            raise CylError("the cam turns +1 or −1")


def cyl(d: dict, unit: str) -> Cyl:
    d = d or {}
    bad = set(d) - set(KEYS)
    if bad:
        raise CylError(f"unknown cylindrical cam field: {sorted(bad)[0]}")
    pm = _num(d.get("psi_mid_deg"))
    c = Cyl(
        follower=d.get("follower", "translating"),
        roller=d.get("roller", "cylinder"),
        Rp=_num(d.get("Rp")) or 0.0,
        rr=_num(d.get("rr")) or 0.0,
        b=_num(d.get("b")) or 0.0,
        length=_num(d.get("length")) or 0.0,
        gap=_num(d.get("gap")) or 0.0,
        bottom=_num(d.get("bottom")) if _num(d.get("bottom")) is not None else 1.0,
        arm=_num(d.get("arm")) or 0.0,
        psi_mid=None if pm is None else math.radians(pm),
        sigma=int(d.get("sigma", 1)),
    )
    c.check(unit)
    return c


# ---------------------------------------------------------------------------------------------------- kinematics


def pose(c: Cyl, prog: Program, th):
    """Roller axis point (c_y, c_z), their θ-derivatives, and (s, s′, s″) at cam angles th."""
    s, s1, s2, _ = prog.eval(th)
    if c.follower == "translating":
        mid = (_smax(prog) + _smin(prog)) / 2
        z = s - mid
        zero = np.zeros_like(s)
        return {"cy": zero, "cz": z, "s": s, "s1": s1, "s2": s2, "psi": None, "dpsi": None}
    mid = c.psi_mid if c.psi_mid is not None else (_smax(prog) + _smin(prog)) / 2
    psi = s - mid
    return {
        "cy": c.arm * (np.cos(psi) - 1),
        "cz": c.arm * np.sin(psi),
        "s": s,
        "s1": s1,
        "s2": s2,
        "psi": psi,
        "dpsi": s1,
    }


def _smax(prog: Program) -> float:
    return float(np.max(prog.eval(np.linspace(0, 2 * math.pi, 3601))[0]))


def _smin(prog: Program) -> float:
    return float(np.min(prog.eval(np.linspace(0, 2 * math.pi, 3601))[0]))


def contact(c: Cyl, ps: dict, x, side: int):
    """Contact on flank side ±1 at axial position x (array broadcast against θ). Returns the contact point P (fixed
    frame, (3, …)), the unit normal n out of the roller into the cam, the unit direction t the roller centre moves
    (positive with s′), the pressure angle α and the relative velocity v_rel (per unit θ)."""
    x = np.asarray(x, dtype=float)
    cy, cz, s1 = ps["cy"], ps["cz"], ps["s1"]
    rho, k = c.rho(x), c.k
    sg = c.sigma
    if c.follower == "translating":
        A = -sg * (x + rho * k) + 0 * s1
        B = s1 + 0 * x
        D = sg * k * cy + 0 * x
    else:
        A = -sg * (x + rho * k) - s1 * cz
        B = s1 * (cy + c.arm) + 0 * x
        D = sg * k * cy + 0 * x
    R = np.hypot(A, B)
    base = np.arctan2(B, A)
    phi = base + side * np.arccos(np.clip(D / R, -1, 1))
    cp, sp = np.cos(phi), np.sin(phi)
    P = np.stack([x + 0 * cp, cy + rho * cp, cz + rho * sp])
    n = np.stack([-k + 0 * cp, cp, sp]) / math.sqrt(1 + k * k)
    if c.follower == "translating":
        vf = np.stack([0 * cp, 0 * cp, s1 + 0 * cp])
        t = np.stack([0 * cp, 0 * cp, 1 + 0 * cp])
    else:
        vf = s1 * np.stack([0 * cp, -P[2], P[1] + c.arm])
        t = np.stack([0 * cp, -cz + 0 * cp, cy + c.arm + 0 * cp]) / c.arm
    vcam = sg * np.stack([-P[1], P[0], 0 * cp])
    vrel = vf - vcam
    # pressure angle in the plane square to the roller axis (x): between n_⊥ and t
    nperp = np.hypot(n[1], n[2])
    cosa = np.abs(n[1] * t[1] + n[2] * t[2]) / np.where(nperp > 0, nperp, np.nan)
    alpha = np.arccos(np.clip(cosa, 0, 1))
    return P, n, t, alpha, vrel


def cam_frame(c: Cyl, V, theta):
    """Fixed-frame points or vectors at cam angle θ into the cam's own frame (the cam turned back by σθ)."""
    a = -c.sigma * np.asarray(theta, dtype=float)
    ca, sa = np.cos(a), np.sin(a)
    return np.stack([ca * V[0] - sa * V[1], sa * V[0] + ca * V[1], V[2] + 0 * ca])


def fixed_frame(c: Cyl, Q, theta):
    a = c.sigma * np.asarray(theta, dtype=float)
    ca, sa = np.cos(a), np.sin(a)
    return np.stack([ca * Q[0] - sa * Q[1], sa * Q[0] + ca * Q[1], Q[2] + 0 * ca])


def surfaces(c: Cyl, prog: Program, m: int = 720, k: int = 9) -> list[dict]:
    """Both groove flanks in the cam frame as (3, m, k) grids over θ and x (for flank_curvature: N into the cam)."""
    th = np.linspace(0, 2 * math.pi, m, endpoint=False)
    ps = pose(c, prog, th[:, None])
    x = np.linspace(c.x1, c.x2, k)[None, :]
    out = []
    for side in (1, -1):
        P, n, _, alpha, _ = contact(c, ps, x, side)
        Q = cam_frame(c, P, th[:, None])
        N = cam_frame(c, n, th[:, None])
        out.append(
            {
                "side": side,
                "Q": Q,
                "N": N,
                "alpha": alpha,
                "theta": th,
                "rho": np.linspace(c.x1, c.x2, k),
                "on": np.ones(Q.shape[1:], dtype=bool),
            }
        )
    return out


def undercut(c: Cyl, prog: Program, pts: np.ndarray, m: int = 1440, tol: float = 1e-3) -> np.ndarray:
    """True for cam-frame points pts (3, N) that the roller, at some cam angle, passes through by more than tol."""
    th = np.linspace(0, 2 * math.pi, m, endpoint=False)
    ps = pose(c, prog, th)
    hit = np.zeros(pts.shape[1], dtype=bool)
    for j in range(m):
        P = fixed_frame(c, pts, th[j])
        xa = P[0]
        rad = np.hypot(P[1] - ps["cy"][j], P[2] - ps["cz"][j])
        inside = (xa > c.x1 + tol) & (xa < c.x2 - tol) & (rad < c.rho(xa) - tol)
        hit |= inside
    return hit


def sliding(c: Cyl, ps: dict, x: np.ndarray, side: int) -> np.ndarray:
    """Sliding between roller and flank along the contact line, as a fraction of the rolling speed at the pitch radius:
    the roller spins so that it rolls without sliding at R_p; (m, k) values, 0 = pure rolling."""
    P, n, _, _, vrel = contact(c, ps, x, side)
    # roller spin ω_r about its axis (x̂ through c): surface velocity ω_r x̂ × (P − c) = ω_r (0, −(P_z − c_z), P_y − c_y)
    ry, rz = P[1] - ps["cy"], P[2] - ps["cz"]
    spin_dir = np.stack([0 * ry, -rz, ry])
    # slip = v_rel − ω_r·spin_dir; choose ω_r per θ from the pitch column (index of x closest to R_p)
    j = int(np.argmin(np.abs(x[0] - c.Rp))) if np.ndim(x) == 2 else 0
    sd, vr = spin_dir[:, :, j], vrel[:, :, j]
    wr = (vr * sd).sum(0) / np.maximum((sd * sd).sum(0), 1e-12)
    slip = vrel - wr[None, :, None] * spin_dir
    roll = np.linalg.norm(vr, axis=0)
    return np.linalg.norm(slip, axis=0) / np.where(roll > 1e-9, roll, np.nan)[:, None]


# ---------------------------------------------------------------------------------------------------- checks


def _ck(cid, zh, en, value, limit, status, unit="", note="", note_zh=""):
    return {
        "id": cid,
        "zh": zh,
        "en": en,
        "value": value,
        "limit": limit,
        "status": status,
        "unit": unit,
        "note": note,
        "note_zh": note_zh or note,
    }


def _limit_status(val, lim, higher_bad=True):
    if val is None:
        return NA
    if lim is None:
        return UNKNOWN
    return PASS if (val <= lim if higher_bad else val >= lim) else FAIL


def analyse(project: dict, m: int = 1440, k: int = 9, undercut_check: bool = True) -> dict:
    """Checks, curves and geometry of a cylindrical cam project:
    {"type": "cylindrical", "program", "cylindrical": {...KEYS}, "loads", "material", "limits"}."""
    from camkit.analyze import loads as _loads
    from camkit.analyze import material as _material

    prog = Program.from_dict(project.get("program") or {})
    if prog.advance:
        raise CylError(
            "an indexing program needs a globoidal cam: a cylindrical cam brings its follower back every turn"
        )
    c = cyl(project.get("cylindrical"), prog.unit)
    ld, mat = _loads(project.get("loads")), _material(project.get("material"))
    lim = project.get("limits") or {}
    th = np.linspace(0, 2 * math.pi, m, endpoint=False)
    ps = pose(c, prog, th[:, None])
    xs = np.linspace(c.x1, c.x2, k)[None, :]
    P1, n1, t1, a1, _ = contact(c, ps, xs, 1)
    P2, n2, _, a2, _ = contact(c, ps, xs, -1)
    alpha = np.maximum(a1, a2)  # (m, k): either flank may carry the load
    a_th = np.nanmax(alpha, axis=1)  # worst along the roller at every θ
    jp = int(np.argmin(np.abs(xs[0] - c.Rp)))
    a_pitch = alpha[:, jp]
    s1 = ps["s1"][:, 0]
    checks = []
    joints = prog.joints()
    rigid = [j for j in joints if j["kind"] == "velocity"]
    soft = [j for j in joints if j["kind"] == "acceleration"]
    checks.append(
        _ck(
            "rigid_impact",
            "无刚性冲击（速度连续）",
            "No rigid impact (velocity continuous)",
            len(rigid),
            0,
            FAIL if rigid else PASS,
            "",
            "; ".join(f"{j['deg']:.1f}°" for j in rigid),
        )
    )
    checks.append(
        _ck(
            "soft_impact",
            "无柔性冲击（加速度连续）",
            "No soft impact (acceleration continuous)",
            len(soft),
            0,
            FAIL if soft else PASS,
            "",
            "; ".join(f"{j['deg']:.1f}°" for j in soft),
        )
    )
    tol = 1e-9 * max(1.0, float(np.max(np.abs(s1))))
    for cid, zh, en, mask, key in (
        (
            "phi_rise",
            "推程最大压力角（槽底处最大）",
            "Max pressure angle, rise (largest at the groove bottom)",
            s1 > tol,
            "phi_rise_deg",
        ),
        (
            "phi_return",
            "回程最大压力角（槽底处最大）",
            "Max pressure angle, return (largest at the groove bottom)",
            s1 < -tol,
            "phi_return_deg",
        ),
    ):
        val = float(np.degrees(np.max(a_th[mask]))) if np.any(mask) else None
        limv = _num(lim.get(key))
        st = _limit_status(val, limv)
        checks.append(
            _ck(
                cid,
                zh,
                en,
                val,
                limv,
                st,
                "°",
                "give the allowed pressure angle" if st == UNKNOWN else "",
                "请填许用压力角" if st == UNKNOWN else "",
            )
        )
    # flank curvature across the contact line (convex towards the roller > 0) and undercut
    sfs = surfaces(c, prog, m=m, k=k)
    kap = [flank_curvature(s) for s in sfs]
    # undercut: sample flank points and see whether the roller passes through them at another cam angle
    if undercut_check:
        pts = np.concatenate([s["Q"][:, ::4, 1:-1].reshape(3, -1) for s in sfs], axis=1)
        hit = undercut(c, prog, pts, m=720)
        frac = float(hit.mean()) if hit.size else 0.0
        checks.append(
            _ck(
                "undercut",
                "不根切（槽侧面不被滚子切掉）",
                "No undercut (no flank cut away by the roller)",
                round(100 * frac, 3),
                0,
                PASS if frac == 0 else FAIL,
                "%",
                ""
                if frac == 0
                else "part of a flank is cut away by the roller: larger pitch radius, smaller "
                "roller or a gentler motion law",
                "" if frac == 0 else "部分槽侧面被滚子切掉：加大节圆半径、减小滚子或换更平缓的运动规律",
            )
        )
    # radius of curvature of the flanks (concave towards the roller is safe for contact; the convex one governs)
    conv = []
    for kp in kap:
        good = np.isfinite(kp) & (kp > 1e-9)
        if np.any(good):
            conv.append(float(np.min(1 / kp[good])))
    rmin = min(conv) if conv else None
    lim_rho = _num(lim.get("rho_min"))
    checks.append(
        _ck(
            "rho_min",
            "槽侧面最小曲率半径（凸处，垂直于接触线）",
            "Min radius of curvature of the flanks (convex, across the contact line)",
            rmin,
            lim_rho,
            INFO if lim_rho is None or rmin is None else (PASS if rmin >= lim_rho else FAIL),
            "mm",
        )
    )
    # forces: a groove is form-closed (no spring, no jump)
    checks.append(
        _ck(
            "jump",
            "高速不跳离",
            "Stays on the cam at speed",
            None,
            None,
            NA,
            "",
            "groove cam: form-closed",
            "槽凸轮：形封闭，不会跳离",
        )
    )
    w = Y.omega(ld.rpm) if ld.rpm else None
    inert = ld.mass if c.follower == "translating" else ld.inertia
    fz = None
    if w is not None and inert is not None:
        s2 = ps["s2"][:, 0]
        f = (ld.mass * s2 * w**2 * 1e-3 if c.follower == "translating" else ld.inertia * s2 * w**2 * 1e3) + ld.load
        # the cam pushes the roller along −n: the loaded flank is the one whose n·t has the sign opposite to f
        nt1 = (n1[:, :, jp] * t1[:, :, jp]).sum(0)
        side1 = (nt1 * np.sign(f)) < 0
        Pp = np.where(side1[None, :], P1[:, :, jp], P2[:, :, jp])
        nn = np.where(side1[None, :], n1[:, :, jp], n2[:, :, jp])
        if c.follower == "translating":
            drive = np.abs((nn * t1[:, :, jp]).sum(0))  # the share of the contact force that drives the roller
            fn = np.abs(f) / np.where(drive > 1e-9, drive, np.nan)
        else:
            pivot = np.array([0.0, -c.arm, 0.0])[:, None]
            lever = np.abs(np.cross((Pp - pivot).T, nn.T)[:, 0])  # moment arm of the contact force about the pivot axis
            fn = np.abs(f) / np.where(lever > 1e-9, lever, np.nan)
        fz = {"force": f, "contact": fn, "torque": f * s1, "side1": side1}
        sign = np.sign(np.where(np.abs(f) > 1e-12, f, 0))
        nz = sign[sign != 0]
        cross = int(np.count_nonzero(np.diff(np.concatenate([nz, nz[:1]])) != 0)) if nz.size else 0
        checks.append(
            _ck(
                "flank_change",
                "滚子换侧次数（槽侧间隙处有冲击）",
                "Roller changes flank (impact across the side clearance)",
                cross,
                None,
                INFO,
                "per turn",
                "",
                "",
            )
        )
    # contact stress (line contact, length b): roller radius at the pitch radius against the loaded flank there
    lim_s = _num(lim.get("stress"))
    smax = None
    if fz is not None and None not in (mat.E1, mat.nu1, mat.E2, mat.nu2):
        kp_pitch = np.where(fz["side1"], kap[0][:, jp], kap[1][:, jp])
        inv = 1 / float(c.rho(c.Rp)) + kp_pitch
        elastic = (1 - mat.nu1**2) / mat.E1 + (1 - mat.nu2**2) / mat.E2
        with np.errstate(invalid="ignore"):
            sig = np.sqrt(np.clip(fz["contact"] * inv, 0, None) / (math.pi * c.b * elastic))
        smax = float(np.nanmax(sig)) if np.any(np.isfinite(sig)) else None
    if smax is None or lim_s is None:
        need = []
        if fz is None:
            need.append(("speed and mass", "转速和质量"))
        if None in (mat.E1, mat.nu1, mat.E2, mat.nu2):
            need.append(("materials", "材料"))
        if lim_s is None:
            need.append(("allowed contact stress", "许用接触应力"))
        checks.append(
            _ck(
                "stress",
                "最大接触应力",
                "Max contact stress",
                smax,
                lim_s,
                UNKNOWN,
                "MPa",
                "give " + ", ".join(e for e, _ in need),
                "请填" + "、".join(z for _, z in need),
            )
        )
    else:
        checks.append(
            _ck("stress", "最大接触应力", "Max contact stress", smax, lim_s, PASS if smax <= lim_s else FAIL, "MPa")
        )
    lim_t = _num(lim.get("torque"))
    if fz is None:
        checks.append(
            _ck(
                "torque",
                "凸轮轴峰值力矩",
                "Peak camshaft torque",
                None,
                lim_t,
                UNKNOWN,
                "N·m",
                "give the speed and the follower mass",
                "请填转速和从动件质量（或转动惯量）",
            )
        )
    else:
        tmax = float(np.max(np.abs(fz["torque"]))) / 1000
        checks.append(
            _ck(
                "torque",
                "凸轮轴峰值力矩",
                "Peak camshaft torque",
                tmax,
                lim_t,
                INFO if lim_t is None else (PASS if tmax <= lim_t else FAIL),
                "N·m",
            )
        )
    # sliding of the roller on the flank (a cone with its apex on the cam axis rolls in the dwells)
    sl = sliding(c, ps, xs, 1)
    slip = float(np.nanmax(sl)) if np.any(np.isfinite(sl)) else 0.0
    checks.append(
        _ck(
            "sliding",
            "滚子滑动（槽口、槽底与节圆处线速度之差，占滚动速度）",
            "Roller sliding (speed difference along the roller, share of rolling speed)",
            round(100 * slip, 2),
            None,
            INFO,
            "%",
            "a cone roller with its apex on the cam axis slides less" if c.roller == "cylinder" else "",
            "锥形滚子（锥顶在凸轮轴线上）滑动更小" if c.roller == "cylinder" else "",
        )
    )
    # ends of the groove inside the cam length
    zmin = float(np.min(np.concatenate([s["Q"][2] for s in sfs]))) - c.gap / 2
    zmax = float(np.max(np.concatenate([s["Q"][2] for s in sfs]))) + c.gap / 2
    wall = min(c.length / 2 + zmin, c.length / 2 - zmax)
    checks.append(
        _ck(
            "end_wall",
            "槽到凸轮端面的最小壁厚",
            "Thinnest wall between the groove and an end face",
            wall,
            None,
            FAIL if wall <= 0 else INFO,
            "mm",
            "" if wall > 0 else "the groove runs out of the cam: make the cam longer",
            "" if wall > 0 else "槽超出凸轮端面：加长凸轮",
        )
    )
    status = (
        FAIL
        if any(x["status"] == FAIL for x in checks)
        else (UNKNOWN if any(x["status"] == UNKNOWN for x in checks) else PASS)
    )
    step = max(1, m // 360)
    idx = np.arange(0, m, step)

    def pick(a):
        return None if a is None else np.asarray(a)[idx].round(6).tolist()

    s0, s2v = ps["s"][:, 0], ps["s2"][:, 0]
    curves = {
        "deg": np.degrees(th[idx]).round(4).tolist(),
        "s": pick(s0),
        "v": pick(s1),
        "a": pick(s2v),
        "j": pick(prog.eval(th)[3]),
        "phi_deg": pick(np.degrees(a_th) * np.sign(s1)),
        "phi_pitch_deg": pick(np.degrees(a_pitch) * np.sign(s1)),
    }
    if w is not None:
        scale = 1e-3 if c.follower == "translating" else 1.0
        curves |= {"vel": pick(s1 * w * scale), "acc": pick(s2v * w**2 * scale)}
    if fz is not None:
        curves |= {"force": pick(fz["force"]), "torque_Nm": pick(fz["torque"] / 1000)}
    return {
        "status": status,
        "checks": checks,
        "joints": joints,
        "curves": curves,
        "lift": prog.lift(),
        "unit": prog.unit,
        "type": "cylindrical",
        "geometry": geometry(c, prog, sfs),
    }


def geometry(c: Cyl, prog: Program, sfs: list[dict] | None = None, m: int = 360) -> dict:
    """What the page draws: the groove development at the outer radius and at the pitch radius (arc length u = R·θ
    against z, both flanks), the roller centre over the turn, and the sizes."""
    th = np.linspace(0, 2 * math.pi, m + 1)
    ps = pose(c, prog, th[:, None])
    out = {
        "Rp": c.Rp,
        "rr": c.rr,
        "b": c.b,
        "x1": c.x1,
        "x2": c.x2,
        "outer": c.x2,
        "core": c.core,
        "length": c.length,
        "gap": c.gap,
        "roller": c.roller,
        "follower": c.follower,
        "arm": c.arm,
        "sigma": c.sigma,
        "k": c.k,
        "centre": {
            "deg": np.degrees(th).round(3).tolist(),
            "y": ps["cy"][:, 0].round(5).tolist(),
            "z": ps["cz"][:, 0].round(5).tolist(),
        },
    }
    dev = {}
    for name, x in (("outer", c.x2), ("pitch", c.Rp), ("bottom", c.x1)):
        sides = []
        for side in (1, -1):
            P, *_ = contact(c, ps, np.array([[x]]), side)
            Q = cam_frame(c, P, th[:, None])
            ang = np.unwrap(np.arctan2(Q[1, :, 0], Q[0, :, 0]))
            g = c.gap / 2 * (1 if side == 1 else -1)  # (the flank opposite the loaded one sits gap away; shown centred)
            sides.append({"u": (x * ang).round(4).tolist(), "z": (Q[2, :, 0] + 0 * g).round(4).tolist()})
        dev[name] = sides
    out["development"] = dev
    out["rings"] = rings(c, prog)
    return out


def rings(c: Cyl, prog: Program, m: int = 2880) -> dict:
    """For the page's 3D view: in the cam frame, at every degree of azimuth (0…360), the z of both flanks at the outer
    radius and at the roller's inner end (the groove continues straight down to its bottom). The side clearance opens
    the two flanks by gap/2 each."""
    th = np.linspace(0, 2 * math.pi, m, endpoint=False)
    ps = pose(c, prog, th[:, None])
    az = np.radians(np.arange(0, 361, 1.0))
    out = {"az_deg": list(range(0, 361))}
    for name, x in (("outer", c.x2), ("inner", c.x1)):
        zs = []
        for side in (1, -1):
            P, *_ = contact(c, ps, np.array([[x]]), side)
            Q = cam_frame(c, P, th[:, None])[:, :, 0]
            a = np.mod(np.arctan2(Q[1], Q[0]), 2 * math.pi)
            o = np.argsort(a)
            a2 = np.concatenate([a[o][-1:] - 2 * math.pi, a[o], a[o][:1] + 2 * math.pi])
            z2 = np.concatenate([Q[2][o][-1:], Q[2][o], Q[2][o][:1]])
            z = np.interp(az, a2, z2)
            zs.append(z)
        lo, hi = np.minimum(zs[0], zs[1]) - c.gap / 2, np.maximum(zs[0], zs[1]) + c.gap / 2
        out[name] = {"lo": lo.round(4).tolist(), "hi": hi.round(4).tolist()}
    return out


def min_pitch_radius(project: dict, lo: float | None = None, hi: float = 2000.0) -> dict:
    """Smallest pitch radius (mm) that keeps the pressure angle within the limits given and the flanks free of
    undercut, other sizes as given. Needs the allowed pressure angle."""
    lim = project.get("limits") or {}
    if _num(lim.get("phi_rise_deg")) is None and _num(lim.get("phi_return_deg")) is None:
        raise CylError("give the allowed pressure angle first")
    d = dict(project.get("cylindrical") or {})
    b = _num(d.get("b")) or 0.0
    bottom = _num(d.get("bottom")) if _num(d.get("bottom")) is not None else 1.0
    lo = lo or (b / 2 + bottom + 0.5)

    def ok(rp: float) -> bool:
        p = dict(project, cylindrical=dict(d, Rp=rp))
        try:
            r = analyse(p, m=720, k=5, undercut_check=True)
        except CylError:
            return False
        bad = {"phi_rise", "phi_return", "undercut"}
        return not any(x["id"] in bad and x["status"] == FAIL for x in r["checks"])

    if not ok(hi):
        raise CylError("no pitch radius up to 2000 mm meets the limits")
    for _ in range(40):
        mid = (lo + hi) / 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
        if hi - lo < 0.01:
            break
    return {"Rp": math.ceil(hi * 100) / 100}
