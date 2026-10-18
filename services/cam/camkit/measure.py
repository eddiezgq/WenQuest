"""Measured cam error, its harmonics, the acceleration it causes, and compensation (round 39, step 3).

Input: a lift table (cam angle, follower lift) measured with the design follower (or a checker set to the same roller
radius and offset), or profile points x, y in the cam frame (external cam or the inner flank of a groove).

- Alignment: the phase shift Δ and constant offset c minimising the squared error over the turn (c is the base-circle /
  zero error and is reported on its own). A best fit cannot tell a phase shift from the part of the error that looks
  like s'·Δ, so that part goes into Δ; when the measuring zero is tied to the part (keyway, pin), turn alignment off.
- Harmonics: the error resampled uniformly and transformed (FFT); amplitude and phase per order; groups 1st order,
  low orders and high orders (group bounds are settings).
- Acceleration error: second derivative of the error (in the frequency domain up to a highest order, so measurement
  noise is not amplified) times ω².
- Compensation: the selected orders subtracted from the motion program (s − e_selected); the tool path and program
  are made again; the remaining error is the orders not selected.
Profile points: normal deviation δn → lift error δs = δn / cos φ (translating) or δψ = δn / (L cos φ) (oscillating;
for a flat face, the distance from the pivot to the contact).

Plain code: no AI, no network. Lengths mm, follower angles rad inside (degrees at the edge).
"""

from __future__ import annotations

import math
import re

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize_scalar

from camkit import disk as D
from camkit import mfg as M
from camkit.analyze import _num, loads, mechanism
from camkit.program import Program

PASS, FAIL, UNKNOWN, NA, INFO = "pass", "fail", "unknown", "na", "info"
N = 3600  # uniform grid, 0.1°


class MeasureError(ValueError):
    pass


def read_table(text: str) -> np.ndarray:
    """Two numeric columns (comma, semicolon, tab or spaces); lines without two numbers are skipped (headers)."""
    rows = []
    for line in (text or "").splitlines():
        nums = re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", line)
        if len(nums) >= 2 and not re.search(r"[A-DF-Za-df-z]", line.split("#")[0]):
            rows.append((float(nums[0]), float(nums[1])))
    if len(rows) < 36:
        raise MeasureError("the measurement needs at least 36 rows of two numbers")
    return np.array(rows).T


def _periodic(x: np.ndarray, y: np.ndarray, grid: np.ndarray, period: float) -> np.ndarray:
    """Periodic interpolation (cubic spline) of samples y(x) onto grid."""
    x = np.mod(x, period)
    o = np.argsort(x)
    x, y = x[o], y[o]
    keep = np.concatenate([[True], np.diff(x) > 1e-9])
    x, y = x[keep], y[keep]
    xx = np.concatenate([x, [x[0] + period]])
    yy = np.concatenate([y, [y[0]]])
    cs = CubicSpline(xx, yy, bc_type="periodic")
    return cs(np.mod(grid - xx[0], period) + xx[0])


def _align(m: np.ndarray, s: np.ndarray):
    """Shift k (grid steps, fractional) and offset c minimising Σ(m(θ+k) − s(θ) − c)². Returns (shift_deg, c, e)."""
    mm, ss = m - m.mean(), s - s.mean()
    corr = np.fft.irfft(np.fft.rfft(mm) * np.conj(np.fft.rfft(ss)), n=len(m))
    k = int(np.argmax(corr))
    a, b, c = corr[k - 1], corr[k], corr[(k + 1) % len(m)]
    den = a - 2 * b + c
    frac = 0.5 * (a - c) / den if den != 0 else 0.0
    shift = (k + frac) * 360.0 / len(m)
    if shift > 180:
        shift -= 360
    grid = np.arange(len(m)) * 360.0 / len(m)
    step = 360.0 / len(m)

    def cost(d):
        r = _periodic(grid, m, grid + d, 360.0) - s
        return float(np.sum((r - r.mean()) ** 2))

    shift = float(minimize_scalar(cost, bounds=(shift - step, shift + step), method="bounded",
                                  options={"xatol": 1e-7}).x)
    m_al = _periodic(grid, m, grid + shift, 360.0)
    off = float(np.mean(m_al - s))
    return shift, off, m_al - s - off


def harmonics(e: np.ndarray, kmax: int) -> dict:
    F = np.fft.rfft(e) / len(e)
    k = np.arange(len(F))
    A = 2 * np.abs(F)
    A[0] = abs(F[0])
    ph = np.angle(F)
    kmax = min(kmax, len(F) - 1)
    return {"k": k[1: kmax + 1], "A": A[1: kmax + 1], "phase": ph[1: kmax + 1], "F": F, "kmax": kmax}


def from_orders(F: np.ndarray, lo: int, hi: int, n: int, deriv: int = 0) -> np.ndarray:
    """The part of a signal made of orders lo..hi (inclusive), optionally differentiated deriv times in θ."""
    G = np.zeros_like(F)
    k = np.arange(len(F))
    sel = (k >= lo) & (k <= hi)
    G[sel] = F[sel] * (1j * k[sel]) ** deriv
    return np.fft.irfft(G * n, n=n)


def _lift_gain(geo: dict, follower: str) -> np.ndarray:
    """Lift error per unit normal deviation of the profile at each cam angle (1/mm or rad/mm)."""
    if follower == "oscillating":
        return 1.0 / np.asarray(geo["lever"])
    return 1.0 / np.cos(np.asarray(geo["phi"]))


def measure(project: dict, meas: dict) -> dict:
    meas = meas or {}
    fmt = meas.get("format", "lift")
    m = mechanism(project.get("mechanism"))
    prog = Program.from_dict(project.get("program") or {})
    geo = D.analyse(m, prog, N)
    theta_deg = np.degrees(geo["theta"])
    s = np.asarray(geo["s"])
    rad = prog.unit == "rad"
    a, b = read_table(meas.get("data", ""))
    if fmt == "lift":
        if a.min() < -360 or a.max() > 720:
            raise MeasureError("cam angles in degrees, within one turn")
        span = (np.max(np.mod(a, 360)) - np.min(np.mod(a, 360)))
        if span < 300:
            raise MeasureError("the measurement must cover the whole turn")
        mv = np.radians(b) if rad else b
        m_grid = _periodic(a, mv, theta_deg, 360.0)
        if meas.get("align", True):
            shift, off, e = _align(m_grid, s)
        else:  # the measuring zero is tied to the part (keyway, pin): only the constant offset is removed
            shift, off = 0.0, float(np.mean(m_grid - s))
            e = m_grid - s - off
    elif fmt == "xy":
        e, shift, off = _xy_error(m, geo, a, b, bool(meas.get("align", True)))
    else:
        raise MeasureError("the measurement is a lift table or profile points")
    kmax = int(_num(meas.get("kmax")) or 60)
    low_hi = int(_num(meas.get("low_hi")) or 6)
    if not 2 <= low_hi < kmax:
        raise MeasureError("the low orders end between 2 and the highest order")
    h = harmonics(e, kmax)
    resid_hi = e - from_orders(h["F"], 0, kmax, N)
    groups = {
        "first": _rms(h["A"][0:1]),
        "low": _rms(h["A"][1:low_hi]),
        "high": _rms(h["A"][low_hi:kmax]),
        "above": float(np.sqrt(np.mean(resid_hi**2))),
    }
    e2 = from_orders(h["F"], 1, kmax, N, deriv=2)
    ld = loads(project.get("loads"))
    rpm = _num(meas.get("rpm")) or ld.rpm
    a_allow = _num(meas.get("a_allow"))
    scale = 1.0 if rad else 1e-3  # mm → m
    unit_acc = "rad/s²" if rad else "m/s²"
    checks = []
    peak_e2 = float(np.max(np.abs(e2)))
    acc = None
    if rpm:
        w = rpm * 2 * math.pi / 60
        acc = e2 * w**2 * scale
        peak = float(np.max(np.abs(acc)))
        status = UNKNOWN if a_allow is None else (PASS if peak <= a_allow else FAIL)
        note = "" if a_allow is not None else "give the allowed acceleration error"
        checks.append(_ck("acc_err", "误差引起的加速度误差峰值", "Peak acceleration error from the profile error", peak,
                          a_allow, status, unit_acc, note, deg=float(theta_deg[int(np.argmax(np.abs(acc)))])))
    else:
        checks.append(_ck("acc_err", "误差引起的加速度误差峰值", "Peak acceleration error from the profile error", None,
                          a_allow, UNKNOWN, unit_acc, "give the speed"))
    if a_allow is not None and peak_e2 > 0:
        rpm_max = math.sqrt(a_allow / (peak_e2 * scale)) * 60 / (2 * math.pi)
        checks.append(_ck("rpm_max", "这样的误差最高能跑的转速", "Highest speed with this error", rpm_max, None, INFO,
                          "r/min"))
    allow_k = None
    if a_allow is not None and rpm:
        w = rpm * 2 * math.pi / 60
        allow_k = (a_allow / (h["k"] ** 2 * w**2 * scale)).tolist()
    unit = "rad" if rad else "mm"
    return {
        "unit": unit,
        "shift_deg": shift,
        "offset": off,
        "deg": theta_deg,
        "e": e,
        "harm": h,
        "groups": groups,
        "low_hi": low_hi,
        "e2": e2,
        "acc": acc,
        "rpm": rpm,
        "a_allow": a_allow,
        "allow_k": allow_k,
        "checks": checks,
        "geo": geo,
        "mechanism": m,
        "program": prog,
    }


def _xy_error(m, geo, x, y, align=True):
    """Normal deviation of measured profile points from the design profile, turned into lift error at each cam
    angle. The rotation of the part on the measuring machine is found like the phase of a lift table."""
    P = np.asarray(geo["profile"])
    ang_d = np.degrees(np.arctan2(P[1], P[0]))
    r_d = np.hypot(P[0], P[1])
    grid = np.arange(N) * 360.0 / N
    if not _star(ang_d):
        raise MeasureError("profile points need a cam outline that every ray from the centre crosses once")
    rd_grid = _periodic(ang_d, r_d, grid, 360.0)
    rm_grid = _periodic(np.degrees(np.arctan2(y, x)), np.hypot(x, y), grid, 360.0)
    if align:
        rot, off, dr = _align(rm_grid, rd_grid)
    else:
        rot, off = 0.0, float(np.mean(rm_grid - rd_grid))
        dr = rm_grid - rd_grid - off
    # back to the design's cam angles: the radial error at each contact point's polar angle, along the normal
    _, nrm, _, flipped = M._closed_geometry(P)
    if flipped:
        nrm = nrm[:, ::-1]
    u = P / np.hypot(P[0], P[1])
    dn = _periodic(grid, dr + off, ang_d, 360.0) * np.sum(u * nrm, axis=0)
    e_all = dn * _lift_gain(geo, m.follower)
    # the constant part is reported as the offset (in lift units) like a lift table
    off_lift = float(np.mean(e_all))
    return e_all - off_lift, rot, off_lift


def _star(ang_deg):
    a = np.unwrap(np.radians(ang_deg))
    d = np.diff(a)
    return bool(np.all(d > 0) or np.all(d < 0))


def _rms(A):
    return float(np.sqrt(np.sum(np.asarray(A) ** 2) / 2)) if len(A) else 0.0


def compensate(project: dict, meas: dict, mfg: dict, lo: int, hi: int) -> dict:
    """Subtract orders lo..hi of the measured error from the motion and make the program again."""
    res = measure(project, meas)
    if not 1 <= lo <= hi <= res["harm"]["kmax"]:
        raise MeasureError("choose orders between 1 and the highest order")
    F = res["harm"]["F"]
    e_sel = from_orders(F, lo, hi, N)
    s = np.asarray(res["geo"]["s"])
    deg = res["deg"]
    corr = Program.from_dict({"unit": res["unit"], "table": {"deg": deg.tolist(), "s": (s - e_sel).tolist()}})
    out = M.manufacture(project, mfg, prog=corr)
    remaining = res["e"] - e_sel
    hr = harmonics(remaining, res["harm"]["kmax"])
    return {"measure": res, "mfg": out, "e_sel": e_sel, "remaining": remaining, "harm_after": hr, "lo": lo, "hi": hi}


def wheel_error(project: dict, mfg: dict, r_actual: float) -> dict:
    """Profile and lift error when a wheel dressed to r_actual runs the program made for the programmed radius."""
    if not r_actual or r_actual <= 0:
        raise MeasureError("give the actual wheel radius")
    out = M.manufacture(project, mfg, sim_R=r_actual)
    geo, m = out["geo"], out["mechanism"]
    flank = out["sim"]["flanks"][0]
    sf = out["surfaces"][0]
    # deviation per design point: nearest ray of the simulation
    P = np.asarray(geo["profile"])
    ang = np.mod(np.degrees(np.arctan2(P[1], P[0])), 360)
    ray = np.round(ang / 0.1).astype(int) % M.SIM_RAYS
    dn = flank["dev"][ray]
    gain = _lift_gain(geo, m.follower)
    idx = np.arange(0, P.shape[1], max(1, P.shape[1] // 360))
    del sf
    return {"deg": np.degrees(geo["theta"])[idx], "dn": dn[idx], "lift": (dn * gain)[idx], "mfg": out,
            "max_dn": float(np.nanmax(np.abs(dn)))}


def synthetic(project: dict, harmonics_list=None, shift_deg=1.5, offset=0.003, noise=0.0002, seed=1, step=0.5) -> str:
    """A made-up measured lift table (clearly synthetic) for the demonstration: design lift + known harmonics."""
    m = mechanism(project.get("mechanism"))
    prog = Program.from_dict(project.get("program") or {})
    hl = harmonics_list or [(1, 0.004, 30.0), (3, 0.002, -60.0), (17, 0.0008, 10.0)]
    n = int(round(360 / step))
    th = np.arange(n) * step
    s, _, _, _ = prog.eval(np.radians(th - shift_deg))
    e = sum(A * np.cos(np.radians(k * (th - shift_deg) + p)) for k, A, p in hl)
    rng = np.random.default_rng(seed)
    rad = prog.unit == "rad"
    val = s + offset + e + rng.normal(0, noise, n)
    if rad:  # a lift table of an oscillating follower is in degrees; the error amplitudes are then in mrad
        val = np.degrees(s + (offset + e + rng.normal(0, noise, n)) * 1e-3)
    del m
    head = "# SYNTHETIC DATA for the demonstration (合成数据，仅作演示): design lift + "
    head += ", ".join(f"order {k}: {A} at {p}°" for k, A, p in hl)
    head += f"; zero shifted {shift_deg}°, offset {offset}, noise {noise}\ncam_deg,lift\n"
    return head + "\n".join(f"{t:.3f},{v:.6f}" for t, v in zip(th, val, strict=True)) + "\n"


def _ck(cid, zh, en, value, limit, status, unit, note="", deg=None):
    nz = note.replace("give the allowed acceleration error", "请填许用加速度误差").replace("give the speed", "请填转速")
    return {"id": cid, "zh": zh, "en": en, "value": value, "limit": limit, "status": status, "unit": unit, "note": note,
            "note_zh": nz, "deg": deg}
