"""Checks of a crossed roller bearing (round 64, plan section 十九, X2): the project → crossed.py → the same kind of
check list as the other types. The rings' V-groove geometry (for the section, drawings and 3D) comes from here too.

Plain code: no AI, no network.
"""

from __future__ import annotations

import math

import numpy as np

from bearingkit import crossed as CX
from bearingkit.analyze import FAIL, INFO, NA, PASS, UNKNOWN, ProjectError, _ck, _limit, _num, scenario_cases


def build(p: dict):
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
    alpha = _num(i.get("alpha0_deg"))
    pc = (p.get("pair") or {}).get("setting") or "endplay"
    E, nu = _num(m.get("E")) or 206000.0, _num(m.get("nu")) or 0.3

    def make(Gr):
        return CX.Crossed(Dw, Lwe, int(Z), dm, alpha, Gr, E, nu, p.get("profile") or {"kind": "straight"})

    try:
        b0 = make(0.0)
    except ValueError as e:
        raise ProjectError(str(e)) from e
    if pc == "preload":
        Fp = _num((p.get("pair") or {}).get("preload"))
        if Fp is None or Fp < 0:
            raise ProjectError("give the preload of the crossed roller bearing (N)")
        Gr = CX.clearance_for_preload(b0, Fp)
    else:
        g_um = _num((p.get("pair") or {}).get("endplay"))
        if g_um is None:
            raise ProjectError("give the radial clearance of the crossed roller bearing (µm; negative for preload)")
        Gr = g_um / 1000
    b = make(Gr)
    a = math.radians(alpha)
    ca, sa = math.cos(a), math.sin(a)
    R0 = dm / 2
    g = {
        "type": "crossed",
        "d": d,
        "D": D,
        "B": B,
        "dm": dm,
        "Dw": Dw,
        "Z": int(Z),
        "Lw": Lw,
        "Lwe": Lwe,
        "alpha_deg": alpha,
        "Gr": Gr,
        # the V grooves: apexes (sharp; the relief under them is not drawn) and the lands just covering the rollers
        "r_ai": R0 - Dw / (2 * ca),
        "r_ao": R0 + Dw / (2 * ca),
        "r_li": R0 - Dw / 2 * ca + Lw / 2 * sa,
        "r_lo": R0 + Dw / 2 * ca - Lw / 2 * sa,
        "split": ((p.get("crossed") or {}).get("split") or "outer"),
    }
    g["di"], g["do"] = 2 * g["r_ai"], 2 * g["r_ao"]
    return b, g


def _case_load(c: dict, s: dict) -> np.ndarray:
    M = c.get("M") or 0.0
    # a robot joint with a horizontal axis held by this one bearing: the overhung weight is a moment too (plan 十九)
    if (
        s.get("kind") == "joint"
        and (s.get("axis") or "horizontal") == "horizontal"
        and not _num(s.get("L"))
        and _num(s.get("x"))
    ):
        M = (c.get("Fr") or 0.0) * _num(s.get("x"))
    return CX.load(c.get("Fr") or 0.0, c.get("Fa") or 0.0, M)


def analyse(p: dict) -> dict:
    b, g = build(p)
    lim = p.get("limits") or {}
    sc = scenario_cases(p)
    s = p.get("scenario") or {"kind": "generic"}
    checks = []
    gap = g["dm"] * math.sin(math.pi / b.Z) - b.Dw
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
        ("inner", g["r_ai"] - g["d"] / 2, "内圈 V 形沟顶点下壁厚"),
        ("outer", g["D"] / 2 - g["r_ao"], "外圈 V 形沟顶点外壁厚"),
    ):
        checks.append(
            _ck(
                "wall_" + ring,
                zh,
                f"{ring.capitalize()} ring wall at the V-groove apex",
                wall,
                lw,
                FAIL if wall <= 0 else (INFO if lw is None else _limit(wall, lw, higher_bad=False)),
                "mm",
            )
        )
    a = math.radians(g["alpha_deg"])
    fits = g["Lw"] <= g["Dw"] * math.tan(a) + 1e-12
    checks.append(
        _ck(
            "x_fit",
            "滚子端角不碰 V 形沟另一面（Lw ≤ Dw·tan α）",
            "Roller corners clear the other V face (Lw ≤ Dw tan α)",
            g["Lw"],
            g["Dw"] * math.tan(a),
            PASS if fits else FAIL,
            "mm",
        )
    )
    lands = g["r_lo"] - g["r_li"]
    checks.append(
        _ck(
            "x_lands",
            "内外圈挡边之间的间隙",
            "Gap between the inner and outer ring lands",
            lands,
            None,
            PASS if lands > 0 else FAIL,
            "mm",
            "" if lands > 0 else "the rings would touch: shorter rollers",
            "" if lands > 0 else "内外圈会相碰：滚子要短一些",
        )
    )
    runs = []
    for c in sc["cases"]:
        P = _case_load(c, s)
        try:
            u = b.solve(P)
        except ValueError as e:
            raise ProjectError(str(e)) from e
        runs.append({"case": c, "P": P, "u": u, "r": b.rollers(u)})
    heavy = max(runs, key=lambda x: max(x["r"]["p_max_inner"], x["r"]["p_max_outer"]))
    ps = _num(lim.get("p_static"))
    for ring, key, zh in (("inner", "p_max_inner", "内圈"), ("outer", "p_max_outer", "外圈")):
        v = heavy["r"][key]
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
    pre = b.preload_force()
    # the preload holds when no roller loses contact in any case (under a moment both sets are always loaded
    # somewhere, so "both sets carry load" says nothing; a roller coming off is where the stiffness drops)
    least = min(x["r"]["loaded"] for x in runs)
    both = least == b.Z
    checks.append(
        _ck("x_gr", "径向游隙（负数为预紧）", "Radial clearance (negative: preload)", g["Gr"] * 1000, None, INFO, "µm")
    )
    checks.append(
        _ck(
            "preload",
            "预紧力（每组滚子的轴向力）",
            "Preload (axial force of each set of rollers)",
            pre,
            None,
            INFO,
            "N",
        )
    )
    checks.append(
        _ck(
            "x_both",
            "预紧不脱开：各工况下所有滚子都保持接触",
            "The preload holds: every roller keeps contact in every case",
            f"{least}/{b.Z}",
            None,
            (PASS if both else FAIL) if pre > 0 else INFO,
            "",
            "" if both or pre <= 0 else "some rollers lose contact under the load: more preload, or accept it",
            "" if both or pre <= 0 else "有滚子在载荷下脱开：加大预紧，或由企业判定可以接受",
        )
    )
    st = b.stiffness(heavy["u"])
    for key, zh, en, unit in (
        ("axial", "轴向刚度", "Axial stiffness", "N/µm"),
        ("radial", "径向刚度", "Radial stiffness", "N/µm"),
        ("tilt", "倾覆刚度", "Tilting stiffness", "N·m/mrad"),
    ):
        checks.append(_ck("k_" + key, zh + "（峰值工况）", en + " (peak case)", st[key], None, INFO, unit))
    r = heavy["r"]
    checks.append(_ck("Qmax", "最大滚子载荷", "Largest roller load", r["Qmax"], None, INFO, "N"))
    checks.append(_ck("loaded", "受载滚子数", "Rollers carrying load", r["loaded"], None, INFO))
    ends = r["q"][:, [0, -1]].max() > 0
    straight = ((p.get("profile") or {}).get("kind") or "straight") == "straight"
    if ends:
        checks.append(
            _ck(
                "x_ends",
                "滚子端部受载",
                "Roller ends carry load",
                "是",
                None,
                UNKNOWN if straight else INFO,
                "",
                "straight rollers: the edge stress at the ends is not captured by the slices; crown them",
                "直线滚子端部有边缘应力，切片法算不出来：请给凸度",
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
    j = int(np.argmax(r["Q"]))
    pr = p.get("pair") or {}
    f, t_ = _num(pr.get("sweep_from")), _num(pr.get("sweep_to"))
    curve = None
    if f is not None and t_ is not None and f != t_:

        def make(gr):
            return CX.Crossed(b.Dw, b.L, b.Z, b.dm, g["alpha_deg"], gr, b.cyl.E, b.cyl.nu, b.cyl.profile)

        c = CX.setting_curve(make, heavy["P"], f, t_, 21)
        curve = {
            "e_um": c["g_um"],
            "p_max": c["p_max"],
            "loaded": c["loaded"],
            "k_axial": c["k_axial"],
            "k_tilt": c["k_tilt"],
            "preload": c["preload"],
        }
    try:
        from bearingkit import parts as PT

        prf = PT.crossed_parts(g)
        profile = {k: [list(x["a"]) for x in prf[k]] for k in ("inner", "outer")}
    except ValueError:
        profile = None
    return {
        "profile": profile,
        "status": status,
        "checks": checks,
        "geometry": g,
        "type": "crossed",
        "pair": {"endplay_um": g["Gr"] * 1000, "preload": pre},
        "crossed": {
            "psi_deg": r["psi_deg"].tolist(),
            "facing": r["facing"].tolist(),
            "Q": r["Q"].tolist(),
            "s": r["s"].tolist(),
            "q_max_roller": r["q"][j].tolist(),
            "p_i": r["p_i"][j].tolist(),
            "p_o": r["p_o"][j].tolist(),
            "Fa_plus": r["Fa_plus"],
            "Fa_minus": r["Fa_minus"],
            "case": heavy["case"].get("label") or "",
            "P": heavy["P"].tolist(),
        },
        "setting_curve": curve,
        "contact": {
            "inner": {"p_max": r["p_max_inner"], "Q": r["Qmax"], "alpha_deg": g["alpha_deg"]},
            "outer": {"p_max": r["p_max_outer"], "Q": r["Qmax"], "alpha_deg": g["alpha_deg"]},
        },
        "scenario": {
            "kind": sc["kind"],
            "motion": sc["motion"],
            "outer_turns": sc["outer_turns"],
            "steps": sc["steps"]
            + (
                [
                    {
                        "zh": "单个交叉滚子承受的倾覆力矩 M = W·x",
                        "en": "Tilting moment on the one crossed roller bearing M = W x",
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
                    "Qmax": x["r"]["Qmax"],
                    "p_inner": x["r"]["p_max_inner"],
                    "p_outer": x["r"]["p_max_outer"],
                }
                for x in runs
            ],
        },
    }
