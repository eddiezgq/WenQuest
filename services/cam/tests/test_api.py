"""The web service of 问渠凸轮 (round 39, step 2): examples, analysis, base-circle search, errors in both
languages, and no infinity in JSON."""

from fastapi.testclient import TestClient

from app import app

c = TestClient(app)


def test_examples_and_laws():
    ex = c.get("/api/examples").json()
    assert {e["id"] for e in ex} == {"packaging-plate", "sewing-feed", "sewing-takeup-groove"}
    assert ex[0]["title"]["zh"].startswith("示例")
    assert c.get("/api/examples/../app").status_code == 404
    laws = {x["key"]: x for x in c.get("/api/laws").json()}
    assert laws["cycloidal"]["zh"] == "摆线（正弦加速度）" and abs(laws["cycloidal"]["Ca"] - 6.2832) < 1e-3


def test_analyse_and_search():
    p = c.get("/api/examples/packaging-plate").json()
    r = c.post("/api/analyse", json={"project": p}).json()
    assert r["status"] == "unknown" and len(r["curves"]["deg"]) == 360 and len(r["shapes"]["follower"][0]) == 360
    stress = {x["id"]: x for x in r["checks"]}["stress"]
    assert stress["status"] == "unknown" and stress["note_zh"] == "请填许用接触应力"
    s = c.post("/api/min-base-radius", json={"project": p}).json()
    assert 0 < s["rb"] < p["mechanism"]["rb"]


def test_errors_in_both_languages():
    bad = {
        "program": {"segments": [{"kind": "rise", "deg": 100, "h": 10}, {"kind": "return", "deg": 100, "h": 10}]},
        "mechanism": {"rb": 30, "rr": 5},
    }
    r = c.post("/api/analyse", json={"project": bad})
    assert r.status_code == 422 and r.json()["detail"]["zh"] == "各段转角加起来是 200.000°，不是 360°"
    assert c.post("/api/analyse", content=b"nope").status_code == 400
    groove = c.get("/api/examples/sewing-takeup-groove").json()
    groove["loads"] = {}
    r = c.post("/api/analyse", json={"project": groove}).json()
    assert {x["id"]: x for x in r["checks"]}["jump"]["status"] == "na"
