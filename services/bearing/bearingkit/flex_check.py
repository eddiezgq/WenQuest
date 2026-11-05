"""Checks of a harmonic reducer's flexible bearing (round 64, plan section 十八, H2): the project → flex.py → the
same kind of check list as the other types. As made, the bearing is a thin deep groove ball bearing: its geometry
(for the section, drawings, process and 3D) is the deep groove one.

Plain code: no AI, no network.
"""

from __future__ import annotations

import math

import numpy as np

from bearingkit import flex as FX
from bearingkit.analyze import FAIL, INFO, NA, PASS, UNKNOWN, ProjectError, _ck, _limit, _num
from bearingkit.analyze import build as ball_build

CAMS = ("cosine", "ellipse", "points")


def build(p: dict):
    q = dict(p, type="deep_groove")
    b, g = ball_build(q)
    return b, {**g, "flex": True}


def params(p: dict, g: dict) -> dict:
    f = p.get("flex") or {}
    kind = f.get("cam") or "cosine"
    if kind not in CAMS:
        raise ProjectError("the cam is cosine, ellipse or points")
    cam = {"kind": kind}
    if kind == "cosine":
        cam["w0"] = _num(f.get("w0"))
    elif kind == "ellipse":
        cam["a"], cam["b"] = _num(f.get("a")), _num(f.get("b"))
    else:
        cam["points"] = f.get("points") or []
    m = p.get("material") or {}
    return {
        "d": g["d"],
        "D": g["D"],
        "B": g["B"],
        "Dw": g["Dw"],
        "Z": g["Z"],
        "dm": g["dm"],
        "fi": g["fi"],
        "fo": g["fo"],
        "Pd": _num((p.get("inner") or {}).get("Pd")) or 0.0,
        "E": _num(m.get("E")) or 206000.0,
        "nu": _num(m.get("nu")) or 0.3,
        "cam": cam,
        "F": _num(f.get("F")),
        "beta_deg": _num(f.get("beta_deg")),
    }


def analyse(p: dict) -> dict:
    b, g = build(p)
    gp = params(p, g)
    try:
        r = FX.analyse(gp)
    except ValueError as e:
        raise ProjectError(str(e)) from e
    f = p.get("flex") or {}
    lim = p.get("limits") or {}
    checks = []
    gap = g["dm"] * math.sin(math.pi / b.Z) - b.D
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
    for ring, R, zh in (("inner", r["inner"], "内圈沟底壁厚"), ("outer", r["outer"], "外圈沟底壁厚")):
        checks.append(
            _ck(
                "wall_" + ring,
                zh,
                f"{ring.capitalize()} ring wall under the groove",
                R.t,
                lw,
                INFO if lw is None else _limit(R.t, lw, higher_bad=False),
                "mm",
            )
        )
    si, sa = _num(f.get("sig_i_allow")), _num(f.get("sig_a_allow"))
    checks.append(
        _ck(
            "flex_sig_i",
            "内圈弯曲应力（装在凸轮上，随凸轮转，不交变）",
            "Inner ring bending stress (on the cam, turning with it: steady)",
            r["sig_i_max"],
            si,
            _limit(r["sig_i_max"], si),
            "MPa",
            "the largest at the raceway; the limit is yours",
            "沟道表面最大值；许用值由企业按材料填",
        )
    )
    checks.append(
        _ck(
            "flex_sig_a",
            "外圈交变弯曲应力幅（凸轮每转两次）",
            "Outer ring alternating bending stress amplitude (twice per cam turn)",
            r["sig_o_amp"],
            sa,
            _limit(r["sig_o_amp"], sa),
            "MPa",
            f"raceway fibre; mean {r['sig_o_mean']:.0f} MPa, from {r['sig_o_min']:.0f} to {r['sig_o_max']:.0f}",
            f"沟道表面；平均应力 {r['sig_o_mean']:.0f} MPa，范围 {r['sig_o_min']:.0f} 到 {r['sig_o_max']:.0f} MPa",
        )
    )
    ps = _num(lim.get("p_static"))
    for ring, key, zh in (("inner", "p_i_max", "内圈"), ("outer", "p_o_max", "外圈")):
        checks.append(
            _ck(
                "p_" + ring,
                f"接触强度：{zh}最大接触应力",
                f"Max contact stress, {ring} ring",
                r[key],
                ps,
                _limit(r[key], ps) if r[key] > 0 else NA,
                "MPa",
                "as made (the bent raceways' curvature not counted)",
                "按未变形的沟道曲率计算",
            )
        )
    checks.append(_ck("Qmax", "最大钢球载荷", "Largest ball load", r["Qmax"], None, INFO, "N"))
    checks.append(
        _ck(
            "loaded",
            "受载钢球数（各保持架位置）",
            "Balls carrying load (over the cage positions)",
            f"{r['loaded']}–{r['loaded_max']}" if r["loaded"] != r["loaded_max"] else r["loaded"],
            None,
            INFO,
        )
    )
    checks.append(
        _ck(
            "flex_gap",
            "不受载钢球处的最大间隙",
            "Widest gap at an unloaded ball",
            r["gap_max"] * 1000,
            None,
            INFO,
            "µm",
        )
    )
    if abs(r["stretch"]) > 1e-9:
        checks.append(
            _ck(
                "flex_stretch",
                "凸轮使内圈周长变化（按平均半径差）",
                "Cam stretches the inner ring (mean radius change)",
                r["stretch"] * 1000,
                None,
                INFO,
                "µm",
                "the ring is taken as not stretching: check the cam size against the bore",
                "计算按内圈不伸长：请核对凸轮尺寸与内孔",
            )
        )
    if not r["F"]:
        checks.append(
            _ck(
                "flex_load",
                "带载工况（柔轮啮合区对外圈的载荷）",
                "Under load (the flexspline's meshing load on the outer ring)",
                None,
                None,
                UNKNOWN,
                "",
                "not given: only the bending from assembly is computed",
                "未填：只算了装配变形",
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
    w = r["worst"]
    th = r["theta"]
    step = max(1, len(th) // 360)
    return {
        "status": status,
        "checks": checks,
        "geometry": g,
        "type": "flex",
        "flex": {
            "theta_deg": np.degrees(th[::step]).round(3).tolist(),
            "w_cam": (r["cam"].w(th[::step]) * 1000).tolist(),  # µm
            "u_outer": (w["u_ring"][::step] * 1000).tolist(),  # µm, the outer ring at the worst cage position
            "sig_i": r["sig_i"][::step].tolist(),
            "sig_o": w["sig_o"][::step].tolist(),
            "balls": {
                "phi_deg": np.degrees(w["phi"]).round(4).tolist(),
                "Q": w["Q"].tolist(),
                "p_i": w["p_i"].tolist(),
                "p_o": w["p_o"].tolist(),
            },
            "t_i": r["inner"].t,
            "t_o": r["outer"].t,
            "R_i": r["inner"].R,
            "R_o": r["outer"].R,
            "sig_o_amp": r["sig_o_amp"],
            "sig_o_mean": r["sig_o_mean"],
            "sig_i_max": r["sig_i_max"],
            "w_max": r["cam"].max * 1000,
            "F": r["F"],
            "beta_deg": gp["beta_deg"],
        },
        "contact": {
            "inner": {"p_max": r["p_i_max"], "Q": r["Qmax"], "alpha_deg": 0.0},
            "outer": {"p_max": r["p_o_max"], "Q": r["Qmax"], "alpha_deg": 0.0},
        },
    }


def deformed(p: dict, n: int = 180) -> dict:
    """The bearing as mounted on the cam, true size, at the heaviest cage position (for the FreeCAD model): the
    rings as plain annuli of their wall under the groove (no groove, no shoulders: a sketch of the shape), as closed
    curves of n points (x, y) in mm; the ball centres. The long axis is x."""
    _b, g = build(p)
    r = FX.analyse(params(p, g))
    w = r["worst"]
    th = 2 * np.pi * np.arange(n) / n
    wi = r["cam"].w(th)
    # the outer ring's radial displacement at these angles, from the solved ball loads (as in flex.analyse)
    o = r["outer"]
    uo = o.u_point(np.subtract.outer(th, w["phi"])) @ w["Q"] + w["t"][0] * np.cos(th) + w["t"][1] * np.sin(th)
    if r["F"]:
        uo = uo + o.zones(r["F"], np.radians(params(p, g)["beta_deg"]), th)[0]

    def curve(rad):
        return np.column_stack([rad * np.cos(th), rad * np.sin(th)]).tolist()

    ti, to = r["inner"].t, r["outer"].t
    ph = w["phi"]
    rc = (
        g["dm"] / 2 + (r["cam"].w(ph) + np.interp(ph % (2 * np.pi), np.append(th, 2 * np.pi), np.append(uo, uo[0]))) / 2
    )
    return {
        "inner": [curve(g["d"] / 2 + wi), curve(g["d"] / 2 + ti + wi)],
        "outer": [curve(g["D"] / 2 - to + uo), curve(g["D"] / 2 + uo)],
        "balls": np.column_stack([rc * np.cos(ph), rc * np.sin(ph)]).tolist(),
        "B": g["B"],
        "Dw": g["Dw"],
        "w_max": r["cam"].max,
    }
