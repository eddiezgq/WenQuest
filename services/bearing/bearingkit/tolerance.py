"""Clearance and groove position dimension chain of a ball bearing (round 64, plan section 二十, part 2).

From the made sizes of the rings and balls, each a nominal value with an upper and lower deviation (the company's):
  d_i, d_o  inner and outer groove bottom diameters;  D_w ball diameter;  r_i, r_o  inner and outer groove radii;
  a_i, a_o  (optional) the axial distance of the inner and outer groove centre from the ring's reference face,
the chain gives
  P_d = d_o − d_i − 2 D_w                       radial (diametral) clearance
  A = r_i + r_o − D_w                           distance of the groove curvature centres with the ball seated
  cos α₀ = 1 − P_d / (2A)                       free contact angle
  G_a = 2 √(A² − (A − P_d/2)²)                  axial play (the inner ring pushed one way and the other)
  s = a_o − a_i + A sin α₀                      standout: how far the inner ring's reference face stands beyond the
                                                outer ring's, the inner ring pushed home in the contact direction
(Harris & Kotzalas, Rolling Bearing Analysis, vol. 1, ch. 2, for P_d, A, α₀ and G_a.)

Three ways, side by side:
- extremes: every combination of upper and lower limits (all the functions are monotonic in each size, so the
  corners hold the extremes);
- statistical: each size normal about the middle of its tolerance with the tolerance as ±3σ; the chain linearised
  at the middle (central differences), σ combined as the root sum of squares; ±3σ given; each size's share;
- Monte Carlo: sampled normal (as above) or uniform over the tolerance, a fixed seed so the same input gives the
  same result; percentiles 0.135 %, 50 %, 99.865 %, a histogram, and the share outside a target range if given.
A negative P_d is an interference: α₀, G_a and s are not defined there and are counted, not computed.

Plain code: no AI, no network. mm, degrees.
"""

from __future__ import annotations

import itertools
import math

import numpy as np

ToleranceError = ValueError
SIZES = ("di", "do", "Dw", "ri", "ro", "ai", "ao")
OUT = ("Pd", "alpha0", "Ga", "s")
SEED = 20261105
P_LO, P_HI = 0.135, 99.865


def chain(x: dict) -> dict:
    """The chain at one set of sizes (arrays allowed). NaN where undefined (interference, or no positions)."""
    di, do, Dw, ri, ro = (np.asarray(x[k], float) for k in ("di", "do", "Dw", "ri", "ro"))
    Pd = do - di - 2 * Dw
    A = ri + ro - Dw
    with np.errstate(invalid="ignore", divide="ignore"):
        c = 1 - Pd / (2 * A)
        ok = (Pd >= 0) & (A > 0) & (c >= -1)
        a0 = np.where(ok, np.arccos(np.clip(c, -1, 1)), np.nan)
        Ga = np.where(ok, 2 * np.sqrt(np.maximum(A * A - (A - Pd / 2) ** 2, 0.0)), np.nan)
        if x.get("ai") is not None and x.get("ao") is not None:
            s = np.asarray(x["ao"], float) - np.asarray(x["ai"], float) + A * np.sin(a0)
        else:
            s = np.full(np.shape(Pd), np.nan)
    return {"Pd": Pd, "alpha0": np.degrees(a0), "Ga": Ga, "s": s}


def _items(spec: dict) -> dict:
    out = {}
    for k in SIZES:
        v = spec.get(k)
        if v is None or v.get("nom") is None:
            if k in ("ai", "ao"):
                continue
            raise ToleranceError(f"give the nominal size and deviations of {k}")
        nom = float(v["nom"])
        if v.get("es") is None or v.get("ei") is None:  # an exact size is written 0, 0: blanks are not taken as 0
            raise ToleranceError(f"give the upper and lower deviations of {k} (0 for an exact size)")
        es, ei = float(v["es"]), float(v["ei"])
        if es < ei:
            raise ToleranceError(f"{k}: the upper deviation is below the lower one")
        out[k] = (nom + ei, nom + es)
    if ("ai" in out) != ("ao" in out):
        raise ToleranceError("give both groove positions a_i and a_o, or neither")
    return out


def analyse(spec: dict, n: int = 100_000, dist: str = "normal", target: dict | None = None, bins: int = 40) -> dict:
    lim = _items(spec)
    keys = list(lim)
    mid = {k: (lo + hi) / 2 for k, (lo, hi) in lim.items()}
    nom = chain({k: spec[k]["nom"] for k in keys})
    out = {"nominal": {k: (float(v) if np.isfinite(v) else None) for k, v in nom.items()}}
    # extremes over every corner
    corners = list(itertools.product(*[lim[k] for k in keys]))
    cv = chain({k: np.array([c[i] for c in corners]) for i, k in enumerate(keys)})
    out["extremes"] = {
        o: ({"min": float(np.nanmin(cv[o])), "max": float(np.nanmax(cv[o]))} if np.isfinite(cv[o]).any() else None)
        for o in OUT
    }
    out["interference_possible"] = bool((cv["Pd"] < 0).any())
    # statistical: linearised at the middle, root sum of squares, and each size's share of the variance
    f0 = chain(mid)
    stat, sens = {}, {}
    for o in OUT:
        if not np.isfinite(f0[o]):
            stat[o] = None
            continue
        var, parts = 0.0, {}
        for k in keys:
            lo, hi = lim[k]
            h = max(1e-7, 1e-6 * max(abs(mid[k]), 1.0))
            up, dn = dict(mid), dict(mid)
            up[k], dn[k] = mid[k] + h, mid[k] - h
            dfdx = float((chain(up)[o] - chain(dn)[o]) / (2 * h))
            sig = (hi - lo) / 6
            parts[k] = {"dfdx": dfdx, "var": (dfdx * sig) ** 2}
            var += (dfdx * sig) ** 2
        sd = math.sqrt(var)
        stat[o] = {"mean": float(f0[o]), "sd": sd, "lo": float(f0[o]) - 3 * sd, "hi": float(f0[o]) + 3 * sd}
        sens[o] = {k: {"dfdx": v["dfdx"], "share": (v["var"] / var if var > 0 else 0.0)} for k, v in parts.items()}
    out["statistical"], out["sensitivity"] = stat, sens
    # Monte Carlo
    if dist not in ("normal", "uniform"):
        raise ToleranceError("the distribution is normal or uniform")
    rng = np.random.default_rng(SEED)
    smp = {}
    for k in keys:
        lo, hi = lim[k]
        smp[k] = rng.normal((lo + hi) / 2, (hi - lo) / 6, n) if dist == "normal" else rng.uniform(lo, hi, n)
    mv = chain(smp)
    mc = {"n": n, "dist": dist, "seed": SEED, "interference": float(np.mean(mv["Pd"] < 0))}
    for o in OUT:
        v = mv[o][np.isfinite(mv[o])]
        if not len(v):
            mc[o] = None
            continue
        h, edges = np.histogram(v, bins=bins)
        mc[o] = {
            "mean": float(v.mean()),
            "sd": float(v.std(ddof=1)),
            "p_lo": float(np.percentile(v, P_LO)),
            "p50": float(np.percentile(v, 50)),
            "p_hi": float(np.percentile(v, P_HI)),
            "hist": h.tolist(),
            "edges": edges.tolist(),
        }
        t = (target or {}).get(o)
        if t and (t.get("min") is not None or t.get("max") is not None):
            lo_t = -np.inf if t.get("min") is None else float(t["min"])
            hi_t = np.inf if t.get("max") is None else float(t["max"])
            mc[o]["outside"] = float(np.mean((mv[o] < lo_t) | (mv[o] > hi_t) | ~np.isfinite(mv[o])))
    out["montecarlo"] = mc
    return out


def nominal_from(g: dict) -> dict:
    """The chain's nominal sizes from a ball bearing design (deviations and groove positions left for the company)."""
    if g.get("type") not in ("deep_groove", "angular") and not g.get("flex"):
        raise ToleranceError("the clearance chain is for ball bearings (deep groove, angular contact, flexible)")
    return {
        "di": {"nom": g["di"], "es": None, "ei": None},
        "do": {"nom": g["do"], "es": None, "ei": None},
        "Dw": {"nom": g["Dw"], "es": None, "ei": None},
        "ri": {"nom": g["fi"] * g["Dw"], "es": None, "ei": None},
        "ro": {"nom": g["fo"] * g["Dw"], "es": None, "ei": None},
        "ai": {"nom": None, "es": None, "ei": None},
        "ao": {"nom": None, "es": None, "ei": None},
    }
