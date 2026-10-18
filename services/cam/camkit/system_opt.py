"""Design search for a cam system (round 39, step 4d): which motion law, and how fast the camshaft can run.

For each candidate law (the same law on every rise and return of every cam; dwells stay) the highest camshaft speed is
found by bisection at which every speed-dependent limit the user gave still holds: tip vibration in the dwells, motor
peak torque and motor speed. Speed-independent checks (pressure angles, interlocks) are reported as they are. Limits
not given are not used (and said so) — nothing is invented. Uses camkit.system's quick analysis (no undercut search,
no contact stress), then the chosen design is checked in full by the normal analysis.
"""

from __future__ import annotations

import copy
import math

from camkit import system as S
from camkit.analyze import _num

LAWS = ("mod_sine", "cycloidal", "poly4567", "mod_trapezoid", "poly345")


def with_law(system: dict, law: str) -> dict:
    s = copy.deepcopy(system)
    for c in s.get("cams") or []:
        for seg in (c.get("program") or {}).get("segments") or []:
            if seg.get("kind") in ("rise", "return"):
                seg["law"] = law
    return s


def with_rpm(system: dict, rpm: float) -> dict:
    s = copy.deepcopy(system)
    s["camshaft"] = dict(s.get("camshaft") or {}, rpm=rpm)
    return s


def metrics(system: dict) -> dict:
    r = S.analyse(system, quick=True)
    ck = {c["id"]: c for c in r["checks"]}
    vib = max((c["value"] for c in r["checks"] if c["id"].startswith("vib_") and c["value"] is not None), default=None)
    sub_fail = [f"{p['id']}:{c['id']}" for p in r["cams"] for c in p["checks"] if c["status"] == "fail"]
    locks_ok = all(c["status"] != "fail" for c in r["checks"] if c["id"].startswith("lock_"))
    return {"vib_um": vib, "motor_peak": ck["motor_peak"]["value"], "motor_speed": ck["motor_speed"]["value"],
            "cycle": r["cycle"], "fails": sub_fail, "locks_ok": locks_ok}


def ok_at(system: dict, rpm: float, lim: dict) -> tuple[bool, dict]:
    m = metrics(with_rpm(system, rpm))
    ok = m["locks_ok"] and not m["fails"]
    if lim["vib"] is not None and m["vib_um"] is not None:
        ok &= m["vib_um"] <= lim["vib"]
    if lim["peak"] is not None:
        ok &= m["motor_peak"] <= lim["peak"]
    if lim["speed"] is not None:
        ok &= m["motor_speed"] <= lim["speed"]
    return ok, m


def optimise(system: dict) -> dict:
    lim = {"vib": _num((system.get("limits") or {}).get("vib_um")),
           "peak": _num((system.get("drive") or {}).get("peak_Nm")),
           "speed": _num((system.get("drive") or {}).get("max_rpm"))}
    rpm0 = _num((system.get("camshaft") or {}).get("rpm")) or 60.0
    used = [k for k, v in lim.items() if v is not None]
    rows = []
    for law in LAWS:
        s = with_law(system, law)
        try:
            ok0, m0 = ok_at(s, rpm0, lim)
        except ValueError as exc:
            rows.append({"law": law, "error": str(exc)})
            continue
        row = {"law": law, "at_rpm": rpm0, "vib_um": m0["vib_um"], "motor_peak": m0["motor_peak"], "ok": ok0,
               "fails": m0["fails"], "rpm_max": None, "cycle_at_max": None}
        if used:
            lo, hi = (rpm0, rpm0 * 4) if ok0 else (rpm0 / 8, rpm0)
            ok_lo, _ = ok_at(s, lo, lim)
            if ok_lo:
                if ok0:
                    ok_hi, _ = ok_at(s, hi, lim)
                    if ok_hi:
                        lo = hi
                        hi = None
                if hi is not None:
                    for _ in range(9):
                        mid = math.sqrt(lo * hi)
                        if ok_at(s, mid, lim)[0]:
                            lo = mid
                        else:
                            hi = mid
                row["rpm_max"] = round(lo, 2)
                row["cycle_at_max"] = metrics(with_rpm(s, lo))["cycle"]
        rows.append(row)
    good = [r for r in rows if r.get("rpm_max")]
    if good:
        best = max(good, key=lambda r: r["rpm_max"])
        basis = "fastest"
    else:
        cand = [r for r in rows if "error" not in r and r["vib_um"] is not None and not r["fails"]]
        best = min(cand, key=lambda r: r["vib_um"]) if cand else None
        basis = "least vibration"
    return {"rows": rows, "best": best, "basis": basis, "limits_used": used,
            "limits_missing": [k for k, v in lim.items() if v is None]}
