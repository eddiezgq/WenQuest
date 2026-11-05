"""Tapered roller bearings with three widths (round 64, plan section 二十, part 1): overall T, cone B, cup C. Only the
drawings, 3D, process and catalogue change; the checks do not. The example's widths are made up."""

import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app as service
from bearingkit import fields as FL
from bearingkit import parts as PT
from bearingkit import step3d as S
from bearingkit.analyze import analyse, geometry_of

EX = Path(__file__).resolve().parents[1] / "examples"
P = json.loads((EX / "scene-tapered.json").read_text(encoding="utf-8"))
P["size"].update(Bi=18, Co=15)  # made-up cone and cup widths on the tapered example


def zr(segs):
    zs = [x for s in segs for x in (s["a"][1], s["b"][1])]
    return min(zs), max(zs)


def test_three_widths_place_the_rings_and_leave_the_checks():
    one = copy.deepcopy(P)
    one["size"] = {k: P["size"][k] for k in ("d", "D", "B")}  # a file from before: one width
    a, b = analyse(one), analyse(P)
    assert [(c["id"], c["status"], c["value"]) for c in a["checks"]] == [
        (c["id"], c["status"], c["value"]) for c in b["checks"]
    ]
    T, Bi, Co = P["size"]["B"], P["size"]["Bi"], P["size"]["Co"]
    p3, p1 = PT.parts(geometry_of(P)), PT.parts(geometry_of(one))
    assert zr(p3["inner"]) == pytest.approx((T / 2 - Bi, T / 2)) and zr(p3["outer"]) == pytest.approx(
        (-T / 2, -T / 2 + Co)
    )
    assert zr(p1["inner"]) == pytest.approx((-T / 2, T / 2)) and zr(p1["outer"]) == pytest.approx((-T / 2, T / 2))
    assert S.volume(p3["inner"]) < S.volume(p1["inner"]) and S.volume(p3["outer"]) < S.volume(p1["outer"])
    # too narrow to carry the roller: refused, in Chinese at the service
    q = copy.deepcopy(P)
    q["size"]["Co"] = 12
    with pytest.raises(ValueError, match="too narrow"):
        PT.parts(geometry_of(q))
    r = TestClient(service.app).post("/api/parts/drawings", json=q)
    assert r.status_code == 422 and "盖不住整个滚子" in r.json()["detail"]["zh"]


def test_the_catalogue_fills_all_three():
    row = {"table": "metric", "model": "X30207", "d": "35", "D": "72", "T": "18.25", "B": "17", "C": "15", "page": "1"}
    p = FL.from_catalog(P, {"name": "示范（虚构）", "version": 1}, row)
    assert p["size"] == {"d": 35.0, "D": 72.0, "B": 18.25, "Bi": 17.0, "Co": 15.0}
    nu = FL.from_catalog(P, {"name": "示范（虚构）"}, {"table": "nu", "model": "N1", "d": "30", "D": "62", "B": "16"})
    assert nu["size"]["Bi"] is None and nu["size"]["B"] == 16.0
