"""Tapered roller bearings in pairs: from the end play as set to the end play at work (round 64, plan section 二十一).

The pair (taper_pair.py) is worked with one axial end play e (e > 0 play, e < 0 preload). That e is what the fitter
sets; at work it changes by three things, each a closing of every roller along the cup normal n = (σ sin α, cos α) in
(z, r) (σ the row's facing, α the cup angle), turned into an equal change of e by Δe = −2 δ / sin α (taper_pair:
each row's closing from the end play is −(e/2) sin α):

1. Fits, when the end play was set before the rings were pressed in (a "bench" setting, e.g. a pair with spacers):
   the cone's raceway grows by g_i and the cup's shrinks by s_o (diametral, thick-walled cylinders as in
   clearance.py); the cone carries its rollers, so each row closes by (g_i + s_o)/2 · cos α:
        Δe_fit = −(g_i + s_o) / tan α.
   When the end play is set after mounting (adjusted with a nut or shims on the mounted rings), Δe_fit = 0.
2. Ring temperatures: the inner side (cone and rollers) at T_i, the cup at T_o, bearing steel α_r; the contact on the
   cup at radius d_o/2 moves out by α_r ΔT (d_o/2) on each side:
        Δe_rad = −(d_o / tan α) · α_r (ΔT_i − ΔT_o).
3. Axial growth of the shaft (T_s, α_s) against the housing (T_h, α_h) over the distance s between the rows (their
   raceway centres): the cones move apart from the cups by (α_s ΔT_s − α_h ΔT_h) s. Back to back (DB) this opens the
   rows, face to face (DF) it closes them:
        Δe_ax = ± s (α_s ΔT_s − α_h ΔT_h),   + for DB, − for DF.
ΔT are from the temperature at which the end play was set. With the shaft and rings of one steel at one temperature
and the housing and cups at another, a DB pair keeps its end play when s = d_o / tan α: the two cup raceway cones then
meet on the axis (the "apexes coincide" rule of the bearing makers); a DF pair always loses end play when the shaft
runs warmer. Simplifications, said in the results: the rollers at the inner ring's temperature; the cups follow their
own temperature (not the housing's) radially; the fits as at the setting temperature (heat does not change them here).

Plain code: no AI, no network. mm, °C, 1/°C.
"""

from __future__ import annotations

import math

from bearingkit import clearance as CL

ThermalError = ValueError


def fits(basis: str, d: float, D: float, di: float, do: float, shaft_I: float, housing_I: float, E: float, nu: float):
    """Growth of the cone raceway and shrinkage of the cup raceway (diametral, mm) that the setting did not see."""
    if basis == "mounted":
        return 0.0, 0.0
    if basis != "bench":
        raise ThermalError("the end play is set on the mounted rings or before mounting (bench)")
    gi = CL.fit_inner(shaft_I, d, di, E_r=E, nu_r=nu, E_s=E, nu_s=nu)["growth"] if shaft_I else 0.0
    so = CL.fit_outer(housing_I, D, do, E_r=E, nu_r=nu, E_h=E, nu_h=nu)["shrink"] if housing_I else 0.0
    return gi, so


def operating(
    e_set: float,
    arrangement: str,
    s: float,
    alpha: float,
    do: float,
    gi: float = 0.0,
    so: float = 0.0,
    temps: dict | None = None,
) -> dict:
    """The end play from the setting to work. temps: T_ref, T_i, T_o, T_shaft, T_house (°C) and a_ring, a_shaft,
    a_house (1/°C), all given (None: temperature not taken). Returns the steps in mm."""
    if arrangement not in ("DB", "DF"):
        raise ThermalError("the arrangement of a tapered pair is DB or DF")
    t = math.tan(alpha)
    d_fit = -(gi + so) / t
    out = {"set": e_set, "fit": d_fit, "mounted": e_set + d_fit, "radial": None, "axial": None, "operating": None}
    if temps is None:
        return out
    dTi, dTo = temps["T_i"] - temps["T_ref"], temps["T_o"] - temps["T_ref"]
    dTs, dTh = temps["T_shaft"] - temps["T_ref"], temps["T_house"] - temps["T_ref"]
    rad = -(do / t) * temps["a_ring"] * (dTi - dTo)
    ax = (1 if arrangement == "DB" else -1) * s * (temps["a_shaft"] * dTs - temps["a_house"] * dTh)
    out.update(radial=rad, axial=ax, operating=e_set + d_fit + rad + ax)
    return out


def apex_distance(alpha: float, do: float) -> float:
    """Row distance at which a DB pair of one steel keeps its end play when the shaft runs warmer than the housing."""
    return do / math.tan(alpha)
