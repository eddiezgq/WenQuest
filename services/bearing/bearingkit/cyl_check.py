"""Checks of a cylindrical roller bearing project (round 64, step 4), in the same form as the ball bearing checks.

Project fields beside the common ones (size, material, scenario or loads, fits, lube, limits):
    inner: {"Dw", "Lw", "Lwe", "Z", "dm", "Pd"}    roller diameter, roller length, effective contact length, number
                                                    of rollers, pitch diameter (default (d + D)/2), diametral clearance
    profile: {"kind": "straight" | "arc" | "partial" | "table", "R", "flat", "points"}   the roller crown
    alignment: {"theta_arcmin"}                     misalignment of the inner ring against the outer (shaft bending,
                                                    housing bores), applied to every case
Static strength, fatigue (× f_p), roller ends, film and fault frequencies as for ball bearings; ratings and life are
"unknown" until the purchased standard texts are entered. Plain code: no AI, no network.
"""

from __future__ import annotations

import math

import numpy as np

from bearingkit import clearance as CL
from bearingkit import roller as RL
from bearingkit.analyze import (
    FAIL,
    INFO,
    NA,
    PASS,
    UNKNOWN,
    ProjectError,
    _ck,
    _label,
    _limit,
    _num,
    scenario_cases,
)

E_STEEL = 206000.0


def build(p: dict) -> tuple[RL.CylBearing, dict]:
    s, i, m = p.get("size") or {}, p.get("inner") or {}, p.get("material") or {}
    d, D, B = _num(s.get("d")), _num(s.get("D")), _num(s.get("B"))
    if not (d and D and B and D > d > 0 and B > 0):
        raise ProjectError("give the bore d, the outside diameter D (larger than d) and the width B")
    Dw, Z, Lw, Lwe = _num(i.get("Dw")), _num(i.get("Z")), _num(i.get("Lw")), _num(i.get("Lwe"))
    if not (Dw and Z and Lw and Lwe):
        raise ProjectError(
            "give the roller diameter Dw, its length Lw, the effective contact length Lwe and the number of rollers Z"
        )
    if Lwe > Lw:
        raise ProjectError("the effective contact length is not longer than the roller")
    dm = _num(i.get("dm")) or (d + D) / 2
    E, nu = _num(m.get("E")) or E_STEEL, _num(m.get("nu")) or 0.3
    try:
        b = RL.bearing(
            {
                "D": Dw,
                "L": Lwe,
                "Z": int(Z),
                "dm": dm,
                "Pd": _num(i.get("Pd")) or 0.0,
                "E": E,
                "nu": nu,
                "profile": p.get("profile") or {"kind": "straight"},
            }
        )
    except RL.RollerError as e:
        raise ProjectError(str(e)) from e
    g = {
        "type": "cylindrical",
        "d": d,
        "D": D,
        "B": B,
        "dm": dm,
        "Dw": Dw,
        "Z": int(Z),
        "Lw": Lw,
        "Lwe": Lwe,
        "di": dm - Dw,
        "do": dm + Dw + b.Pd,
        "profile": b.profile.get("kind", "straight"),
    }
    return b, g


def _run(b, Fr, theta):
    try:
        r = RL.distribute(b, Fr, theta)
    except RL.RollerError as e:
        raise ProjectError(str(e)) from e
    s = RL.stresses(b, r["q"])
    j = int(np.argmax(r["Q"]))
    return {
        "dist": r,
        "st": s,
        "j": j,
        "pmax": {k: float(v["p"].max()) for k, v in s.items()},
        "ends": float(max(r["q"][:, 0].max(), r["q"][:, -1].max())),
        "qmax": float(r["q"].max()),
    }


def analyse(p: dict) -> dict:
    b, g = build(p)
    lim = p.get("limits") or {}
    sc = scenario_cases(p)
    fp = _num((p.get("scenario") or {}).get("fp"))
    theta = math.radians((_num((p.get("alignment") or {}).get("theta_arcmin")) or 0.0) / 60)
    checks = []
    # geometry
    gap = g["dm"] * math.sin(math.pi / b.Z) - b.D
    lg, lw = _num(lim.get("gap_min")), _num(lim.get("wall_min"))
    checks.append(
        _ck(
            "ball_gap",
            "相邻滚子间隙（节圆上）",
            "Gap between neighbouring rollers (on the pitch circle)",
            gap,
            lg,
            FAIL if gap <= 0 else (INFO if lg is None else _limit(gap, lg, higher_bad=False)),
            "mm",
        )
    )
    for ring, wall, zh in (
        ("inner", (g["di"] - g["d"]) / 2, "内圈滚道下壁厚"),
        ("outer", (g["D"] - g["do"]) / 2, "外圈滚道下壁厚"),
    ):
        checks.append(
            _ck(
                "wall_" + ring,
                zh,
                f"{ring.capitalize()} ring wall under the raceway",
                wall,
                lw,
                FAIL if wall <= 0 else (INFO if lw is None else _limit(wall, lw, higher_bad=False)),
                "mm",
            )
        )
    checks.append(
        _ck(
            "length",
            "滚子长度不超过套圈宽度",
            "Roller no longer than the ring width",
            g["Lw"],
            g["B"],
            PASS if g["Lw"] < g["B"] else FAIL,
            "mm",
        )
    )
    if abs(b.E - E_STEEL) / E_STEEL > 0.05:
        checks.append(
            _ck(
                "material",
                "材料：滚子与滚道的变形公式按钢",
                "Material: the deflection formula is for steel",
                b.E,
                E_STEEL,
                UNKNOWN,
                "MPa",
                "Palmgren's formula is for steel; results for this material are approximate",
                "Palmgren 变形公式适用于钢，这种材料的结果只是近似",
            )
        )
    # clearance chain: the load distribution runs at the operating clearance
    fits = p.get("fits") or {}
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
            "" if op >= 0 else "negative: the bearing is preloaded; a larger clearance group or a looser fit",
            "" if op >= 0 else "负值：轴承被预紧，请选大一组游隙或放松配合",
        )
    )
    b.Pd = max(op, 0.0)
    # what a cylindrical roller bearing does not carry
    if any(c["Fa"] > 0 for c in sc["cases"]):
        checks.append(
            _ck(
                "axial",
                "轴向力",
                "Axial force",
                max(c["Fa"] for c in sc["cases"]),
                0.0,
                FAIL,
                "N",
                "NU / N cylindrical roller bearings carry no axial load: put the axial force on another bearing",
                "NU / N 型圆柱滚子轴承不承受轴向力：轴向力请由另一个轴承承担",
            )
        )
    if any(c["M"] for c in sc["cases"]):
        checks.append(
            _ck(
                "moment_in",
                "力矩载荷",
                "Moment load",
                max(abs(c["M"]) for c in sc["cases"]) / 1000,
                0.0,
                FAIL,
                "N·m",
                "a single cylindrical roller bearing does not carry a moment; give the misalignment instead",
                "单个圆柱滚子轴承不承受力矩；请改填倾斜角",
            )
        )
    # every case
    runs = [(_run(b, c["Fr"], theta) if c["Fr"] > 0 else None) for c in sc["cases"]]
    live = [k for k, r in enumerate(runs) if r is not None]
    rotating = sc["motion"] == "rotating"
    many = len(sc["cases"]) > 1
    film, slices = None, None
    if not live:
        checks.append(
            _ck(
                "qmax",
                "最大滚子载荷",
                "Largest roller load",
                None,
                None,
                UNKNOWN,
                "N",
                "give the radial load",
                "请填径向载荷",
            )
        )
        checks.append(
            _ck(
                "film",
                "最小油膜厚度",
                "Minimum film thickness",
                None,
                None,
                UNKNOWN,
                "µm",
                "give the radial load",
                "请填径向载荷",
            )
        )
        rp = None
    else:
        kp = max(live, key=lambda k: max(runs[k]["pmax"].values()))
        rp, cp = runs[kp], sc["cases"][kp]
        nm = _label(cp)
        sz, se = (f"（峰值工况 {nm['zh']}）", f" (peak case {nm['en']})") if many else ("", "")
        d_ = rp["dist"]
        checks.append(_ck("qmax", "最大滚子载荷" + sz, "Largest roller load" + se, d_["Qmax"], None, INFO, "N"))
        checks.append(_ck("loaded", "受载滚子数" + sz, "Rollers carrying load" + se, d_["loaded"], b.Z, INFO, ""))
        if theta:
            checks.append(
                _ck(
                    "moment",
                    "倾斜引起的力矩（作用在轴上）",
                    "Moment from the misalignment (on the shaft)",
                    d_["M"] / 1000,
                    None,
                    INFO,
                    "N·m",
                )
            )
        ls = _num(lim.get("p_static"))
        lf = _num(lim.get("p_fatigue"))
        for ring, zh in (("inner", "内圈"), ("outer", "外圈")):
            v = rp["pmax"][ring]
            checks.append(
                _ck(
                    "p_" + ring,
                    f"静强度：{zh}最大接触应力" + sz,
                    f"Static strength: max contact stress, {ring} ring" + se,
                    v,
                    ls,
                    _limit(v, ls),
                    "MPa",
                    "" if ls is not None else "give the allowed static contact stress",
                    "" if ls is not None else "请填静强度许用接触应力",
                    group="static",
                )
            )
        fat = {}
        if rotating and fp is not None:
            for k in live:
                fat[k] = _run(b, fp * sc["cases"][k]["Fr"], theta)
        for ring, zh in (("inner", "内圈"), ("outer", "外圈")):
            cid, czh = "pf_" + ring, f"疲劳：{zh}最大接触应力（各工况 × 载荷系数 fp）"
            cen = f"Fatigue: max contact stress, {ring} ring (every case × load factor f_p)"
            if not rotating:
                checks.append(
                    _ck(
                        cid,
                        czh,
                        cen,
                        None,
                        None,
                        NA,
                        "MPa",
                        "the bearing swings, it does not turn: static strength governs",
                        "轴承摆动、不整圈转：以静强度为主",
                        group="fatigue",
                    )
                )
            elif fp is None:
                v = max(runs[k]["pmax"][ring] for k in live)
                checks.append(
                    _ck(
                        cid,
                        czh,
                        cen,
                        v,
                        lf,
                        UNKNOWN,
                        "MPa",
                        "give the load factor f_p (from a handbook or your own standard); shown at the nominal loads",
                        "请填载荷系数 fp（按手册或企业规范）；现显示名义载荷下的值",
                        group="fatigue",
                    )
                )
            else:
                v, kw = max((fat[k]["pmax"][ring], k) for k in live)
                n2 = _label(sc["cases"][kw])
                checks.append(
                    _ck(
                        cid,
                        czh,
                        cen,
                        v,
                        lf,
                        _limit(v, lf),
                        "MPa",
                        (f"worst case {n2['en']}" if many else "")
                        + (
                            "" if lf is not None else ("; " if many else "") + "give the allowed fatigue contact stress"
                        ),
                        (f"最不利工况 {n2['zh']}" if many else "")
                        + ("" if lf is not None else ("；" if many else "") + "请填疲劳许用接触应力"),
                        group="fatigue",
                    )
                )
        # roller ends: a loaded end means edge stress the slices cannot show
        worst = [runs[k] for k in live] + list(fat.values())
        ends = max(r["ends"] / r["qmax"] for r in worst)
        straight = g["profile"] == "straight"
        ok = ends < 1e-9
        checks.append(
            _ck(
                "ends",
                "滚子两端不受载（凸度足够）",
                "Roller ends unloaded (enough crown)",
                ends * 100,
                0.0,
                PASS if ok else FAIL,
                "%",
                ""
                if ok
                else (
                    "end load as a share of the peak; the stress concentration at a loaded end "
                    "is not captured by slices: "
                    + ("crown the roller" if straight else "more crown or less misalignment")
                ),
                ""
                if ok
                else (
                    "端部载荷占峰值的百分比；切片法算不出受载端部的应力集中："
                    + ("滚子需要凸度" if straight else "加大凸度或减小倾斜")
                ),
            )
        )
        j = rp["j"]
        slices = {
            "x": d_["x"].round(4).tolist(),
            "q": d_["q"][j].round(3).tolist(),
            "p_inner": rp["st"]["inner"]["p"][j].round(2).tolist(),
            "p_outer": rp["st"]["outer"]["p"][j].round(2).tolist(),
            "drop": b.drop(d_["x"]).round(6).tolist(),
        }
        # film: the thinnest over the turning cases, heaviest slice, inner raceway
        lu = p.get("lube") or {}
        eta, ap, sig = _num(lu.get("eta0")), _num(lu.get("alpha_p")), _num(lu.get("sigma"))
        spun = [k for k in live if sc["cases"][k]["n"] > 0]
        if eta and ap and spun:
            best = None
            for k in spun:
                w = sc["cases"][k]["n"] * 2 * math.pi / 60
                u = w * b.dm * (1 - b.gamma**2) / 4
                f_ = RL.film(runs[k]["qmax"], b.radius("inner"), b.Es, eta, ap, u)
                if best is None or f_["h_min"] < best[0]["h_min"]:
                    best = (f_, k)
            film, kf = best
            lam = film["h_min"] * 1000 / sig if sig else None
            checks.append(
                _ck(
                    "film",
                    "最小油膜厚度（最重载切片、内圈，线接触）",
                    "Minimum film thickness (heaviest slice, inner ring, line contact)",
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
                    NA if not rotating else UNKNOWN,
                    "µm",
                    "give the speed, the oil viscosity and its pressure-viscosity coefficient",
                    "请填转速、润滑油黏度和黏压系数",
                )
            )
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
    n = max((c["n"] for c in sc["cases"]), default=0.0)
    out = {
        "status": status,
        "checks": checks,
        "geometry": g,
        "type": "cylindrical",
        "chain": chain,
        "freq": RL.frequencies(b, n, sc["outer_turns"]) if n else None,
        "film": film,
        "slices": slices,
        "contact": (
            {
                "inner": {"p_max": rp["pmax"]["inner"], "Q": rp["dist"]["Qmax"], "alpha_deg": 0.0},
                "outer": {"p_max": rp["pmax"]["outer"], "Q": rp["dist"]["Qmax"], "alpha_deg": 0.0},
            }
            if rp
            else {}
        ),
        "scenario": {
            "kind": sc["kind"],
            "motion": sc["motion"],
            "outer_turns": sc["outer_turns"],
            "steps": sc["steps"],
            "notes": sc["notes"],
            "curve": sc.get("curve"),
            "fp": fp,
            "cases": [
                {
                    **c,
                    "Qmax": r["dist"]["Qmax"] if r else 0.0,
                    "p_inner": r["pmax"]["inner"] if r else 0.0,
                    "p_outer": r["pmax"]["outer"] if r else 0.0,
                }
                for c, r in zip(sc["cases"], runs, strict=True)
            ],
        },
    }
    if rp:
        d_ = rp["dist"]
        out["balls"] = {
            "psi_deg": d_["psi_deg"].round(3).tolist(),
            "Q": d_["Q"].round(3).tolist(),
            "dr": d_["dr"],
            "theta": d_["theta"],
        }
    return out
