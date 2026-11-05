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
from bearingkit import highspeed as HS
from bearingkit import scenarios as SC

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


def _ck(cid, zh, en, value, limit, status, unit="", note="", note_zh="", group=""):
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
        "group": group,
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
        raise ProjectError("the bearing type is deep_groove, angular, cylindrical, tapered or flex")
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


def scenario_cases(p: dict) -> dict:
    """The load cases of a project: from its application scenario, or the single set of loads it gives."""
    s = p.get("scenario") or {}
    if (s.get("kind") or "generic") == "generic" and not s.get("cases"):
        ld = p.get("loads") or {}
        s = {**s, "kind": "generic", "cases": [{"label": "", **{k: ld.get(k) for k in ("Fr", "Fa", "M", "n")}}]}
    try:
        return SC.loads(s)
    except SC.ScenarioError as e:
        raise ProjectError(str(e)) from e


def _label(c: dict) -> dict:
    lab = c.get("label") or ""
    return lab if isinstance(lab, dict) else {"zh": str(lab), "en": str(lab)}


def _contacts(b, Qi, ai, Qo, ao):
    """Peak stress, ellipse ends and the heaviest contacts over a set of balls (inner and outer loads and angles
    may differ at speed)."""
    pmax, edge, heavy = {"inner": 0.0, "outer": 0.0}, {"inner": 0.0, "outer": 0.0}, {}
    for ring, Qs, als, f in (("inner", Qi, ai, b.fi), ("outer", Qo, ao, b.fo)):
        for Q, al in zip(Qs, als, strict=True):
            if Q <= 0:
                continue
            c = H.solve(float(Q), H.curvatures(b.D, b.dm, float(al), f, ring), b.Es)
            if c.p_max > pmax[ring]:
                heavy[ring] = {"a": c.a, "b": c.b, "p_max": c.p_max, "alpha_deg": math.degrees(al), "Q": float(Q)}
                pmax[ring] = c.p_max
            edge[ring] = max(edge[ring], abs(al) + c.a / (f * b.D))  # groove bottom to the far end of the ellipse
    return pmax, edge, heavy


def _run(b, Fr, Fa, M, tilt, ctx=None, n=0.0) -> dict:
    """One load case. ctx (angular contact bearings): the row model at speed and the pair, if any."""
    if ctx is not None and (n > 0 or ctx.get("pair")):
        return _run_hs(b, Fr, Fa, M, tilt, ctx, n)
    try:
        dist = BB.distribute(b, Fr=Fr, Fa=Fa, M=M, tilt=tilt)
    except BB.BallError as e:
        raise ProjectError(str(e)) from e
    al = np.radians(dist["alpha_deg"])
    pmax, edge, heavy = _contacts(b, dist["Q"], al, dist["Q"], al)
    return {"dist": dist, "pmax": pmax, "edge": edge, "heavy": heavy, "tilt": tilt}


def _run_hs(b, Fr, Fa, M, tilt, ctx, n) -> dict:
    row, pr, ot = ctx["row"], ctx.get("pair"), ctx.get("outer_turns", False)
    try:
        if pr:
            r = HS.pair(row, pr["arrangement"], pr["preload"], pr["spacing"], Fr, Fa, M, n, ot)
            rows = r["rows"]
        else:
            one = HS.single(row, Fr, Fa, M, n, tilt, ot)
            rows = [{**one, "Fa": Fa, "Fr": Fr}]
    except (HS.SpeedError, BB.BallError) as e:
        raise ProjectError(str(e)) from e
    Qi = np.concatenate([x["Qi"] for x in rows])
    Qo = np.concatenate([x["Qo"] for x in rows])
    ai = np.concatenate([x["ai"] for x in rows])
    ao = np.concatenate([x["ao"] for x in rows])
    pmax, edge, heavy = _contacts(b, Qi, ai, Qo, ao)
    k = int(np.argmax([np.max(x["Qi"]) for x in rows]))  # the more loaded row for the pictures
    main = rows[k]
    dist = {
        "psi_deg": np.degrees(np.radians(0.0) + 2 * np.pi * np.arange(b.Z) / b.Z),
        "Q": main["Qi"],
        "alpha_deg": np.degrees(main["ai"]),
        "alpha_o_deg": np.degrees(main["ao"]),
        "da": r["da"] if pr else one["da"],
        "dr": r["dr"] if pr else one["dr"],
        "theta": r["theta"] if pr else one["theta"],
        "M": 0.0 if pr else one["M"],
        "Qmax": float(np.max(Qi)),
        "loaded": int(np.count_nonzero(main["Qi"] > 0)),
    }
    extra = {
        "Fc": float(np.max(np.concatenate([x["Fc"] for x in rows]))),
        "rows": [
            {
                "z": x.get("z", 0.0),
                "facing": x.get("facing", 1),
                "Fa": x["Fa"],
                "Fr": x["Fr"],
                "Qmax": float(np.max(x["Qi"])),
                "loaded": int(np.count_nonzero(x["Qi"] > 0)),
            }
            for x in rows
        ],
    }
    return {"dist": dist, "pmax": pmax, "edge": edge, "heavy": heavy, "tilt": "pair" if pr else tilt, **extra}


def _speed_ctx(p: dict, b, g: dict, sc: dict):
    """Angular contact bearings: the row model at speed (centrifugal force) and the pair arrangement, if any."""
    if g["type"] != "angular":
        return None
    rho = _num((p.get("material") or {}).get("density"))  # g/cm³
    pr = p.get("pair") or {}
    arr = pr.get("arrangement") or "single"
    if arr not in ("single", "DB", "DF", "DT"):
        raise ProjectError("the arrangement is single, DB, DF or DT")
    pair = None
    if arr != "single":
        s_, fp_ = _num(pr.get("spacing")), _num(pr.get("preload"))
        if s_ is None or (arr != "DT" and fp_ is None):
            raise ProjectError("a pair needs the distance between the rows and (DB, DF) the preload")
        pair = {"arrangement": arr, "spacing": s_, "preload": fp_ or 0.0}
        g["pair"] = pair
    g["density"] = rho
    return {"row": HS.Row(b, (rho or 7.85) * 1e-6), "pair": pair, "outer_turns": sc["outer_turns"]}


def _freq(b, sc: dict):
    n = max((c["n"] for c in sc["cases"]), default=0.0)
    return BB.frequencies(b, n, outer_turns=sc["outer_turns"]) if n else None


def geometry_of(p: dict) -> dict:
    """The design geometry of a project, as the checks see it (for drawings and 3D models)."""
    t = p.get("type") or "deep_groove"
    if t == "cylindrical":
        from bearingkit import cyl_check

        return cyl_check.build(p)[1]
    if t == "tapered":
        from bearingkit import taper_check

        return taper_check.build(p)[1]
    if t == "flex":
        from bearingkit import flex_check

        return flex_check.build(p)[1]
    return build(p)[1]


def analyse(p: dict) -> dict:
    if p.get("type") == "cylindrical":
        from bearingkit import cyl_check  # round 64 step 4 (imports the helpers above)

        return cyl_check.analyse(p)
    if p.get("type") == "tapered":
        from bearingkit import taper_check  # round 64 step 4 part 2

        return taper_check.analyse(p)
    if p.get("type") == "flex":
        from bearingkit import flex_check  # plan section 十八: harmonic reducer flexible bearings

        return flex_check.analyse(p)
    b, g = build(p)
    lim = p.get("limits") or {}
    sc = scenario_cases(p)
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
    # every load case: ball loads, contact stresses, ellipse ends
    tilt_given = (p.get("loads") or {}).get("tilt")
    ctx = _speed_ctx(p, b, g, sc)
    fp = _num((p.get("scenario") or {}).get("fp"))
    runs = []
    for c in sc["cases"]:
        if not (c["Fr"] > 0 or c["Fa"] > 0 or c["M"] != 0):
            runs.append(None)
            continue
        # the shaft holds the inner ring square unless a moment is given (then the ring tilts until it balances)
        runs.append(_run(b, c["Fr"], c["Fa"], c["M"], tilt_given or ("free" if c["M"] else "fixed"), ctx, c["n"]))
    live = [k for k, r in enumerate(runs) if r is not None]
    trunc, heavy, dist, film = {}, {}, None, None
    rotating = sc["motion"] == "rotating"
    if not live:
        checks.append(
            _ck("qmax", "最大钢球载荷", "Largest ball load", None, None, UNKNOWN, "N", "give the loads", "请填载荷")
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
                "give the loads",
                "请填载荷",
            )
        )
    else:
        # the peak case: the largest contact stress at the nominal loads
        kp = max(live, key=lambda k: max(runs[k]["pmax"].values()))
        rp, cp = runs[kp], sc["cases"][kp]
        dist, heavy = rp["dist"], rp["heavy"]
        name = _label(cp)
        many = len(sc["cases"]) > 1
        suffix_zh, suffix_en = (f"（峰值工况 {name['zh']}）", f" (peak case {name['en']})") if many else ("", "")
        checks.append(
            _ck("qmax", "最大钢球载荷" + suffix_zh, "Largest ball load" + suffix_en, dist["Qmax"], None, INFO, "N")
        )
        checks.append(
            _ck("loaded", "受载钢球数" + suffix_zh, "Balls carrying load" + suffix_en, dist["loaded"], b.Z, INFO, "")
        )
        if rp["tilt"] == "fixed":
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
        if "Fc" in rp:  # angular contact at speed or in a pair
            if rp["Fc"] > 0:
                j = int(np.argmax(dist["Q"]))
                checks.append(
                    _ck(
                        "fc",
                        "高速：每个钢球的离心力" + suffix_zh,
                        "At speed: centrifugal force on each ball" + suffix_en,
                        rp["Fc"],
                        None,
                        INFO,
                        "N",
                        "gyroscopic moment taken as held by friction; cage speed from pure rolling",
                        "陀螺力矩按由摩擦平衡、不计入力平衡；保持架转速按纯滚动",
                    )
                )
                checks.append(
                    _ck(
                        "angles",
                        "高速：最重载钢球的外圈 / 内圈接触角",
                        "At speed: outer / inner contact angle of the heaviest ball",
                        f"{float(dist['alpha_o_deg'][j]):.2f} / {float(dist['alpha_deg'][j]):.2f}",
                        None,
                        INFO,
                        "°",
                        "",
                        "",
                        group="speed",
                    )
                )
                if g.get("density") is None:
                    checks.append(
                        _ck(
                            "density",
                            "钢球密度",
                            "Ball density",
                            7.85,
                            None,
                            INFO,
                            "g/cm³",
                            "not given: a common value for bearing steel",
                            "未填：按轴承钢的常用值",
                        )
                    )
            if "pair" in g:
                # a preloaded pair should keep every ball of both rows in contact: an unloaded ball skids
                # judged at rest: at speed the centrifugal force keeps a let-go ball only lightly touching
                worst_k, worst_free = None, 0
                pr0 = g["pair"]
                for k in live:
                    c0 = sc["cases"][k]
                    try:
                        r0 = HS.pair(
                            ctx["row"],
                            pr0["arrangement"],
                            pr0["preload"],
                            pr0["spacing"],
                            c0["Fr"],
                            c0["Fa"],
                            c0["M"],
                            0.0,
                            sc["outer_turns"],
                        )
                    except HS.SpeedError as e:
                        raise ProjectError(str(e)) from e
                    free = sum(int(np.count_nonzero(x["Qi"] <= 0)) for x in r0["rows"])
                    if free > worst_free:
                        worst_k, worst_free = k, free
                ok = worst_free == 0
                nm = _label(sc["cases"][worst_k]) if not ok else None
                checks.append(
                    _ck(
                        "preload",
                        "成对：各工况下两列的钢球都保持接触（预紧够）",
                        "Pair: every ball of both rows stays in contact in every case (enough preload)",
                        worst_free,
                        0,
                        PASS if ok else FAIL,
                        "",
                        ""
                        if ok
                        else f"{worst_free} balls lose contact (at rest) in case {nm['en']} and may skid: more preload",
                        ""
                        if ok
                        else f"工况 {nm['zh']} 有 {worst_free} 个钢球失去接触（按静止判断），可能打滑：加大预紧",
                    )
                )
                pr = g["pair"]
                try:
                    st = HS.stiffness(
                        ctx["row"],
                        pr["arrangement"],
                        pr["preload"],
                        pr["spacing"],
                        cp["Fr"],
                        cp["Fa"],
                        cp["n"],
                        sc["outer_turns"],
                    )
                    checks.append(
                        _ck(
                            "k_axial",
                            "成对：轴向刚度" + suffix_zh,
                            "Pair: axial stiffness" + suffix_en,
                            st["axial"],
                            None,
                            INFO,
                            "N/µm",
                        )
                    )
                    checks.append(
                        _ck(
                            "k_radial",
                            "成对：径向刚度" + suffix_zh,
                            "Pair: radial stiffness" + suffix_en,
                            st["radial"],
                            None,
                            INFO,
                            "N/µm",
                        )
                    )
                except HS.SpeedError:
                    pass
        # static strength: the peak nominal load
        ls = _num(lim.get("p_static"))
        if ls is None:
            ls = _num(lim.get("p_max"))  # projects saved before step 3
        for ring, zh in (("inner", "内圈"), ("outer", "外圈")):
            v = rp["pmax"][ring]
            checks.append(
                _ck(
                    "p_" + ring,
                    f"静强度：{zh}最大接触应力" + suffix_zh,
                    f"Static strength: max contact stress, {ring} ring" + suffix_en,
                    v,
                    ls,
                    _limit(v, ls),
                    "MPa",
                    "" if ls is not None else "give the allowed static contact stress",
                    "" if ls is not None else "请填静强度许用接触应力",
                    group="static",
                )
            )
        # fatigue: every rotating case times the load factor
        lf = _num(lim.get("p_fatigue"))
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
                continue
            if fp is None:
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
                continue
            vals = []
            for k in live:
                c = sc["cases"][k]
                r = _run(b, fp * c["Fr"], fp * c["Fa"], fp * c["M"], runs[k]["tilt"], ctx, c["n"])
                vals.append((r["pmax"][ring], k))
            v, kw = max(vals)
            nm = _label(sc["cases"][kw])
            checks.append(
                _ck(
                    cid,
                    czh,
                    cen,
                    v,
                    lf,
                    _limit(v, lf),
                    "MPa",
                    (f"worst case {nm['en']}" if many else "")
                    + ("" if lf is not None else ("; " if many else "") + "give the allowed fatigue contact stress"),
                    (f"最不利工况 {nm['zh']}" if many else "")
                    + ("" if lf is not None else ("；" if many else "") + "请填疲劳许用接触应力"),
                    group="fatigue",
                )
            )
        # contact ellipse and shoulder, at the peak case
        for ring, zh in (("inner", "内圈"), ("outer", "外圈")):
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
                continue
            shoulder = math.acos(max(-1.0, 1 - h / (f * b.D)))
            edge = max(runs[k]["edge"][ring] for k in live)
            trunc[ring] = {"edge_deg": math.degrees(edge), "shoulder_deg": math.degrees(shoulder)}
            ok = edge < shoulder
            checks.append(
                _ck(
                    "trunc_" + ring,
                    f"{zh}接触椭圆不越过挡肩（椭圆端点角 / 挡肩角，各工况最大）",
                    f"Contact ellipse inside the {ring} shoulder (ellipse end / shoulder angle, worst case)",
                    math.degrees(edge),
                    math.degrees(shoulder),
                    PASS if ok else FAIL,
                    "°",
                    "" if ok else "the ellipse runs over the shoulder: edge loading",
                    "" if ok else "接触椭圆越过挡肩：边缘受载",
                )
            )
        # lubrication film: the thinnest over the turning cases
        lu = p.get("lube") or {}
        eta, ap, sig = _num(lu.get("eta0")), _num(lu.get("alpha_p")), _num(lu.get("sigma"))
        spun = [k for k in live if sc["cases"][k]["n"] > 0]
        if eta and ap and spun:
            best = None
            for k in spun:
                d_ = runs[k]["dist"]
                j = int(np.argmax(d_["Q"]))
                al = math.radians(d_["alpha_deg"][j])
                rho = H.curvatures(b.D, b.dm, al, b.fi, "inner")
                f_ = EH.film(
                    float(d_["Q"][j]), rho, b.Es, eta, ap, EH.entraining_speed(b.dm, b.gamma(al), sc["cases"][k]["n"])
                )
                if best is None or f_["h_min"] < best[0]["h_min"]:
                    best = (f_, k)
            film, kf = best
            nm = _label(sc["cases"][kf])
            lam = film["h_min"] * 1000 / sig if sig else None
            checks.append(
                _ck(
                    "film",
                    "最小油膜厚度（最重载钢球、内圈）" + (f"（工况 {nm['zh']}）" if many else ""),
                    "Minimum film thickness (heaviest ball, inner ring)" + (f" (case {nm['en']})" if many else ""),
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
        "freq": _freq(b, sc),
        "chain": chain,
        "truncation": trunc,
        "film": film,
        "contact": heavy,
        "pair_rows": (
            runs[max(live, key=lambda k: max(runs[k]["pmax"].values()))].get("rows")
            if live and ctx and ctx.get("pair")
            else None
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
                    "alpha_deg": r["heavy"].get("inner", {}).get("alpha_deg") if r else None,
                }
                for c, r in zip(sc["cases"], runs, strict=True)
            ],
        },
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
