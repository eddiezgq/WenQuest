"""What the cam software asks the digital factory's CAE for (round 39, step 4d), and the gates in front of it.

The full round trip (cam service → hub design-software interface → CAE service: arm FEA, modal, fatigue, MuJoCo
dynamics) was run in development against the real CAE service; its results ship with the example
(examples/atc-globoidal.cae.json) and are checked here for what they must show. Tests do not reach the network.
"""

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

import cae_bridge as B
from app import app
from camkit import atc_arm as AR
from camkit import cae_setup as CS
from camkit import system as S

EX = Path(__file__).resolve().parents[1] / "examples"
FACES = json.loads((Path(__file__).parent / "arm_faces.json").read_text(encoding="utf-8"))["faces"]


def atc():
    return json.loads((EX / "atc-globoidal.json").read_text(encoding="utf-8"))


def test_mbd_model_matches_the_programs():
    p = atc()
    xml, setup, notes = CS.mbd_model(p)
    root = ET.fromstring(xml)
    joints = {j.get("name"): j.get("type") for j in root.iter("joint")}
    assert joints == {"camshaft": "hinge", "index": "hinge", "plunge": "slide"}
    r = S.analyse(p)
    # the camshaft's trapezoidal move = start, run, brake of camkit
    d = setup["drives"][0]
    assert d["joint"] == "camshaft" and abs(d["to"] - 2 * math.pi) < 1e-12 and abs(d["t1"] - r["cycle"]) < 1e-12
    w = 2 * math.pi / (d["t1"] * (1 - d["accel"]))
    assert abs(w - p["camshaft"]["rpm"] * 2 * math.pi / 60) < 1e-9
    # the coupling tables are the cams' programs; the lever's stroke is −radius·ψ (pulling down), in metres
    c = {x["follower"]: x for x in setup["couplings"]}
    th = np.radians(c["index"]["params"]["deg"])
    prog = next(x["program"] for x in r["cams"] if x["id"] == "index")
    assert np.allclose(c["index"]["params"]["value"], prog.eval(th)[0]) and abs(
        c["index"]["params"]["advance"] - math.pi) < 1e-12
    pl = next(x["program"] for x in r["cams"] if x["id"] == "plunge")
    assert np.allclose(c["plunge"]["params"]["value"], -0.3 * pl.eval(th)[0])
    assert notes["outputs"][1] == {"id": "plunge", "joint": "slide", "mass": 30.0, "radius_m": 0.3}


def test_compare_torque_with_itself():
    p = atc()
    q = dict(p, camshaft=dict(p["camshaft"], friction=0))
    r = S.analyse(q)
    t = np.linspace(0, r["cycle"], 400)
    vals = np.interp(t, r["t"], r["T_cs"])
    c = CS.compare_torque(p, vals.tolist(), r["cycle"])
    assert c["rel_rms"] < 1e-9 and abs(c["peak_mbd"] - c["peak_camkit"]) < 1e-9


def test_arm_loads_and_setup():
    p = atc()
    loads = CS.arm_loads(p, "index", 8.0, 150.0)
    r = S.analyse(p)
    cam = next(x for x in r["cams"] if x["id"] == "index")
    i = loads["i"]
    w = cam["s1"][i] * r["thd"][i]
    assert abs(loads["Ft_max"] - 8 * cam["acc"][i] * 0.15) < 1e-9 and abs(loads["Fc_max"] - 8 * w * w * 0.15) < 1e-9
    F = np.hypot(8 * cam["acc"] * 0.15, 8 * (cam["s1"] * r["thd"]) ** 2 * 0.15)
    assert loads["F_max"] == pytest.approx(np.max(F))
    st = CS.arm_fea_setup(FACES, AR.sizes(p["arm"]), loads, 8.0, "40Cr-QT")
    kinds = {x["type"]: x for x in st["loads"]}
    assert kinds["fixed"]["faces"] == [7]  # the bore
    forces = [x for x in st["loads"] if x["type"] == "force"]
    assert sorted(f["faces"][0] for f in forces) == [2, 4]
    for f in forces:  # equal and opposite in the plane, the tools' weight down on both
        assert f["vector_n"][2] == pytest.approx(-8 * 9.81, abs=1e-3)
    assert np.allclose(np.add(forces[0]["vector_n"][:2], forces[1]["vector_n"][:2]), 0, atol=1e-6)
    fb = CS.fatigue_body(loads, 500)
    assert fb["block_seconds"] == pytest.approx(172.8) and max(fb["series"]) == pytest.approx(1.0)
    with pytest.raises(CS.CaeSetupError):
        CS.fatigue_body(loads, 0)


def test_example_results():
    """What the precomputed example shows: MuJoCo and camkit agree on the camshaft torque within 5 %."""
    c = json.loads((EX / "atc-globoidal.cae.json").read_text(encoding="utf-8"))
    assert c["compare"]["compare"]["rel_rms"] < 0.05
    assert abs(c["compare"]["compare"]["peak_mbd"] - c["compare"]["compare"]["peak_camkit"]) / c["compare"]["compare"][
        "peak_camkit"] < 0.05
    st = c["arm"]["job"]["stats"]
    assert st["safety_factor"] > 1 and st["vm_max_mpa"] > 0
    assert c["modal"]["freqs"][0]["hz"] > 0 and "life_hours" in c["fatigue"]["summary"]
    assert c["note"]["zh"].startswith("示例结果")


def test_gates(monkeypatch):
    client = TestClient(app)
    p = atc()
    monkeypatch.delenv("WQ_FACTORY_URL", raising=False)
    monkeypatch.delenv("WQ_FACTORY_CAE_KEY", raising=False)
    assert client.get("/api/cae/me").json()["configured"] is False
    r = client.post("/api/cae/arm", json={"project": p})
    assert r.status_code == 503 and "还没有接上" in r.json()["detail"]["zh"]
    monkeypatch.setenv("WQ_FACTORY_URL", "http://factory.test")
    monkeypatch.setenv("WQ_FACTORY_CAE_KEY", "k")
    who = {"login": False, "licensed": False}
    monkeypatch.setattr(B, "identity", lambda req: dict(who))
    assert client.post("/api/cae/arm", json={"project": p}).status_code == 401
    who.update(login=True)
    assert client.post("/api/cae/arm", json={"project": p}).status_code == 403
    who.update(licensed=True, org="示例机床厂", user_id=7, name="张工")
    calls = []

    def hub(method, path, **kw):
        calls.append((method, path, kw))
        if path == "/geometry":
            return {"sha": "s1", "faces": FACES}
        return {"id": "j1", "status": "queued"}
    monkeypatch.setattr(B, "hub", hub)
    r = client.post("/api/cae/arm", json={"project": p})
    assert r.status_code == 200, r.text
    geo, fea = calls
    assert geo[2]["params"] == {"app": "cam", "org": "示例机床厂"} and geo[2]["content"].startswith(b"ISO-10303-21")
    body = fea[2]["json"]
    assert body["org"] == "示例机床厂" and body["user"] == "7" and body["app"] == "cam" and body["sha"] == "s1"
    assert client.get("/api/examples/atc-globoidal/cae").status_code == 200
    assert client.get("/api/examples/packaging-plate/cae").status_code == 404
