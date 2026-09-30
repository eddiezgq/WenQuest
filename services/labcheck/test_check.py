"""The lab checker against the house example and deliberately broken labs (needs Playwright + Chromium)."""
import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("playwright")
from fastapi.testclient import TestClient  # noqa: E402

import app as checker  # noqa: E402  (services/labcheck/app.py)

# The lab kit lives in the gateway (it builds the pages); load that one module by path.
_spec = importlib.util.spec_from_file_location(
    "gateway_labs", Path(__file__).resolve().parents[1] / "gateway" / "app" / "production" / "labs.py")
labs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(labs)

COURSE, CHAPTER = ["大学物理", "Physics"], ["第2章", "Chapter 2"]
EXAMPLE = labs.physics_example()
TECHNIQUE = labs.example_code()


def check(code: str) -> dict:
    page = labs.page([("2.1", code)], course=COURSE, chapter=CHAPTER)
    with TestClient(checker.app) as c:
        return c.post("/check", json={"html": page, "lab": "2-1"}).json()


def test_the_example_passes_with_a_picture():
    r = check(EXAMPLE)
    assert r["ok"], r["problems"]
    assert r["tasks"] == {"slide": True, "safe": True, "strap": True}
    assert r["screenshot"] and r["seconds"] < 60


def test_script_errors_are_caught():
    r = check(EXAMPLE.replace("s.xa += s.va * dt;", "s.xa += s.va * dt; undefinedThing.go();"))
    assert not r["ok"] and any("undefinedThing" in p for p in r["problems"])


def test_a_blank_picture_is_caught():
    r = check(EXAMPLE.replace("  draw(api, s) {", "  draw(api, s) { return;"))
    assert not r["ok"] and any("blank" in p for p in r["problems"])


def test_a_task_that_cannot_be_done_is_caught():
    r = check(EXAMPLE.replace('api.done("strap")', 'api.done("strap-typo")'))
    assert not r["ok"] and r["tasks"]["strap"] is False
    assert any("'strap'" in p for p in r["problems"])


def test_network_is_blocked():
    # The static check stops this before it runs; here the page itself must not reach anything either.
    code = EXAMPLE + "\nconst img = new Image(); img.src = 'ht' + 'tp://example.com/x.png';"
    r = check(code)
    assert not r["ok"]


def test_the_technique_example_passes_too():
    r = check(TECHNIQUE)
    assert r["ok"], r["problems"]
    assert r["tasks"] == {"reach": True, "slow": True, "life": True}


def _gateway_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "gateway" / "app" / "production" / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_3d_scene_renders_to_video(tmp_path):
    pytest.importorskip("trimesh")
    L = _gateway_module("gateway_library_sample", "library_sample.py")
    S = _gateway_module("gateway_scene3d", "scene3d.py")
    root = L.build(tmp_path)
    models = S.load_models(root / L.VERSION, ["B-ARM-6R-S"])
    script = S.joints("B-ARM-6R-S", models, [{"shoulder_pan": 1.0}], seg=0.6, captions=[[0, 2, ["转", "Turn"]]])
    with TestClient(checker.app) as c:
        r = c.post("/render3d", json={"html": S.page(script, models), "duration": 2.0, "fps": 10}).json()
    assert r["ok"], r.get("error")
    import base64
    video = base64.b64decode(r["video"])
    assert video[4:8] == b"ftyp" and len(r["frames"]) >= 2 and r["poster"]


def test_a_broken_scene_is_reported():
    with TestClient(checker.app) as c:
        r = c.post("/render3d", json={"html": "<html><script>window.FAIL='model missing'</script></html>", "duration": 1}).json()
    assert not r["ok"] and "model missing" in r["error"]
