"""Checks of a single-row tapered roller bearing project (round 64, step 4, part 2).

Project fields beside the common ones:
    inner: {"Dw", "Lw", "Lwe", "Z", "dm", "alpha_o_deg", "alpha_i_deg", "alpha_f_deg", "R_end"}
           mean roller diameter, roller length, effective contact length, number of rollers, pitch diameter, cup
           angle (contact angle), cone angle, direction of the rib's push (blank: square to the roller axis),
           radius of the roller's large end face
    profile, alignment: as for cylindrical roller bearings
A single row is worked with zero end play. A pair (side by side, or one bearing at each end of the shaft) is worked
with the end play or preload set at mounting (taper_pair.py, plan section 十六). Ring walls use the mean roller diameter
projected onto the radial direction, so they are approximate and say so.
Plain code: no AI, no network.
"""

from __future__ import annotations

import math

import numpy as np

from bearingkit import roller as RL
from bearingkit import scenarios as SC
from bearingkit import taper as TP
from bearingkit import taper_pair as TPP
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
        "B": B,  # the overall width T (plan section 二十: one width before; the cone and cup widths below)
        "Bi": _num(s.get("Bi")) or B,
        "Co": _num(s.get("Co")) or B,
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


def pair_config(p: dict, b) -> dict | None:
    """The pair settings of a project, or None for a single row. End play in mm (negative: preload)."""
    pr = p.get("pair") or {}
    arr = pr.get("arrangement") or "single"
    if arr in ("single", ""):
        return None
    if arr not in TPP.ARRANGEMENTS:
        raise ProjectError("a tapered roller bearing pair is back to back (DB) or face to face (DF)")
    mount = pr.get("mount") or "pair"
    if mount not in ("pair", "two_end"):
        raise ProjectError("the pair is side by side or one bearing at each end of the shaft")
    setting = pr.get("setting") or "endplay"
    if setting == "preload":
        Fp = _num(pr.get("preload"))
        if Fp is None or Fp < 0:
            raise ProjectError("give the preload of the tapered pair (N)")
        e = TPP.endplay_for_preload(b, Fp)
    else:
        e_um = _num(pr.get("endplay"))
        if e_um is None:
            raise ProjectError("give the axial end play of the tapered pair (µm; negative for preload)")
        e = e_um / 1000
    s = (p.get("scenario") or {}).get("kind") or "generic"
    spacing = _num(pr.get("spacing"))
    if mount == "two_end" and s != "generic":
        spacing = _num((p.get("scenario") or {}).get("L"))
    if not spacing or spacing <= 0:
        raise ProjectError(
            "give the distance between the two rows"
            if mount == "pair"
            else "give the distance between the two bearings (the span L of the application)"
        )
    sweep = (_num(pr.get("sweep_from")), _num(pr.get("sweep_to")))
    return {
        "arrangement": arr,
        "mount": mount,
        "endplay": e,
        "spacing": spacing,
        "setting": setting,
        "sweep": sweep if None not in sweep and sweep[0] != sweep[1] else None,
    }


def _pair_run(pr: TPP.Pair, b, P) -> dict:
    """One load case on a pair: both rows, the heavier one shown as the single row is."""
    try:
        u = pr.solve(P)
    except TPP.PairError as e:
        raise ProjectError(str(e)) from e
    rows = TPP.rows_of(pr, u)
    best = None
    summ = []
    for r in rows:
        st = TP.stresses(b, r["q"])
        pm = {k: float(v["p"].max()) for k, v in st.items()}
        summ.append(
            {
                "z": r["z"],
                "facing": r["facing"],
                "Fa": r["Fa"],
                "Fr": r["Fr"],
                "Qmax": r["Qmax"],
                "loaded": r["loaded"],
                "p_inner": pm["inner"],
                "p_outer": pm["outer"],
            }
        )
        if best is None or max(pm.values()) > max(best["pmax"].values()):
            best = {
                "dist": r,
                "st": st,
                "j": int(np.argmax(r["Q"])),
                "pmax": pm,
                "ends": float(max(r["q"][:, 0].max(), r["q"][:, -1].max())),
                "qmax": float(r["q"].max()),
                "Qf": float(r["Qf"].max()),
            }
    return {**best, "rows": summ, "u": u}


def setting_curve(pr: TPP.Pair, b, P, e_from_um: float, e_to_um: float, n: int = 21) -> dict:
    """Sweep the end play: the largest contact stress, the rollers carrying load (both rows) and the axial stiffness."""
    out = {"e_um": [], "p_max": [], "loaded": [], "k_axial": [], "preload": []}
    for e_um in np.linspace(e_from_um, e_to_um, n):
        q = TPP.Pair(b, pr.arr, pr.s, e_um / 1000)
        try:
            r = _pair_run(q, b, P)
            k = TPP.stiffness(q, P, r["u"])["axial"]
            row = (max(r["pmax"].values()), sum(x["loaded"] for x in r["rows"]), k)
        except (ProjectError, np.linalg.LinAlgError):
            row = (None, None, None)
        out["e_um"].append(float(e_um))
        out["p_max"].append(row[0])
        out["loaded"].append(row[1])
        out["k_axial"].append(row[2])
        out["preload"].append(q.preload_force())
    return out


def analyse(p: dict) -> dict:
    b, g = build(p)
    lim = p.get("limits") or {}
    sc = scenario_cases(p)
    fp = _num((p.get("scenario") or {}).get("fp"))
    theta = math.radians((_num((p.get("alignment") or {}).get("theta_arcmin")) or 0.0) / 60)
    lam, mu = b.ratios()
    pc = pair_config(p, b)
    pair = TPP.Pair(b, pc["arrangement"], pc["spacing"], pc["endplay"]) if pc else None
    if pc and pc["mount"] == "two_end":
        try:
            sp = SC.supports(p.get("scenario") or {"kind": "generic"}, p.get("loads") or {}, pc["spacing"])
        except SC.ScenarioError as e:
            raise ProjectError(str(e)) from e
        cases = []
        for c in sp["cases"]:
            Pv = SC.shaft_load(c, sp["L"])
            cases.append({**c, "Fr": math.hypot(Pv[0], Pv[1]), "Fa": c["Fz"], "M": 0.0, "P": Pv})
        sc = {
            **sc,
            "cases": cases,
            "motion": sp["motion"],
            "outer_turns": sp["outer_turns"],
            "notes": list(sc["notes"])
            + [
                {
                    "zh": "两端支承：表里是作用在轴上的合力；两端轴承各自分担多少，"
                    "由两列的刚度和安装时调的轴向游隙算出，见“两列”。",
                    "en": "Two supports: the table gives the load on the shaft; how the two bearings "
                    "share it follows from their stiffness and the end play set at mounting (see the two rows).",
                }
            ],
        }
    elif pc:
        for c in sc["cases"]:
            c["P"] = [c["Fr"], 0.0, c["Fa"], c["M"], 0.0]

    def run(c, f=1.0):
        if pair is not None:
            return _pair_run(pair, b, [f * v for v in c["P"]])
        return _run(b, f * c["Fr"], f * c["Fa"], theta)

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
    if pc:
        checks.append(
            _ck(
                "endplay",
                "轴向游隙（安装时调整；负数为预紧）",
                "End play set at mounting (negative: preload)",
                pc["endplay"] * 1000,
                None,
                INFO,
                "µm",
            )
        )
        checks.append(
            _ck(
                "preload",
                "预紧力（无外载时每列的轴向力）",
                "Preload (axial force in each row with no outside load)",
                pair.preload_force(),
                None,
                INFO,
                "N",
            )
        )
    else:
        checks.append(
            _ck(
                "endplay",
                "轴向游隙",
                "End play",
                None,
                None,
                INFO,
                "",
                "set at mounting; a single row is worked with zero end play (choose a pair to set it)",
                "安装时调整；单列按零游隙计算（选成对或两端支承可以给游隙或预紧）",
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
    if not pc and any(c["M"] for c in sc["cases"]):
        checks.append(
            _ck(
                "moment_in",
                "力矩载荷",
                "Moment load",
                max(abs(c["M"]) for c in sc["cases"]) / 1000,
                0.0,
                FAIL,
                "N·m",
                "a single row does not carry a moment; pair it or give the misalignment",
                "单列圆锥滚子轴承不承受力矩：请成对使用或改填倾斜角",
            )
        )
    loaded = [(c["Fr"] > 0 or c["Fa"] != 0 or (pc is not None and (c["M"] or pc["endplay"] < 0))) for c in sc["cases"]]
    runs = [(run(c) if ok else None) for c, ok in zip(sc["cases"], loaded, strict=True)]
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
                fat[k] = run(c, fp)
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
        if pc:
            unl = [k for k in live if any(x["loaded"] == 0 for x in runs[k]["rows"])]
            names = "、".join(_label(sc["cases"][k])["zh"] for k in unl)
            names_en = ", ".join(_label(sc["cases"][k])["en"] for k in unl)
            if pc["endplay"] < 0:
                st_ = FAIL if unl else PASS
                nz = f"卸载的工况：{names}；预紧不够或外载太大" if unl else ""
                ne = f"cases where a row unloads: {names_en}; too little preload or too much load" if unl else ""
            else:
                st_ = INFO
                nz = f"有轴向游隙时一列卸载是正常的（{names}）" if unl else ""
                ne = f"with end play one row unloading is normal ({names_en})" if unl else ""
            checks.append(
                _ck(
                    "pair_loaded",
                    "各工况下两列都有滚子受载（按静止判）",
                    "Both rows carry rollers in every case (at rest)",
                    len(live) - len(unl),
                    len(live),
                    st_,
                    "",
                    ne,
                    nz,
                )
            )
            try:
                k = TPP.stiffness(pair, sc["cases"][kp]["P"], rp["u"])
                for kid, zh, en, unit, val in (
                    ("k_axial", "轴向刚度（峰值工况）", "Axial stiffness (peak case)", "N/µm", k["axial"]),
                    ("k_radial", "径向刚度（峰值工况）", "Radial stiffness (peak case)", "N/µm", k["radial"]),
                    ("k_tilt", "倾覆刚度（峰值工况）", "Tilting stiffness (peak case)", "N·m/mrad", k["tilt"]),
                ):
                    checks.append(_ck(kid, zh, en, val, None, INFO, unit))
            except np.linalg.LinAlgError:
                pass
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
                    **{k: v for k, v in c.items() if k != "P"},
                    "Qmax": r["dist"]["Qmax"] if r else 0.0,
                    "p_inner": r["pmax"]["inner"] if r else 0.0,
                    "p_outer": r["pmax"]["outer"] if r else 0.0,
                }
                for c, r in zip(sc["cases"], runs, strict=True)
            ],
        },
    }
    if pc:
        out["pair"] = {k: v for k, v in pc.items() if k != "sweep"} | {
            "endplay_um": pc["endplay"] * 1000,
            "preload": pair.preload_force(),
        }
        out["pair_rows"] = rp["rows"] if rp else None
        if pc["sweep"] and rp:
            out["setting_curve"] = setting_curve(pair, b, sc["cases"][kp]["P"], *pc["sweep"])
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
