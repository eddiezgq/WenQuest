"""Typical application scenarios (round 64, step 3): the loads on one bearing worked out from the machine it sits in.

A scenario turns machine data into load cases on this bearing: {"label", "Fr", "Fa", "M", "n", "share"} (N, N, N·mm,
r/min, fraction of the running time), plus how the bearing moves ("rotating" or "oscillating") and which ring turns.
The arithmetic is textbook statics (forces in the plane across the shaft, beam on two supports); no factor values
are built in: load factors and allowable stresses are the user's (or a standard's, once entered).

  - gearbox:  helical or spur gear on a shaft between bearings A and B. d = m_n z / cos β, T = 9.549·10⁶ P / n (N·mm,
              P in kW), F_t = 2T/d, F_r = F_t tan α_n / cos β, F_a = F_t tan β. The axial force at the pitch radius
              adds the couple F_a·d/2 in the radial plane. Reactions of a simply supported shaft: R_A = F (L − x)/L,
              R_B = F x / L for a force F at x from A (x may lie outside the span: an overhung load).
  - motor:    rotor weight and residual unbalance (F_u = U ω², U in g·mm) at the rotor, a belt pull on an overhung
              pulley; the unbalance turns with the shaft, so the load on the bearing changes round the turn: it is
              sampled every 10°.
  - spindle:  cutting force at the nose, overhang a in front of the front bearing A, span L to the rear bearing B:
              R_A = F (a + L)/L, R_B = F a / L; the axial cutting force goes to the front bearing.
  - hub:      wheel load W, lateral force W·a_y at the tyre contact, rolling radius R: the couple W·a_y·R and the
              offset e of the wheel plane share the load between the outboard and inboard rows (spacing L); each row
              of a back-to-back pair takes the axial force in one direction. The outer ring turns.
  - joint:    robot joint or swing arm. Horizontal axis: the weight W at x along the axis is shared by the two
              bearings. Vertical axis: the weight W at radius r gives the axial force W and the tilting moment W·r,
              taken by the pair as ±W·r/L (or by a single bearing as a moment). The joint oscillates.
  - camshaft: the force from the cam (a table of cam angle, F_x, F_y, optionally F_z) at x from bearing A; the
              reactions are worked out at every angle (the output of 问渠凸轮 or the sewing-machine software).
  - generic:  the cases are given directly.

Plain code: no AI, no network. N, mm, r/min, kW, g·mm, kg.
"""

from __future__ import annotations

import math

G0 = 9.80665  # m/s², standard gravity (by definition)


class ScenarioError(ValueError):
    pass


def _f(d: dict, k: str, required: bool = True, default: float | None = None) -> float | None:
    v = d.get(k)
    if v in (None, ""):
        if required and default is None:
            raise ScenarioError(f"scenario: give {k}")
        return default
    x = float(v)
    if not math.isfinite(x):
        raise ScenarioError("numbers must be finite")
    return x


def reactions(F: float, x: float, L: float) -> tuple[float, float]:
    """Simply supported shaft, bearings A at 0 and B at L, force F at x (x outside the span: overhung)."""
    if not L > 0:
        raise ScenarioError("scenario: the bearing span L is more than 0")
    return F * (L - x) / L, F * x / L


def _which(s: dict) -> int:
    w = (s.get("this") or "A").upper()
    if w not in ("A", "B"):
        raise ScenarioError("scenario: this bearing is A or B")
    return 0 if w == "A" else 1


def _spectrum(s: dict) -> list[dict]:
    rows = s.get("cases") or []
    if not rows:
        raise ScenarioError("scenario: give at least one operating case")
    tot = sum((_f(r, "share", False, 1.0) or 0.0) for r in rows)
    if not tot > 0:
        raise ScenarioError("scenario: the time shares add up to more than 0")
    return rows


def _share(r: dict, rows: list[dict]) -> float:
    tot = sum((_f(x, "share", False, 1.0) or 0.0) for x in rows)
    return (_f(r, "share", False, 1.0) or 0.0) / tot


def _line(zh: str, en: str, value: float, unit: str) -> dict:
    return {"zh": zh, "en": en, "value": value, "unit": unit}


def gearbox(s: dict) -> dict:
    mn, z, an, beta = _f(s, "mn"), _f(s, "z"), _f(s, "alpha_n_deg"), _f(s, "beta_deg", False, 0.0)
    x, L = _f(s, "x"), _f(s, "L")
    me, fixed = _which(s), (s.get("fixed") or "A").upper()
    sign = 1.0 if (s.get("axial_to") or "B").upper() == "B" else -1.0  # the gear's axial force points to A or B
    if not (mn > 0 and z > 0 and 0 < an < 45 and 0 <= beta < 45):
        raise ScenarioError("scenario: gear module, teeth, pressure angle (0–45°) and helix angle (0–45°)")
    cb = math.cos(math.radians(beta))
    d = mn * z / cb
    rows = _spectrum(s)
    cases, steps = [], [_line("分度圆直径 d = mn·z / cos β", "Pitch diameter d = m_n z / cos β", d, "mm")]
    for k, r in enumerate(rows):
        P, n = _f(r, "P"), _f(r, "n")
        if not (P >= 0 and n > 0):
            raise ScenarioError("scenario: each case has a power ≥ 0 and a speed > 0")
        T = 9.549e6 * P / n
        Ft = 2 * T / d
        Fr = Ft * math.tan(math.radians(an)) / cb
        Fa = Ft * math.tan(math.radians(beta))
        t = reactions(Ft, x, L)  # tangential plane
        couple = sign * Fa * d / 2 / L  # the axial force at the pitch radius, in the radial plane
        rp = reactions(Fr, x, L)
        rr = (rp[0] + couple, rp[1] - couple)
        R = math.hypot(t[me], rr[me])
        axial = Fa if "AB"[me] == fixed else 0.0
        cases.append(
            {"label": r.get("label") or f"#{k + 1}", "Fr": R, "Fa": axial, "M": 0.0, "n": n, "share": _share(r, rows)}
        )
        if k == 0:
            steps += [
                _line("转矩 T = 9.549×10⁶ P / n", "Torque T = 9.549×10⁶ P / n", T, "N·mm"),
                _line("圆周力 Ft = 2T / d", "Tangential force F_t = 2T/d", Ft, "N"),
                _line("径向力 Fr = Ft·tan αn / cos β", "Radial force F_r = F_t tan α_n / cos β", Fr, "N"),
                _line("轴向力 Fa = Ft·tan β", "Axial force F_a = F_t tan β", Fa, "N"),
            ]
    return {"cases": cases, "motion": "rotating", "outer_turns": False, "steps": steps}


def motor(s: dict) -> dict:
    m, U, xr, L = _f(s, "m"), _f(s, "U", False, 0.0), _f(s, "x"), _f(s, "L")
    Fb, xb, phi = _f(s, "F_belt", False, 0.0), _f(s, "x_belt", False, 0.0), _f(s, "belt_deg", False, 0.0)
    Fa, n, me = _f(s, "Fa", False, 0.0), _f(s, "n"), _which(s)
    if not (m >= 0 and U >= 0 and n > 0):
        raise ScenarioError("scenario: rotor mass ≥ 0, unbalance ≥ 0 and a speed > 0")
    W = m * G0
    w = n * 2 * math.pi / 60
    Fu = U * 1e-6 * w * w  # g·mm → kg·m
    # static loads in the cross plane (y up, z across): weight down, belt pull at belt_deg from straight down
    gy = reactions(-W, xr, L)[me]
    by = reactions(-Fb * math.cos(math.radians(phi)), xb, L)[me]
    bz = reactions(Fb * math.sin(math.radians(phi)), xb, L)[me]
    ur = reactions(Fu, xr, L)[me]
    sy, sz = gy + by, bz
    cases = []
    for k in range(36):
        th = math.radians(10 * k)
        R = math.hypot(sy + ur * math.cos(th), sz + ur * math.sin(th))
        cases.append({"label": f"{10 * k}°", "Fr": R, "Fa": Fa, "M": 0.0, "n": n, "share": 1 / 36, "angle": 10 * k})
    steps = [
        _line("转子重力 W = m·g", "Rotor weight W = m g", W, "N"),
        _line("不平衡离心力 Fu = U·ω²", "Unbalance force F_u = U ω²", Fu, "N"),
        _line(
            "本轴承上的静载荷（重力 + 带拉力）", "Steady load on this bearing (weight + belt)", math.hypot(sy, sz), "N"
        ),
        _line("本轴承上随轴转的载荷（不平衡）", "Load turning with the shaft (unbalance)", abs(ur), "N"),
    ]
    return {
        "cases": cases,
        "motion": "rotating",
        "outer_turns": False,
        "steps": steps,
        "curve": "angle",
        "notes": [
            {
                "zh": "不平衡载荷随轴一起转，相对内圈不动：内圈承受的是“旋转载荷”，配合选择要考虑。",
                "en": "The unbalance load turns with the shaft and stands still relative to the inner ring: "
                "a rotating load for the inner ring, which the fit has to allow for.",
            }
        ]
        if Fu > 0
        else [],
    }


def spindle(s: dict) -> dict:
    a, L, me = _f(s, "a"), _f(s, "L"), _which(s)
    rows = _spectrum(s)
    cases = []
    for k, r in enumerate(rows):
        Fc, Ff, n = _f(r, "Fr"), _f(r, "Fa", False, 0.0), _f(r, "n")
        RA, RB = reactions(Fc, -a, L)  # the nose is a in front of the front bearing A
        cases.append(
            {
                "label": r.get("label") or f"#{k + 1}",
                "Fr": abs((RA, RB)[me]),
                "Fa": Ff if me == 0 else 0.0,
                "M": 0.0,
                "n": n,
                "share": _share(r, rows),
            }
        )
    Fc0 = _f(rows[0], "Fr")
    steps = [
        _line(
            "前轴承反力 RA = F·(a + L)/L（第 1 工况）",
            "Front bearing R_A = F (a + L)/L (case 1)",
            Fc0 * (a + L) / L,
            "N",
        ),
        _line("后轴承反力 RB = F·a / L（第 1 工况）", "Rear bearing R_B = F a / L (case 1)", Fc0 * a / L, "N"),
    ]
    return {"cases": cases, "motion": "rotating", "outer_turns": False, "steps": steps}


def hub(s: dict) -> dict:
    W, ay, Rw, L, e = _f(s, "W"), _f(s, "ay"), _f(s, "R"), _f(s, "L"), _f(s, "e", False, 0.0)
    row = (s.get("row") or "outboard").lower()
    if row not in ("outboard", "inboard"):
        raise ScenarioError("scenario: the row is outboard or inboard")
    n = _f(s, "n")
    shares = s.get("shares") or {}
    cases, steps = [], []
    for label, sgn, key in (
        (("直行", "straight"), 0, "straight"),
        (("转弯，侧向力朝外", "turning, lateral force outward"), 1, "out"),
        (("转弯，侧向力朝内", "turning, lateral force inward"), -1, "in"),
    ):
        Fy = sgn * W * ay
        # radial: wheel load shared by the offset, plus the couple Fy·R (positive Fy loads the outboard row)
        RO = W * (L / 2 + e) / L + Fy * Rw / L
        RI = W * (L / 2 - e) / L - Fy * Rw / L
        R = RO if row == "outboard" else RI
        takes = (Fy > 0 and row == "outboard") or (Fy < 0 and row == "inboard")
        cases.append(
            {
                "label": {"zh": label[0], "en": label[1]},
                "Fr": abs(R),
                "Fa": abs(Fy) if takes else 0.0,
                "M": 0.0,
                "n": n,
                "share": _f(shares, key, False, 1.0) or 0.0,
                "lift": R < 0,
            }
        )
        if sgn == 1:
            steps = [
                _line("侧向力 Fy = W·ay", "Lateral force F_y = W a_y", W * ay, "N"),
                _line("外排径向载荷（转弯）", "Outboard row radial load (turning)", RO, "N"),
                _line("内排径向载荷（转弯）", "Inboard row radial load (turning)", RI, "N"),
            ]
    tot = sum(c["share"] for c in cases)
    if not tot > 0:
        raise ScenarioError("scenario: the time shares add up to more than 0")
    for c in cases:
        c["share"] /= tot
    notes = []
    if any(c["lift"] for c in cases):
        notes.append(
            {
                "zh": "有工况下本排的反力为负：这一排被提离，载荷全由另一排承担；表里给的是反力的大小。",
                "en": "In some cases the reaction on this row is negative: the row lifts off and the other row "
                "carries the load; the table gives the size of the reaction.",
            }
        )
    return {"cases": cases, "motion": "rotating", "outer_turns": True, "steps": steps, "notes": notes}


def joint(s: dict) -> dict:
    axis = (s.get("axis") or "horizontal").lower()
    W, n = _f(s, "W"), _f(s, "n", False, 0.0)
    swing = _f(s, "swing_deg", False, None)
    L = _f(s, "L", False, None)
    me = _which(s)
    if axis == "horizontal":
        x = _f(s, "x")
        R = reactions(W, x, L)[me] if L else W
        case = {"label": "W", "Fr": abs(R), "Fa": 0.0, "M": 0.0, "n": n, "share": 1.0}
        steps = [_line("本轴承径向载荷", "Radial load on this bearing", abs(R), "N")]
    elif axis == "vertical":
        r = _f(s, "r")
        Mt = W * r
        fixed = (s.get("fixed") or "A").upper()
        if L:  # a pair: the moment as opposite radial forces
            case = {"label": "W", "Fr": Mt / L, "Fa": W if "AB"[me] == fixed else 0.0, "M": 0.0, "n": n, "share": 1.0}
        else:  # one bearing takes the moment itself
            case = {"label": "W", "Fr": 0.0, "Fa": W, "M": Mt, "n": n, "share": 1.0}
        steps = [_line("倾覆力矩 M = W·r", "Tilting moment M = W r", Mt, "N·mm")]
    else:
        raise ScenarioError("scenario: the joint axis is horizontal or vertical")
    notes = [
        {
            "zh": "关节来回摆动、不整圈转：以静强度为主；小角度摆动时滚动体在同一处来回碾压，易产生伪布氏压痕，"
            "润滑和摆角要注意。",
            "en": "The joint swings back and forth rather than turning: static strength governs; small swings roll "
            "the balls over the same spot and can cause false brinelling: watch the lubrication and the "
            "swing angle.",
        }
    ]
    return {
        "cases": [case],
        "motion": "oscillating",
        "outer_turns": False,
        "steps": steps,
        "notes": notes,
        "swing_deg": swing,
    }


def camshaft(s: dict) -> dict:
    x, L, n, me = _f(s, "x"), _f(s, "L"), _f(s, "n"), _which(s)
    fixed = (s.get("fixed") or "A").upper()
    pts = s.get("table") or []
    if isinstance(pts, str):
        rows = []
        for ln in pts.replace("\t", " ").replace(",", " ").splitlines():
            if ln.strip():
                try:
                    rows.append([float(v) for v in ln.split()])
                except ValueError as e:
                    raise ScenarioError("scenario: each line of the table is angle, Fx, Fy (and Fz)") from e
        pts = rows
    if len(pts) < 4 or any(len(r) not in (3, 4) for r in pts):
        raise ScenarioError("scenario: at least 4 lines of angle, Fx, Fy (and Fz)")
    cases = []
    for r in pts:
        ang, fx, fy = r[0], r[1], r[2]
        fz = r[3] if len(r) == 4 else 0.0
        rx, ry = reactions(fx, x, L)[me], reactions(fy, x, L)[me]
        cases.append(
            {
                "label": f"{ang:g}°",
                "Fr": math.hypot(rx, ry),
                "Fa": abs(fz) if "AB"[me] == fixed else 0.0,
                "M": 0.0,
                "n": n,
                "share": 1 / len(pts),
                "angle": ang,
            }
        )
    steps = [
        _line(
            "一圈内本轴承最大径向载荷",
            "Largest radial load on this bearing in a turn",
            max(c["Fr"] for c in cases),
            "N",
        )
    ]
    return {"cases": cases, "motion": "rotating", "outer_turns": False, "steps": steps, "curve": "angle"}


def generic(s: dict) -> dict:
    rows = _spectrum(s)
    cases = []
    for k, r in enumerate(rows):
        cases.append(
            {
                "label": r.get("label") or f"#{k + 1}",
                "Fr": _f(r, "Fr", False, 0.0),
                "Fa": _f(r, "Fa", False, 0.0),
                "M": _f(r, "M", False, 0.0),
                "n": _f(r, "n", False, 0.0),
                "share": _share(r, rows),
            }
        )
    return {
        "cases": cases,
        "motion": (s.get("motion") or "rotating"),
        "outer_turns": bool(s.get("outer_turns")),
        "steps": [],
    }


KINDS = {
    "generic": generic,
    "gearbox": gearbox,
    "motor": motor,
    "spindle": spindle,
    "hub": hub,
    "joint": joint,
    "camshaft": camshaft,
}


def loads(s: dict) -> dict:
    kind = s.get("kind") or "generic"
    if kind not in KINDS:
        raise ScenarioError(f"scenario: unknown kind {kind}")
    out = KINDS[kind](s)
    if out["motion"] not in ("rotating", "oscillating"):
        raise ScenarioError("scenario: the motion is rotating or oscillating")
    for c in out["cases"]:
        if c["Fa"] < 0:
            c["Fa"] = abs(c["Fa"])
    out["kind"] = kind
    out.setdefault("notes", [])
    return out
