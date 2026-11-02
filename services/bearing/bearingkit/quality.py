"""Inspection and SPC (round 64, step 5, part 4): roundness and waviness of a raceway, control charts, capability.

1. Roundness and waviness. A measured turn of the raceway (radius deviations, µm, at equal angle steps or with
   angles) is transformed (FFT): amplitude and phase per order (undulations per revolution, UPR). Order 1 is the
   set-up eccentricity and is taken out; what remains, peak to valley, is the roundness about the least-squares
   circle (LSC; for small deviations the LSC centre is exactly the first harmonic). Order bands (e.g. a roundness
   band and waviness bands) are the user's: the RMS of each band is given; no band limits are built in.
2. Control charts (Shewhart): mean and range (subgroups of 2 to 25), mean and standard deviation (subgroups of 2 or
   more), individuals and moving range (n = 1). The chart constants are worked out from the normal distribution,
   not copied from a table:
       d2(n) = E[range of n standard normals] = ∫ [1 − Φ(x)ⁿ − (1 − Φ(x))ⁿ] dx
       d3(n)² = Var(range) = 2 ∫∫_{x<y} [1 − Φ(y)ⁿ − (1 − Φ(x))ⁿ + (Φ(y) − Φ(x))ⁿ] dx dy − d2²
       c4(n) = √(2/(n − 1)) Γ(n/2) / Γ((n − 1)/2)
   (Montgomery, Introduction to Statistical Quality Control, ch. 6; the tests compare with the familiar values.)
   Tests for special causes: the eight rules of L. S. Nelson, "The Shewhart Control Chart—Tests for Special
   Causes", Journal of Quality Technology 16(4), 1984, pp. 238–239, applied to the mean (or individuals) chart; the
   range / s / moving-range chart uses rule 1.
3. Capability: Cp = (USL − LSL) / 6σ, Cpk = min(USL − μ, μ − LSL) / 3σ with σ the within-subgroup estimate
   (R̄/d2, s̄/c4 or MR̄/d2(2)); Pp, Ppk with the overall standard deviation. Specification limits are the user's.

Plain code: no AI, no network.
"""

from __future__ import annotations

import math
import random
from functools import lru_cache

import numpy as np
from scipy import integrate
from scipy.interpolate import CubicSpline
from scipy.special import gammaln
from scipy.stats import norm


class QualityError(ValueError):
    pass


# ---------------------------------------------------------------- roundness and waviness


def profile(p: dict) -> dict:
    """Harmonics of one measured turn. p: {"r": [µm …] equally spaced} or {"points": [[angle_deg, µm], …]},
    optional "bands": [[from_order, to_order, name], …]."""
    if p.get("points"):
        pts = np.array([[float(a), float(b)] for a, b in p["points"]])
        if len(pts) < 16:
            raise QualityError("a profile needs at least 16 points round the turn")
        a = np.mod(pts[:, 0], 360.0)
        order = np.argsort(a)
        a, r = a[order], pts[order, 1]
        if np.ptp(a) < 300:
            raise QualityError("the profile must go round the whole turn")
        n = int(2 ** math.ceil(math.log2(max(len(a), 64))))
        grid = np.arange(n) * 360.0 / n
        # periodic cubic spline through the measured points (straight lines would flatten the higher orders)
        a2, keep = np.unique(a, return_index=True)
        r2 = r[keep]
        spl = CubicSpline(np.append(a2, a2[0] + 360.0), np.append(r2, r2[0]), bc_type="periodic")
        r = spl(np.mod(grid - a2[0], 360.0) + a2[0])
    else:
        r = np.array([float(x) for x in (p.get("r") or [])])
        if len(r) < 16:
            raise QualityError("a profile needs at least 16 points round the turn")
    n = len(r)
    F = np.fft.rfft(r) / n
    amp = 2 * np.abs(F)
    amp[0] = abs(F[0])
    phase = np.degrees(np.angle(F))
    # take out the mean (order 0) and the eccentricity (order 1): what is left is about the least-squares circle
    G = F.copy()
    G[0] = 0
    if len(G) > 1:
        G[1] = 0
    resid = np.fft.irfft(G * n, n)
    top = len(amp) - 1
    bands = []
    for b in p.get("bands") or []:
        lo, hi = int(b[0]), int(b[1])
        name = str(b[2]) if len(b) > 2 else f"{lo}–{hi}"
        if not 2 <= lo <= hi:
            raise QualityError("a band runs from order 2 or more up to a higher order")
        hi = min(hi, top)
        rms = float(np.sqrt(np.sum((amp[lo : hi + 1] ** 2) / 2))) if lo <= hi else 0.0
        bands.append(
            {
                "name": name,
                "from": lo,
                "to": hi,
                "rms": rms,
                "peak_order": int(lo + np.argmax(amp[lo : hi + 1])) if lo <= hi else None,
            }
        )
    return {
        "n": n,
        "roundness": float(np.ptp(resid)),
        "eccentricity": float(amp[1]) if top >= 1 else 0.0,
        "orders": list(range(top + 1)),
        "amp": amp.round(6).tolist(),
        "phase": phase.round(3).tolist(),
        "resid": resid.round(5).tolist(),
        "bands": bands,
    }


# ---------------------------------------------------------------- chart constants


@lru_cache(maxsize=64)
def d2(n: int) -> float:
    if n < 2:
        raise QualityError("a range needs at least 2 values")
    f = lambda x: 1 - norm.cdf(x) ** n - (1 - norm.cdf(x)) ** n  # noqa: E731
    return integrate.quad(f, -12, 12, limit=200, epsabs=1e-12)[0]


@lru_cache(maxsize=64)
def d3(n: int) -> float:
    def inner(y):
        Fy = norm.cdf(y)
        g = lambda x: 1 - Fy**n - (1 - norm.cdf(x)) ** n + (Fy - norm.cdf(x)) ** n  # noqa: E731
        return integrate.quad(g, -12, y, limit=200, epsabs=1e-12)[0]

    e = 2 * integrate.quad(inner, -12, 12, limit=200, epsabs=1e-10)[0]
    return math.sqrt(max(e - d2(n) ** 2, 0.0))


def c4(n: int) -> float:
    if n < 2:
        raise QualityError("a standard deviation needs at least 2 values")
    return math.sqrt(2 / (n - 1)) * math.exp(gammaln(n / 2) - gammaln((n - 1) / 2))


# ---------------------------------------------------------------- tests for special causes (Nelson 1984)


def nelson(x: list[float], cl: float, sigma: float) -> list[dict]:
    """Points that break each of Nelson's eight rules: [{"rule", "points": [index of the last point of a run]}]."""
    z = (np.asarray(x, dtype=float) - cl) / sigma
    n = len(z)
    hits = {k: set() for k in range(1, 9)}
    for i in range(n):
        if abs(z[i]) > 3:
            hits[1].add(i)
        if i >= 8 and (np.all(z[i - 8 : i + 1] > 0) or np.all(z[i - 8 : i + 1] < 0)):
            hits[2].add(i)
        if i >= 5:
            d = np.diff(z[i - 5 : i + 1])
            if np.all(d > 0) or np.all(d < 0):
                hits[3].add(i)
        if i >= 13:
            d = np.diff(z[i - 13 : i + 1])
            if np.all(d[1:] * d[:-1] < 0):
                hits[4].add(i)
        if i >= 2:
            w = z[i - 2 : i + 1]
            if np.sum(w > 2) >= 2 or np.sum(w < -2) >= 2:
                hits[5].add(i)
        if i >= 4:
            w = z[i - 4 : i + 1]
            if np.sum(w > 1) >= 4 or np.sum(w < -1) >= 4:
                hits[6].add(i)
        if i >= 14 and np.all(np.abs(z[i - 14 : i + 1]) < 1):
            hits[7].add(i)
        if i >= 7:
            w = z[i - 7 : i + 1]
            if np.all(np.abs(w) > 1) and np.any(w > 0) and np.any(w < 0):
                hits[8].add(i)
    return [{"rule": k, "points": sorted(v)} for k, v in hits.items() if v]


# ---------------------------------------------------------------- control charts and capability


def spc(p: dict) -> dict:
    """p: {"data": [[subgroup values …], …] (n = 1: one value per row), "chart": "xbar_r" | "xbar_s" | "i_mr",
    "lsl", "usl", "name", "unit"}."""
    rows = [[float(v) for v in r] for r in (p.get("data") or []) if len(r)]
    if len(rows) < 2:
        raise QualityError("give at least 2 subgroups")
    sizes = {len(r) for r in rows}
    if len(sizes) != 1:
        raise QualityError("every subgroup has the same number of values")
    n = sizes.pop()
    chart = p.get("chart") or ("i_mr" if n == 1 else "xbar_r" if n <= 10 else "xbar_s")
    X = np.array(rows)
    allv = X.ravel()
    out = {"n": n, "k": len(rows), "chart": chart, "name": p.get("name") or "", "unit": p.get("unit") or ""}
    if chart == "i_mr":
        if n != 1:
            raise QualityError("the individuals chart takes one value per row")
        x = X[:, 0]
        mr = np.abs(np.diff(x))
        mrbar = float(mr.mean())
        sigma = mrbar / d2(2)
        cl = float(x.mean())
        out["main"] = {"name": "I", "points": x.tolist(), "cl": cl, "ucl": cl + 3 * sigma, "lcl": cl - 3 * sigma}
        out["spread"] = {
            "name": "MR",
            "points": [None] + mr.tolist(),
            "cl": mrbar,
            "ucl": mrbar * (1 + 3 * d3(2) / d2(2)),
            "lcl": max(0.0, mrbar * (1 - 3 * d3(2) / d2(2))),
        }
        main_pts = x
    elif chart in ("xbar_r", "xbar_s"):
        if n < 2:
            raise QualityError("a mean chart needs subgroups of 2 or more")
        if chart == "xbar_r" and n > 25:
            raise QualityError("the range chart is for subgroups up to 25; use the s chart")
        xb = X.mean(axis=1)
        cl = float(xb.mean())
        if chart == "xbar_r":
            R = np.ptp(X, axis=1)
            rbar = float(R.mean())
            sigma = rbar / d2(n)
            k3 = 3 * d3(n) / d2(n)
            out["spread"] = {
                "name": "R",
                "points": R.tolist(),
                "cl": rbar,
                "ucl": rbar * (1 + k3),
                "lcl": max(0.0, rbar * (1 - k3)),
            }
        else:
            S = X.std(axis=1, ddof=1)
            sbar = float(S.mean())
            sigma = sbar / c4(n)
            k3 = 3 * math.sqrt(1 - c4(n) ** 2) / c4(n)
            out["spread"] = {
                "name": "s",
                "points": S.tolist(),
                "cl": sbar,
                "ucl": sbar * (1 + k3),
                "lcl": max(0.0, sbar * (1 - k3)),
            }
        out["main"] = {
            "name": "X̄",
            "points": xb.tolist(),
            "cl": cl,
            "ucl": cl + 3 * sigma / math.sqrt(n),
            "lcl": cl - 3 * sigma / math.sqrt(n),
        }
        main_pts = xb
    else:
        raise QualityError("the chart is xbar_r, xbar_s or i_mr")
    sig_main = (out["main"]["ucl"] - out["main"]["cl"]) / 3
    out["rules"] = nelson(main_pts.tolist(), out["main"]["cl"], sig_main)
    sp = out["spread"]
    out["spread_out"] = [i for i, v in enumerate(sp["points"]) if v is not None and (v > sp["ucl"] or v < sp["lcl"])]
    out["sigma_within"] = sigma
    out["sigma_overall"] = float(allv.std(ddof=1))
    out["mean"] = float(allv.mean())
    lsl = None if p.get("lsl") in (None, "") else float(p["lsl"])
    usl = None if p.get("usl") in (None, "") else float(p["usl"])
    cap = {}
    mu = out["mean"]
    for key, s in (("C", sigma), ("P", out["sigma_overall"])):
        if lsl is not None and usl is not None:
            cap[key + "p"] = (usl - lsl) / (6 * s)
        sides = [
            v
            for v in (
                (usl - mu) / (3 * s) if usl is not None else None,
                (mu - lsl) / (3 * s) if lsl is not None else None,
            )
            if v is not None
        ]
        if sides:
            cap[key + "pk"] = min(sides)
    out["capability"] = cap
    out["out_of_spec"] = int(
        np.sum((allv > usl) if usl is not None else 0) + np.sum((allv < lsl) if lsl is not None else 0)
    )
    return out


# ---------------------------------------------------------------- synthetic data (labelled synthetic where shown)


def synthetic_profile(n: int = 512, seed: int = 1) -> dict:
    """A raceway turn: eccentricity, ovality, a lobed order and grinding waviness with noise (µm)."""
    rnd = np.random.default_rng(seed)
    th = np.arange(n) * 2 * np.pi / n
    r = (
        3.0 * np.cos(th - 0.4)
        + 0.6 * np.cos(2 * th + 1.0)
        + 0.25 * np.cos(3 * th)
        + 0.08 * np.cos(27 * th + 0.3)
        + 0.05 * np.cos(54 * th)
        + rnd.normal(0, 0.01, n)
    )
    return {"r": r.round(4).tolist(), "synthetic": True}


def synthetic_spc(
    k: int = 25,
    n: int = 5,
    mean: float = 0.0,
    sd: float = 1.0,
    shift_at: int | None = 18,
    shift: float = 1.5,
    seed: int = 1,
) -> dict:
    """Subgroups from a normal process with a step shift (so the rules have something to find)."""
    rnd = random.Random(seed)
    data = []
    for i in range(k):
        m = mean + (shift * sd if shift_at is not None and i >= shift_at else 0.0)
        data.append([round(rnd.gauss(m, sd), 4) for _ in range(n)])
    return {"data": data, "synthetic": True}
