"""Code checks on what the AI drafts (round 64, step 7; plan section 十五). The AI only drafts; everything here is plain
code and decides what of a draft may be shown.

Application drafts (one sentence → the application kind and its fields):
  - the kind must be one of the application kinds; the fields must be fields of that kind (the same field table as
    the web editor and the FreeCAD form, bearingkit/fields.py), anything else is dropped and reported;
  - a number the AI wrote must be stated in the sentence (a percentage may also stand as its fraction: 60 % → 0.6);
    any other number is cleared and reported, never kept, never estimated;
  - a word choice (A or B, the axis, the row) must be one of the field's options;
  - the fields of the kind still empty are listed for the user to fill in (yellow on the page).
Texts (explanations, the design description): a sentence whose numbers are not among the check results' or the
project's numbers, written to the same decimals, is dropped. The same rules as the cam software (camkit/ai_check.py).

No AI, no network here.
"""

from __future__ import annotations

import copy
import math
import re

from bearingkit import fields as FL

NUM = re.compile(r"(?<![A-Za-z0-9_.])[-+]?\d+(?:\.\d+)?")  # Chinese text may touch the digits
PCT = re.compile(r"(\d+(?:\.\d+)?)\s*[%％]")
SMALL = 10  # plain counts (two bearings, the 3rd case) are not checked in texts
CASE_COLS = {"gearbox": ("label", "P", "n", "share"), "spindle": ("label", "Fr", "Fa", "n", "share")}
MAX_CASES = 8
# fields that may stay empty (the web editor treats them as not given: no fatigue check, no moment, no belt …)
OPTIONAL = {
    "scenario.fp",
    "loads.M",
    "loads.Fa",
    "scenario.shares.straight",
    "scenario.shares.out",
    "scenario.shares.in",
    "scenario.F_belt",
    "scenario.x_belt",
    "scenario.U",
    "scenario.Fa",
}


def sentence_numbers(text: str) -> set[float]:
    text = text.replace("，", ",").replace("．", ".")
    out = {abs(float(m.group(0))) for m in NUM.finditer(text)}
    out |= {float(m.group(1)) / 100 for m in PCT.finditer(text)}
    return out


def _in(v: float, allowed: set[float]) -> bool:
    return any(abs(v - a) <= 1e-9 * max(1.0, abs(a)) for a in allowed)


def kind_fields(lang: str = "zh") -> dict:
    """Each application kind with its fields (path, label, unit, options): what the model may fill in."""
    scene = next(fs for g, _w, fs in FL.GROUPS if g == "gScene")
    loads = next(fs for g, _w, fs in FL.GROUPS if g == "gLoads")
    out = {}
    for kind in FL.SCENES:
        rows = []
        for f in scene + (loads if kind == "generic" else []):
            if f["path"] == "scenario.kind":
                continue
            sc = f["when"].get("scene")
            if f["path"].startswith("scenario.") and sc is not None and kind not in sc:
                continue
            row = {"path": f["path"], "label": FL.label(f["key"], lang), "unit": f["unit"]}
            if f["kind"] == "select":
                row["options"] = [v for v, _k in f["options"]]
            if f["kind"] == "cases":
                row["columns"] = list(CASE_COLS[kind])
            if f["kind"] == "text":
                row["kind"] = "text"
            rows.append(row)
        out[kind] = {"label": FL.label("sk_" + kind, lang), "fields": rows}
    return out


def _number(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def apply_draft(draft: dict, sentence: str, project: dict, lang: str = "zh") -> dict:
    """The draft checked and put into a copy of the project. Returns {"kind", "project", "values": rows for the
    table, "cleared", "dropped", "missing", "usable", "error"}. "usable" means it may be adopted into the form; the
    missing fields are then filled in by the user before anything is computed from them."""
    kinds = kind_fields(lang)
    kind = draft.get("kind")
    out = {
        "kind": kind,
        "project": None,
        "values": [],
        "cleared": [],
        "dropped": [],
        "missing": [],
        "usable": False,
        "error": None,
    }
    if kind not in kinds:
        out["error"] = "the draft names no application kind of this software"
        return out
    nums = sentence_numbers(sentence)
    spec = {f["path"]: f for f in kinds[kind]["fields"]}
    q = FL.normalise(copy.deepcopy(project))
    FL.set_scene(q, kind)
    q["scenario"] = copy.deepcopy(FL.FRESH[kind])
    if kind == "generic":
        q["loads"] = copy.deepcopy(FL.BLANK["loads"])
    if kind in CASE_COLS:
        q["scenario"]["cases"] = []
    cases: dict[int, dict] = {}
    for item in draft.get("values") or []:
        path, val = str(item.get("path") or ""), item.get("value")
        if val is None:
            continue
        m = re.fullmatch(r"(?:scenario\.)?cases\.(\d+)\.(\w+)", path)
        if m:
            i, col = int(m.group(1)), m.group(2)
            if kind not in CASE_COLS or col not in CASE_COLS[kind] or i >= MAX_CASES:
                out["dropped"].append({"path": path, "value": val})
                continue
            if col == "label":
                lab = str(val).strip()
                if lab and lab in sentence:
                    cases.setdefault(i, {})["label"] = lab[:40]
                else:
                    out["cleared"].append({"path": path, "value": val})
                continue
            x = _number(val)
            if x is None or not _in(abs(x), nums):
                out["cleared"].append({"path": path, "value": val})
                continue
            cases.setdefault(i, {})[col] = x
            continue
        f = spec.get(path)
        if f is None or "columns" in f:
            out["dropped"].append({"path": path, "value": val})
            continue
        if "options" in f:
            if val in f["options"]:
                FL.put(q, path, val)
            else:
                out["cleared"].append({"path": path, "value": val})
            continue
        if f.get("kind") == "text":
            t = str(val)
            if t.strip() and all(_in(abs(float(tok)), nums) for tok in NUM.findall(t)):
                FL.put(q, path, t)
            else:
                out["cleared"].append({"path": path, "value": val})
            continue
        x = _number(val)
        if x is None or not _in(abs(x), nums):
            out["cleared"].append({"path": path, "value": val})
            continue
        FL.put(q, path, int(x) if path == "scenario.z" and float(x).is_integer() else x)
    if kind in CASE_COLS:
        cols = CASE_COLS[kind]
        for i in sorted(cases):
            row = {c: None for c in cols}
            row["label"] = ""
            row.update(cases[i])
            q["scenario"]["cases"].append(row)
        if not q["scenario"]["cases"]:
            q["scenario"]["cases"] = copy.deepcopy(FL.FRESH[kind]["cases"])
            q["scenario"]["cases"][0]["share"] = None
    # what is still empty: the fields the form shows for this draft
    rows = []
    for _g, fs in FL.visible(q):
        for f in fs:
            if (
                not (f["path"].startswith("scenario.") or f["path"].startswith("loads."))
                or f["path"] == "scenario.kind"
            ):
                continue
            if f["kind"] == "cases":
                for i, c in enumerate(q["scenario"].get("cases") or []):
                    for col in CASE_COLS[kind]:
                        if col != "label" and c.get(col) is None:
                            out["missing"].append(
                                {"path": f"scenario.cases.{i}.{col}", "label": FL.label("cases", lang)}
                            )
                continue
            v = FL.get(q, f["path"])
            rows.append({"path": f["path"], "label": FL.label(f["key"], lang), "unit": f["unit"], "value": v})
            optional = f["path"] in OPTIONAL or (kind == "joint" and f["path"] == "scenario.L")
            if v in (None, "") and not optional:
                out["missing"].append({"path": f["path"], "label": FL.label(f["key"], lang)})
    out["values"] = rows
    out["project"] = q
    out["usable"] = True  # adopted into the form; what is missing is yellow there and filled in by the user
    return out


# ------------------------------------------------------------------------------------------------ texts


def numbers_in(x) -> list[float]:
    if isinstance(x, bool):
        return []
    if isinstance(x, (int, float)):
        return [float(x)] if math.isfinite(x) else []
    if isinstance(x, dict):
        return [v for y in x.values() for v in numbers_in(y)]
    if isinstance(x, (list, tuple)):
        return [v for y in x for v in numbers_in(y)]
    return []


def _matches(tok: str, vals: list[float]) -> bool:
    v = abs(float(tok))
    if v <= SMALL and float(v).is_integer():
        return True
    dec = len(tok.split(".")[1]) if "." in tok else 0
    for a in vals:
        x = abs(a)
        if round(x, dec) == round(v, dec) or abs(x - v) <= 0.5 * 10 ** (-dec) + 1e-12:
            return True
    return False


def keep_supported(sentences: list[str], vals: list[float]) -> tuple[list[str], list[str]]:
    """Sentences whose every number is one of vals (as written, to its decimals); the others are dropped."""
    kept, dropped = [], []
    for s in sentences:
        toks = NUM.findall(s.replace("，", ","))
        (kept if all(_matches(t, vals) for t in toks) else dropped).append(s)
    return kept, dropped
