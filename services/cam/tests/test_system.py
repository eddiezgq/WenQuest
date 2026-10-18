"""Standard problems for cam systems, step 4b of round 39 (see docs/实施细则/第39轮, section 九).

Closed forms written out:
  - start, run, brake: constant acceleration over a1, run at ω, constant deceleration over a2:
        cycle time = (2·a1 + (2π − a1 − a2) + 2·a2) / ω
  - residual vibration of an undamped single degree of freedom after a cycloidal rise h in time T (base excitation,
    y″ + ω_n² y = −ψ̈, ψ̈ = (2πh/T²) sin(2πt/T)): with a = 2π/T,
        amplitude = h·a³·|sin(ω_n T/2)| / (π·ω_n·|a² − ω_n²|)
    (Duhamel's integral; zero when ω_n T/2 is a multiple of π other than at a = ω_n, as Norton shows for cycloidal
    motion)
  - over a cycle at constant speed with no load or friction the camshaft does no net work: ∮ T dθ = 0
"""

import json
import math
from pathlib import Path

import numpy as np
import pytest

from camkit import system as S

EX = Path(__file__).resolve().parents[1] / "examples"


def atc():
    return json.loads((EX / "atc-globoidal.json").read_text(encoding="utf-8"))


def test_start_run_brake_timing():
    for a1, a2 in ((0, 0), (15, 15), (30, 10)):
        th, t, thd, _, T = S.motion_time({"rpm": 60, "start_deg": a1, "stop_deg": a2})
        w = 2 * math.pi
        expect = (2 * math.radians(a1) + (2 * math.pi - math.radians(a1 + a2)) + 2 * math.radians(a2)) / w
        assert abs(T - expect) < 1e-12 and abs(t[-1] - T) < 1e-6
        assert np.all(np.diff(t) > 0) and abs(thd.max() - w) < 1e-9


@pytest.mark.parametrize("fn", [17.0, 37.0, 80.0])
def test_residual_vibration_cycloidal(fn):
    h, T = 0.5, 0.1
    wn, a = 2 * math.pi * fn, 2 * math.pi / T
    t = np.linspace(0, 0.5, 50001)
    acc = np.where(t <= T, (2 * math.pi * h / T**2) * np.sin(a * t), 0.0)
    y = S.sdof(t, acc, wn, 0.0)
    got = np.max(np.abs(y[t > T + 1e-9]))
    expect = h * a**3 * abs(math.sin(wn * T / 2)) / (math.pi * wn * abs(a * a - wn * wn))
    assert abs(got - expect) <= 1e-6 * h + 1e-6 * expect


def test_no_net_work_at_constant_speed():
    s = atc()
    s["camshaft"] |= {"start_deg": 0, "stop_deg": 0, "friction": 0}
    for c in s["cams"]:
        c["output"]["load"] = 0
    r = S.analyse(s)
    work = np.trapezoid(r["T_cs"], r["theta"])
    assert abs(work) < 1e-6 * np.max(np.abs(r["T_cs"])) * 2 * math.pi


def test_torque_of_one_output():
    """One rotating output J driven by a cycloidal index of h over β at constant ω: peak camshaft torque
    J·ψ′·ψ″·ω² with ψ′ = (h/β)(1 − cos 2πu), ψ″ = (2πh/β²) sin 2πu, found by scanning u."""
    J, h, beta, rpm = 0.5, math.radians(90), math.radians(120), 50
    s = {"camshaft": {"rpm": rpm}, "cams": [{"id": "a", "type": "disk", "program": {
        "unit": "rad", "advance_deg": 90,
        "segments": [{"kind": "rise", "deg": 120, "h_deg": 90, "law": "cycloidal"}, {"kind": "dwell", "deg": 240}]},
        "mechanism": {"follower": "oscillating", "contact": "roller", "rb": 40, "rr": 10, "a": 120, "L": 90},
        "output": {"J": J}}]}
    with pytest.raises(ValueError):
        S.analyse(s)  # an indexing program on an oscillating disk-cam follower is refused by the disk checks
    s["cams"][0]["type"] = "globoidal"
    s["cams"][0]["globoidal"] = {"C": 200, "n": 8, "Rp": 50, "rr": 10, "b": 20, "L": 100, "phase_deg": 22.5}
    r = S.analyse(s)
    u = np.linspace(0, 1, 200001)
    w = rpm * 2 * math.pi / 60
    T = J * (h / beta) * (1 - np.cos(2 * math.pi * u)) * (2 * math.pi * h / beta**2) * np.sin(2 * math.pi * u) * w * w
    assert abs(np.max(r["T_cs"]) - T.max()) / T.max() < 2e-3
    assert abs(np.min(r["T_cs"]) - T.min()) / T.max() < 2e-3


def test_interlocks():
    s = atc()
    r = S.analyse(s)
    ck = {c["id"]: c for c in r["checks"]}
    assert ck["lock_index_plunge"]["status"] == "pass" and ck["lock_plunge_index"]["status"] == "pass"
    # move the pull-out earlier by 20°: it now runs while the arm is still turning to grip
    seg = s["cams"][1]["program"]["segments"]
    seg[0]["deg"] -= 20
    seg[-1]["deg"] += 20
    r = S.analyse(s)
    ck = {c["id"]: c for c in r["checks"]}
    assert ck["lock_plunge_index"]["status"] == "fail" and ck["lock_plunge_index"]["bad"]
    a, b = ck["lock_plunge_index"]["bad"][0]
    assert 44 < a < 46 and 64 < b < 66


def test_atc_example():
    r = S.analyse(atc())
    ck = {c["id"]: c for c in r["checks"]}
    assert ck["motor_peak"]["status"] == "unknown"  # no motor rating given: unknown, never a pass
    assert 1.0 < r["cycle"] < 1.2
    idx = next(c for c in r["cams"] if c["id"] == "index")
    sub = {c["id"]: c for c in idx["checks"]}
    assert sub["undercut"]["status"] == "pass" and sub["pressure"]["status"] == "pass"
    assert sub["stress"]["status"] == "unknown" and sub["stress"]["value"] > 0
    assert idx["vib"] and all(d["tip_um"] >= 0 for d in idx["vib"])
    pl = next(c for c in r["cams"] if c["id"] == "plunge")
    assert {c["id"]: c for c in pl["checks"]}["phi_rise"]["status"] == "pass"
