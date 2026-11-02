"""Selective assembly (round 64, step 5, part 3): measured inner rings, outer rings and ball groups into bearings
whose radial clearance lands in the required range.

Radial (diametral) clearance of a set:  P = d_o − d_i − 2 D_w
(outer raceway diameter, inner raceway diameter, ball diameter of the group used; all measured, mm).

1. Piece by piece: the most sets first, then the clearances closest to the target,
       maximise  Σ (W − |P − P_t|)  over the chosen sets        W larger than any possible deviation;
   each ring used at most once, each ball group for at most ⌊balls in the group / Z⌋ sets. When the ball groups
   are not short, each inner–outer pair takes its best group and the problem is a bipartite assignment (Hungarian
   algorithm, exact, fast for a few hundred rings). When a group runs short, every feasible triple (inner, outer,
   group) becomes a variable of an integer programme solved by HiGHS (scipy.optimize.milp, deterministic; if its
   time limit is reached the best answer found is used and the result says it is not proven optimal). For large
   batches with short groups the groups get prices (Lagrangian relaxation, subgradient steps) and the matching is
   repaired to fit; that answer is marked as not proven optimal. The tests check against exhaustive search.
2. By groups (the usual shop method, for comparison). Inner and outer rings are sorted into size classes of width h;
   for each pair of classes the ball group whose nominal clearance (class centres) is nearest the target is taken,
   and the rings in the two classes are paired in order. A set counts only if its real clearance is in range: the
   grouping does not see where in a class a ring lies.

Plain code: no AI, no network. mm in, clearances also given in µm.
"""

from __future__ import annotations

import itertools
import math
import random

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linear_sum_assignment, milp
from scipy.sparse import coo_matrix

MAX_PARTS = 600  # rings of each kind in one run


class AssemblyError(ValueError):
    pass


def _rings(rows, what: str) -> list[tuple[str, float]]:
    out = []
    for k, r in enumerate(rows or []):
        if isinstance(r, dict):
            rid, d = r.get("id") or f"{what[0].upper()}{k + 1}", r.get("d")
        else:
            rid, d = (str(r[0]), r[1]) if len(r) > 1 else (f"{what[0].upper()}{k + 1}", r[0])
        try:
            d = float(d)
        except (TypeError, ValueError) as e:
            raise AssemblyError(f"{what}: line {k + 1} has no diameter") from e
        if not (d > 0 and math.isfinite(d)):
            raise AssemblyError(f"{what}: line {k + 1} has no diameter")
        out.append((str(rid), d))
    if not out:
        raise AssemblyError(f"give the measured {what}")
    if len(out) > MAX_PARTS:
        raise AssemblyError(f"at most {MAX_PARTS} {what} in one run")
    if len({r[0] for r in out}) != len(out):
        raise AssemblyError(f"{what}: the numbers repeat")
    return out


def _groups(rows, Z: int) -> list[dict]:
    out = []
    for k, r in enumerate(rows or []):
        try:
            g = {"id": str(r.get("id") or f"G{k + 1}"), "Dw": float(r["Dw"]), "qty": int(r["qty"])}
        except (KeyError, TypeError, ValueError) as e:
            raise AssemblyError(f"ball groups: line {k + 1} needs a diameter and a quantity") from e
        if not (g["Dw"] > 0 and g["qty"] >= 0):
            raise AssemblyError(f"ball groups: line {k + 1} needs a diameter and a quantity")
        g["sets"] = g["qty"] // Z
        out.append(g)
    if not out:
        raise AssemblyError("give the ball groups")
    return out


def _parse(p: dict):
    Z = int(p.get("Z") or 0)
    if Z < 3:
        raise AssemblyError("give the number of balls per bearing (at least 3)")
    pmin, pmax = p.get("P_min"), p.get("P_max")
    if pmin in (None, "") or pmax in (None, ""):
        raise AssemblyError("give the required clearance range")
    pmin, pmax = float(pmin), float(pmax)
    if not pmax > pmin:
        raise AssemblyError("the clearance range: the largest is above the smallest")
    pt = float(p["P_target"]) if p.get("P_target") not in (None, "") else (pmin + pmax) / 2
    return (
        _rings(p.get("inner"), "inner rings"),
        _rings(p.get("outer"), "outer rings"),
        _groups(p.get("groups"), Z),
        Z,
        pmin,
        pmax,
        pt,
    )


def _assign(inner, outer, groups, pmin, pmax, pt, price=None):
    """Bipartite matching inner × outer with each pair using its best ball group (an optional price per group
    steers it away from short groups): Hungarian algorithm, exact for this cost matrix."""
    di = np.array([d for _, d in inner])
    do = np.array([d for _, d in outer])
    W = 1.0 + (pmax - pmin)  # one more set always beats any saving in deviation
    best = np.zeros((len(inner), len(outer)))
    arg = -np.ones((len(inner), len(outer)), dtype=int)
    for g, gr in enumerate(groups):
        if gr["sets"] <= 0:
            continue
        P = do[None, :] - di[:, None] - 2 * gr["Dw"]
        ok = (P >= pmin - 1e-9) & (P <= pmax + 1e-9)  # measured to 0.1 µm: no rounding traps
        val = np.where(ok, W - np.abs(P - pt) - (price[g] if price is not None else 0.0), 0.0)
        better = val > best
        best = np.where(better, val, best)
        arg = np.where(better, g, arg)
    r, c = linear_sum_assignment(best, maximize=True)
    keep = [(int(i), int(o), int(arg[i, o])) for i, o in zip(r, c, strict=True) if arg[i, o] >= 0]
    return [(i, o, g, do[o] - di[i] - 2 * groups[g]["Dw"]) for i, o, g in keep]


def _repair(chosen, inner, outer, groups, pmin, pmax, pt):
    """Make a matching respect the ball groups: an over-used group hands its worst sets to another group that
    still has balls and keeps the clearance in range; what cannot move is dropped."""
    di = {k: d for k, (_, d) in enumerate(inner)}
    do = {k: d for k, (_, d) in enumerate(outer)}
    left = [gr["sets"] for gr in groups]
    out = []
    for i, o, g, P in sorted(chosen, key=lambda t: abs(t[3] - pt)):
        if left[g] > 0:
            left[g] -= 1
            out.append((i, o, g, P))
            continue
        alts = [
            (abs(do[o] - di[i] - 2 * gr["Dw"] - pt), h)
            for h, gr in enumerate(groups)
            if left[h] > 0 and pmin - 1e-9 <= do[o] - di[i] - 2 * gr["Dw"] <= pmax + 1e-9
        ]
        if alts:
            _, h = min(alts)
            left[h] -= 1
            out.append((i, o, h, do[o] - di[i] - 2 * groups[h]["Dw"]))
    return out


def _lagrange(inner, outer, groups, pmin, pmax, pt):
    """Prices on the short ball groups (subgradient steps) until the matching fits the groups; the best feasible
    answer after repair is kept. Not proven optimal."""
    W = 1.0 + (pmax - pmin)
    price = np.zeros(len(groups))
    best, best_key = None, None
    for it in range(80):
        ch = _assign(inner, outer, groups, pmin, pmax, pt, price)
        use = np.zeros(len(groups))
        for *_, g, _P in ch:
            use[g] += 1
        fixed = _repair(ch, inner, outer, groups, pmin, pmax, pt)
        key = (len(fixed), -sum(abs(t[3] - pt) for t in fixed))
        if best_key is None or key > best_key:
            best, best_key = fixed, key
        cap = np.array([gr["sets"] for gr in groups], dtype=float)
        if np.all(use <= cap):
            break
        step = 0.5 * W / (1 + it) / max(np.max(np.abs(use - cap)), 1.0)
        price = np.maximum(0.0, price + step * (use - cap))
    return best


MILP_MAX = 60000  # feasible triples above which the exact programme is not tried


def piecewise(inner, outer, groups, pmin, pmax, pt) -> dict:
    """The most sets, then the least total deviation from the target. Hungarian matching when the ball groups are
    not short; otherwise the integer programme (HiGHS, exact) on the feasible triples."""
    chosen = _assign(inner, outer, groups, pmin, pmax, pt)
    use = {}
    for *_, g, _P in chosen:
        use[g] = use.get(g, 0) + 1
    optimal, method = True, "matching"
    if any(use[g] > groups[g]["sets"] for g in use):
        di = np.array([d for _, d in inner])
        do = np.array([d for _, d in outer])
        trip = []
        for g, gr in enumerate(groups):
            if gr["sets"] <= 0:
                continue
            P = do[None, :] - di[:, None] - 2 * gr["Dw"]
            ii, oo = np.nonzero((P >= pmin - 1e-9) & (P <= pmax + 1e-9))
            trip += [(int(a), int(b), g, float(P[a, b])) for a, b in zip(ii, oo, strict=True)]
        res = None
        if len(trip) <= MILP_MAX:
            method = "milp"
            n = len(trip)
            W = 1.0 + (pmax - pmin)
            c = -np.array([W - abs(P - pt) for *_, P in trip])
            rows, cols = [], []
            ni, no = len(inner), len(outer)
            for k, (a, b, g, _) in enumerate(trip):
                rows += [a, ni + b, ni + no + g]
                cols += [k, k, k]
            A = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(ni + no + len(groups), n)).tocsr()
            ub = np.array([1] * ni + [1] * no + [gr["sets"] for gr in groups], dtype=float)
            res = milp(
                c,
                constraints=LinearConstraint(A, -np.inf, ub),
                integrality=np.ones(n),
                bounds=Bounds(0, 1),
                options={"time_limit": 20, "disp": False},
            )
        if res is not None and res.x is not None:
            optimal = res.status == 0
            chosen = [trip[k] for k in range(len(trip)) if res.x[k] > 0.5]
        else:
            method, optimal = "lagrange", False
            chosen = _lagrange(inner, outer, groups, pmin, pmax, pt)
    return {
        "sets": [
            {"inner": inner[i][0], "outer": outer[o][0], "group": groups[g]["id"], "P": float(P)}
            for i, o, g, P in sorted(chosen, key=lambda t: (t[0], t[1]))
        ],
        "count": len(chosen),
        "optimal": optimal,
        "method": method,
        # no method can make more sets than rings or ball sets allow: when this is reached the count is the best
        "upper": min(len(inner), len(outer), sum(gr["sets"] for gr in groups)),
    }


def grouped(inner, outer, groups, pmin, pmax, pt, h: float) -> dict:
    """The size-class method: classes of width h for inner and outer rings, one ball group per class pair."""
    if not h > 0:
        raise AssemblyError("the class width is more than 0")
    lo_i, lo_o = min(d for _, d in inner), min(d for _, d in outer)

    def cls(d, lo):
        return int((d - lo) // h)

    ci, co = {}, {}
    for rid, d in inner:
        ci.setdefault(cls(d, lo_i), []).append((rid, d))
    for rid, d in outer:
        co.setdefault(cls(d, lo_o), []).append((rid, d))
    left = {g["id"]: g["sets"] for g in groups}
    sets, tried = [], 0
    # pair the classes whose nominal clearance (any ball group) is nearest the target, best first
    cand = []
    for a in ci:
        for b in co:
            di_c, do_c = lo_i + (a + 0.5) * h, lo_o + (b + 0.5) * h
            g = min(groups, key=lambda gr: abs(do_c - di_c - 2 * gr["Dw"] - pt))
            Pn = do_c - di_c - 2 * g["Dw"]
            if pmin <= Pn <= pmax:
                cand.append((abs(Pn - pt), a, b, g["id"], g["Dw"]))
    for _, a, b, gid, Dw in sorted(cand):
        rs_i = sorted(ci[a], key=lambda r: r[1])
        rs_o = sorted(co[b], key=lambda r: r[1])
        m = min(len(rs_i), len(rs_o), left[gid])
        for k in range(m):
            (ii, di), (oo, do) = rs_i[k], rs_o[k]
            P = do - di - 2 * Dw
            tried += 1
            sets.append({"inner": ii, "outer": oo, "group": gid, "P": P, "ok": pmin <= P <= pmax})
        ci[a], co[b] = rs_i[m:], rs_o[m:]
        left[gid] -= m
    good = [s for s in sets if s["ok"]]
    return {"sets": sets, "count": len(good), "out_of_range": len(sets) - len(good), "h": h}


def run(p: dict) -> dict:
    inner, outer, groups, Z, pmin, pmax, pt = _parse(p)
    pw = piecewise(inner, outer, groups, pmin, pmax, pt)
    h = float(p["h"]) if p.get("h") not in (None, "") else (pmax - pmin) / 2
    gp = grouped(inner, outer, groups, pmin, pmax, pt, h)
    used_i = {s["inner"] for s in pw["sets"]}
    used_o = {s["outer"] for s in pw["sets"]}
    usage = {g["id"]: 0 for g in groups}
    for s in pw["sets"]:
        usage[s["group"]] += 1

    def why(d, other, is_inner):
        # no partner in range at all, or partners all taken
        for _, d2 in other:
            for g in groups:
                P = (d2 - d if is_inner else d - d2) - 2 * g["Dw"]
                if pmin <= P <= pmax and g["sets"] > 0:
                    return "taken"
        return "none"

    left_i = [{"id": r, "d": d, "why": why(d, outer, True)} for r, d in inner if r not in used_i]
    left_o = [{"id": r, "d": d, "why": why(d, inner, False)} for r, d in outer if r not in used_o]
    Ps = np.array([s["P"] for s in pw["sets"]])
    return {
        "Z": Z,
        "P_min": pmin,
        "P_max": pmax,
        "P_target": pt,
        "piecewise": pw,
        "grouped": gp,
        "left_inner": left_i,
        "left_outer": left_o,
        "groups": [
            {
                "id": g["id"],
                "Dw": g["Dw"],
                "qty": g["qty"],
                "sets_max": g["sets"],
                "used": usage[g["id"]],
                "balls_used": usage[g["id"]] * Z,
            }
            for g in groups
        ],
        "stats": (
            {"mean": float(Ps.mean()), "std": float(Ps.std()), "min": float(Ps.min()), "max": float(Ps.max())}
            if len(Ps)
            else None
        ),
        "n_inner": len(inner),
        "n_outer": len(outer),
    }


def brute_force(inner, outer, groups, pmin, pmax, pt) -> tuple[int, float]:
    """Exhaustive search for small batches (tests): the most sets, then the least total deviation."""
    best = (0, 0.0)
    no = len(outer)
    for perm in itertools.permutations(list(range(no)) + [None] * len(inner), len(inner)):
        pairs = [(i, o) for i, o in enumerate(perm) if o is not None]
        for gs in itertools.product(range(len(groups)), repeat=len(pairs)):
            cnt = {}
            dev, ok = 0.0, True
            for (i, o), g in zip(pairs, gs, strict=True):
                P = outer[o][1] - inner[i][1] - 2 * groups[g]["Dw"]
                cnt[g] = cnt.get(g, 0) + 1
                if not (pmin <= P <= pmax) or cnt[g] > groups[g]["sets"]:
                    ok = False
                    break
                dev += abs(P - pt)
            if ok and (len(pairs) > best[0] or (len(pairs) == best[0] and dev < best[1] - 1e-15)):
                best = (len(pairs), dev)
    return best


def synthetic(n: int, di: float, do: float, Dw: float, Z: int, seed: int = 1) -> dict:
    """Synthetic measured data for trying the tool (labelled synthetic everywhere it is shown): ring raceway
    diameters scattered about the design values, three ball groups 2 µm apart."""
    rnd = random.Random(seed)
    inner = [{"id": f"I{k + 1:03d}", "d": round(rnd.gauss(di, 0.004), 4)} for k in range(n)]
    outer = [{"id": f"O{k + 1:03d}", "d": round(rnd.gauss(do, 0.004), 4)} for k in range(n)]
    groups = [{"id": f"{s:+d}", "Dw": round(Dw + s * 0.001, 4), "qty": Z * n // 2} for s in (-2, 0, 2)]
    return {"inner": inner, "outer": outer, "groups": groups, "Z": Z, "synthetic": True}
