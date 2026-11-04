"""The project's input fields, for the FreeCAD form (round 64, step 6): the same fields, the same file format and the
same words as the web editor (apps/bearing/src/components/Fields.vue and Scenario.vue). A test checks that every
field the web editor writes is here and the other way round, and the words come from the web app's i18n table
(labels.json, made by tools/labels.py from apps/bearing/src/i18n.js).

A field: path in the project ("size.d"), the i18n key of its label, unit, kind (num, int, select, text, cases),
options for a select, and when it shows (the same conditions as the web editor).

Plain data: no AI, no network.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

LABELS = json.loads((Path(__file__).with_name("labels.json")).read_text(encoding="utf-8"))

TYPES = ["deep_groove", "angular", "cylindrical", "tapered"]
BALL, ROLLER = ["deep_groove", "angular"], ["cylindrical", "tapered"]
SCENES = ["generic", "gearbox", "motor", "spindle", "hub", "joint", "camshaft"]
AB = [("A", None), ("B", None)]


def F(path, key, unit="", kind="num", when=None, options=None, hint=None, step=None):
    return {
        "path": path,
        "key": key,
        "unit": unit,
        "kind": kind,
        "when": when or {},
        "options": options,
        "hint": hint,
        "step": step,
    }


def opts(values, prefix=""):
    return [(v, (prefix + v) if prefix is not None else None) for v in values]


# (group i18n key, when, fields): the order of the web editor
GROUPS = [
    ("type", {}, [F("type", "type", kind="select", options=opts(TYPES))]),
    (
        "gScene",
        {},
        [
            F("scenario.kind", "sceneKind", kind="select", options=opts(SCENES, "sk_")),
            # gearbox
            F("scenario.mn", "mn", "mm", when={"scene": ["gearbox"]}),
            F("scenario.z", "zGear", kind="int", when={"scene": ["gearbox"]}),
            F("scenario.alpha_n_deg", "alphaN", "°", when={"scene": ["gearbox"]}),
            F("scenario.beta_deg", "beta", "°", when={"scene": ["gearbox"]}),
            # motor
            F("scenario.m", "rotorM", "kg", when={"scene": ["motor"]}),
            F("scenario.U", "unbalance", "g·mm", when={"scene": ["motor"]}),
            F("scenario.F_belt", "beltF", "N", when={"scene": ["motor"]}),
            F("scenario.x_belt", "beltX", "mm", when={"scene": ["motor"]}, hint="xHint"),
            F("scenario.belt_deg", "beltDeg", "°", when={"scene": ["motor"]}),
            F("scenario.Fa", "Fa", "N", when={"scene": ["motor"]}),
            # spindle
            F("scenario.a", "overhang", "mm", when={"scene": ["spindle"]}),
            # hub
            F("scenario.W", "wheelW", "N", when={"scene": ["hub"]}),
            F("scenario.ay", "ay", "g", when={"scene": ["hub"]}),
            F("scenario.R", "wheelR", "mm", when={"scene": ["hub"]}),
            F("scenario.e", "hubE", "mm", when={"scene": ["hub"]}),
            F("scenario.L", "rowL", "mm", when={"scene": ["hub"]}),
            F("scenario.row", "row", kind="select", options=opts(["outboard", "inboard"]), when={"scene": ["hub"]}),
            F("scenario.shares.straight", "shareStraight", when={"scene": ["hub"]}),
            F("scenario.shares.out", "shareOut", when={"scene": ["hub"]}),
            F("scenario.shares.in", "shareIn", when={"scene": ["hub"]}),
            # joint
            F(
                "scenario.axis",
                "axis",
                kind="select",
                options=opts(["horizontal", "vertical"]),
                when={"scene": ["joint"]},
            ),
            F("scenario.W", "jointW", "N", when={"scene": ["joint"]}),
            F("scenario.r", "lever", "mm", when={"scene": ["joint"], "axis": ["vertical"]}),
            F("scenario.swing_deg", "swing", "°", when={"scene": ["joint"]}),
            # camshaft
            F("scenario.table", "camTable", kind="text", when={"scene": ["camshaft"]}, hint="camTableHint"),
            # speed (motor, hub, joint, camshaft)
            F("scenario.n", "n", "r/min", when={"scene": ["motor", "hub", "joint", "camshaft"]}),
            # where the load sits between the bearings
            F(
                "scenario.x",
                "loadX",
                "mm",
                when={"scene": ["gearbox", "motor", "camshaft", "joint"], "axis_not": ["vertical"]},
                hint="xHint",
            ),
            F("scenario.L", "spanL", "mm", when={"scene": ["gearbox", "motor", "spindle", "camshaft", "joint"]}),
            F(
                "scenario.this",
                "thisBearing",
                kind="select",
                options=AB,
                when={"scene": ["gearbox", "motor", "spindle", "camshaft", "joint"]},
            ),
            F(
                "scenario.fixed",
                "fixedBearing",
                kind="select",
                options=AB,
                when={"scene": ["gearbox", "camshaft", "joint"]},
            ),
            F("scenario.axial_to", "axialTo", kind="select", options=AB, when={"scene": ["gearbox"]}),
            # load spectrum
            F("scenario.cases", "cases", kind="cases", when={"scene": ["gearbox", "spindle"]}),
            F(
                "scenario.fp",
                "fp",
                step=0.05,
                hint="fpHint",
                when={"scene": ["generic", "gearbox", "motor", "spindle", "hub", "camshaft"]},
            ),
        ],
    ),
    ("gSize", {}, [F("size.d", "d", "mm"), F("size.D", "D", "mm"), F("size.B", "B", "mm")]),
    (
        "gBalls",
        {"type": BALL},
        [
            F("inner.Dw", "Dw", "mm"),
            F("inner.Z", "Z", kind="int"),
            F("inner.dm", "dm", "mm", hint="dmHint"),
            F("inner.fi", "fi", step=0.001, hint="fHint"),
            F("inner.fo", "fo", step=0.001),
            F("inner.Pd", "Pd", "mm", step=0.001, when={"type": ["deep_groove"]}),
            F("inner.alpha0_deg", "alpha0", "°", when={"type": ["angular"]}),
            F(
                "pair.arrangement",
                "arrangement",
                kind="select",
                options=opts(["single", "DB", "DF", "DT"], "arr_"),
                when={"type": ["angular"]},
            ),
            F("pair.preload", "preloadF", "N", when={"type": ["angular"], "pair": ["DB", "DF"]}),
            F(
                "pair.spacing",
                "rowSpacing",
                "mm",
                hint="rowSpacingHint",
                when={"type": ["angular"], "pair": ["DB", "DF", "DT"]},
            ),
            F("inner.h_i", "h_i", "mm", hint="hHint"),
            F("inner.h_o", "h_o", "mm"),
        ],
    ),
    (
        "gRollers",
        {"type": ROLLER},
        [
            F("inner.Dw", "DwR", "mm", when={"type": ["cylindrical"]}),
            F("inner.Dw", "DwT", "mm", when={"type": ["tapered"]}),
            F("inner.Lw", "Lw", "mm"),
            F("inner.Lwe", "Lwe", "mm", hint="LweHint"),
            F("inner.Z", "ZR", kind="int"),
            F("inner.dm", "dm", "mm", hint="dmHint"),
            F("inner.Pd", "Pd", "mm", step=0.001, when={"type": ["cylindrical"]}),
            F("inner.alpha_o_deg", "cupAngle", "°", hint="cupHint", when={"type": ["tapered"]}),
            F("inner.alpha_i_deg", "coneAngle", "°", when={"type": ["tapered"]}),
            F("inner.alpha_f_deg", "ribAngle", "°", hint="ribHint", when={"type": ["tapered"]}),
            F("inner.R_end", "rEnd", "mm", when={"type": ["tapered"]}),
            F("profile.kind", "crown", kind="select", options=opts(["straight", "arc", "partial", "table"], "crown_")),
            F("profile.R", "crownR", "mm", when={"profile": ["arc", "partial"]}),
            F("profile.flat", "crownFlat", "mm", when={"profile": ["partial"]}),
            F("profile.points", "crownTable", kind="points", hint="crownTableHint", when={"profile": ["table"]}),
            F("alignment.theta_arcmin", "misalign", "′", hint="misalignHint"),
        ],
    ),
    (
        "gMat",
        {},
        [
            F("material.E", "E", "MPa"),
            F("material.nu", "nu", step=0.01),
            F("material.density", "density", "g/cm³", step=0.01, hint="densityHint", when={"type": ["angular"]}),
        ],
    ),
    (
        "gLoads",
        {"scene": ["generic"]},
        [
            F("loads.Fr", "Fr", "N"),
            F("loads.Fa", "Fa", "N"),
            F("loads.M", "M", "N·mm", hint="MHint"),
            F("loads.n", "n", "r/min"),
        ],
    ),
    (
        "gFits",
        {"type": ["deep_groove", "cylindrical"]},
        [
            F("fits.shaft_I", "shaft_I", "mm", step=0.001),
            F("fits.housing_I", "housing_I", "mm", step=0.001),
            F("fits.T_i", "T_i", "°C"),
            F("fits.T_o", "T_o", "°C"),
        ],
    ),
    (
        "gLube",
        {},
        [
            F("lube.eta0", "eta0", "Pa·s", step=0.001),
            F("lube.alpha_p", "alpha_p", "1/Pa"),
            F("lube.sigma", "sigma", "µm", step=0.01),
        ],
    ),
    (
        "gLimits",
        {},
        [
            F("limits.p_static", "p_static", "MPa"),
            F("limits.p_fatigue", "p_fatigue", "MPa"),
            F("limits.gap_min", "gap_min", "mm"),
            F("limits.wall_min", "wall_min", "mm"),
        ],
    ),
]

# a fresh scenario of each kind (the same as Scenario.vue's FRESH): structure only, no numbers
FRESH = {
    "generic": {"kind": "generic", "fp": None},
    "gearbox": {
        "kind": "gearbox",
        "fp": None,
        "mn": None,
        "z": None,
        "alpha_n_deg": None,
        "beta_deg": 0,
        "x": None,
        "L": None,
        "this": "A",
        "fixed": "A",
        "axial_to": "B",
        "cases": [{"label": "", "P": None, "n": None, "share": 1}],
    },
    "motor": {
        "kind": "motor",
        "fp": None,
        "m": None,
        "U": None,
        "x": None,
        "L": None,
        "F_belt": None,
        "x_belt": None,
        "belt_deg": 0,
        "Fa": None,
        "n": None,
        "this": "A",
    },
    "spindle": {
        "kind": "spindle",
        "fp": None,
        "a": None,
        "L": None,
        "this": "A",
        "cases": [{"label": "", "Fr": None, "Fa": None, "n": None, "share": 1}],
    },
    "hub": {
        "kind": "hub",
        "fp": None,
        "W": None,
        "ay": None,
        "R": None,
        "L": None,
        "e": 0,
        "row": "outboard",
        "n": None,
        "shares": {"straight": None, "out": None, "in": None},
    },
    "joint": {
        "kind": "joint",
        "axis": "horizontal",
        "W": None,
        "x": None,
        "r": None,
        "L": None,
        "this": "A",
        "fixed": "A",
        "swing_deg": None,
        "n": None,
    },
    "camshaft": {
        "kind": "camshaft",
        "fp": None,
        "x": None,
        "L": None,
        "n": None,
        "this": "A",
        "fixed": "A",
        "table": "",
    },
}

# a blank project (the same as store.js blank())
BLANK = {
    "title": {"zh": "", "en": ""},
    "type": "deep_groove",
    "size": {"d": None, "D": None, "B": None},
    "inner": {
        k: None
        for k in (
            "Dw",
            "Z",
            "dm",
            "fi",
            "fo",
            "Pd",
            "alpha0_deg",
            "h_i",
            "h_o",
            "Lw",
            "Lwe",
            "alpha_o_deg",
            "alpha_i_deg",
            "alpha_f_deg",
            "R_end",
        )
    },
    "profile": {"kind": "straight", "R": None, "flat": None, "points": []},
    "alignment": {"theta_arcmin": None},
    "pair": {"arrangement": "single", "preload": None, "spacing": None},
    "material": {"E": 206000, "nu": 0.3, "density": None},
    "scenario": {"kind": "generic", "fp": None},
    "loads": {"Fr": None, "Fa": None, "M": None, "n": None},
    "fits": {"shaft_I": None, "housing_I": None, "T_i": 20, "T_o": 20},
    "lube": {"eta0": None, "alpha_p": None, "sigma": None},
    "limits": {"p_static": None, "p_fatigue": None, "gap_min": None, "wall_min": None},
}


def label(key: str, lang: str = "zh") -> str:
    zh, en = LABELS.get(key, (key, key))
    return zh if lang == "zh" else en


def blank() -> dict:
    return copy.deepcopy(BLANK)


def normalise(p: dict) -> dict:
    """A project as the web editor holds it after opening a file (store.js replace())."""
    b = blank()
    out = {}
    for k, v in b.items():
        if isinstance(v, dict):
            out[k] = {**v, **(p.get(k) or {})}
        else:
            out[k] = p.get(k, v) if p.get(k) is not None else v
    out["scenario"] = copy.deepcopy(p["scenario"]) if p.get("scenario") else b["scenario"]
    lim = p.get("limits") or {}
    if lim.get("p_max") is not None and lim.get("p_static") is None:
        out["limits"]["p_static"] = lim["p_max"]
    out["limits"].pop("p_max", None)
    out["note"] = p.get("note")
    for k, v in p.items():  # anything else the file carries (e.g. a design id) goes through untouched
        out.setdefault(k, v)
    return out


def get(p: dict, path: str):
    cur = p
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def put(p: dict, path: str, value) -> None:
    parts = path.split(".")
    cur = p
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def shown(when: dict, p: dict) -> bool:
    t = p.get("type") or "deep_groove"
    s = (p.get("scenario") or {}).get("kind") or "generic"
    checks = {
        "type": t,
        "scene": s,
        "pair": (p.get("pair") or {}).get("arrangement") or "single",
        "profile": (p.get("profile") or {}).get("kind") or "straight",
        "axis": (p.get("scenario") or {}).get("axis") or "horizontal",
    }
    for k, allowed in when.items():
        if k == "axis_not":
            if s == "joint" and checks["axis"] in allowed:
                return False
            continue
        if k == "axis" and s != "joint":
            return False
        if checks[k] not in allowed:
            return False
    return True


def visible(p: dict) -> list[tuple[str, list[dict]]]:
    """Groups and fields the form shows for this project, in order."""
    out = []
    for g, when, fs in GROUPS:
        if not shown(when, p):
            continue
        out.append((g, [f for f in fs if shown(f["when"], p)]))
    return out


def set_scene(p: dict, kind: str) -> None:
    if kind not in FRESH:
        raise ValueError("the scenario is " + ", ".join(SCENES))
    if (p.get("scenario") or {}).get("kind") != kind:
        p["scenario"] = copy.deepcopy(FRESH[kind])


def parse_points(text: str) -> list[list[float]]:
    """Crown points "x, drop" per line (the web editor's text box)."""
    rows = []
    for line in text.splitlines():
        parts = [x for x in line.replace(",", " ").replace(";", " ").split() if x]
        try:
            r = [float(x) for x in parts]
        except ValueError:
            continue
        if len(r) == 2:
            rows.append(r)
    return rows


def points_text(rows) -> str:
    return "\n".join(", ".join(f"{v:g}" for v in r) for r in rows or [])


def save(p: dict, path: str) -> None:
    Path(path).write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


def load(path: str) -> dict:
    return normalise(json.loads(Path(path).read_text(encoding="utf-8")))
