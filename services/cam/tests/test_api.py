"""The web service of 问渠凸轮 (round 39, step 2): examples, analysis, base-circle search, errors in both
languages, and no infinity in JSON."""

from fastapi.testclient import TestClient

from app import app

c = client = TestClient(app)


def test_examples_and_laws():
    ex = c.get("/api/examples").json()
    assert {e["id"] for e in ex} == {"packaging-plate", "sewing-feed", "sewing-takeup-groove", "atc-globoidal"}
    assert {e["id"]: e["kind"] for e in ex}["atc-globoidal"] == "system"
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


def test_manufacture_measure_compensate_export():
    p = client.get("/api/examples/packaging-plate").json()
    p["mfg"] = {"process": "grind", "tool_r": 150}
    r = client.post("/api/manufacture", json={"project": p})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["program"].startswith("%") and d["sim"]["flanks"][0]["dev_um"]
    assert {c["id"]: c for c in d["checks"]}["sim"]["status"] == "pass"
    for kind in ("nc", "dxf", "csv", "step"):
        r = client.post(f"/api/export/{kind}", json={"project": p})
        assert r.status_code == 200, (kind, r.text)
        assert r.json()["text"]
    syn = client.post("/api/synthetic", json={"project": p}).json()["text"]
    p["measure"] = {"format": "lift", "data": syn, "a_allow": 5, "comp": {"lo": 1, "hi": 6}}
    m = client.post("/api/measure", json={"project": p}).json()
    assert m["err_unit"] == "µm" and abs(m["shift_deg"] - 1.5) < 0.01 and len(m["harm"]["A"]) == 60
    cp = client.post("/api/compensate", json={"project": p}).json()
    assert cp["rms_after"] < cp["rms_before"] and cp["mfg"]["program"]
    p["mfg"]["r_actual"] = 149.99
    w = client.post("/api/wheel-error", json={"project": p}).json()
    assert 9 < w["max_dn_um"] < 12  # 10 µm from the wheel plus up to the chord tolerance


def test_manufacture_errors_in_chinese():
    p = client.get("/api/examples/sewing-takeup-groove").json()
    p["mfg"] = {"process": "mill", "tool_r": 9}
    r = client.post("/api/manufacture", json={"project": p})
    assert r.status_code == 422 and "刀具比槽宽" in r.json()["detail"]["zh"]


def test_image_copies_every_service_module():
    """2026-10-18：镜像只拷了 app.py，新加的 system_api.py 没进镜像，线上 /cam/ 起不来（502）"""
    from pathlib import Path
    here = Path(__file__).resolve().parents[1]
    docker = (here / "Dockerfile").read_text(encoding="utf-8")
    mods = sorted(p.name for p in here.glob("*.py"))
    assert "COPY services/cam/*.py ./" in docker or all(f"services/cam/{m}" in docker for m in mods), mods
    # 构建上下文的白名单（Dockerfile.dockerignore）也要放行：只改 Dockerfile 时线上仍然缺 system_api.py
    ignore = (here / "Dockerfile.dockerignore").read_text(encoding="utf-8").splitlines()
    assert "!services/cam/*.py" in ignore or all(f"!services/cam/{m}" in ignore for m in mods), mods


def test_freecad_pack():
    """第 39 轮第 5 步：FreeCAD 工作台包——工作台（InitGui + wq_workbench）、凸轮页、camkit、示例项目、说明。"""
    import io
    import zipfile
    from pathlib import Path

    r = client.get("/api/freecad.zip")
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip"
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(z.namelist())
    root = "wenquest-cam-freecad/Mod/WenQuest/"
    for f in ("InitGui.py", "wq_workbench.py", "wq_cam.py", "wq_cam_drawing.py", "camkit/globoid_solid.py",
              "camkit/__init__.py", "examples/atc-globoidal.wqcam.json"):
        assert root + f in names, f
    assert not any("__pycache__" in n or n.endswith(".cae.wqcam.json") for n in names)
    here = Path(__file__).resolve().parents[1]
    assert {root + "camkit/" + f.name for f in (here / "camkit").glob("*.py")} <= names
    # the image gets the workbench files too (the build allow-list and the Dockerfile name them)
    ignore = (here / "Dockerfile.dockerignore").read_text(encoding="utf-8")
    docker = (here / "Dockerfile").read_text(encoding="utf-8")
    assert "!services/cam/freecad" in ignore and "wq_workbench.py" in ignore and "wq_workbench.py" in docker
