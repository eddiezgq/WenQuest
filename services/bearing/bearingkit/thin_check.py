"""Checks of a thin-section ball bearing (round 64, plan section 二十一, part 2): the project → thin.py → the same kind
of check list as the other types, and the ring geometry for the section, drawings and 3D.

Project fields beside the common ones:
    thin:  {"section"}                       X four-point contact, A angular contact, C radial (deep groove)
    inner: {"Dw", "Z", "dm", "fi", "fo", "alpha0_deg", "h_i", "h_o"}
           ball diameter, number of balls, pitch diameter, groove radius ratios, contact angle (X, A), shoulder heights
           above the groove bottoms (for X above the middle of the arch)
    pair:  {"arrangement", "spacing", "setting", "endplay", "preload", "sweep_from", "sweep_to"}
           A: single, back to back DB or face to face DF, the row distance; the setting: X and C a radial clearance
           (µm, negative: preload), an A pair an axial end play (µm, negative: preload), or (X, A pair) a preload force
Rigid rings (said in the results: a thin ring bends, so the real stiffness is lower and the loads spread wider).
Plain code: no AI, no network.
"""

from __future__ import annotations

import math

import numpy as np

from bearingkit import thin as TH
from bearingkit.analyze import FAIL, INFO, NA, PASS, UNKNOWN, ProjectError, _ck, _label, _limit, _num, scenario_cases
from bearingkit.crossed_check import _case_load

TYPE_OF = {"X": "four_point", "A": "angular", "C": "deep_groove"}


def spec_of(p: dict) -> tuple[dict, dict]:
    s, i, m = p.get("size") or {}, p.get("inner") or {}, p.get("material") or {}
    sec = (p.get("thin") or {}).get("section") or "X"
    d, D, B = _num(s.get("d")), _num(s.get("D")), _num(s.get("B"))
    if not (d and D and B and D > d > 0 and B > 0):
        raise ProjectError("give the bore d, the outside diameter D (larger than d) and the width B")
    Dw, Z, fi, fo = _num(i.get("Dw")), _num(i.get("Z")), _num(i.get("fi")), _num(i.get("fo"))
    if not (Dw and Z):
        raise ProjectError("give the ball diameter Dw and the number of balls Z")
    if fi is None or fo is None:
        raise ProjectError("give the groove radius ratios f_i and f_o (groove radius / ball diameter)")
    pr = p.get("pair") or {}
    arr = (pr.get("arrangement") or "single") if sec == "A" else "single"
    spec = {
        "Dw": Dw,
        "Z": int(Z),
        "dm": _num(i.get("dm")) or (d + D) / 2,
        "fi": fi,
        "fo": fo,
        "section": sec,
        "alpha_deg": _num(i.get("alpha0_deg")) if sec != "C" else None,
        "arrangement": arr,
        "spacing": _num(pr.get("spacing")) if arr != "single" else None,
        "E": _num(m.get("E")) or 206000.0,
        "nu": _num(m.get("nu")) or 0.3,
    }
    if sec == "A" and arr == "single":
        setting = {"play": 0.0}
    elif (pr.get("setting") or "endplay") == "preload":
        Fp = _num(pr.get("preload"))
        if Fp is None:
            raise ProjectError("give the preload of the thin-section bearing (N)")
        setting = {"preload": Fp}
    else:
        v = _num(pr.get("endplay"))
        if v is None:
            raise ProjectError(
                "give the axial end play of the pair (µm; negative for preload)"
                if sec == "A"
                else "give the radial clearance of the thin-section bearing (µm; negative for preload)"
            )
        setting = {"play": v / 1000}
    return spec, setting


def build(p: dict):
    spec, setting = spec_of(p)
    try:
        b = TH.make(spec, setting)
    except ValueError as e:
        raise ProjectError(str(e)) from e
    s, i = p.get("size") or {}, p.get("inner") or {}
    sec = spec["section"]
    Dw, dm = spec["Dw"], spec["dm"]
    ri, ro = spec["fi"] * Dw, spec["fo"] * Dw
    ai, ao = ri - Dw / 2, ro - Dw / 2
    a = b.alpha
    g = {
        "type": TYPE_OF[sec],
        "thin": sec,
        "d": _num(s.get("d")),
        "D": _num(s.get("D")),
        "B": _num(s.get("B")),
        "dm": dm,
        "Dw": Dw,
        "Z": b.Z,
        "fi": spec["fi"],
        "fo": spec["fo"],
        "h_i": _num(i.get("h_i")),
        "h_o": _num(i.get("h_o")),
        "arrangement": spec["arrangement"],
        "spacing": spec["spacing"],
        "Gr": b.Gr,
        "endplay": b.e,
    }
    # the rings are drawn with the clearance, or at zero clearance when preloaded (the preload then comes from the
    # balls' size grade at assembly, so the drawn rings and balls do not overlap)
    gr = max(b.Gr, 0.0)
    if sec == "C":
        g["Pd"] = gr
        g["di"], g["do"] = dm - Dw, dm + Dw + gr
    elif sec == "A":
        g["alpha0_deg"] = math.degrees(a)
        g["di"] = 2 * (dm / 2 + ai * math.cos(a) - ri)
        g["do"] = 2 * (dm / 2 - ao * math.cos(a) + ro)
    else:
        g["alpha0_deg"] = math.degrees(a)
        zi, zo = ai * math.sin(a), ao * math.sin(a)
        rci, rco = dm / 2 + ai * math.cos(a), dm / 2 - ao * math.cos(a) + gr / 2
        g["x_arcs"] = {"ri": ri, "ro": ro, "zi": zi, "zo": zo, "rci": rci, "rco": rco}
        g["di"] = 2 * (rci - math.sqrt(ri * ri - zi * zi))  # the middles of the arches
        g["do"] = 2 * (rco + math.sqrt(ro * ro - zo * zo))
    return b, g, spec


def _ellipse(b: TH.Thin, c: dict, h: dict) -> dict:
    """For each ring, the worst ellipse end (as an angle at the arc's centre) against the shoulder and, for X, the
    middle of the arch; also whether any contact went past the middle."""
    out = {}
    for ring, inn in (("inner", True), ("outer", False)):
        ks = [k for k in range(b.m) if b.inner[k] == inn]
        worst_sh, worst_mid, past = -math.inf, math.inf, False
        sh = None
        for k in ks:
            Q, ang, aa = c["Q"][:, k], c["angle"][:, k], c["a"][:, k]
            on = Q > 0
            if not on.any():
                continue
            span = aa[on] / b.r[k]
            al = ang[on] if b.section != "C" else np.abs(ang[on])
            worst_sh = max(worst_sh, float((np.abs(al) + span).max()))
            if b.section == "X":
                mid = b.apex_angle(k)
                worst_mid = min(worst_mid, float((al - span).min()) - mid)
                past = past or bool((al <= mid).any())
        hh = h.get(ring)
        if hh is not None and ks:
            try:
                sh = b.shoulder_angle(ks[0], hh)
            except ValueError as e:
                raise ProjectError(str(e)) from e
        out[ring] = {
            "edge": None if worst_sh == -math.inf else worst_sh,
            "shoulder": sh,
            "mid_margin": None if worst_mid == math.inf else worst_mid,
            "past_mid": past,
        }
    return out


def _heaviest(c: dict, cols, p_max: float) -> dict:
    """The heaviest contact of one ring: its load and its working contact angle."""
    Q = c["Q"][:, cols]
    n, k = np.unravel_index(int(np.argmax(Q)), Q.shape)
    return {"p_max": p_max, "Q": float(Q[n, k]), "alpha_deg": float(np.degrees(abs(c["angle"][:, cols][n, k])))}


def analyse(p: dict) -> dict:
    b, g, spec = build(p)
    lim = p.get("limits") or {}
    sc = scenario_cases(p)
    s = p.get("scenario") or {"kind": "generic"}
    sec = g["thin"]
    checks = []
    gap = g["dm"] * math.sin(math.pi / b.Z) - b.Dw
    lg, lw = _num(lim.get("gap_min")), _num(lim.get("wall_min"))
    checks.append(
        _ck(
            "ball_gap",
            "相邻钢球间隙（节圆上）",
            "Gap between neighbouring balls (on the pitch circle)",
            gap,
            lg,
            FAIL if gap <= 0 else (INFO if lg is None else _limit(gap, lg, higher_bad=False)),
            "mm",
        )
    )
    for ring, wall, zh in (
        ("inner", g["di"] / 2 - g["d"] / 2, "内圈沟底下壁厚" if sec != "X" else "内圈桃形沟中线下壁厚"),
        ("outer", g["D"] / 2 - g["do"] / 2, "外圈沟底外壁厚" if sec != "X" else "外圈桃形沟中线外壁厚"),
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
            )
        )
    H_ = (g["D"] - g["d"]) / 2
    checks.append(
        _ck(
            "thin_ratio",
            "截面高度 / 内径（薄壁程度）",
            "Section height / bore (how thin)",
            H_ / g["d"],
            None,
            INFO,
            "",
            "rings taken as rigid: a thin ring bends, so the real stiffness is lower and the load spreads over more "
            "balls; mount it on a stiff shaft and housing",
            "按刚性套圈计算：薄壁套圈会变形，实际刚度更低、载荷分到更多钢球上；轴和座孔要足够刚",
        )
    )
    # the setting
    if sec == "A":
        if g["arrangement"] == "single":
            checks.append(
                _ck(
                    "endplay",
                    "轴向游隙",
                    "End play",
                    None,
                    None,
                    INFO,
                    "",
                    "a single angular contact row carries axial force one way only; pair it for the other way",
                    "单列角接触只承受一个方向的轴向力；另一方向要成对",
                )
            )
        else:
            checks.append(
                _ck(
                    "endplay",
                    "轴向游隙（两列合计；负数为预紧）",
                    "End play of the pair (negative: preload)",
                    b.e * 1000,
                    None,
                    INFO,
                    "µm",
                )
            )
    else:
        checks.append(
            _ck("x_gr", "径向游隙（负数为预紧）", "Radial clearance (negative: preload)", b.Gr * 1000, None, INFO, "µm")
        )
        fp = b.free_play()
        if fp["axial"] is not None:
            checks.append(
                _ck(
                    "x_ga",
                    "轴向游隙（由径向游隙按几何关系算）",
                    "Axial play (from the radial clearance by the geometry)",
                    fp["axial"] * 1000,
                    None,
                    INFO,
                    "µm",
                )
            )
    pre = b.preload_force()
    if not (sec == "A" and g["arrangement"] == "single"):
        checks.append(
            _ck(
                "preload",
                {
                    "X": "预紧力（每条对角线上全部钢球的轴向力）",
                    "A": "预紧力（无外载时每列的轴向力）",
                    "C": "预紧力（每个钢球的径向接触力）",
                }[sec],
                {
                    "X": "Preload (axial force of all balls on one diagonal)",
                    "A": "Preload (axial force in each row with no outside load)",
                    "C": "Preload (radial contact force of one ball)",
                }[sec],
                pre,
                None,
                INFO,
                "N",
            )
        )
    # the cases
    runs = []
    for c in sc["cases"]:
        P = _case_load(c, s)
        if not np.any(P) and pre <= 0:
            runs.append({"case": c, "P": P, "u": None, "c": None})
            continue
        try:
            u = b.solve(P)
            cc = b.contacts(u)
        except ValueError as e:
            raise ProjectError(str(e)) from e
        runs.append({"case": c, "P": P, "u": u, "c": cc})
    live = [x for x in runs if x["c"] is not None]
    if not live:
        raise ProjectError("give the loads (or a scenario with loads)")
    pmax = {
        "inner": lambda x: float(x["c"]["p"][:, b.inner].max(initial=0.0)),
        "outer": lambda x: float(x["c"]["p"][:, ~b.inner].max(initial=0.0)),
    }
    heavy = max(live, key=lambda x: max(pmax["inner"](x), pmax["outer"](x)))
    ps = _num(lim.get("p_static"))
    for ring, zh in (("inner", "内圈"), ("outer", "外圈")):
        v = max(pmax[ring](x) for x in live)
        checks.append(
            _ck(
                "p_" + ring,
                f"接触强度：{zh}最大接触应力（各工况）",
                f"Max contact stress, {ring} ring (all cases)",
                v,
                ps,
                _limit(v, ps) if v > 0 else NA,
                "MPa",
            )
        )
    # every ball (every diagonal of a four-point bearing, every ball of both rows of a pair) keeps contact
    if sec == "X":
        pairs_on = [
            int(np.count_nonzero(x["c"]["Q"][:, 0] > 0) + np.count_nonzero(x["c"]["Q"][:, 1] > 0)) for x in live
        ]
        total, unit_zh = 2 * b.Z, "（钢球 × 对角线）"
    else:
        pairs_on = [int(np.count_nonzero(x["c"]["Q"].sum(axis=1) > 0)) for x in live]
        total, unit_zh = b.N, ""
    least = min(pairs_on)
    names = "、".join(_label(x["case"])["zh"] for x, n in zip(live, pairs_on, strict=True) if n < total)
    checks.append(
        _ck(
            "x_both",
            "预紧不脱开：各工况下所有钢球都保持接触" + unit_zh,
            "The preload holds: every ball keeps contact in every case",
            f"{least}/{total}",
            None,
            (PASS if least == total else FAIL) if pre > 0 else INFO,
            "",
            "" if least == total or pre <= 0 else "some balls lose contact under the load: more preload, or accept it",
            "" if least == total or pre <= 0 else f"有钢球在载荷下脱开（{names}）：加大预紧，或由企业判定可以接受",
        )
    )
    # an angular contact row carries axial force one way: a contact gone past the groove bottom is a reversed load
    if sec == "A":
        rev = [x for x in live if bool(((x["c"]["Q"] > 0) & (x["c"]["angle"] <= 0)).any())]
        names = "、".join(_label(x["case"])["zh"] for x in rev)
        checks.append(
            _ck(
                "a_side",
                "角接触方向：钢球都在接触角一侧受载（各工况）",
                "Angular contact: every ball loaded on its contact angle side (all cases)",
                "否" if rev else "是",
                None,
                FAIL if rev else PASS,
                "",
                "" if not rev else "the axial force pushes the wrong way: the balls ride towards the low shoulder",
                "" if not rev else f"轴向力方向反了（{names}）：钢球压向低挡肩一侧；改成成对，或换方向安装",
            )
        )
    # the contact ellipse against the shoulders and (four-point) the middle of the arch
    worst = {}
    for x in live:
        e = _ellipse(b, x["c"], {"inner": g["h_i"], "outer": g["h_o"]})
        for ring, v in e.items():
            w = worst.setdefault(ring, {"edge": None, "shoulder": v["shoulder"], "mid_margin": None, "past_mid": False})
            if v["edge"] is not None:
                w["edge"] = v["edge"] if w["edge"] is None else max(w["edge"], v["edge"])
            if v["mid_margin"] is not None:
                w["mid_margin"] = v["mid_margin"] if w["mid_margin"] is None else min(w["mid_margin"], v["mid_margin"])
            w["past_mid"] = w["past_mid"] or v["past_mid"]
    for ring, zh in (("inner", "内圈"), ("outer", "外圈")):
        w = worst.get(ring) or {}
        if w.get("edge") is None:
            continue
        if w["shoulder"] is None:
            checks.append(
                _ck(
                    "trunc_" + ring,
                    f"{zh}接触椭圆不越过挡肩",
                    f"Contact ellipse inside the {ring} shoulder",
                    None,
                    None,
                    UNKNOWN,
                    "",
                    "give the shoulder height",
                    "请填挡肩高度",
                )
            )
        else:
            ok = w["edge"] < w["shoulder"]
            checks.append(
                _ck(
                    "trunc_" + ring,
                    f"{zh}接触椭圆不越过挡肩（椭圆端点角 / 挡肩角，各工况最大）",
                    f"Contact ellipse inside the {ring} shoulder (ellipse end / shoulder angle, worst case)",
                    math.degrees(w["edge"]),
                    math.degrees(w["shoulder"]),
                    PASS if ok else FAIL,
                    "°",
                    "" if ok else "the ellipse runs over the shoulder: edge loading",
                    "" if ok else "接触椭圆越过挡肩：边缘受载",
                )
            )
        if sec == "X" and w.get("mid_margin") is not None:
            ok = w["mid_margin"] > 0 and not w["past_mid"]
            checks.append(
                _ck(
                    "mid_" + ring,
                    f"{zh}接触椭圆不越过桃形沟中线（离中线的余量，各工况最小）",
                    f"Contact ellipse clear of the middle of the {ring} gothic arch (margin, worst case)",
                    math.degrees(w["mid_margin"]),
                    0.0,
                    PASS if ok else FAIL,
                    "°",
                    ""
                    if ok
                    else "the contact runs onto the middle of the arch: a larger contact angle or less clearance",
                    "" if ok else "接触到了桃形沟中线附近：加大接触角或减小游隙",
                )
            )
    st = b.stiffness(heavy["u"])
    for key, zh, en, unit in (
        ("axial", "轴向刚度", "Axial stiffness", "N/µm"),
        ("radial", "径向刚度", "Radial stiffness", "N/µm"),
        ("tilt", "倾覆刚度", "Tilting stiffness", "N·m/mrad"),
    ):
        v = st.get(key) if st else None
        checks.append(
            _ck(
                "k_" + key,
                zh + "（峰值工况）",
                en + " (peak case)",
                v,
                None,
                INFO,
                unit,
                "" if v is not None else "nothing holds the ring in this direction at this load",
                "" if v is not None else "这个载荷下套圈在这个方向没有支承",
            )
        )
    hc = heavy["c"]
    Qb = hc["Q"]
    checks.append(
        _ck(
            "Qmax", "最大接触载荷（单个接触点）", "Largest contact load (one contact)", float(Qb.max()), None, INFO, "N"
        )
    )
    checks.append(
        _ck(
            "loaded",
            "受载钢球数（峰值工况）",
            "Balls carrying load (peak case)",
            int(np.count_nonzero(Qb.sum(axis=1) > 0)),
            None,
            INFO,
        )
    )
    on = Qb > 0
    if on.any():
        angs = np.degrees(np.abs(hc["angle"][on]))
        checks.append(
            _ck(
                "angle_range",
                "受载后的接触角范围（峰值工况）",
                "Contact angles under load (peak case)",
                f"{angs.min():.1f}–{angs.max():.1f}",
                None,
                INFO,
                "°",
            )
        )
    for cid, zh, en in (
        ("C", "基本额定动载荷与寿命", "Basic dynamic load rating and life"),
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
    pr = p.get("pair") or {}
    f, t_ = _num(pr.get("sweep_from")), _num(pr.get("sweep_to"))
    curve = None
    if f is not None and t_ is not None and f != t_ and not (sec == "A" and g["arrangement"] == "single"):
        curve = TH.setting_curve(spec, heavy["P"], f, t_, 11)
    try:
        from bearingkit import parts as PT

        prf = PT.parts(g)
        profile = {k: PT.outline(prf[k]) for k in ("inner", "outer")}
    except ValueError:
        profile = None
    slots = [{"ring": "inner" if b.inner[k] else "outer", "side": int(b.side[k])} for k in range(b.m)]
    return {
        "profile": profile,
        "status": status,
        "checks": checks,
        "geometry": g,
        "type": "thin",
        "pair": {"endplay_um": (b.e if sec == "A" else b.Gr) * 1000, "preload": pre},
        "thin": {
            "section": sec,
            "psi_deg": np.degrees(b.psi).tolist(),
            "row": (np.arange(b.N) // b.Z).tolist(),
            "slots": slots,
            "Q": hc["Q"].tolist(),
            "angle_deg": np.degrees(hc["angle"]).tolist(),
            "p": hc["p"].tolist(),
            "case": heavy["case"].get("label") or "",
            "P": heavy["P"].tolist(),
        },
        "setting_curve": curve,
        "contact": {
            ring: _heaviest(hc, b.inner if ring == "inner" else ~b.inner, pmax[ring](heavy))
            for ring in ("inner", "outer")
        },
        "scenario": {
            "kind": sc["kind"],
            "motion": sc["motion"],
            "outer_turns": sc["outer_turns"],
            "steps": sc["steps"]
            + (
                [
                    {
                        "zh": "单个薄壁轴承承受的倾覆力矩 M = W·x",
                        "en": "Tilting moment on the one thin-section bearing M = W x",
                        "value": float(runs[0]["P"][3]),
                        "unit": "N·mm",
                    }
                ]
                if s.get("kind") == "joint" and runs and runs[0]["P"][3] and not (runs[0]["case"].get("M") or 0)
                else []
            ),
            "notes": sc["notes"],
            "curve": sc.get("curve"),
            "fp": None,
            "cases": [
                {
                    **x["case"],
                    "M": float(x["P"][3]),
                    "Qmax": float(x["c"]["Q"].max()) if x["c"] is not None else 0.0,
                    "p_inner": pmax["inner"](x) if x["c"] is not None else 0.0,
                    "p_outer": pmax["outer"](x) if x["c"] is not None else 0.0,
                }
                for x in runs
            ],
        },
    }
