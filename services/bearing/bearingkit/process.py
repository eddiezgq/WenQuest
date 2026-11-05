"""Process routes and operation sheets for the rings (round 64, step 5, part 2).

The software gives the structure and the arithmetic; the numbers (allowances, tolerances, heat-treatment change,
grinding and superfinishing parameters) are the company's own, from its machines and experience. There are no
default values: a number not given is unknown, and so is everything that depends on it.

Each ring has machined features taken from the design: the bore, the outside diameter (the land of the inner ring),
the width (both faces) and the raceway diameter (groove bottom of a ball bearing, mid-length of a tapered raceway).
All sizes are on the diameter or on the width. An operation size is written by the "into the material" rule: an
external feature (outside diameters, the inner raceway, the width) has its upper deviation 0, an internal feature
(bores, the outer raceway) its lower deviation 0. A state of a feature is then (mm, w): its max-material limit and
the width of its tolerance; external sizes lie in [mm − w, mm], internal in [mm, mm + w].

Working back from the finished size, a cutting operation with nominal allowance Z (max-material to max-material)
had before it mm_in = mm_out + Z (external) or mm_out − Z (internal). Heat treatment changes a size by Δ (growth
positive) with a scatter s: after it, mm = mm_before + Δ ± s/2 and w = w_before + s; its distortion e (out of
round) only matters for the first cut after it. The stock actually removed by a cut then lies between
    Z_min = Z − w_in − e_heat − e_setup     and     Z_max = Z + w_out,
which is the usual allowance calculation (e.g. 机械制造工艺学, minimum allowance = preceding tolerance + defect
layer + spatial deviations + setup error). Z_min ≤ 0 means the cut may not clean up: a fail. Against the company's
required minimum (defect layer and roughness) and, when given, its largest allowed stock.

Plain code: no AI, no network. mm.
"""

from __future__ import annotations

import copy
import math

from bearingkit import parts as PT

PASS, FAIL, UNKNOWN, NA, INFO = "pass", "fail", "unknown", "na", "info"
CUT, HEAT, OTHER = "cut", "heat", "other"
KINDS = {
    "turn": CUT,
    "grind": CUT,
    "superfinish": CUT,
    "cut": CUT,
    "heat": HEAT,
    "wash": OTHER,
    "assemble": OTHER,
    "inspect": OTHER,
    "other": OTHER,
}
MAX_OPS = 40


class ProcessError(ValueError):
    pass


FEATURE_NAMES = {
    "bore": ("内孔", "Bore"),
    "od": ("外径", "Outside diameter"),
    "land": ("挡边外径", "Land diameter"),
    "land_bore": ("挡边内径", "Land bore"),
    "rib": ("挡边外径", "Rib diameter"),
    "width": ("宽度（两端面）", "Width (both faces)"),
    "race": ("沟道直径", "Raceway diameter"),
    "dia": ("直径", "Diameter"),
    "length": ("长度（两端面）", "Length (both ends)"),
}


def _num(v):
    if v is None or v == "":
        return None
    try:
        x = float(v)
    except (TypeError, ValueError) as exc:
        raise ProcessError("numbers must be finite") from exc
    if not math.isfinite(x):
        raise ProcessError("numbers must be finite")
    return x


def _f(fid, size, side, zh=None, en=None):
    nz, ne = FEATURE_NAMES[fid]
    return {"id": fid, "zh": zh or nz, "en": en or ne, "size": float(size), "side": side}


def features(g: dict) -> dict:
    """Machined features of the inner and outer ring from the design geometry (the same profiles as the drawings)."""
    pr = PT.parts(g)
    t = g["type"]
    B = g["B"]
    rs_in = [p for s in pr["inner"] for p in (s["a"][0], s["b"][0])]
    rs_out = [p for s in pr["outer"] for p in (s["a"][0], s["b"][0])]
    if t in ("deep_groove", "angular"):
        ai = next(s["arc"] for s in pr["inner"] if s["arc"])
        ao = next(s["arc"] for s in pr["outer"] if s["arc"])
        race_i, race_o = 2 * (ai["c"][0] - ai["rho"]), 2 * (ao["c"][0] + ao["rho"])
        rname = ("沟底直径", "Groove bottom diameter")
        inner = [
            _f("bore", g["d"], "int"),
            _f("land", 2 * max(rs_in), "ext"),
            _f("width", B, "ext"),
            _f("race", race_i, "ext", *rname),
        ]
        outer = [
            _f("od", g["D"], "ext"),
            _f("land_bore", 2 * min(rs_out), "int"),
            _f("width", B, "ext"),
            _f("race", race_o, "int", *rname),
        ]
    elif t == "cylindrical":
        rname = ("滚道直径", "Raceway diameter")
        inner = [_f("bore", g["d"], "int"), _f("width", B, "ext"), _f("race", g["di"], "ext", *rname)]
        outer = [_f("od", g["D"], "ext"), _f("width", B, "ext"), _f("race", g["do"], "int", *rname)]
    elif t == "tapered":
        rname = ("滚道中点直径", "Raceway diameter at mid-length")
        cone_seg = max(
            (s for s in pr["inner"] if abs(s["a"][1] - s["b"][1]) > 1e-9 and abs(s["a"][0] - s["b"][0]) > 1e-9),
            key=lambda s: math.dist(s["a"], s["b"]),
        )
        cup_seg = next(
            s for s in pr["outer"] if abs(s["a"][0] - s["b"][0]) > 1e-9 and abs(s["a"][1] - s["b"][1]) > 1e-9
        )
        mid = lambda s: s["a"][0] + s["b"][0]  # noqa: E731 (diameter at the middle of the segment)
        inner = [
            _f("bore", g["d"], "int"),
            _f("rib", 2 * max(rs_in), "ext"),
            _f("width", g.get("Bi") or B, "ext"),  # the cone width B (plan section 二十)
            _f("race", mid(cone_seg), "ext", *rname),
        ]
        outer = [
            _f("od", g["D"], "ext"),
            _f("width", g.get("Co") or B, "ext"),  # the cup width C
            _f("race", mid(cup_seg), "int", *rname),
        ]
    else:
        raise ProcessError("the bearing type is deep_groove, angular, cylindrical or tapered")
    return {"inner": inner, "outer": outer}


def element_features(g: dict) -> tuple[str, list[dict]]:
    """The rolling element's machined features (plan section 二十, part 3): a ball's diameter; a roller's diameter
    (the mean one of a tapered roller) and length. Returns ("ball" | "roller", features)."""
    pr = PT.parts(g)
    if pr["element_kind"] == "ball":
        return "ball", [_f("dia", g["Dw"], "ext", "钢球直径", "Ball diameter")]
    dz = ("平均直径", "Mean diameter") if g["type"] == "tapered" else ("滚子直径", "Roller diameter")
    return "roller", [_f("dia", g["Dw"], "ext", *dz), _f("length", g["Lw"], "ext", "滚子长度", "Roller length")]


# The usual chain of a bearing ring (plan section 十三 (二)); structure only, no numbers.
CHAIN = {
    "inner": [
        ("turn", "车削", "Turning", ["bore", "land", "rib", "width", "race"]),
        ("heat", "热处理（淬火、回火）", "Heat treatment", ["bore", "land", "rib", "width", "race"]),
        ("grind", "磨端面", "Face grinding", ["width"]),
        ("grind", "磨外径（挡边）", "Land grinding", ["land", "rib"]),
        ("grind", "磨沟道 / 滚道", "Raceway grinding", ["race"]),
        ("grind", "磨内孔", "Bore grinding", ["bore"]),
        ("superfinish", "超精沟道 / 滚道", "Raceway superfinishing", ["race"]),
        ("wash", "清洗", "Washing", []),
        ("assemble", "合套", "Assembly", []),
        ("inspect", "检测", "Inspection", []),
    ],
    "outer": [
        ("turn", "车削", "Turning", ["od", "land_bore", "width", "race"]),
        ("heat", "热处理（淬火、回火）", "Heat treatment", ["od", "land_bore", "width", "race"]),
        ("grind", "磨端面", "Face grinding", ["width"]),
        ("grind", "磨外径", "Outside diameter grinding", ["od"]),
        ("grind", "磨沟道 / 滚道", "Raceway grinding", ["race"]),
        ("superfinish", "超精沟道 / 滚道", "Raceway superfinishing", ["race"]),
        ("wash", "清洗", "Washing", []),
        ("assemble", "合套", "Assembly", []),
        ("inspect", "检测", "Inspection", []),
    ],
}
# The usual chain of a ball and of a roller (plan section 二十, part 3); structure only, no numbers. The cold-headed
# (or cut) blank is the starting state: its tolerance is the "blank" one.
ELEMENT_CHAIN = {
    "ball": [
        ("grind", "光球", "Flashing", ["dia"]),
        ("grind", "软磨", "Soft grinding", ["dia"]),
        ("heat", "热处理（淬火、回火）", "Heat treatment", ["dia"]),
        ("grind", "硬磨", "Hard grinding", ["dia"]),
        ("superfinish", "精研", "Lapping", ["dia"]),
        ("wash", "清洗", "Washing", []),
        ("inspect", "分选（按直径分组）", "Sorting (diameter groups)", []),
    ],
    "roller": [
        ("turn", "车削（或冷镦后车）", "Turning (or heading, then turning)", ["dia", "length"]),
        ("heat", "热处理（淬火、回火）", "Heat treatment", ["dia", "length"]),
        ("grind", "磨端面", "End face grinding", ["length"]),
        ("grind", "磨外径（无心磨）", "Outside diameter grinding (centreless)", ["dia"]),
        ("superfinish", "超精外径（凸度）", "Superfinishing (crown)", ["dia"]),
        ("wash", "清洗", "Washing", []),
        ("inspect", "分选（按直径分组）", "Sorting (diameter groups)", []),
    ],
}
CUT_FIELDS = ("Z", "T", "Zreq", "Zmax", "setup")
STOCK_FIELDS = ("Z", "dz", "Zreq")
HEAT_FIELDS = ("change", "scatter", "distortion")


def blank_template(g: dict) -> dict:
    """The usual chain for this bearing's rings with every number left empty for the company to fill."""
    fs = features(g)
    return {"rings": {ring: _blank_ring(fs[ring], CHAIN[ring]) for ring in ("inner", "outer")}}


def element_template(g: dict) -> dict:
    """The usual chain of this bearing's balls or rollers, every number left empty (plan section 二十, part 3)."""
    kind, fs = element_features(g)
    return {"rings": {"element": _blank_ring(fs, ELEMENT_CHAIN[kind])}}


def _blank_ring(feats: list[dict], chain_of) -> dict:
    ids = [f["id"] for f in feats]
    ops = []
    for kind, zh, en, use_ids in chain_of:
        use = [f for f in use_ids if f in ids]
        if kind in ("grind", "superfinish") and not use:
            continue  # e.g. the lands of a cylindrical roller ring are not drawn
        mode = "stock" if kind == "superfinish" else "size"
        names = (
            HEAT_FIELDS
            if kind == "heat"
            else (STOCK_FIELDS if mode == "stock" else CUT_FIELDS)
            if KINDS[kind] == CUT
            else ()
        )
        ops.append(
            {
                "no": 10 * (len(ops) + 1),
                "kind": kind,
                "mode": mode if KINDS[kind] == CUT else None,
                "name": {"zh": zh, "en": en},
                "equipment": "",
                "params": [],
                "features": {f: {n: None for n in names} for f in use},
            }
        )
    return {
        "ops": ops,
        "finish": {f: {"es": None, "ei": None} for f in ids},
        "blank": {f: {"T": None} for f in ids},
    }


def _state_str(side, mm, w):
    if mm is None:
        return None
    return {"size": mm, "upper": 0.0 if side == "ext" else w, "lower": -w if side == "ext" else 0.0}


def _ck(cid, zh, en, value, limit, status, note_zh="", note_en="", op=None, feature=None):
    return {
        "id": cid,
        "zh": zh,
        "en": en,
        "value": value,
        "limit": limit,
        "status": status,
        "unit": "mm",
        "note": note_en,
        "note_zh": note_zh or note_en,
        "op": op,
        "feature": feature,
    }


def _ring(feats: list[dict], spec: dict, ring_zh: str, ring_en: str) -> dict:
    ops_in = spec.get("ops") or []
    if not isinstance(ops_in, list) or len(ops_in) > MAX_OPS:
        raise ProcessError(f"a ring has at most {MAX_OPS} operations")
    ops = []
    for o in ops_in:
        kind = o.get("kind") or "other"
        if kind not in KINDS:
            raise ProcessError(
                "an operation kind is turn, grind, superfinish, cut, heat, wash, assemble, inspect or other"
            )
        mode = o.get("mode") or ("stock" if kind == "superfinish" else "size")
        if mode not in ("size", "stock"):
            raise ProcessError("a cutting operation works to size or removes a set stock")
        ops.append({**o, "kind": kind, "cls": KINDS[kind], "mode": mode, "features": o.get("features") or {}})
    finish = spec.get("finish") or {}
    blank = spec.get("blank") or {}
    checks, table = [], {}
    by_id = {f["id"]: f for f in feats}
    for fid in list(by_id):
        f = by_id[fid]
        side, sg = f["side"], (1 if f["side"] == "ext" else -1)
        steps = [(k, o) for k, o in enumerate(ops) if fid in o["features"] and o["cls"] in (CUT, HEAT)]
        cuts = [(k, o) for k, o in steps if o["cls"] == CUT]
        fin = finish.get(fid) or {}
        es, ei = _num(fin.get("es")), _num(fin.get("ei"))
        rows = []
        name = (f["zh"], f["en"])
        if not cuts:
            checks.append(
                _ck(
                    "not_machined",
                    f"{ring_zh}{name[0]}：没有工序加工",
                    f"{ring_en} {name[1].lower()}: no operation machines it",
                    None,
                    None,
                    INFO,
                    feature=fid,
                )
            )
            table[fid] = {"feature": f, "rows": [], "finish": None}
            continue
        # forward pass: tolerance widths of the state after each step
        w = _num((blank.get(fid) or {}).get("T"))
        widths_in, widths_out = [], []
        for _k, o in steps:
            d = o["features"][fid] or {}
            widths_in.append(w)
            if o["cls"] == CUT and o["mode"] == "size":
                w = _num(d.get("T"))
            elif o["cls"] == CUT:
                dz = _num(d.get("dz"))
                w = None if w is None or dz is None else w + dz
            else:
                s = _num(d.get("scatter"))
                w = None if w is None or s is None else w + s
            widths_out.append(w)
        last_T = widths_out[-1]  # tolerance of the finished state
        dev = es if side == "ext" else ei
        mm = f["size"] + (dev if dev is not None else 0.0)
        # backward pass: max-material size after and before each step
        mm_out, mm_in = [None] * len(steps), [None] * len(steps)
        for j in range(len(steps) - 1, -1, -1):
            k, o = steps[j]
            d = o["features"][fid] or {}
            mm_out[j] = mm
            if mm is None:
                mm_in[j] = None
            elif o["cls"] == CUT and o["mode"] == "size":
                Z = _num(d.get("Z"))
                mm_in[j] = None if Z is None else mm + sg * Z
            elif o["cls"] == CUT:
                Z, dz = _num(d.get("Z")), _num(d.get("dz"))
                mm_in[j] = None if Z is None or dz is None else mm + sg * (Z - dz / 2)
            else:
                ch, s = _num(d.get("change")), _num(d.get("scatter"))
                mm_in[j] = None if ch is None or s is None else mm - ch - sg * s / 2
            mm = mm_in[j]
        # the cuts: stock removed, checks
        after_heat = None
        for j, (k, o) in enumerate(steps):
            d = o["features"][fid] or {}
            op_label = f"{o.get('no', '')}"
            if o["cls"] == HEAT:
                after_heat = _num(d.get("distortion"))
                if after_heat is None:
                    after_heat = "missing"
                rows.append(
                    {
                        "op": k,
                        "no": o.get("no"),
                        "kind": o["kind"],
                        "after": _state_str(side, mm_out[j], widths_out[j]) if widths_out[j] is not None else None,
                        "mm_before": mm_in[j],
                        "mm_after": mm_out[j],
                        "change": _num(d.get("change")),
                        "scatter": _num(d.get("scatter")),
                        "distortion": _num(d.get("distortion")),
                    }
                )
                continue
            if o["mode"] == "stock":
                after_heat = None
                Z, dz, Zreq = _num(d.get("Z")), _num(d.get("dz")), _num(d.get("Zreq"))
                zmin = None if Z is None or dz is None else Z - dz / 2
                rows.append(
                    {
                        "op": k,
                        "no": o.get("no"),
                        "kind": o["kind"],
                        "mode": "stock",
                        "size": _state_str(side, mm_out[j], widths_out[j]) if widths_out[j] is not None else None,
                        "mm": mm_out[j],
                        "T": widths_out[j],
                        "Z": Z,
                        "dz": dz,
                        "Zmin": zmin,
                        "Zmax": None if zmin is None else Z + dz / 2,
                        "Zreq": Zreq,
                    }
                )
                lz = f"{ring_zh}{name[0]}，工序 {op_label}"
                le = f"{ring_en} {name[1].lower()}, operation {op_label}"
                if zmin is None:
                    st, nz, ne = UNKNOWN, "去除量或其波动没填", "the stock or its scatter is not given"
                elif zmin <= 0:
                    st, nz, ne = FAIL, "最小去除量 ≤ 0", "the smallest stock removed is ≤ 0"
                elif Zreq is None:
                    st, nz, ne = UNKNOWN, "需要的最小去除量没填", "the required smallest stock is not given"
                else:
                    st, nz, ne = (PASS if zmin >= Zreq - 1e-12 else FAIL), "", ""
                cz, ce = f"{lz}：最小去除量", f"{le}: smallest stock removed"
                checks.append(_ck("stock_min", cz, ce, zmin, Zreq, st, nz, ne, k, fid))
                continue
            Z, T = _num(d.get("Z")), _num(d.get("T"))
            Zreq, Zmax_lim, setup = _num(d.get("Zreq")), _num(d.get("Zmax")), _num(d.get("setup"))
            first = j == 0
            dist = 0.0
            dist_known = True
            if after_heat is not None:
                if after_heat == "missing":
                    dist_known = False
                else:
                    dist = after_heat
                after_heat = None  # only the first cut after heat treatment
            w_in, w_out = widths_in[j], widths_out[j]
            zmin = zmax = None
            if Z is not None and w_in is not None and dist_known:
                zmin = Z - w_in - dist - (setup or 0.0)
            if Z is not None and w_out is not None:
                zmax = Z + w_out
            rows.append(
                {
                    "op": k,
                    "no": o.get("no"),
                    "kind": o["kind"],
                    "mode": "size",
                    "first": first,
                    "size": _state_str(side, mm_out[j], T) if T is not None else None,
                    "mm": mm_out[j],
                    "T": T,
                    "Z": Z,
                    "Zmin": zmin,
                    "Zmax": zmax,
                    "Zreq": Zreq,
                    "Zmax_limit": Zmax_lim,
                    "setup": setup,
                    "distortion": dist if dist_known and dist else None,
                }
            )
            label_zh = f"{ring_zh}{name[0]}，工序 {op_label}"
            label_en = f"{ring_en} {name[1].lower()}, operation {op_label}"
            if Z is None:
                if not first or w_in is not None:
                    checks.append(
                        _ck(
                            "stock_min",
                            f"{label_zh}：最小留量",
                            f"{label_en}: smallest stock",
                            None,
                            Zreq,
                            UNKNOWN,
                            "没填公称留量",
                            "the nominal allowance is not given",
                            k,
                            fid,
                        )
                    )
                continue
            if Z <= 0:
                checks.append(
                    _ck(
                        "stock_min",
                        f"{label_zh}：最小留量",
                        f"{label_en}: smallest stock",
                        Z,
                        Zreq,
                        FAIL,
                        "公称留量要大于 0",
                        "the nominal allowance must be above 0",
                        k,
                        fid,
                    )
                )
                continue
            if zmin is None:
                why_zh = (
                    "毛坯公差没填" if first else "热处理变形没填" if not dist_known else "上道工序公差或热处理波动没填"
                )
                why_en = (
                    "the blank tolerance is not given"
                    if first
                    else "the heat-treatment distortion is not given"
                    if not dist_known
                    else "the preceding tolerance or the heat-treatment scatter is not given"
                )
                checks.append(
                    _ck(
                        "stock_min",
                        f"{label_zh}：最小留量",
                        f"{label_en}: smallest stock",
                        None,
                        Zreq,
                        UNKNOWN,
                        why_zh,
                        why_en,
                        k,
                        fid,
                    )
                )
            elif zmin <= 0:
                checks.append(
                    _ck(
                        "stock_min",
                        f"{label_zh}：最小留量",
                        f"{label_en}: smallest stock",
                        zmin,
                        Zreq,
                        FAIL,
                        "最小留量 ≤ 0：这一道可能加工不出来，加大留量或收紧上道公差",
                        "the smallest stock is ≤ 0: the cut may not clean up; more allowance or a tighter preceding "
                        "tolerance",
                        k,
                        fid,
                    )
                )
            else:
                st = UNKNOWN if Zreq is None else PASS if zmin >= Zreq - 1e-12 else FAIL
                checks.append(
                    _ck(
                        "stock_min",
                        f"{label_zh}：最小留量",
                        f"{label_en}: smallest stock",
                        zmin,
                        Zreq,
                        st,
                        "需要的最小留量没填" if Zreq is None else "",
                        "the required smallest stock is not given" if Zreq is None else "",
                        k,
                        fid,
                    )
                )
            if Zmax_lim is not None:
                st = UNKNOWN if zmax is None else PASS if zmax <= Zmax_lim + 1e-12 else FAIL
                checks.append(
                    _ck(
                        "stock_max",
                        f"{label_zh}：最大留量",
                        f"{label_en}: largest stock",
                        zmax,
                        Zmax_lim,
                        st,
                        "本道公差没填" if zmax is None else "",
                        "this operation's tolerance is not given" if zmax is None else "",
                        k,
                        fid,
                    )
                )
        # finished tolerance
        zone = None if es is None or ei is None else es - ei
        if zone is not None and zone <= 0:
            raise ProcessError("the upper deviation of a finished size must be above the lower one")
        st = UNKNOWN if zone is None or last_T is None else PASS if last_T <= zone + 1e-12 else FAIL
        checks.append(
            _ck(
                "finish_tol",
                f"{ring_zh}{name[0]}：末道工序公差在成品公差内",
                f"{ring_en} {name[1].lower()}: last operation's tolerance within the finished tolerance",
                last_T,
                zone,
                st,
                "成品公差没填，以公称尺寸为基准" if zone is None else "",
                "the finished tolerance is not given: sizes are based on the nominal size" if zone is None else "",
                steps[-1][0],
                fid,
            )
        )
        blank_row = None
        if steps and mm_in[0] is not None and steps[0][1]["cls"] == CUT:
            blank_row = _state_str(side, mm_in[0], widths_in[0] if widths_in[0] is not None else 0.0)
            blank_row["T_known"] = widths_in[0] is not None
        table[fid] = {
            "feature": f,
            "rows": rows,
            "finish": {"es": es, "ei": ei},
            "blank": blank_row,
        }
    status = (
        FAIL
        if any(c["status"] == FAIL for c in checks)
        else (UNKNOWN if any(c["status"] == UNKNOWN for c in checks) else PASS)
    )
    cards = []
    for k, o in enumerate(ops):
        lines = []
        for fid in o["features"]:
            if fid not in table:
                continue
            for r in table[fid]["rows"]:
                if r["op"] == k:
                    lines.append({"feature": fid, "zh": by_id[fid]["zh"], "en": by_id[fid]["en"], **r})
        cards.append(
            {
                "op": k,
                "no": o.get("no"),
                "kind": o["kind"],
                "name": o.get("name") or {"zh": "", "en": ""},
                "equipment": o.get("equipment") or "",
                "params": [p for p in (o.get("params") or []) if isinstance(p, dict)],
                "lines": lines,
                "checks": [c for c in checks if c["op"] == k],
                "unknown_features": [x for x in o["features"] if x not in by_id],
            }
        )
    return {"features": feats, "table": table, "checks": checks, "status": status, "cards": cards}


def run(design_geometry: dict, process: dict) -> dict:
    if not isinstance(process, dict):
        raise ProcessError("give the process as an object")
    fs = features(design_geometry)
    rings_in = process.get("rings") or {}
    if "element" in rings_in:
        fs["element"] = element_features(design_geometry)[1]
    out = {}
    for ring, zh, en in (
        ("inner", "内圈", "Inner ring"),
        ("outer", "外圈", "Outer ring"),
        ("element", "滚动体", "Rolling element"),
    ):
        if ring in rings_in:
            out[ring] = _ring(fs[ring], rings_in[ring] or {}, zh, en)
    if not out:
        raise ProcessError("give the operations of the inner or the outer ring")
    sts = [r["status"] for r in out.values()]
    status = FAIL if FAIL in sts else UNKNOWN if UNKNOWN in sts else PASS
    return {
        "type": design_geometry["type"],
        "rings": out,
        "status": status,
        "fictional": bool(process.get("fictional")),
        "notes": [
            {
                "zh": "尺寸都按直径或宽度计；工序尺寸按入体原则标注（外表面上偏差 0，内表面下偏差 0）。",
                "en": "Sizes are on the diameter or the width; operation sizes follow the into-the-material rule "
                "(external upper deviation 0, internal lower deviation 0).",
            },
            {
                "zh": "超精等按定量去除的工序：去除量 Z、波动 dz，出来的公差 = 上道公差 + dz，最小去除量 = Z − dz/2。",
                "en": "Operations removing a set stock (superfinishing): stock Z with scatter dz; the tolerance after "
                "them is the preceding one + dz, the smallest stock Z − dz/2.",
            },
            {
                "zh": "最小留量 = 公称留量 − 上道公差（含热处理波动）− 热处理变形（热处理后第一刀）− 装夹误差；"
                "最大留量 = 公称留量 + 本道公差。",
                "en": "Smallest stock = nominal allowance − preceding tolerance (with the heat-treatment scatter) − "
                "heat-treatment distortion (first cut after it) − setup error; largest = nominal + this tolerance.",
            },
            {
                "zh": "装夹误差没填时不扣（视为已含在“需要的最小留量”里）。",
                "en": "A setup error left blank is not subtracted (taken as included in the required smallest stock).",
            },
            {
                "zh": "沟曲率半径和沟位置的影响在“合套选配”页的“游隙尺寸链”里算；这里只算直径和宽度方向的工序尺寸。",
                "en": "The groove radius and position are worked in the clearance chain (Selective assembly page); "
                "here only diameters and widths.",
            },
            {
                "zh": "滚动体：钢球按直径、滚子按直径和长度倒推；分选的组距与“合套选配”的钢球分组对应，由企业定。",
                "en": "Rolling elements: a ball by its diameter, a roller by its diameter and length; the sorting "
                "groups match the ball groups of selective assembly and are the company's.",
            },
        ],
    }


def with_values(template: dict, values: dict) -> dict:
    """Fill a structure-only template from {ring: {op_no: {feature: {field: value}}}} (for the example)."""
    t = copy.deepcopy(template)
    for ring, ops in values.items():
        for o in t["rings"][ring]["ops"]:
            for fid, d in (ops.get(o["no"]) or {}).items():
                if fid in o["features"]:
                    o["features"][fid].update(d)
    return t
