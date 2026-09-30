"""Round 4 · step 6: the published parts and robot library (digital factory, library-v2026.09.0) — its format is read,
robots get the fields the course tools use, and they work in 3D scenes and figures. Fixture: two real entries."""
import asyncio
import json
from pathlib import Path

import httpx

from app.library import Library, normalize_entry
from app.production import figures as F
from app.production import scene3d as S

ROOT = Path(__file__).parent / "data" / "library_real"


def handler(request: httpx.Request) -> httpx.Response:
    p = ROOT / request.url.path.lstrip("/")
    return httpx.Response(200, content=p.read_bytes()) if p.is_file() else httpx.Response(404)


def lib(tmp_path):
    return Library("https://factory.test", str(tmp_path), httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def test_index_entries_and_catalog(tmp_path):
    L = lib(tmp_path)
    idx = asyncio.run(L.index())                   # latest.json points at "library/2026.09.0/index.json"
    assert idx["version"] == "2026.09.0"
    rows = asyncio.run(L.entries())
    assert set(rows) == {"B-ARM-XARM7", "B-LEG-ANYMALB", "A-BRG-DG"}
    text = asyncio.run(L.catalog_text("轴承"))
    assert text.splitlines()[0].startswith("A-BRG-DG")          # asked-for words first
    assert asyncio.run(L.catalog_text("")).splitlines()[0].startswith("B-")   # otherwise robots first


def test_copy_normalises_a_real_arm(tmp_path):
    L = lib(tmp_path)
    rec = asyncio.run(L.copy_into(tmp_path / "assets", "B-ARM-XARM7"))
    assert rec["spec"] == "default" and {"default.glb", "default.png"} <= set(rec["files"]) and rec["license"]
    e = json.loads((tmp_path / "assets" / "B-ARM-XARM7" / "entry.json").read_text())
    assert len(e["joints"]) == 13 and all("lower" in j and "upper" in j for j in e["joints"])   # 7 arm joints + gripper
    # the tool point is the flange: the end of the chain of arm joints (the gripper hangs on it)
    assert e["root"] == e["links"][0] and e["tool"]["link"] == "link7"
    assert set(e["demo"]) == {j["name"] for j in e["joints"]}
    for j in e["joints"]:
        lo, hi = e["demo"][j["name"]]
        assert j["lower"] <= lo <= hi <= j["upper"]
    # in 3D: a joints scene with a tool trace
    models = S.load_models(tmp_path / "assets", ["B-ARM-XARM7"])
    sc = S.build({"template": "joints", "item": "B-ARM-XARM7", "poses": [{e["joints"][1]["name"]: 0.5}]}, models)
    assert sc["traces"] and {t["joint"] for t in sc["tracks"]} == {j["name"] for j in e["joints"]}
    # the rendered picture stands in for a drawing (the first phase has no drawings)
    out = F.render_picture(tmp_path / "assets" / "B-ARM-XARM7" / "default.png", tmp_path / "fig-1.png")
    assert (tmp_path / out["png"]).stat().st_size > 5000


def test_legged_robot_keeps_its_legs(tmp_path):
    raw = json.loads((ROOT / "library" / "2026.09.0" / "B-LEG-ANYMALB" / "entry.json").read_text())
    e = normalize_entry(raw)
    assert len(e["joints"]) == 12 and "tool" not in e
    assert all(abs(b - a) < 2 for a, b in e["demo"].values())    # leg joints swing, they do not spin
    wheels = normalize_entry({"robot": {"type": "mobile_base", "links": [{"name": "base", "node": "base"}, "w"],
                                        "joints": [{"name": "wheel_left", "type": "continuous", "parent": "base", "child": "w",
                                                    "axis": [0, 1, 0]}]}})
    assert wheels["demo"]["wheel_left"][1] > 6                   # wheels spin
    assert normalize_entry({"joints": [{"name": "x"}], "rest": {"x": 1}})["rest"] == {"x": 1}   # sample entries unchanged
    home = dict(raw, robot={**raw["robot"], "rest": {"LF_KFE": -1.2}})
    assert normalize_entry(home)["rest"]["LF_KFE"] == -1.2        # the library's own standing pose wins
