"""One project in, checks and curves out (round 64, step 2): deep groove and angular contact ball bearings.

A project (dict, as the web page sends it):
    {"type": "deep_groove" | "angular",
     "size":  {"d", "D", "B"}                              bore, outside diameter, width (mm)
     "inner": {"Dw", "Z", "dm", "fi", "fo", "Pd" | "alpha0_deg", "h_i", "h_o"}
               ball diameter, number of balls, pitch diameter (default (d + D)/2), groove radius ratios, diametral
               clearance (deep groove) or contact angle (angular), shoulder heights above the groove bottoms
     "material": {"E", "nu"}                               MPa, rings and balls
     "loads": {"Fr", "Fa", "M", "n"}                       N, N, N·mm, r/min (inner ring turns, outer fixed)
     "fits":  {"shaft_I", "housing_I", "T_i", "T_o"}       diametral interferences (mm), ring temperatures (°C)
     "lube":  {"eta0", "alpha_p", "sigma"}                 Pa·s at operating temperature, 1/Pa, composite roughness µm
     "limits": {"p_max", "gap_min", "wall_min"}}           allowed contact stress (MPa), smallest ball gap, ring wall
Every check: pass, fail, unknown (data missing: never a pass), na or info. Ratings and life from the national
standards are "unknown" until the purchased texts are entered (plan section 五). Plain code: no AI, no network.
"""

from __future__ import annotations

import math

import numpy as np

from bearingkit import ball as BB
from bearingkit import clearance as CL
from bearingkit import ehl as EH
from bearingkit import hertz as H

PASS, FAIL, UNKNOWN, NA, INFO = "pass", "fail", "unknown", "na", "info"


class ProjectError(ValueError):
    pass


def _num(v):
    if v in (None, ""):
        return None
    x = float(v)
    if not math.isfinite(x):
        raise ProjectError("numbers must be finite")
    return x


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


def _limit(val, lim, higher_bad=True):
    if val is None:
        return NA
    if lim is None:
        return UNKNOWN
    return PASS if ((val <= lim) if higher_bad else (val >= lim)) else FAIL


def build(p: dict) -> tuple[BB.BallBearing, dict]:
    kind = p.get("type") or "deep_groove"
    if kind not in ("deep_groove", "angular"):
        raise ProjectError("the bearing type is deep_groove or angular (rollers come in step 3)")
    s, i, m = p.get("size") or {}, p.get("inner") or {}, p.get("material") or {}
    d, D, B = _num(s.get("d")), _num(s.get("D")), _num(s.get("B"))
    if not (d and D and B and D > d > 0 and B > 0):
        raise ProjectError("give the bore d, the outside diameter D (larger than d) and the width B")
    Dw, Z = _num(i.get("Dw")), _num(i.get("Z"))
    if not (Dw and Z):
        raise ProjectError("give the ball diameter Dw and the number of balls Z")
    dm = _num(i.get("dm")) or (d + D) / 2
    fi, fo = _num(i.get("fi")), _num(i.get("fo"))
    if fi is None or fo is None:
        raise ProjectError("give the groove radius ratios f_i and f_o (groove radius / ball diameter)")
    spec = {
        "D": Dw,
        "Z": int(Z),
        "dm": dm,
        "fi": fi,
        "fo": fo,
        "E": _num(m.get("E")) or 206000.0,
        "nu": _num(m.get("nu")) or 0.3,
    }
    if kind == "angular":
        a0 = _num(i.get("alpha0_deg"))
        if a0 is None or not 0 < a0 < 60:
            raise ProjectError("give the contact angle of the angular contact bearing (between 0° and 60°)")
        spec["alpha0_deg"] = a0
    else:
        spec["Pd"] = _num(i.get("Pd")) or 0.0
    try:
        b = BB.bearing(spec)
    except BB.BallError as e:
        raise ProjectError(str(e)) from e
    geo = {
        "d": d,
        "D": D,
        "B": B,
        "dm": dm,
        "Dw": Dw,
        "Z": int(Z),
        "fi": b.fi,
        "fo": b.fo,
        "di": dm - Dw,
        "do": dm + Dw + (spec.get("Pd") or 0.0) if kind == "deep_groove" else dm + Dw,
        "alpha0_deg": math.degrees(b.alpha0),
        "h_i": _num(i.get("h_i")),
        "h_o": _num(i.get("h_o")),
        "type": kind,
    }
    if kind == "angular":
        # the groove centres sit on the contact line, (f − ½)·Dw from the ball centre: each groove bottom lies
        # (f − ½)·Dw·(1 − cos α₀) beyond the zero-clearance one (together P_d = 2A(1 − cos α₀))
        k = 1 - math.cos(b.alpha0)
        geo["di"] = dm - Dw - 2 * (b.fi - 0.5) * Dw * k
        geo["do"] = dm + Dw + 2 * (b.fo - 0.5) * Dw * k
    return b, geo


def analyse(p: dict) -> dict:
    b, g = build(p)
    lim = p.get("limits") or {}
    ld = p.get("loads") or {}
    Fr, Fa, M, n = (_num(ld.get(k)) or 0.0 for k in ("Fr", "Fa", "M", "n"))
    checks = []
    # geometry
    gap = g["dm"] * math.sin(math.pi / b.Z) - b.D
    lg = _num(lim.get("gap_min"))
    checks.append(
        _ck(
            "ball_gap",
            "相邻钢球间隙（节圆上）",
            "Gap between neighbouring balls (on the pitch circle)",
            gap,
            lg,
            FAIL if gap <= 0 else (INFO if lg is None else _limit(gap, lg, higher_bad=False)),
            "mm",
            "" if gap > 0 else "the balls touch: fewer or smaller balls",
            "" if gap > 0 else "钢球相碰：减少球数或减小球径",
        )
    )
    lw = _num(lim.get("wall_min"))
    for ring, wall, zh in (
        ("inner", (g["di"] - g["d"]) / 2, "内圈沟底壁厚"),
        ("outer", (g["D"] - g["do"]) / 2, "外圈沟底壁厚"),
    ):
        checks.append(
            _ck(
                "wall_" + ring,
                zh,
                f"{ring.capitalize()} ring wall under the groove",
                wall,
                lw,
                FAIL if wall <= 0 else (INFO if lw is None else _limit(wall, lw, higher_bad=False)),
                "mm",
                "" if wall > 0 else "the groove cuts through the ring",
                "" if wall > 0 else "沟道切穿套圈",
            )
        )
    for ring, f, zh in (("inner", b.fi, "内圈"), ("outer", b.fo, "外圈")):
        h = g["h_" + ring[0]]
        if h is None:
            continue
        if not 0 < h < f * b.D:
            raise ProjectError("the shoulder height is above zero and below the groove radius")
        width = 2 * f * b.D * math.sin(math.acos(1 - h / (f * b.D)))  # groove width at the shoulder
        checks.append(
            _ck(
                "groove_w_" + ring,
                f"{zh}沟道口宽度小于套圈宽度",
                f"{ring.capitalize()} groove narrower than the ring",
                width,
                g["B"],
                PASS if width < g["B"] else FAIL,
                "mm",
            )
        )
    # clearance chain (deep groove): the load distribution runs at the operating clearance
    fits = p.get("fits") or {}
    chain = None
    if g["type"] == "deep_groove":
        si, hi = _num(fits.get("shaft_I")) or 0.0, _num(fits.get("housing_I")) or 0.0
        chain = CL.chain(
            b.Pd,
            g["di"],
            g["do"],
            inner={"interference": si, "d": g["d"], "d_ie": g["di"]} if si else None,
            outer={"interference": hi, "D": g["D"], "d_oe": g["do"]} if hi else None,
            T_i=_num(fits.get("T_i")) or 20.0,
            T_o=_num(fits.get("T_o")) or 20.0,
        )
        op = chain["operating"]
        checks.append(
            _ck(
                "clearance",
                "工作游隙（初始 → 装配 → 温差）",
                "Operating clearance (initial → fitted → temperature)",
                op * 1000,
                0.0,
                PASS if op >= 0 else FAIL,
                "µm",
                ""
                if op >= 0
                else "negative: the deep groove bearing is preloaded; a larger clearance group or a looser fit",
                "" if op >= 0 else "负值：深沟球轴承被预紧，请选大一组游隙或放松配合",
            )
        )
        b = BB.bearing(
            {"D": b.D, "Z": b.Z, "dm": b.dm, "fi": b.fi, "fo": b.fo, "Pd": max(op, 0.0), "E": b.E, "nu": b.nu}
        )
        g["alpha_op_deg"] = math.degrees(b.alpha0)
    # load distribution
    loaded = Fr > 0 or Fa > 0 or M != 0
    # the shaft holds the inner ring square unless a moment is given (then the ring tilts until it balances)
    tilt = ld.get("tilt") or ("free" if M else "fixed")
    dist = None
    if loaded:
        try:
            dist = BB.distribute(b, Fr=Fr, Fa=Fa, M=M, tilt=tilt)
        except BB.BallError as e:
            raise ProjectError(str(e)) from e
        checks.append(_ck("qmax", "最大钢球载荷", "Largest ball load", dist["Qmax"], None, INFO, "N"))
        checks.append(_ck("loaded", "受载钢球数", "Balls carrying load", dist["loaded"], b.Z, INFO, ""))
        if tilt == "fixed":
            checks.append(
                _ck(
                    "moment",
                    "轴承作用在轴上的力矩（内圈不倾斜）",
                    "Moment the bearing puts on the shaft (inner ring held square)",
                    dist["M"] / 1000,
                    None,
                    INFO,
                    "N·m",
                )
            )
        else:
            checks.append(_ck("tilt", "内圈倾角", "Inner ring tilt", math.degrees(dist["theta"]) * 60, None, INFO, "′"))
    else:
        checks.append(
            _ck("qmax", "最大钢球载荷", "Largest ball load", None, None, UNKNOWN, "N", "give the loads", "请填载荷")
        )
    # contact stress and ellipse truncation, inner and outer
    lp = _num(lim.get("p_max"))
    trunc = {}
    heavy = {}  # the most stressed contact on each ring, for the drawing
    if dist is not None:
        pmax = {"inner": 0.0, "outer": 0.0}
        worst = {"inner": None, "outer": None}
        for Q, al in zip(dist["Q"], np.radians(dist["alpha_deg"]), strict=True):
            if Q <= 0:
                continue
            for ring, c in BB.contacts(b, float(Q), float(al)).items():
                if c.p_max > pmax[ring]:
                    heavy[ring] = {"a": c.a, "b": c.b, "p_max": c.p_max, "alpha_deg": math.degrees(al), "Q": float(Q)}
                pmax[ring] = max(pmax[ring], c.p_max)
                f = b.fi if ring == "inner" else b.fo
                edge = abs(al) + c.a / (f * b.D)  # angle from the groove bottom to the far end of the ellipse
                worst[ring] = edge if worst[ring] is None else max(worst[ring], edge)
        for ring, zh in (("inner", "内圈"), ("outer", "外圈")):
            checks.append(
                _ck(
                    "p_" + ring,
                    f"{zh}最大接触应力",
                    f"Max contact stress, {ring} ring",
                    pmax[ring],
                    lp,
                    _limit(pmax[ring], lp),
                    "MPa",
                    "" if lp is not None else "give the allowed contact stress",
                    "" if lp is not None else "请填许用接触应力",
                )
            )
            h = g["h_" + ring[0]]
            f = b.fi if ring == "inner" else b.fo
            if h is None:
                checks.append(
                    _ck(
                        "trunc_" + ring,
                        f"{zh}接触椭圆不越过挡肩",
                        f"Contact ellipse inside the {ring} shoulder",
                        None,
                        None,
                        UNKNOWN,
                        "°",
                        "give the shoulder height",
                        "请填挡肩高度",
                    )
                )
            else:
                shoulder = math.acos(max(-1.0, 1 - h / (f * b.D)))
                trunc[ring] = {"edge_deg": math.degrees(worst[ring]), "shoulder_deg": math.degrees(shoulder)}
                checks.append(
                    _ck(
                        "trunc_" + ring,
                        f"{zh}接触椭圆不越过挡肩（椭圆端点角 / 挡肩角）",
                        f"Contact ellipse inside the {ring} shoulder (ellipse end / shoulder angle)",
                        math.degrees(worst[ring]),
                        math.degrees(shoulder),
                        PASS if worst[ring] < shoulder else FAIL,
                        "°",
                        "" if worst[ring] < shoulder else "the ellipse runs over the shoulder: edge loading",
                        "" if worst[ring] < shoulder else "接触椭圆越过挡肩：边缘受载",
                    )
                )
    # lubrication film
    lu = p.get("lube") or {}
    eta, ap, sig = _num(lu.get("eta0")), _num(lu.get("alpha_p")), _num(lu.get("sigma"))
    film = None
    if dist is not None and eta and ap and n:
        j = int(np.argmax(dist["Q"]))
        al = math.radians(dist["alpha_deg"][j])
        rho = H.curvatures(b.D, b.dm, al, b.fi, "inner")
        film = EH.film(float(dist["Q"][j]), rho, b.Es, eta, ap, EH.entraining_speed(b.dm, b.gamma(al), n))
        lam = film["h_min"] * 1000 / sig if sig else None
        checks.append(
            _ck(
                "film",
                "最小油膜厚度（最重载钢球、内圈）",
                "Minimum film thickness (heaviest ball, inner ring)",
                film["h_min"] * 1000,
                None,
                INFO,
                "µm",
            )
        )
        checks.append(
            _ck(
                "lambda",
                "油膜厚度比 λ = h_min / σ",
                "Film thickness ratio λ = h_min / σ",
                lam,
                None,
                INFO if lam is not None else UNKNOWN,
                "",
                "" if lam is not None else "give the composite surface roughness",
                "" if lam is not None else "请填综合表面粗糙度",
            )
        )
    else:
        checks.append(
            _ck(
                "film",
                "最小油膜厚度",
                "Minimum film thickness",
                None,
                None,
                UNKNOWN,
                "µm",
                "give the speed, the oil viscosity and its pressure-viscosity coefficient",
                "请填转速、润滑油黏度和黏压系数",
            )
        )
    # ratings and life: from the national standards once their texts are entered
    for cid, zh, en in (
        ("C", "基本额定动载荷 C 与寿命 L10", "Dynamic load rating C and life L10"),
        ("C0", "基本额定静载荷 C0 与静安全系数", "Static load rating C0 and static safety factor"),
    ):
        checks.append(
            _ck(
                cid,
                zh,
                en,
                None,
                None,
                UNKNOWN,
                "",
                "the national standard's tables are not entered yet",
                "国家标准的系数表尚未录入",
            )
        )
    status = (
        FAIL
        if any(c["status"] == FAIL for c in checks)
        else (UNKNOWN if any(c["status"] == UNKNOWN for c in checks) else PASS)
    )
    out = {
        "status": status,
        "checks": checks,
        "geometry": g,
        "type": g["type"],
        "freq": BB.frequencies(b, n) if n else None,
        "chain": chain,
        "truncation": trunc,
        "film": film,
        "contact": heavy,
    }
    if dist is not None:
        out["balls"] = {
            "psi_deg": dist["psi_deg"].round(3).tolist(),
            "Q": dist["Q"].round(3).tolist(),
            "alpha_deg": dist["alpha_deg"].round(4).tolist(),
            "da": dist["da"],
            "dr": dist["dr"],
            "theta": dist["theta"],
        }
    return out
