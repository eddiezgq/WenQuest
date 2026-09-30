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
