"""Round 64 step 2: one project in, checks out; and the web API."""

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import app
from bearingkit.analyze import ProjectError, analyse

EX = Path(__file__).resolve().parents[1] / "examples"


def load(name):
    return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))


def by_id(r):
    return {c["id"]: c for c in r["checks"]}


@pytest.mark.parametrize("name", ["demo-deep-groove", "demo-angular"])
def test_examples_never_pass_without_ratings(name):
    r = analyse(load(name))
    c = by_id(r)
    assert c["C"]["status"] == "unknown" and c["C0"]["status"] == "unknown"
    assert r["status"] == "unknown"  # missing standard data is never a pass
    assert all(v["status"] != "fail" for v in r["checks"])


def test_angular_equilibrium():
    p = load("demo-angular")
    r = analyse(p)
    Q, al, psi = (np.array(r["balls"][k]) for k in ("Q", "alpha_deg", "psi_deg"))
    assert np.sum(Q * np.sin(np.radians(al))) == pytest.approx(p["loads"]["Fa"], rel=1e-5)  # rounded for the page
    assert np.sum(Q * np.cos(np.radians(al)) * np.cos(np.radians(psi))) == pytest.approx(p["loads"]["Fr"], rel=1e-5)


def test_missing_stress_limit_is_unknown():
    p = load("demo-deep-groove")
    del p["limits"]["p_max"]
    c = by_id(analyse(p))
    assert c["p_inner"]["status"] == "unknown" and c["p_outer"]["status"] == "unknown"


def test_missing_shoulder_is_unknown():
    p = load("demo-deep-groove")
    del p["inner"]["h_i"]
    assert by_id(analyse(p))["trunc_inner"]["status"] == "unknown"


def test_low_shoulder_truncates():
    p = load("demo-angular")
    p["inner"]["h_o"] = 0.4
    c = by_id(analyse(p))["trunc_outer"]
    assert c["status"] == "fail" and c["value"] > c["limit"]


def test_crowded_balls_fail():
    p = load("demo-deep-groove")
    p["inner"]["Z"] = 16  # the chord between ball centres 44·sin(π/16) = 8.58: 0.08 mm left, below the 1 mm asked
    c = by_id(analyse(p))["ball_gap"]
    assert c["value"] == pytest.approx(44 * math.sin(math.pi / 16) - 8.5)
    assert c["status"] == "fail"


def test_tight_fit_preloads_and_fails():
    p = load("demo-deep-groove")
    p["fits"]["shaft_I"] = 0.040
    r = analyse(p)
    c = by_id(r)["clearance"]
    assert c["value"] < 0 and c["status"] == "fail" and r["status"] == "fail"


def test_operating_clearance_drives_contact_angle():
    p = load("demo-deep-groove")
    r = analyse(p)
    op = r["chain"]["operating"]
    A = (0.515 + 0.525 - 1) * 8.5
    assert r["geometry"]["alpha_op_deg"] == pytest.approx(math.degrees(math.acos(1 - op / (2 * A))))


def test_no_loads_no_stress_check():
    p = load("demo-deep-groove")
    p["loads"] = {}
    r = analyse(p)
    c = by_id(r)
    assert c["qmax"]["status"] == "unknown" and "p_inner" not in c and c["film"]["status"] == "unknown"


@pytest.mark.parametrize("bad", [{"type": "roller"}, {"inner": {"Dw": 8.5, "Z": 10}}, {"size": {"d": 60}}])
def test_bad_projects(bad):
    p = load("demo-deep-groove")
    for k, v in bad.items():
        p[k] = v if k == "type" else {**p[k], **v} if k == "size" else v
    with pytest.raises(ProjectError):
        analyse(p)


client = TestClient(app)


def test_api():
    assert client.get("/api/health").json() == {"ok": True}
    ids = [e["id"] for e in client.get("/api/examples").json()]
    assert ids == ["demo-angular", "demo-deep-groove"]
    assert client.get("/api/examples/nope").status_code == 404
    assert client.get("/api/examples/..%2Fapp").status_code == 404
    r = client.post("/api/analyse", json={"project": load("demo-angular")})
    assert r.status_code == 200 and r.json()["status"] == "unknown"


def test_api_errors_in_chinese():
    p = copy.deepcopy(load("demo-deep-groove"))
    p["inner"]["fi"] = 0.7
    r = client.post("/api/analyse", json={"project": p})
    assert r.status_code == 422 and r.json()["detail"]["zh"].startswith("沟曲率半径系数")
    assert client.post("/api/analyse", content=b"[1]").status_code == 400


def test_angular_groove_bottoms():
    g = analyse(load("demo-angular"))["geometry"]
    A = (0.52 + 0.53 - 1) * 9
    assert g["do"] - g["di"] - 2 * 9 == pytest.approx(2 * A * (1 - math.cos(math.radians(25))))
    assert g["di"] < 54 - 9 and g["do"] > 54 + 9
