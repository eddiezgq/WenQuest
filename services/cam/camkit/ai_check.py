"""Code checks on what the AI drafts (round 39, step 6; plan section 十一). The AI only drafts; everything here is
plain code and decides whether a draft may be shown as usable.

Motion program drafts:
  - a number the AI wrote must be in the requirement sentence (or follow from it by the fixed readings below: one
    turn = 360°, half a turn = 180°, a fraction "a/b" of a turn); any other number is cleared and reported;
  - one dwell left without an angle is filled with the rest of the turn; a closed (non-indexing) program left with
    one rise or return without a lift is filled so the follower comes back; anything else left empty is asked for;
  - the result must pass camkit.program's own checks (360° in all, rises and returns cancel or make the advance).
Texts (explanations, the design description): a sentence whose numbers are not among the check results' numbers,
written to the same decimals, is dropped.

No AI, no network here.
"""

from __future__ import annotations

import math
import re

from camkit.laws import LAWS
from camkit.program import Program, ProgramError

NUM = re.compile(r"(?<![A-Za-z0-9_.])[-+]?\d+(?:\.\d+)?(?:/\d+)?")  # Chinese text may touch the digits
TURN_WORDS = {"一圈": 360.0, "一转": 360.0, "整圈": 360.0, "转一圈": 360.0, "one turn": 360.0, "a turn": 360.0,
              "full turn": 360.0, "半圈": 180.0, "half a turn": 180.0, "半转": 180.0}
SMALL = 10  # plain counts (two rollers, the 3rd segment) are not checked


def sentence_numbers(text: str) -> set[float]:
    """Numbers a sentence states, with the fixed readings of turns and fractions of a turn."""
    out: set[float] = set()
    low = text.lower()
    for m in NUM.finditer(text):
        tok = m.group(0)
        if "/" in tok:
            a, b = tok.split("/")
            if float(b):
                out.add(float(a) / float(b))
                out.add(360.0 * float(a) / float(b))
            continue
        out.add(abs(float(tok)))
    for w, v in TURN_WORDS.items():
        if w in low:
            out.add(v)
    return out


def _in(v: float, allowed: set[float]) -> bool:
    return any(abs(v - a) <= 1e-6 * max(1.0, abs(a)) for a in allowed)


def program_from_draft(draft: dict, follower: str, sentence: str) -> dict:
    """The draft as a project program, with notes. Returns {"program": dict | None, "segments": rows for the table,
    "cleared": [...], "filled": [...], "missing": [...], "error": str | None, "usable": bool}."""
    allowed = sentence_numbers(sentence)
    rows, cleared, filled, missing = [], [], [], []
    for k, s in enumerate(draft.get("segments") or [], 1):
        kind = s.get("kind")
        if kind not in ("rise", "dwell", "return"):
            continue
        row = {"kind": kind, "deg": s.get("deg"), "h": s.get("h") if kind != "dwell" else None,
               "law": s.get("law") if kind != "dwell" else None, "why": str(s.get("why") or "")[:200],
               "ai": {"deg": s.get("deg") is not None, "h": s.get("h") is not None and kind != "dwell"}}
        for f in ("deg", "h"):
            v = row[f]
            if v is None:
                continue
            try:
                v = float(v)
            except (TypeError, ValueError):
                v = None
            if v is None or not math.isfinite(v) or not _in(abs(v), allowed):
                cleared.append({"seg": k, "field": f, "value": row[f]})
                row[f] = None
                row["ai"][f] = False
            else:
                row[f] = abs(v)
        if row["law"] is not None and row["law"] not in LAWS:
            cleared.append({"seg": k, "field": "law", "value": row["law"]})
            row["law"] = None
        rows.append(row)
    indexing = follower == "indexing"
    adv = draft.get("advance_deg")
    if adv is not None:
        try:
            adv = float(adv)
        except (TypeError, ValueError):
            adv = None
        if adv is not None and not _in(abs(adv), allowed):
            cleared.append({"seg": 0, "field": "advance", "value": draft.get("advance_deg")})
            adv = None
    # code fills what follows from the rest
    no_deg = [r for r in rows if r["deg"] is None]
    if len(no_deg) == 1 and no_deg[0]["kind"] == "dwell":
        rest = 360.0 - sum(r["deg"] for r in rows if r["deg"] is not None)
        if rest > 0:
            no_deg[0]["deg"] = rest
            filled.append({"seg": rows.index(no_deg[0]) + 1, "field": "deg", "value": rest, "why": "rest of the turn"})
    moving = [r for r in rows if r["kind"] != "dwell"]
    no_h = [r for r in moving if r["h"] is None]
    if not indexing and len(no_h) == 1:
        sgn = {"rise": 1.0, "return": -1.0}
        net = sum(sgn[r["kind"]] * r["h"] for r in moving if r["h"] is not None)
        need = -net * sgn[no_h[0]["kind"]]
        if need > 0:
            no_h[0]["h"] = need
            filled.append({"seg": rows.index(no_h[0]) + 1, "field": "h", "value": need, "why": "back to the start"})
    if indexing and adv is None and moving and all(r["h"] is not None for r in moving):
        adv = sum((1 if r["kind"] == "rise" else -1) * r["h"] for r in moving)
        filled.append({"seg": 0, "field": "advance", "value": adv, "why": "net of the rises and returns"})
    for k, r in enumerate(rows, 1):
        if r["deg"] is None:
            missing.append({"seg": k, "field": "deg"})
        if r["kind"] != "dwell" and r["h"] is None:
            missing.append({"seg": k, "field": "h"})
        if r["kind"] != "dwell" and r["law"] is None:
            missing.append({"seg": k, "field": "law"})
    out = {"segments": rows, "cleared": cleared, "filled": filled, "missing": missing, "program": None, "error": None,
           "usable": False, "advance_deg": adv}
    if not rows:
        out["error"] = "the draft has no segments"
        return out
    if missing:
        return out
    unit = "mm" if follower == "translating" else "rad"
    segs = []
    for r in rows:
        d = {"kind": r["kind"], "deg": r["deg"]}
        if r["kind"] != "dwell":
            d["h" if unit == "mm" else "h_deg"] = r["h"]
            d["law"] = r["law"]
        segs.append(d)
    prog = {"unit": unit, "segments": segs}
    if indexing:
        prog["advance_deg"] = adv
    try:
        Program.from_dict(prog)
    except (ProgramError, ValueError) as e:
        out["error"] = str(e)
        return out
    out["program"], out["usable"] = prog, True
    return out


# ------------------------------------------------------------------------------------------------ texts


def result_numbers(checks: list[dict], extra: list[float] = ()) -> list[float]:
    vals = []
    for c in checks:
        for k in ("value", "limit"):
            v = c.get(k)
            if isinstance(v, (int, float)) and math.isfinite(v):
                vals.append(float(v))
    return vals + [float(x) for x in extra if isinstance(x, (int, float))]


def _matches(tok: str, vals: list[float]) -> bool:
    v = abs(float(tok))
    if v <= SMALL and float(v).is_integer():
        return True
    dec = len(tok.split(".")[1]) if "." in tok else 0
    for a in vals:
        for x in (a, abs(a)):
            if round(x, dec) == round(v, dec) or abs(x - v) <= 0.5 * 10 ** (-dec) + 1e-12:
                return True
    return False


def keep_supported(sentences: list[str], vals: list[float]) -> tuple[list[str], list[str]]:
    """Sentences whose every number is one of vals (as written, to its decimals); the others are dropped."""
    kept, dropped = [], []
    for s in sentences:
        toks = [m.group(0) for m in NUM.finditer(s) if "/" not in m.group(0)]
        (kept if all(_matches(t, vals) for t in toks) else dropped).append(s)
    return kept, dropped
