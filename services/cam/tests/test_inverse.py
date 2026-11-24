"""Importing a drawn outline and finding the follower motion from it (round 179, 细则第四节).

Round trip: the outline the kernel makes for a known motion is exported (DXF as the software writes it, or the point
table) and imported again; the motion found must match the one it came from. Six followers, both zero settings, the
errors a user meets, and the check that catches a follower that does not fit the outline."""

import io
import math

import ezdxf
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import app
from camkit import disk as D
from camkit import inverse as IV
from camkit import mfg as MF
from camkit.analyze import analyse, mechanism
from camkit.program import Program

client = TestClient(app)

SEG_MM = [{"kind": "rise", "deg": 120, "h": 12, "law": "cycloidal"}, {"kind": "dwell", "deg": 60},
          {"kind": "return", "deg": 120, "h": 12, "law": "poly345"}, {"kind": "dwell", "deg": 60}]
SEG_RAD = [{"kind": "rise", "deg": 120, "h_deg": 15, "law": "cycloidal"}, {"kind": "dwell", "deg": 60},
           {"kind": "return", "deg": 120, "h_deg": 15, "law": "poly345"}, {"kind": "dwell", "deg": 60}]
CASES = {
    "packaging-plate": ({"follower": "translating", "contact": "roller", "rb": 60, "rr": 15, "e": 10, "sigma": 1},
                        [{"kind": "rise", "deg": 100, "h": 40, "law": "cycloidal"}, {"kind": "dwell", "deg": 80},
                         {"kind": "return", "deg": 120, "h": 40, "law": "poly345"}, {"kind": "dwell", "deg": 60}]),
    "sewing-feed": ({"follower": "translating", "contact": "roller", "rb": 14, "rr": 3, "e": 0, "sigma": 1},
                    [{"kind": "rise", "deg": 150, "h": 4, "law": "mod_trapezoid"}, {"kind": "dwell", "deg": 30},
                     {"kind": "return", "deg": 150, "h": 4, "law": "mod_trapezoid"}, {"kind": "dwell", "deg": 30}]),
    "tr-knife": ({"follower": "translating", "contact": "knife", "rb": 40, "e": 5, "sigma": 1}, SEG_MM),
    "tr-flat": ({"follower": "translating", "contact": "flat", "rb": 40, "sigma": -1}, SEG_MM),
    "os-roller": ({"follower": "oscillating", "contact": "roller", "rb": 40, "rr": 10, "a": 100, "L": 80, "sigma": 1},
                  SEG_RAD),
    "os-flat": ({"follower": "oscillating", "contact": "flat", "rb": 40, "a": 100, "sigma": 1}, SEG_RAD),
    "os-knife": ({"follower": "oscillating", "contact": "knife", "rb": 40, "a": 100, "L": 80, "sigma": -1}, SEG_RAD),
}


def project(name):
    m, segs = CASES[name]
    return {"mechanism": dict(m), "program": {"unit": "rad" if m["follower"] == "oscillating" else "mm",
                                              "segments": segs}}


def exported(p, fmt):
    if fmt == "dxf":
        _, _, sfs, _ = MF.design(p)
        return MF.dxf(sfs[:1], 0.0002)
    return MF.point_table(p, 0.5)


@pytest.mark.parametrize("name,fmt", [("packaging-plate", "dxf"), ("packaging-plate", "xy"), ("sewing-feed", "dxf"),
                                      ("tr-knife", "xy"), ("tr-flat", "dxf"), ("os-roller", "xy"),
                                      ("os-flat", "xy"), ("os-knife", "dxf")])
def test_round_trip(name, fmt):
    p = project(name)
    out = IV.import_outline({"mechanism": p["mechanism"], "outline": {"format": fmt, "data": exported(p, fmt)}})
    r = out["report"]
    prog = Program.from_dict(p["program"])
    rad = prog.unit == "rad"
    sh = math.radians(r["shift_deg"])
    tb = out["program"]["table"]
    th = np.radians(np.array(tb["deg"]))
    s_true = prog.eval(th + sh)[0]
    s_imp = np.radians(tb["s_deg"]) if rad else np.array(tb["s"])
    # lift within 0.001 mm (oscillating 0.001°)
    assert np.abs(s_imp - s_true).max() * (180 / math.pi if rad else 1) <= 1e-3
    assert abs(r["rb"] - p["mechanism"]["rb"]) <= 1e-3
    # acceleration peak (smoothed) within 2 %
    a_true = np.abs(prog.eval(np.arange(3600) * math.pi / 1800 + sh)[2]).max() * (180 / math.pi if rad else 1)
    assert abs(r["acc"]["smooth_peak"] / a_true - 1) <= 0.02
    assert r["check"]["ok"] and r["check"]["max_dev"] < 1e-3
    # pressure angles from the full analysis within 0.05°
    a0 = {c["id"]: c for c in analyse(p)["checks"]}
    p2 = {"mechanism": out["mechanism"], "program": out["program"]}
    a1 = {c["id"]: c for c in analyse(p2)["checks"]}
    for k in ("phi_rise", "phi_return"):
        if a0[k]["value"] is not None:
            assert abs(a1[k]["value"] - a0[k]["value"]) <= 0.05, k


def test_zero_as_drawn():
    p = project("tr-knife")
    out = IV.import_outline({"mechanism": p["mechanism"],
                             "outline": {"format": "xy", "data": exported(p, "xy"), "zero": "drawing"}})
    assert out["report"]["shift_deg"] == 0
    tb = out["program"]["table"]
    s_true = Program.from_dict(p["program"]).eval(np.radians(np.array(tb["deg"])))[0]
    assert np.abs(np.array(tb["s"]) - s_true).max() <= 1e-3


def test_zero_at_the_rise_on_a_turned_drawing():
    """The drawing turned 40° (and moved off the origin, with the centre given): the rise is found within a degree
    and the motion is the same."""
    p = project("tr-knife")
    m = mechanism(p["mechanism"])
    P = np.asarray(D.analyse(m, Program.from_dict(p["program"]), 3600)["profile"])[:, ::4]
    a = math.radians(40)
    P = np.stack([math.cos(a) * P[0] - math.sin(a) * P[1] + 100, math.sin(a) * P[0] + math.cos(a) * P[1] - 50])
    text = "x,y\n" + "\n".join(f"{x:.6f},{y:.6f}" for x, y in P.T)
    out = IV.import_outline({"mechanism": p["mechanism"],
                             "outline": {"format": "xy", "data": text, "center": [100, -50], "zero": "rise"}})
    r = out["report"]
    turned = (360 - r["shift_deg"]) % 360  # σ = +1: the drawing is ahead by the turn
    assert abs(turned - 40) < 1.0
    assert r["check"]["ok"] and abs(r["lift"] - 12) < 1e-3


def _dxf(add):
    doc = ezdxf.new("R2010")
    add(doc.modelspace())
    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue()


def test_dxf_picks_the_outline_and_leaves_marks_out():
    """A drawing with a bore, centre lines and a note: the largest closed loop is the cam."""
    p = project("sewing-feed")
    P = np.asarray(D.analyse(mechanism(p["mechanism"]), Program.from_dict(p["program"]), 3600)["profile"])[:, ::5]

    def add(msp):
        msp.add_spline(fit_points=[(float(x), float(y)) for x, y in P.T] + [(float(P[0, 0]), float(P[1, 0]))])
        msp.add_circle((0, 0), 4)
        msp.add_line((-25, 0), (25, 0))
        msp.add_line((0, -25), (0, 25))
        msp.add_text("CAM")

    out = IV.import_outline({"mechanism": p["mechanism"], "outline": {"format": "dxf", "data": _dxf(add)}})
    src = out["report"]["source"]
    assert src["loops"] == 2 and src["ignored"] == {"open lines": 2, "TEXT": 1} and not src["spline"]
    assert abs(out["report"]["rb"] - 14) < 1e-3 and out["report"]["check"]["ok"]


def _err(outline, mech=None):
    r = client.post("/api/inverse", json={"project": {"mechanism": mech or CASES["tr-knife"][0], "outline": outline}})
    assert r.status_code == 422, r.text
    return r.json()["detail"]["zh"]


def test_errors_are_told_plainly():
    # an outline with a gap: two arcs that do not meet
    def gap(msp):
        msp.add_arc((0, 0), 40, 0, 170)
        msp.add_arc((0, 0), 40, 180, 360)
    assert _err({"format": "dxf", "data": _dxf(gap)}).startswith("廓线没有封闭：在 (")
    # only straight lines that never close
    def lines(msp):
        msp.add_line((0, 0), (10, 0))
        msp.add_line((20, 0), (30, 5))
    assert _err({"format": "dxf", "data": _dxf(lines)}) == "DXF 里的线连不成一条封闭的廓线"
    circ = "\n".join(f"{40 * math.cos(t) + 100:.4f}, {40 * math.sin(t):.4f}" for t in np.linspace(0, 6.2, 60))
    assert _err({"format": "xy", "data": circ}) == "回转中心不在廓线里面：请检查回转中心坐标"
    assert _err({"format": "xy", "data": "1, 2\n3, 4"}) == "廓线至少要 12 个点，每个点有 x、y"
    assert _err({"format": "dxf", "data": "not a drawing"}) == "读不了这个 DXF 文件"
    g = dict(CASES["sewing-feed"][0], groove=True)
    assert _err({"format": "xy", "data": circ}, g) == "导入廓线目前只做盘形凸轮外廓，槽凸轮以后再做"


def _dented(width):
    t = np.linspace(0, 2 * math.pi, 1440, endpoint=False)
    r = 40 - 4 * np.exp(-((np.mod(t - math.pi, 2 * math.pi) - math.pi) / width) ** 2)  # a hollow at 0°
    return "\n".join(f"{x:.6f}, {y:.6f}" for x, y in zip(r * np.cos(t), r * np.sin(t), strict=True))


def test_a_roller_too_large_for_a_hollow_is_caught():
    """A cam with a hollow a few millimetres across driven by a 15 mm roller: the roller bridges the hollow; the
    check finds the part of the outline it never touches. A small roller follows the hollow."""
    roller = {"follower": "translating", "contact": "roller", "sigma": 1}
    out = IV.import_outline({"mechanism": {**roller, "rr": 15}, "outline": {"format": "xy", "data": _dented(0.12)}})
    ck = out["report"]["check"]
    assert not ck["ok"] and ck["max_dev"] > 0.5 and ck["where"] == "outline"
    out = IV.import_outline({"mechanism": {**roller, "rr": 2}, "outline": {"format": "xy", "data": _dented(0.25)}})
    assert out["report"]["check"]["ok"]
    assert out["report"]["smooth"]["largest"] <= 1e-3  # auto smoothing never moves the lift by more than 1 µm


def test_api_and_the_example():
    ex = client.get("/api/examples/sewing-feed-outline").json()
    o = ex["outline"]
    r = client.post("/api/inverse", json={"project": {"mechanism": ex["mechanism"], "outline": {
        "format": o["format"], "data": o["data"], "center": [o["cx"], o["cy"]], "zero": o["zero"],
        "smooth": o["smooth"]}}})
    assert r.status_code == 200
    rep = r.json()["report"]
    assert rep["check"]["ok"] and abs(rep["rb"] - 14) < 1e-3 and abs(rep["lift"] - 4) < 1e-3
    assert r.json()["program"]["table"]["s"] == ex["program"]["table"]["s"]
    a = client.post("/api/analyse", json={"project": ex}).json()
    assert len(a["curves"]["deg"]) == 360
