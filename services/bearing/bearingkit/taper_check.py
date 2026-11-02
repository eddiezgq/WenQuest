"""Checks of a single-row tapered roller bearing project (round 64, step 4, part 2).

Project fields beside the common ones:
    inner: {"Dw", "Lw", "Lwe", "Z", "dm", "alpha_o_deg", "alpha_i_deg", "alpha_f_deg", "R_end"}
           mean roller diameter, roller length, effective contact length, number of rollers, pitch diameter, cup
           angle (contact angle), cone angle, direction of the rib's push (blank: square to the roller axis),
           radius of the roller's large end face
    profile, alignment: as for cylindrical roller bearings
Mounted with zero end play (pairs, end play and preload come in part 3). Ring walls use the mean roller diameter
projected onto the radial direction, so they are approximate and say so.
Plain code: no AI, no network.
"""

from __future__ import annotations

import math

import numpy as np

from bearingkit import roller as RL
from bearingkit import taper as TP
from bearingkit.analyze import FAIL, INFO, NA, PASS, UNKNOWN, ProjectError, _ck, _label, _limit, _num, scenario_cases

E_STEEL = 206000.0


def build(p: dict):
    s, i, m = p.get("size") or {}, p.get("inner") or {}, p.get("material") or {}
    d, D, B = _num(s.get("d")), _num(s.get("D")), _num(s.get("B"))
    if not (d and D and B and D > d > 0 and B > 0):
        raise ProjectError("give the bore d, the outside diameter D (larger than d) and the width B")
    Dw, Z, Lw, Lwe = _num(i.get("Dw")), _num(i.get("Z")), _num(i.get("Lw")), _num(i.get("Lwe"))
    ao, ai = _num(i.get("alpha_o_deg")), _num(i.get("alpha_i_deg"))
    if not (Dw and Z and Lw and Lwe):
        raise ProjectError(
            "give the roller diameter Dw, its length Lw, the effective contact length Lwe and the number of rollers Z"
        )
    if ao is None or ai is None:
        raise ProjectError("give the cup angle and the cone angle of the tapered roller bearing")
    if Lwe > Lw:
        raise ProjectError("the effective contact length is not longer than the roller")
    dm = _num(i.get("dm")) or (d + D) / 2
    try:
        b = TP.bearing(
            {
                "D": Dw,
                "L": Lwe,
                "Z": int(Z),
                "dm": dm,
                "alpha_o_deg": ao,
                "alpha_i_deg": ai,
                "alpha_f_deg": _num(i.get("alpha_f_deg")),
                "R_end": _num(i.get("R_end")),
                "E": _num(m.get("E")) or E_STEEL,
                "nu": _num(m.get("nu")) or 0.3,
                "profile": p.get("profile") or {"kind": "straight"},
            }
        )
    except (TP.TaperError, RL.RollerError) as e:
        raise ProjectError(str(e)) from e
    g = {
        "type": "tapered",
        "d": d,
        "D": D,
        "B": B,
        "dm": dm,
        "Dw": Dw,
        "Z": int(Z),
        "Lw": Lw,
        "Lwe": Lwe,
        "alpha_o_deg": ao,
        "alpha_i_deg": ai,
        "di": dm - Dw * math.cos(b.ai),
        "do": dm + Dw * math.cos(b.ao),
        "profile": b.profile.get("kind", "straight"),
        "R_end": b.R_end,
    }
    return b, g


def _run(b, Fr, Fa, theta):
    try:
        r = TP.distribute(b, Fr, Fa, theta)
    except (TP.TaperError, RL.RollerError) as e:
        raise ProjectError(str(e)) from e
    s = TP.stresses(b, r["q"])
    return {
        "dist": r,
        "st": s,
        "j": int(np.argmax(r["Q"])),
        "pmax": {k: float(v["p"].max()) for k, v in s.items()},
        "ends": float(max(r["q"][:, 0].max(), r["q"][:, -1].max())),
        "qmax": float(r["q"].max()),
        "Qf": float(r["Qf"].max()),
    }


def analyse(p: dict) -> dict:
    b, g = build(p)
    lim = p.get("limits") or {}
    sc = scenario_cases(p)
    fp = _num((p.get("scenario") or {}).get("fp"))
    theta = math.radians((_num((p.get("alignment") or {}).get("theta_arcmin")) or 0.0) / 60)
    lam, mu = b.ratios()
    checks = []
    gap = g["dm"] * math.sin(math.pi / b.Z) - b.D
    lg, lw = _num(lim.get("gap_min")), _num(lim.get("wall_min"))
    checks.append(
        _ck(
            "ball_gap",
            "相邻滚子间隙（节圆上，按平均直径）",
            "Gap between neighbouring rollers (pitch circle, mean diameter)",
            gap,
            lg,
            FAIL if gap <= 0 else (INFO if lg is None else _limit(gap, lg, higher_bad=False)),
            "mm",
        )
    )
    for ring, wall, zh in (
        ("inner", (g["di"] - g["d"]) / 2, "内圈（锥）滚道下壁厚，近似"),
        ("outer", (g["D"] - g["do"]) / 2, "外圈（杯）滚道下壁厚，近似"),
    ):
        checks.append(
            _ck(
                "wall_" + ring,
                zh,
                f"{ring.capitalize()} ring wall under the raceway, approximate",
                wall,
                lw,
                FAIL if wall <= 0 else (INFO if lw is None else _limit(wall, lw, higher_bad=False)),
                "mm",
                "mean roller diameter projected on the radius",
                "按滚子平均直径投影估算",
            )
        )
    checks.append(
        _ck(
            "length",
            "滚子长度不超过轴承宽度",
            "Roller no longer than the bearing width",
            g["Lw"],
            g["B"],
            PASS if g["Lw"] < g["B"] else FAIL,
            "mm",
        )
    )
    ai_apex = TP.on_apex_cone_angle(b.D, b.dm, g["alpha_o_deg"])
    g["alpha_i_apex_deg"] = ai_apex
    ok_apex = abs(ai_apex - g["alpha_i_deg"]) < 0.005  # angles are entered to 0.01°
    checks.append(
        _ck(
            "apex",
            "锥顶重合（滚子纯滚动）：内圈锥角应为",
            "Apexes meet (rollers roll without sliding): the cone angle should be",
            f"{g['alpha_i_deg']:.3f}",
            f"{ai_apex:.3f}",
            PASS if ok_apex else FAIL,
            "°",
            ""
            if ok_apex
            else "the cup, cone and roller apexes do not meet on the axis: the rollers slide and skew; "
            "set the cone angle to the value given",
            "" if ok_apex else "外圈、内圈和滚子的锥顶不在轴线上同一点：滚子会滑动和歪斜；请把内圈锥角改成给出的值",
        )
    )
    checks.append(
        _ck(
            "rib_ratio",
            "挡边力 / 外滚道接触力（滚子受力平衡）",
            "Rib force / cup contact force (roller equilibrium)",
            mu,
            None,
            INFO,
            "",
            "",
            "",
        )
    )
    checks.append(
        _ck(
            "endplay",
            "轴向游隙",
            "End play",
            None,
            None,
            INFO,
            "",
            "set at mounting; worked here with zero end play (pairs and preload in part 3)",
            "安装时调整；这里按零游隙计算（配对与预紧在第 4 步之三）",
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
                "a single row does not carry a moment; pair it (part 3) or give the misalignment",
                "单列圆锥滚子轴承不承受力矩：请配对使用（第 4 步之三）或改填倾斜角",
            )
        )
    loaded = [c["Fr"] > 0 or c["Fa"] > 0 for c in sc["cases"]]
    runs = [(_run(b, c["Fr"], c["Fa"], theta) if ok else None) for c, ok in zip(sc["cases"], loaded, strict=True)]
    live = [k for k, r in enumerate(runs) if r is not None]
    rotating = sc["motion"] == "rotating"
    many = len(sc["cases"]) > 1
    film, slices, rp = None, None, None
    if not live:
        checks.append(
            _ck("qmax", "最大滚子载荷", "Largest roller load", None, None, UNKNOWN, "N", "give the loads", "请填载荷")
        )
    else:
        kp = max(live, key=lambda k: max(runs[k]["pmax"].values()))
        rp = runs[kp]
        nm = _label(sc["cases"][kp])
        sz, se = (f"（峰值工况 {nm['zh']}）", f" (peak case {nm['en']})") if many else ("", "")
        d_ = rp["dist"]
        checks.append(
            _ck("qmax", "最大滚子载荷（外滚道）" + sz, "Largest roller load (cup)" + se, d_["Qmax"], None, INFO, "N")
        )
        checks.append(_ck("loaded", "受载滚子数" + sz, "Rollers carrying load" + se, d_["loaded"], b.Z, INFO, ""))
        checks.append(_ck("rib_force", "最大挡边力" + sz, "Largest rib force" + se, rp["Qf"], None, INFO, "N"))
        ls, lf = _num(lim.get("p_static")), _num(lim.get("p_fatigue"))
        for ring, zh in (("inner", "内圈（锥）"), ("outer", "外圈（杯）")):
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
                c = sc["cases"][k]
                fat[k] = _run(b, fp * c["Fr"], fp * c["Fa"], theta)
        for ring, zh in (("inner", "内圈（锥）"), ("outer", "外圈（杯）")):
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
        # the rib: roller end against the rib face, taken as flat
        ps = TP.rib_stress(b, max(r["Qf"] for r in list(fat.values()) or [rp]))
        checks.append(
            _ck(
                "rib_p",
                "挡边接触应力（滚子球基面对平面近似）",
                "Rib contact stress (roller end sphere on a flat rib, approximate)",
                ps,
                None,
                INFO if ps is not None else UNKNOWN,
                "MPa",
                "" if ps is not None else "give the radius of the roller's large end face",
                "" if ps is not None else "请填滚子大端球基面半径",
            )
        )
        worst = [runs[k] for k in live] + list(fat.values())
        ends = max(r["ends"] / r["qmax"] for r in worst)
        ok = ends < 1e-9
        straight = g["profile"] == "straight"
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
            "drop": b.cyl.drop(d_["x"]).round(6).tolist(),
        }
        lu = p.get("lube") or {}
        eta, ap, sig = _num(lu.get("eta0")), _num(lu.get("alpha_p")), _num(lu.get("sigma"))
        spun = [k for k in live if sc["cases"][k]["n"] > 0]
        if eta and ap and spun:
            best = None
            for k in spun:
                w = sc["cases"][k]["n"] * 2 * math.pi / 60
                gm = b.D * math.cos(b.ai) / b.dm
                u = w * b.dm * (1 - gm**2) / 4
                f_ = RL.film(lam * runs[k]["qmax"], b.radius("inner"), b.Es, eta, ap, u)
                if best is None or f_["h_min"] < best[0]["h_min"]:
                    best = (f_, k)
            film = best[0]
            lam_f = film["h_min"] * 1000 / sig if sig else None
            checks.append(
                _ck(
                    "film",
                    "最小油膜厚度（最重载切片、内圈，线接触）",
                    "Minimum film thickness (heaviest slice, cone, line contact)",
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
                    lam_f,
                    None,
                    INFO if lam_f is not None else UNKNOWN,
                    "",
                    "" if lam_f is not None else "give the composite surface roughness",
                    "" if lam_f is not None else "请填综合表面粗糙度",
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
        "type": "tapered",
        "chain": None,
        "freq": TP.frequencies(b, n, sc["outer_turns"]) if n else None,
        "film": film,
        "slices": slices,
        "contact": (
            {
                "inner": {"p_max": rp["pmax"]["inner"], "Q": lam * rp["dist"]["Qmax"], "alpha_deg": g["alpha_i_deg"]},
                "outer": {"p_max": rp["pmax"]["outer"], "Q": rp["dist"]["Qmax"], "alpha_deg": g["alpha_o_deg"]},
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
            "da": d_["da"],
            "dr": d_["dr"],
            "theta": d_["theta"],
        }
    return out
