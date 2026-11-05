"""Process of the rolling elements and the tapered rings' own widths (round 64, plan section 二十, parts 1 and 3).
The templates' numbers are made up."""

import json
from pathlib import Path

import pytest

from bearingkit import drawing as D
from bearingkit import process as P
from bearingkit.analyze import geometry_of

EX = Path(__file__).resolve().parents[1] / "examples"


def load(name, sub=""):
    return json.loads((EX / sub / f"{name}.json").read_text(encoding="utf-8"))


def test_features_and_chains_of_each_element():
    kb, ball = P.element_features(geometry_of(load("demo-deep-groove")))
    kr, roll = P.element_features(geometry_of(load("scene-cylindrical")))
    taper = P.element_features(geometry_of(load("scene-tapered")))[1]
    assert kb == "ball" and [f["id"] for f in ball] == ["dia"]
    assert kr == "roller" and [f["id"] for f in roll] == ["dia", "length"]
    assert taper[0]["zh"] == "平均直径"
    # the tapered rings' widths are their own (plan 二十, part 1): cone B, cup C
    p = load("scene-tapered")
    p["size"].update(Bi=18, Co=15)
    fs = P.features(geometry_of(p))
    w = {r: next(f["size"] for f in fs[r] if f["id"] == "width") for r in ("inner", "outer")}
    assert w == {"inner": 18.0, "outer": 15.0}
    assert set(P.blank_template(geometry_of(p))["rings"]) == {"inner", "outer"}  # the rings' chain as before
    tb = P.element_template(geometry_of(load("demo-deep-groove")))["rings"]["element"]
    assert [o["name"]["zh"] for o in tb["ops"]][:5] == ["光球", "软磨", "热处理（淬火、回火）", "硬磨", "精研"]
    assert all(v is None for o in tb["ops"] for f in o["features"].values() for v in f.values())  # no numbers
    tr = P.element_template(geometry_of(load("scene-cylindrical")))["rings"]["element"]
    assert "超精外径（凸度）" in [o["name"]["zh"] for o in tr["ops"]]


def test_ball_worked_back_by_hand():
    t = load("element-ball", "process")
    r = P.run(geometry_of(load("demo-deep-groove")), t)
    assert r["status"] == "pass" and r["fictional"]
    rows = {x["no"]: x for x in r["rings"]["element"]["table"]["dia"]["rows"]}
    # lapping removes a set stock: before it the ball is 8.5005 + (Z − dz/2), its tolerance shrinks by dz
    assert rows[50]["mm"] == pytest.approx(8.5005) and rows[40]["mm"] == pytest.approx(8.5005 + 0.004 - 0.00015)
    # the first cut after heat treatment: Zmin = Z − (T before + scatter) − distortion
    assert rows[40]["Zmin"] == pytest.approx(0.06 - (0.01 + 0.006) - 0.01, abs=1e-12)
    # too little stock fails, a number left out is unknown
    bad = json.loads(json.dumps(t))
    next(o for o in bad["rings"]["element"]["ops"] if o["no"] == 40)["features"]["dia"]["Z"] = 0.02
    assert P.run(geometry_of(load("demo-deep-groove")), bad)["status"] == "fail"
    bad["rings"]["element"]["ops"][0]["features"]["dia"]["Z"] = None
    assert P.run(geometry_of(load("demo-deep-groove")), bad)["status"] in ("fail", "unknown")


def test_roller_example_and_sketches():
    g = geometry_of(load("scene-cylindrical"))
    r = P.run(g, load("element-roller", "process"))
    assert r["status"] == "pass"
    sk = D.sketches(g, r)
    assert [n for n, _ in sk] == ["element-op30-sketch.svg", "element-op40-sketch.svg", "element-op50-sketch.svg"]
    assert all(s.startswith("<svg") and "滚动体" in s for _n, s in sk)
    # the service gives the blank chain of the elements
    from fastapi.testclient import TestClient

    import app as service

    c = TestClient(service.app)
    r = c.post("/api/process/element-template", json={"project": load("scene-cylindrical")}).json()
    assert [f["id"] for f in r["features"]["element"]] == ["dia", "length"] and "element" in r["template"]["rings"]
    # the surfaces each operation works: the ends for the end grinding, the cylinder for the outside grinding
    segs = __import__("bearingkit.parts", fromlist=["parts"]).parts(g)["element"]
    assert D.feature_segments(segs, "element", "length", "cylindrical") and D.feature_segments(
        segs, "element", "dia", "cylindrical"
    )
