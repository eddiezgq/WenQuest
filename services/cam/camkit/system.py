"""Cam systems (round 39, step 4b): several cams on one camshaft, the timing between them, the drive (motor →
reducer → camshaft, started and braked every cycle), the torque the camshaft needs, and the elastic dynamics of the
driven members (vibration left over in the dwells).

A system (dict):
    {"kind": "system",
     "camshaft": {"rpm": run speed, "J": own inertia kg·m², "friction": N·m, "start_deg": accelerating angle,
                  "stop_deg": braking angle},
     "drive": {"ratio": motor turns per camshaft turn, "eta": efficiency 0–1, "J_motor": kg·m² (motor side),
               "rated_Nm", "peak_Nm", "max_rpm": the motor's ratings (optional; empty = unknown)},
     "cams": [{"id", "name": {zh, en}, "type": "globoidal" | "disk", "program": {...},
               "globoidal": {...} | "mechanism": {...}, "material": {...}, "limits": {...},
               "output": {"J": kg·m² about the output axis (rotating) or "m": kg (translating),
                          "load": N·m or N (steady, against the motion), "radius": mm (lever / fork radius that turns
                          the output angle into a stroke, for reporting), "tip": mm (radius of the point whose
                          vibration matters, e.g. the tool gripper)},
               "elastic": {"fn": Hz natural frequency of the driven member on its drive, or "k": N·m/rad,
                           "zeta": damping ratio}}],
     "interlocks": [{"moving": cam id, "still": cam id, "gap_deg": smallest gap}],
     "limits": {"vib_um": allowed vibration at the tip in a dwell}}

Rigid model (camshaft angle θ, speed θ̇, acceleration θ̈):
    J_e(θ) = J_cs + Σ J_i ψ_i′²                          equivalent inertia at the camshaft
    T(θ)  = J_e θ̈ + ½ J_e′ θ̇² + Σ L_i ψ_i′ + T_friction  camshaft torque (Lagrange; Norton, Chen: cam drive torque)
    T_motor = T / (i η) + J_m i θ̈
Elastic model of each driven member (single degree of freedom on its drive, base excitation):
    y″ + 2ζω_n y′ + ω_n² y = −ψ̈(t),  y = ψ_actual − ψ_cam   (Norton, ch. on cam dynamics: residual vibration)
Plain code: no AI, no network. SI inside this module (rad, s, N·m, kg·m²) unless named otherwise.
"""

from __future__ import annotations

import math

import numpy as np

from camkit import analyze as A
from camkit import globoidal as G
from camkit.analyze import _num
from camkit.program import Program

PASS, FAIL, UNKNOWN, NA, INFO = "pass", "fail", "unknown", "na", "info"
N = 3600


class SystemError_(ValueError):
    pass


def _prog(c: dict) -> Program:
    return Program.from_dict(c.get("program") or {})


def motion_time(cs: dict, n: int = N):
    """Camshaft angle θ over time: constant acceleration from rest over start_deg, run at rpm, constant
    deceleration to rest over stop_deg (the brake). Returns θ grid (rad), t(θ), θ̇, θ̈, cycle time."""
    rpm = _num(cs.get("rpm"))
    if not rpm or rpm <= 0:
        raise SystemError_("give the camshaft speed")
    w = rpm * 2 * math.pi / 60
    a1 = math.radians(_num(cs.get("start_deg")) or 0.0)
    a2 = math.radians(_num(cs.get("stop_deg")) or 0.0)
    if a1 + a2 >= 2 * math.pi:
        raise SystemError_("starting and braking take more than a turn")
    th = np.linspace(0, 2 * math.pi, n + 1)
    acc1 = w * w / (2 * a1) if a1 > 0 else 0.0
    acc2 = w * w / (2 * a2) if a2 > 0 else 0.0
    t1 = w / acc1 if a1 > 0 else 0.0
    t2 = w / acc2 if a2 > 0 else 0.0
    run = 2 * math.pi - a1 - a2
    tr = run / w
    thd = np.empty_like(th)
    thdd = np.zeros_like(th)
    t = np.empty_like(th)
    m1 = th < a1
    thd[m1] = np.sqrt(2 * acc1 * th[m1]) if a1 > 0 else w
    t[m1] = thd[m1] / acc1 if a1 > 0 else 0.0
    thdd[m1] = acc1
    m2 = (th >= a1) & (th <= 2 * math.pi - a2)
    thd[m2] = w
    t[m2] = t1 + (th[m2] - a1) / w
    m3 = th > 2 * math.pi - a2
    rem = 2 * math.pi - th[m3]
    thd[m3] = np.sqrt(np.maximum(0.0, 2 * acc2 * rem))
    t[m3] = t1 + tr + (w - thd[m3]) / acc2 if a2 > 0 else t1 + tr
    thdd[m3] = -acc2
    return th, t, thd, thdd, t1 + tr + t2


def _output(c: dict, prog: Program) -> dict:
    o = c.get("output") or {}
    rot = prog.unit == "rad"
    J = _num(o.get("J"))
    m = _num(o.get("m"))
    if rot:
        if J is None:
            raise SystemError_(f"cam {c.get('id')}: give the inertia of what it turns")
        inertia = J
    else:
        if m is None:
            raise SystemError_(f"cam {c.get('id')}: give the mass of what it moves")
        inertia = m  # with ψ in m (s in mm × 1e-3)
    return {"inertia": inertia, "load": _num(o.get("load")) or 0.0, "scale": 1.0 if rot else 1e-3,
            "tip": _num(o.get("tip")), "radius": _num(o.get("radius"))}


def moving_mask(prog: Program, th: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    _, s1, _, _ = prog.eval(th)
    return np.abs(s1) > tol * max(1e-12, prog.lift())


def intervals(mask: np.ndarray, th_deg: np.ndarray) -> list[tuple[float, float]]:
    """Runs of True as (start°, end°)."""
    out = []
    n = len(mask)
    i = 0
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            out.append((float(th_deg[i]), float(th_deg[j])))
            i = j + 1
        else:
            i += 1
    return out


def sdof(t: np.ndarray, acc: np.ndarray, wn: float, zeta: float, cycles: int = 1) -> np.ndarray:
    """y(t) of y″ + 2ζω_n y′ + ω_n² y = −acc(t), from rest (the machine waits between cycles, so each starts at
    rest; cycles > 1 runs them back to back and returns the last). Exact solution for an input that is linear
    between samples (first-order hold)."""
    T = t[-1]
    tt = np.concatenate([t[:-1] + k * T for k in range(cycles)] + [[t[-1] + (cycles - 1) * T]])
    aa = np.concatenate([acc[:-1]] * cycles + [acc[-1:]])
    A_ = np.array([[0.0, 1.0], [-wn * wn, -2 * zeta * wn]])
    x = np.zeros(2)
    ys = np.empty(len(tt))
    ys[0] = 0.0
    from scipy.linalg import expm  # noqa: PLC0415

    cache = {}
    for k in range(1, len(tt)):
        h = tt[k] - tt[k - 1]
        key = round(h, 12)
        if key not in cache:
            # augmented matrix for x' = A x + B u, u linear over the step: [A B 0; 0 0 1/h; 0 0 0]
            M = np.zeros((4, 4))
            M[:2, :2] = A_
            M[:2, 2] = [0.0, -1.0]
            M[2, 3] = 1.0
            E = expm(M * h)
            cache[key] = (E[:2, :2], E[:2, 2], E[:2, 3] / h)
        Phi, G0, G1 = cache[key]
        u0, u1 = aa[k - 1], aa[k]
        x = Phi @ x + G0 * u0 + G1 * (u1 - u0)
        ys[k] = x[0]
    n = len(t)
    return ys[-n:]


def analyse(system: dict, quick: bool = False) -> dict:
    """quick: skip the slow checks of each cam (undercut search, contact stress) — used by the optimiser."""
    cs = system.get("camshaft") or {}
    dr = system.get("drive") or {}
    lim = system.get("limits") or {}
    cams = system.get("cams") or []
    if not cams:
        raise SystemError_("a cam system has at least one cam")
    ids = [c.get("id") for c in cams]
    if len(set(ids)) != len(ids) or not all(ids):
        raise SystemError_("every cam has its own id")
    th, t, thd, thdd, T_cycle = motion_time(cs)
    th_deg = np.degrees(th)
    checks = []
    per = []
    Je = np.full_like(th, _num(cs.get("J")) or 0.0)
    dJe = np.zeros_like(th)
    load_t = np.zeros_like(th)
    for c in cams:
        prog = _prog(c)
        o = _output(c, prog)
        s, s1, s2, _ = prog.eval(th)
        k = o["scale"]
        Je += o["inertia"] * (s1 * k) ** 2
        dJe += 2 * o["inertia"] * (s1 * k) * (s2 * k)
        load_t += o["load"] * s1 * k
        # the cam on its own: the same checks as a single cam, at the camshaft's run speed
        sub = _cam_checks(c, prog, cs, o, quick)
        # elastic dynamics: the motion of the output over time, the member on its drive
        acc = (s2 * thd**2 + s1 * thdd) * k
        el = c.get("elastic") or {}
        fn, kk, zeta = _num(el.get("fn")), _num(el.get("k")), _num(el.get("zeta"))
        wn = 2 * math.pi * fn if fn else (math.sqrt(kk / o["inertia"]) if kk else None)
        vib = None
        if wn:
            y = sdof(t, acc, wn, zeta if zeta is not None else 0.02)
            vib = _dwell_vibration(prog, th, th_deg, y, o)
        per.append({"id": c["id"], "name": c.get("name") or {"zh": c["id"], "en": c["id"]}, "type": c.get("type"),
                    "unit": prog.unit, "s": s, "s1": s1, "s2": s2, "acc": acc, "moving": moving_mask(prog, th),
                    "checks": sub["checks"], "sub": sub, "vib": vib, "wn": wn, "output": o, "program": prog})
    T_cs = Je * thdd + 0.5 * dJe * thd**2 + load_t + (_num(cs.get("friction")) or 0.0) * np.sign(thd + 1e-12)
    # interlocks
    for il in system.get("interlocks") or []:
        a = next((p for p in per if p["id"] == il.get("moving")), None)
        b = next((p for p in per if p["id"] == il.get("still")), None)
        if a is None or b is None:
            raise SystemError_("an interlock names a cam that is not in the system")
        both = a["moving"] & b["moving"]
        gap = _gap_deg(a["moving"], b["moving"], th_deg)
        need = _num(il.get("gap_deg")) or 0.0
        bad = intervals(both, th_deg)
        ok = (not both.any()) and gap >= need - 1e-9
        checks.append({"id": f"lock_{a['id']}_{b['id']}", "zh": f"联锁：{a['name']['zh']} 动时 {b['name']['zh']} 不动",
                       "en": f"Interlock: {b['name']['en']} still while {a['name']['en']} moves",
                       "value": round(gap, 3) if not both.any() else 0, "limit": need,
                       "status": PASS if ok else FAIL, "unit": "°",
                       "note": "" if ok else ("overlap " + ", ".join(f"{x:.1f}–{y:.1f}°" for x, y in bad) if bad
                                              else "gap smaller than required"),
                       "note_zh": "" if ok else ("重叠 " + "、".join(f"{x:.1f}–{y:.1f}°" for x, y in bad) if bad
                                                 else "间隔小于要求"),
                       "bad": bad})
    # motor
    i_r = _num(dr.get("ratio")) or 1.0
    eta = _num(dr.get("eta")) or 1.0
    Jm = _num(dr.get("J_motor")) or 0.0
    Tm = T_cs / (i_r * eta) * np.where(T_cs >= 0, 1.0, eta * eta) + Jm * i_r * thdd
    Tm_peak = float(np.max(np.abs(Tm)))
    dt = np.diff(t)
    Tm_rms = float(math.sqrt(np.sum(0.5 * (Tm[:-1] ** 2 + Tm[1:] ** 2) * dt) / T_cycle))
    rpm_motor = float(np.max(thd)) * 60 / (2 * math.pi) * i_r
    power = float(np.max(np.abs(T_cs * thd)))
    for cid, zh, en, val, key, unit in (
        ("motor_peak", "电机峰值转矩", "Motor peak torque", Tm_peak, "peak_Nm", "N·m"),
        ("motor_rms", "电机均方根转矩（按一次换刀）", "Motor RMS torque (one cycle)", Tm_rms, "rated_Nm", "N·m"),
        ("motor_speed", "电机转速", "Motor speed", rpm_motor, "max_rpm", "r/min"),
    ):
        limv = _num(dr.get(key))
        checks.append({"id": cid, "zh": zh, "en": en, "value": val, "limit": limv,
                       "status": UNKNOWN if limv is None else (PASS if val <= limv else FAIL), "unit": unit,
                       "note": "" if limv is not None else "give the motor's rating",
                       "note_zh": "" if limv is not None else "请填电机额定值"})
    checks.append({"id": "power", "zh": "凸轮轴峰值功率", "en": "Camshaft peak power", "value": power, "limit": None,
                   "status": INFO, "unit": "W", "note": "", "note_zh": ""})
    checks.append({"id": "cycle", "zh": "一次循环时间（起动到制动停住）", "en": "Cycle time (start to stop)",
                   "value": T_cycle, "limit": _num(lim.get("cycle_s")),
                   "status": INFO if _num(lim.get("cycle_s")) is None else (
                       PASS if T_cycle <= _num(lim.get("cycle_s")) else FAIL), "unit": "s", "note": "", "note_zh": ""})
    vlim = _num(lim.get("vib_um"))
    for p in per:
        if p["vib"] is None:
            checks.append({"id": f"vib_{p['id']}", "zh": f"{p['name']['zh']}：停歇时的残余振动",
                           "en": f"{p['name']['en']}: vibration in the dwells", "value": None, "limit": vlim,
                           "status": UNKNOWN, "unit": "µm", "note": "give the natural frequency or stiffness",
                           "note_zh": "请填固有频率或刚度"})
            continue
        worst = max((d["tip_um"] for d in p["vib"] if d["tip_um"] is not None), default=None)
        checks.append({"id": f"vib_{p['id']}", "zh": f"{p['name']['zh']}：停歇时端部残余振动",
                       "en": f"{p['name']['en']}: tip vibration in the dwells", "value": worst, "limit": vlim,
                       "status": UNKNOWN if (vlim is None or worst is None) else (PASS if worst <= vlim else FAIL),
                       "unit": "µm", "note": "" if vlim is not None else "give the allowed vibration",
                       "note_zh": "" if vlim is not None else "请填允许的残余振动"})
    status = FAIL if any(c["status"] == FAIL for c in checks + [x for p in per for x in p["checks"]]) else (
        UNKNOWN if any(c["status"] == UNKNOWN for c in checks + [x for p in per for x in p["checks"]]) else PASS)
    return {"status": status, "checks": checks, "cams": per, "theta": th, "deg": th_deg, "t": t, "thd": thd,
            "thdd": thdd, "cycle": T_cycle, "Je": Je, "T_cs": T_cs, "T_motor": Tm, "ratio": i_r}


def _gap_deg(a: np.ndarray, b: np.ndarray, th_deg: np.ndarray) -> float:
    """Smallest angle between a motion of a and a motion of b (0 if they overlap), around the cycle."""
    ia, ib = np.flatnonzero(a), np.flatnonzero(b)
    if not len(ia) or not len(ib):
        return 360.0
    step = th_deg[1] - th_deg[0]
    da = np.abs(ia[:, None] - ib[None, :])
    n = len(th_deg) - 1
    d = np.minimum(da, n - da).min()
    return max(0.0, (d - 1) * step)


def _dwell_vibration(prog, th, th_deg, y, o):
    """Largest |y| in each dwell of the output (after it stops), as angle and as displacement at the tip."""
    mov = moving_mask(prog, th)
    out = []
    for a, b in intervals(~mov, th_deg):
        sel = (th_deg >= a) & (th_deg <= b)
        amp = float(np.max(np.abs(y[sel])))
        tip = o["tip"]
        if prog.unit == "rad":
            tip_um = amp * tip * 1e3 if tip else None
            val = math.degrees(amp) * 3600  # arc-seconds
        else:
            tip_um = amp * 1e6
            val = amp * 1e6
        out.append({"from": a, "to": b, "amp": val, "tip_um": tip_um})
    return out


def _cam_checks(c: dict, prog: Program, cs: dict, o: dict, quick: bool = False) -> dict:
    """The cam's own checks at the run speed (pressure angle, undercut, contact stress …)."""
    rpm = _num(cs.get("rpm"))
    if c.get("type") == "globoidal":
        r = G.analyse({"program": c.get("program"), "globoidal": c.get("globoidal"), "limits": c.get("limits")},
                      undercut_check=not quick)
        stress = None if quick else _globoid_stress(c, prog, rpm, o)
        if stress is not None:
            r["checks"].append(stress)
        return r
    sub = {"program": c.get("program"), "mechanism": c.get("mechanism"), "material": c.get("material"),
           "limits": c.get("limits"), "loads": {"rpm": rpm}}
    if prog.unit == "rad":
        sub["loads"]["inertia"] = o["inertia"]
        sub["loads"]["load"] = o["load"] * 1e3  # N·m → N·mm
    else:
        sub["loads"]["mass"] = o["inertia"]
        sub["loads"]["load"] = o["load"]
    return A.analyse(sub, n=720 if quick else 1440, out_n=361)


def _globoid_stress(c, prog, rpm, o):
    """Hertz line contact between the loaded roller and the rib at the pitch radius, at the run speed. The output
    torque is J ψ″ω² + load; one roller carries it (the one with the smallest pressure angle)."""
    mat = c.get("material") or {}
    E1, n1, E2, n2 = (_num(mat.get(k)) for k in ("E1", "nu1", "E2", "nu2"))
    lim = _num((c.get("limits") or {}).get("stress"))
    if None in (E1, n1, E2, n2) or not rpm:
        return {"id": "stress", "zh": "滚子与凸轮筋最大接触应力", "en": "Peak roller–rib contact stress", "value": None,
                "limit": lim, "status": UNKNOWN, "unit": "MPa", "note": "give the materials and the speed",
                "note_zh": "请填材料和转速"}
    g = G.globoid(c.get("globoidal"))
    m = 720
    th = np.linspace(0, 2 * math.pi, m, endpoint=False)
    phi, dphi, ddphi, _ = prog.eval(th)
    w = rpm * 2 * math.pi / 60
    T = o["inertia"] * ddphi * w * w + o["load"] * np.sign(dphi + 1e-15)  # N·m at the turret
    sfs = G.surfaces(g, prog, m=m, k=9)
    ang = G.roller_angles(g, phi)
    on = G.engaged(g, ang, g.Rp)
    alpha = np.where(on, np.arctan2(np.abs(g.Rp * g.hand * dphi)[None, :], g.C - g.Rp * np.cos(ang)), np.inf)
    best = np.argmin(alpha, axis=0)
    a_best = alpha[best, np.arange(m)]
    F = np.abs(T) / (g.Rp * 1e-3 * np.cos(np.minimum(a_best, 1.5)))  # N
    # flank curvature at the pitch radius of the loaded roller, on the side that is pushed
    kap = np.zeros(m)
    for j in range(m):
        side = 1 if T[j] * g.hand >= 0 else -1
        sf = next(s for s in sfs if s["roller"] == best[j] and s["side"] == side)
        kap[j] = G.flank_curvature(sf)[j, 4]
    Estar = 1 / ((1 - n1**2) / E1 + (1 - n2**2) / E2)
    curv = 1 / g.rr + kap  # 1/mm
    sig = np.sqrt(np.maximum(0.0, F * curv * Estar / (math.pi * g.b)))
    j = int(np.argmax(sig))
    peak = float(sig[j])
    return {"id": "stress", "zh": "滚子与凸轮筋最大接触应力", "en": "Peak roller–rib contact stress", "value": peak,
            "limit": lim, "status": UNKNOWN if lim is None else (PASS if peak <= lim else FAIL), "unit": "MPa",
            "note": "" if lim is not None else "give the allowed contact stress",
            "note_zh": "" if lim is not None else "请填许用接触应力", "deg": float(np.degrees(th[j])),
            "force_N": float(F[j])}
