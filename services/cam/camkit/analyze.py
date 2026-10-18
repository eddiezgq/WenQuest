"""One project in, curves and checks out (第 39 轮).

A project (dict, as the web app and the FreeCAD workbench send it):
    {"program": {...see program.Program.from_dict...},
     "mechanism": {"follower", "contact", "rb", "rr", "e", "a", "L", "sigma", "groove", "width"},
     "loads": {"rpm", "mass" | "inertia", "k", "preload", "load"},
     "material": {"E1", "nu1", "E2", "nu2"},
     "limits": {"phi_rise_deg", "phi_return_deg", "rho_min", "stress", "torque"}}
Lengths mm, angles in degrees at the edge, forces N, stresses MPa.

Every check has a status: pass, fail, unknown (data missing: never a pass), na (does not apply) or info (a value
with no limit given). Plain code: no AI, no network.
"""

from __future__ import annotations

from math import degrees, isfinite, radians

import numpy as np

from camkit import disk as D
from camkit import dynamics as Y
from camkit.program import Program

PASS, FAIL, UNKNOWN, NA, INFO = "pass", "fail", "unknown", "na", "info"
MECH_KEYS = ("follower", "contact", "rb", "rr", "e", "a", "L", "sigma", "groove", "width")


def _num(v):
    if v in (None, ""):
        return None
    x = float(v)
    if not isfinite(x):
        raise ValueError("numbers must be finite")
    return x


def mechanism(d: dict) -> D.Mechanism:
    d = d or {}
    bad = set(d) - set(MECH_KEYS)
    if bad:
        raise D.GeometryError(f"unknown mechanism field: {sorted(bad)[0]}")
    m = D.Mechanism(
        follower=d.get("follower", "translating"),
        contact=d.get("contact", "roller"),
        rb=_num(d.get("rb")) or 0.0,
        rr=_num(d.get("rr")) or 0.0,
        e=_num(d.get("e")) or 0.0,
        a=_num(d.get("a")) or 0.0,
        L=_num(d.get("L")) or 0.0,
        sigma=int(d.get("sigma", 1)),
        groove=bool(d.get("groove", False)),
        width=_num(d.get("width")) or 0.0,
    )
    m.check()
    return m


def loads(d: dict) -> Y.Loads:
    d = d or {}
    return Y.Loads(
        rpm=_num(d.get("rpm")),
        mass=_num(d.get("mass")),
        inertia=_num(d.get("inertia")),
        k=_num(d.get("k")) or 0.0,
        preload=_num(d.get("preload")) or 0.0,
        load=_num(d.get("load")) or 0.0,
    )


def material(d: dict) -> Y.Material:
    d = d or {}
    return Y.Material(E1=_num(d.get("E1")), nu1=_num(d.get("nu1")), E2=_num(d.get("E2")), nu2=_num(d.get("nu2")))


def _check(cid, zh, en, value, limit, status, unit="", note=""):
    return {"id": cid, "zh": zh, "en": en, "value": value, "limit": limit, "unit": unit, "status": status, "note": note}


def _phase_mask(geo):
    """Where the follower rises (s' > 0) and where it returns (s' < 0)."""
    s1 = geo["s1"]
    tol = 1e-9 * max(1.0, float(np.max(np.abs(s1))))
    return s1 > tol, s1 < -tol


def checks(prog: Program, m: D.Mechanism, geo: dict, ld: Y.Loads, mat: Y.Material, lim: dict) -> list[dict]:
    out = []
    joints = prog.joints()
    rigid = [j for j in joints if j["kind"] == "velocity"]
    soft = [j for j in joints if j["kind"] == "acceleration"]
    out.append(
        _check(
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
    out.append(
        _check(
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
    # pressure angle, rise and return separately
    up, down = _phase_mask(geo)
    for cid, zh, en, mask, key in (
        ("phi_rise", "推程最大压力角", "Max pressure angle, rise", up, "phi_rise_deg"),
        ("phi_return", "回程最大压力角", "Max pressure angle, return", down, "phi_return_deg"),
    ):
        val = float(degrees(np.max(geo["phi"][mask]))) if np.any(mask) else None
        limit = _num(lim.get(key))
        if val is None:
            st = NA
        elif limit is None:
            st = UNKNOWN
        else:
            st = PASS if val <= limit else FAIL
        out.append(
            _check(
                cid,
                zh,
                en,
                val,
                limit,
                st,
                "°",
                "" if limit is not None or val is None else "give the allowed pressure angle",
            )
        )
    # curvature: undercut (always decidable) and the minimum radius against the company's limit
    rp = geo["rho_profile"]
    if m.contact == "flat":
        cusp = bool(np.any(rp <= 0))
        out.append(
            _check(
                "undercut",
                "廓线不变尖、不根切（平底：曲率半径处处大于 0）",
                "No cusp or undercut (flat face: radius of curvature > 0)",
                float(np.min(rp)),
                0,
                FAIL if cusp else PASS,
                "mm",
            )
        )
        conv = rp
    elif m.contact == "knife":
        conv = geo["rho_pitch"][geo["rho_pitch"] > 0]
        out.append(_check("undercut", "廓线连续（尖顶）", "Profile continuous (knife edge)", None, None, PASS))
    else:
        rho = geo["rho_pitch"]
        convex = rho > 0
        bad_inner = bool(np.any(convex & (rho <= m.rr)))
        bad_outer = bool(m.groove and np.any(~convex & (np.abs(rho) <= m.rr)))
        worst = float(np.min(rho[convex])) if np.any(convex) else None
        out.append(
            _check(
                "undercut",
                "不根切（理论廓线凸处曲率半径大于滚子半径" + ("，槽外侧凹处同样" if m.groove else "") + "）",
                "No undercut (convex pitch radius above roller radius"
                + (", and the groove's outer flank" if m.groove else "")
                + ")",
                worst,
                m.rr,
                FAIL if (bad_inner or bad_outer) else PASS,
                "mm",
                "outer flank undercut" if bad_outer else "",
            )
        )
        conv = (rho - m.rr)[convex]
    rho_min = float(np.min(conv)) if len(conv) else None
    lim_rho = _num(lim.get("rho_min"))
    out.append(
        _check(
            "rho_min",
            "实际廓线最小曲率半径",
            "Min radius of curvature of the profile",
            rho_min,
            lim_rho,
            INFO if lim_rho is None else (PASS if rho_min is not None and rho_min >= lim_rho else FAIL),
            "mm",
        )
    )
    # forces at speed
    fz = Y.forces(m.follower, geo, ld)
    if m.groove:
        out.append(
            _check("jump", "高速不跳离", "Stays on the cam at speed", None, None, NA, "", "groove cam: form-closed")
        )
        if fz is not None:
            sign = np.sign(fz["force"])
            cross = int(np.count_nonzero(np.diff(np.concatenate([sign, sign[:1]])) != 0))
            out.append(
                _check(
                    "flank_change",
                    "滚子换侧次数（槽间隙处冲击）",
                    "Roller changes flank (impact across the clearance)",
                    cross,
                    None,
                    INFO,
                    "per turn",
                )
            )
    else:
        nj = Y.jump_speed(m.follower, geo, ld)
        if nj is None or ld.rpm is None:
            out.append(
                _check(
                    "jump",
                    "高速不跳离",
                    "Stays on the cam at speed",
                    nj,
                    ld.rpm,
                    UNKNOWN,
                    "r/min",
                    "give the speed and the follower mass" if ld.rpm is None or nj is None else "",
                )
            )
        else:
            out.append(
                _check(
                    "jump",
                    "高速不跳离（不跳离的最高转速）",
                    "Stays on the cam (highest speed without jump)",
                    nj,
                    ld.rpm,
                    PASS if nj > ld.rpm else FAIL,
                    "r/min",
                )
            )
    # contact stress
    lim_s = _num(lim.get("stress"))
    if m.contact == "knife":
        out.append(
            _check("stress", "接触应力", "Contact stress", None, lim_s, NA, "MPa", "knife edge: not a line contact")
        )
    else:
        sig = (
            Y.hertz(fz["contact"], m.rr if m.contact == "roller" else None, geo["rho_profile"], m.width, mat)
            if fz is not None
            else None
        )
        smax = float(np.nanmax(sig)) if sig is not None and np.any(np.isfinite(sig)) else None
        if smax is None or lim_s is None:
            note = []
            if fz is None:
                note.append("speed and mass")
            if not m.width or None in (mat.E1, mat.nu1, mat.E2, mat.nu2):
                note.append("contact width and materials")
            if lim_s is None:
                note.append("allowed contact stress")
            out.append(
                _check(
                    "stress",
                    "最大接触应力",
                    "Max contact stress",
                    smax,
                    lim_s,
                    UNKNOWN,
                    "MPa",
                    "give " + ", ".join(note),
                )
            )
        else:
            out.append(
                _check(
                    "stress", "最大接触应力", "Max contact stress", smax, lim_s, PASS if smax <= lim_s else FAIL, "MPa"
                )
            )
    # torque
    lim_t = _num(lim.get("torque"))
    if fz is None:
        out.append(
            _check(
                "torque",
                "凸轮轴峰值力矩",
                "Peak camshaft torque",
                None,
                lim_t,
                UNKNOWN,
                "N·m",
                "give the speed and the follower mass",
            )
        )
    else:
        tmax = float(np.max(np.abs(fz["torque"]))) / 1000
        out.append(
            _check(
                "torque",
                "凸轮轴峰值力矩",
                "Peak camshaft torque",
                tmax,
                lim_t,
                INFO if lim_t is None else (PASS if tmax <= lim_t else FAIL),
                "N·m",
            )
        )
    return out


def analyse(project: dict, n: int = 3600, out_n: int = 361) -> dict:
    prog = Program.from_dict(project.get("program") or {})
    m = mechanism(project.get("mechanism"))
    ld, mat = loads(project.get("loads")), material(project.get("material"))
    lim = project.get("limits") or {}
    geo = D.analyse(m, prog, n)
    cks = checks(prog, m, geo, ld, mat, lim)
    fz = Y.forces(m.follower, geo, ld)
    step = n // (out_n - 1) if out_n > 1 else 1
    idx = np.arange(0, n, max(1, step))

    def pick(a):
        return None if a is None else np.asarray(a)[..., idx].round(6).tolist()

    w = Y.omega(ld.rpm) if ld.rpm else None
    curves = {
        "deg": np.degrees(geo["theta"][idx]).round(4).tolist(),
        "s": pick(geo["s"]),
        "v": pick(geo["s1"]),
        "a": pick(geo["s2"]),
        "phi_deg": pick(np.degrees(geo["phi_signed"])),
        "rho_profile": pick(geo["rho_profile"]),
    }
    if w is not None:
        scale = 1e-3 if m.follower == "translating" else 1.0
        curves |= {"vel": pick(geo["s1"] * w * scale), "acc": pick(geo["s2"] * w**2 * scale)}
    if fz is not None:
        curves |= {"force": pick(fz["force"]), "torque_Nm": pick(fz["torque"] / 1000)}
    shapes = {"profile": pick(geo["profile"]), "pitch": pick(geo["pitch"]), "outer": pick(geo["outer"])}
    status = (
        FAIL if any(c["status"] == FAIL for c in cks) else UNKNOWN if any(c["status"] == UNKNOWN for c in cks) else PASS
    )
    return {
        "status": status,
        "checks": cks,
        "joints": prog.joints(),
        "curves": curves,
        "shapes": shapes,
        "lift": prog.lift(),
        "unit": prog.unit,
        "psi0_deg": None if geo["psi0"] is None else degrees(geo["psi0"]),
    }


def min_base_radius(project: dict, tol: float = 0.01) -> dict:
    """The smallest base circle radius meeting the allowed pressure angles, no undercut and the minimum radius of
    curvature (Angeles & López-Cajún treat this as an optimisation; here the checks are monotone in r_b, so a
    bracketing search is enough). Returns {"rb", "binding"} or raises when no limit is given."""
    lim = project.get("limits") or {}
    if all(_num(lim.get(k)) is None for k in ("phi_rise_deg", "phi_return_deg", "rho_min")):
        raise ValueError("give the allowed pressure angle or minimum radius of curvature to search for")
    prog = Program.from_dict(project.get("program") or {})
    base = dict(project.get("mechanism") or {})

    def ok(rb: float) -> tuple[bool, list[str]]:
        try:
            m = mechanism(base | {"rb": rb})
            geo = D.analyse(m, prog, 1440)
        except D.GeometryError:
            return False, ["geometry"]
        cks = {c["id"]: c for c in checks(prog, m, geo, Y.Loads(), Y.Material(), lim)}
        bad = [k for k in ("phi_rise", "phi_return", "undercut", "rho_min") if cks[k]["status"] == FAIL]
        return not bad, bad

    hi = max(1.0, prog.lift() if prog.unit == "mm" else 10.0)
    for _ in range(40):
        good, _ = ok(hi)
        if good:
            break
        hi *= 1.6
    else:
        raise ValueError("no base circle up to a very large radius meets the limits")
    lo = 0.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if ok(mid)[0]:
            hi = mid
        else:
            lo = mid
    _, binding = ok(lo)
    return {"rb": round(hi, 3), "binding": binding}


__all__ = ["analyse", "checks", "min_base_radius", "radians"]
