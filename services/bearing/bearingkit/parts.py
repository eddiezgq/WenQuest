"""Part profiles of a bearing, and from them the STEP model and the DXF sections (round 64, step 5, part 1).

Every part is a profile in its own (r, z) half plane, counter-clockwise, straight lines and circular arcs, taken
from the design geometry (the same construction as the section drawing on the page):
  - ball bearings: rings with their grooves (groove radius f·D_w, centre on the contact line, shoulders of the
    given heights; both shoulders drawn at the given height), balls as spheres on the pitch circle;
  - cylindrical roller bearings: plain rings to the raceways, cylindrical rollers (length L_w);
  - tapered roller bearings: cone with its large-end rib (square to the roller axis, up to the roller axis), cup,
    rollers as frustums on the inclined axis.
Not drawn, because there are no data for them: chamfers, undercuts, the ribs of cylindrical roller bearings, the
roller crown (a few microns), cages. The drawing notes say so, and tolerances stay "unknown" until entered.

Plain code: no AI, no network. mm.
"""

from __future__ import annotations

import math

import numpy as np

from bearingkit import step3d as S


class PartsError(ValueError):
    pass


def _poly(pts):
    """Closed polygon → straight segments, made counter-clockwise in (r, z)."""
    P = [tuple(map(float, p)) for p in pts]
    area = sum(P[k][0] * P[(k + 1) % len(P)][1] - P[(k + 1) % len(P)][0] * P[k][1] for k in range(len(P)))
    if area < 0:
        P = P[::-1]
    return [{"a": P[k], "b": P[(k + 1) % len(P)], "arc": None} for k in range(len(P))]


def ball_parts(g: dict) -> dict:
    d, D, B, dm, Dw = g["d"], g["D"], g["B"], g["dm"], g["Dw"]
    hi, ho = g.get("h_i"), g.get("h_o")
    if hi is None or ho is None:
        raise PartsError("give the shoulder heights: the rings cannot be drawn without them")
    ri, ro = g["fi"] * Dw, g["fo"] * Dw
    a0 = math.radians(g["alpha0_deg"]) if g["type"] == "angular" else 0.0
    n0 = (math.sin(a0), math.cos(a0))  # (axial, radial)
    ci = ((ri - Dw / 2) * n0[0], dm / 2 + (ri - Dw / 2) * n0[1])  # (z, r)
    co = (-(ro - Dw / 2) * n0[0], dm / 2 - (ro - Dw / 2) * n0[1]) if g["type"] == "angular" else (0.0, g["do"] / 2 - ro)
    rsI = ci[1] - ri + hi
    rsO = co[1] + ro - ho
    wI = math.sqrt(max(ri * ri - (rsI - ci[1]) ** 2, 0))
    wO = math.sqrt(max(ro * ro - (rsO - co[1]) ** 2, 0))
    if ci[0] - wI <= -B / 2 or ci[0] + wI >= B / 2 or co[0] - wO <= -B / 2 or co[0] + wO >= B / 2:
        raise PartsError("the groove is wider than the ring at the shoulder")
    if not (d / 2 < ci[1] - ri and rsI < rsO and co[1] + ro < D / 2):
        raise PartsError("the rings do not fit: check the shoulder heights and the sizes")
    inner = [
        {"a": (d / 2, -B / 2), "b": (rsI, -B / 2), "arc": None},
        {"a": (rsI, -B / 2), "b": (rsI, ci[0] - wI), "arc": None},
        {"a": (rsI, ci[0] - wI), "b": (rsI, ci[0] + wI), "arc": {"c": (ci[1], ci[0]), "rho": ri, "ccw": False}},
        {"a": (rsI, ci[0] + wI), "b": (rsI, B / 2), "arc": None},
        {"a": (rsI, B / 2), "b": (d / 2, B / 2), "arc": None},
        {"a": (d / 2, B / 2), "b": (d / 2, -B / 2), "arc": None},
    ]
    outer = [
        {"a": (rsO, -B / 2), "b": (D / 2, -B / 2), "arc": None},
        {"a": (D / 2, -B / 2), "b": (D / 2, B / 2), "arc": None},
        {"a": (D / 2, B / 2), "b": (rsO, B / 2), "arc": None},
        {"a": (rsO, B / 2), "b": (rsO, co[0] + wO), "arc": None},
        {"a": (rsO, co[0] + wO), "b": (rsO, co[0] - wO), "arc": {"c": (co[1], co[0]), "rho": ro, "ccw": False}},
        {"a": (rsO, co[0] - wO), "b": (rsO, -B / 2), "arc": None},
    ]
    ball = [
        {"a": (0.0, -Dw / 2), "b": (0.0, Dw / 2), "arc": {"c": (0.0, 0.0), "rho": Dw / 2, "ccw": True}},
        {"a": (0.0, Dw / 2), "b": (0.0, -Dw / 2), "arc": None},
    ]
    return {"inner": inner, "outer": outer, "element": ball, "element_kind": "ball"}


def cyl_parts(g: dict) -> dict:
    d, D, B, Dw, Lw = g["d"], g["D"], g["B"], g["Dw"], g["Lw"]
    inner = _poly([(d / 2, -B / 2), (g["di"] / 2, -B / 2), (g["di"] / 2, B / 2), (d / 2, B / 2)])
    outer = _poly([(g["do"] / 2, -B / 2), (D / 2, -B / 2), (D / 2, B / 2), (g["do"] / 2, B / 2)])
    roller = _poly([(0, -Lw / 2), (Dw / 2, -Lw / 2), (Dw / 2, Lw / 2), (0, Lw / 2)])
    return {"inner": inner, "outer": outer, "element": roller, "element_kind": "roller"}


def taper_parts(g: dict) -> dict:
    d, D, B, dm, Dw, Lw = g["d"], g["D"], g["B"], g["dm"], g["Dw"], g["Lw"]
    ao, ai = math.radians(g["alpha_o_deg"]), math.radians(g["alpha_i_deg"])
    am, ph = (ao + ai) / 2, (ao - ai) / 2
    u, n = (math.cos(am), math.sin(am)), (-math.sin(am), math.cos(am))  # (axial, radial)

    def rad(s):
        return Dw / 2 + s * math.tan(ph)

    def pt(s, side):
        return (s * u[0] + side * rad(s) * n[0], dm / 2 + s * u[1] + side * rad(s) * n[1])

    cup0, cone0 = pt(0, 1), pt(0, -1)

    def cupR(x):
        return cup0[1] + (x - cup0[0]) * math.tan(ao)

    def coneR(x):
        return cone0[1] + (x - cone0[0]) * math.tan(ai)

    end = pt(Lw / 2, -1)
    top = (Lw / 2 * u[0], dm / 2 + Lw / 2 * u[1])
    if not (top[0] < B / 2 and coneR(-B / 2) > d / 2 and cupR(B / 2) < D / 2):
        raise PartsError("the rollers do not fit in these rings: check the width, angles and sizes")
    cone = _poly(
        [(d / 2, -B / 2), (coneR(-B / 2), -B / 2), (end[1], end[0]), (top[1], top[0]), (top[1], B / 2), (d / 2, B / 2)]
    )
    cup = _poly([(cupR(-B / 2), -B / 2), (D / 2, -B / 2), (D / 2, B / 2), (cupR(B / 2), B / 2)])
    R_end = g.get("R_end")
    r_l = rad(Lw / 2)
    if R_end and R_end > r_l:
        # the large end is a sphere of radius R_end touching the rib at the roller axis (a flat end would cut into
        # the rib off the section plane)
        zc = Lw / 2 - R_end
        z_rim = zc + math.sqrt(R_end * R_end - r_l * r_l)
        roller = [
            {"a": (0.0, -Lw / 2), "b": (rad(-Lw / 2), -Lw / 2), "arc": None},
            {"a": (rad(-Lw / 2), -Lw / 2), "b": (r_l, z_rim), "arc": None},
            {"a": (r_l, z_rim), "b": (0.0, Lw / 2), "arc": {"c": (0.0, zc), "rho": R_end, "ccw": True}},
            {"a": (0.0, Lw / 2), "b": (0.0, -Lw / 2), "arc": None},
        ]
    else:
        roller = _poly([(0, -Lw / 2), (rad(-Lw / 2), -Lw / 2), (r_l, Lw / 2), (0, Lw / 2)])
    return {"inner": cone, "outer": cup, "element": roller, "element_kind": "taper", "axis_deg": math.degrees(am)}


def parts(g: dict) -> dict:
    t = g["type"]
    if t in ("deep_groove", "angular"):
        return ball_parts(g)
    if t == "cylindrical":
        return cyl_parts(g)
    if t == "tapered":
        return taper_parts(g)
    raise PartsError("no parts for this bearing type")


def _elements(g: dict, pr: dict):
    """Frames (or centres) of the rolling elements round the pitch circle."""
    out = []
    for j in range(g["Z"]):
        psi = 2 * math.pi * j / g["Z"]
        er = np.array([math.cos(psi), math.sin(psi), 0.0])
        c = er * g["dm"] / 2
        if pr["element_kind"] == "ball":
            out.append(c)
        elif pr["element_kind"] == "roller":
            out.append(S.Frame(c, (0, 0, 1), er))
        else:
            am = math.radians(pr["axis_deg"])
            z = np.array([0, 0, 1.0]) * math.cos(am) + er * math.sin(am)
            x = -np.array([0, 0, 1.0]) * math.sin(am) + er * math.cos(am)
            out.append(S.Frame(c, z, x))
    return out


def step(g: dict, which: str = "bearing", name: str = "bearing") -> tuple[str, dict]:
    """STEP text of one part ("inner", "outer", "element") or of the bearing as assembled, and the analytic volumes."""
    pr = parts(g)
    w = S.Writer()
    breps, vol = [], {}
    F0 = S.Frame()
    if which in ("inner", "bearing"):
        breps.append(S.revolve(w, F0, pr["inner"], "inner ring"))
        vol["inner"] = S.volume(pr["inner"])
    if which in ("outer", "bearing"):
        breps.append(S.revolve(w, F0, pr["outer"], "outer ring"))
        vol["outer"] = S.volume(pr["outer"])
    if which in ("element", "bearing"):
        places = _elements(g, pr) if which == "bearing" else [None]
        for k, pl in enumerate(places):
            if pr["element_kind"] == "ball":
                breps.append(S.sphere(w, pl if pl is not None else (0, 0, 0), g["Dw"] / 2, f"ball {k + 1}"))
            else:
                breps.append(S.revolve(w, pl if pl is not None else F0, pr["element"], f"roller {k + 1}"))
        ve = (math.pi * g["Dw"] ** 3 / 6) if pr["element_kind"] == "ball" else S.volume(pr["element"])
        vol["element"] = ve * len(places)
    if not breps:
        raise PartsError("the part is inner, outer, element or bearing")
    return S.wrap(w, name, breps), vol


# ---------------------------------------------------------------- DXF and drawing data


def _arc_angles(s):
    rc, zc = s["arc"]["c"]
    a0 = math.degrees(math.atan2(s["a"][1] - zc, s["a"][0] - rc))
    a1 = math.degrees(math.atan2(s["b"][1] - zc, s["b"][0] - rc))
    return (a0, a1) if s["arc"]["ccw"] else (a1, a0)  # DXF arcs run counter-clockwise


def dxf(segs: list[dict], layer: str = "SECTION") -> str:
    """DXF (R12) of a part's half section: x = axial (z), y = radius (r)."""
    out = ["0", "SECTION", "2", "ENTITIES"]
    for s in segs:
        if s.get("arc") is None:
            (r0, z0), (r1, z1) = s["a"], s["b"]
            out += ["0", "LINE", "8", layer, "10", f"{z0:.6f}", "20", f"{r0:.6f}", "11", f"{z1:.6f}", "21", f"{r1:.6f}"]
        else:
            rc, zc = s["arc"]["c"]
            a0, a1 = _arc_angles(s)
            # in the drawing x = z, y = r: the angle measured from +x is 90° − (angle from +r)
            out += [
                "0",
                "ARC",
                "8",
                layer,
                "10",
                f"{zc:.6f}",
                "20",
                f"{rc:.6f}",
                "40",
                f"{s['arc']['rho']:.6f}",
                "50",
                f"{(90 - a1) % 360:.6f}",
                "51",
                f"{(90 - a0) % 360:.6f}",
            ]
    out += ["0", "ENDSEC", "0", "EOF"]
    return "\n".join(out) + "\n"


def outline(segs: list[dict], n_arc: int = 48) -> list[list[float]]:
    """Polyline (z, r) of a profile for the page's drawing."""
    pts = []
    for s in segs:
        if s.get("arc") is None:
            pts.append([s["a"][1], s["a"][0]])
        else:
            rc, zc = s["arc"]["c"]
            rho = s["arc"]["rho"]
            a0 = math.atan2(s["a"][1] - zc, s["a"][0] - rc)
            a1 = math.atan2(s["b"][1] - zc, s["b"][0] - rc)
            if s["arc"]["ccw"] and a1 <= a0:
                a1 += 2 * math.pi
            if not s["arc"]["ccw"] and a1 >= a0:
                a1 -= 2 * math.pi
            for a in np.linspace(a0, a1, n_arc, endpoint=False):
                pts.append([zc + rho * math.sin(a), rc + rho * math.cos(a)])
    return [[round(z, 5), round(r, 5)] for z, r in pts]


def drawings(g: dict) -> dict:
    pr = parts(g)
    names = {
        "inner": ("内圈", "Inner ring"),
        "outer": ("外圈", "Outer ring"),
        "element": {"ball": ("钢球", "Ball"), "roller": ("滚子", "Roller"), "taper": ("圆锥滚子", "Tapered roller")}[
            pr["element_kind"]
        ],
    }
    out = {}
    for k in ("inner", "outer", "element"):
        segs = pr[k]
        rs = [p for s in segs for p in (s["a"][0], s["b"][0])]
        zs = [p for s in segs for p in (s["a"][1], s["b"][1])]
        out[k] = {
            "zh": names[k][0],
            "en": names[k][1],
            "outline": outline(segs),
            "volume": S.volume(segs) if pr["element_kind"] != "ball" or k != "element" else math.pi * g["Dw"] ** 3 / 6,
            "r_min": min(rs),
            "r_max": max(rs),
            "width": max(zs) - min(zs),
            "arcs": [{"r": s["arc"]["rho"], "c": [s["arc"]["c"][1], s["arc"]["c"][0]]} for s in segs if s.get("arc")],
        }
    out["kind"] = pr["element_kind"]
    out["notes"] = [
        {
            "zh": "倒角、退刀槽、保持架"
            + ("、挡边" if g["type"] == "cylindrical" else "")
            + ("、凸度" if g["type"] in ("cylindrical", "tapered") else "")
            + "没有数据，图和三维模型里没有画；尺寸公差在企业填写或标准正文录入前为“未知”。",
            "en": "Chamfers, undercuts and cages"
            + (", ribs" if g["type"] == "cylindrical" else "")
            + (", crown" if g["type"] in ("cylindrical", "tapered") else "")
            + " have no data and are not drawn or modelled; tolerances are unknown until entered.",
        }
    ]
    return out
