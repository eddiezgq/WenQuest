"""Round 4 · step 1: the parts and robot library (sample stand-in), copies into a course, sources in the lesson."""
import io
import json
import math

import numpy as np
import pytest

from app import main
from app.library import Library
from app.production import library_sample as L
from tests.test_materials import login
from tests.test_studio import _write_first_lesson, client, settle  # noqa: F401 - the fixture


@pytest.fixture(scope="module")
def lib_root(tmp_path_factory):
    return L.build(tmp_path_factory.mktemp("lib"))


def test_the_sample_library_has_the_published_layout(lib_root):
    latest = json.loads((lib_root / "latest.json").read_text())
    idx = json.loads((lib_root / latest["index"]).read_text())
    ids = {r["id"] for r in idx["items"]}
    assert {"B-ARM-6R-S", "B-SCA-4-S", "B-MOB-DIFF-S", "B-LEG-4-S", "B-HUM-S", "C-LNK-4BAR-S", "A-BRG-DG-S"} <= ids
    assert {r["spec"] for r in idx["items"] if r["id"] == "A-BRG-DG-S"} == {"6205", "6206", "6207"}
    for eid in ids:
        e = json.loads((lib_root / latest["version"] / eid / "entry.json").read_text())
        assert e["source"]["license"] and e["source"]["attribution"]
        links = set(e["links"])
        for j in e["joints"]:            # R4: joints name real links, with axis and origin
            assert j["parent"] in links and j["child"] in links and len(j["axis"]) == 3 and "xyz" in j["origin"]


def test_models_have_one_node_per_link(lib_root):
    import trimesh
    d = lib_root / L.VERSION / "B-ARM-6R-S"
    scene = trimesh.load(io.BytesIO((d / "default.glb").read_bytes()), file_type="glb")
    nodes = set(scene.graph.nodes)
    entry = json.loads((d / "entry.json").read_text())
    assert "zup" in nodes and set(entry["links"]) <= nodes
    assert "<svg" in (d / "default.svg").read_text()


def test_four_bar_motion_table_closes():
    fb = L.four_bar()
    for row in fb["motion"]:
        P = L.fk(fb, {k: row[k] for k in ("crank", "coupler", "rocker")})
        c1 = (P["coupler"] @ np.array([fb["defaults"]["b_mm"] / 1000, 0, 0, 1]))[:2]
        c2 = (P["rocker"] @ np.array([fb["defaults"]["c_mm"] / 1000, 0, 0, 1]))[:2]
        assert math.dist(c1, c2) < 1e-5


def test_library_reads_and_copies(tmp_path, lib_root):
    import asyncio
    lib = Library("", str(tmp_path))
    lib._sample_root = lambda: lib_root          # noqa: E731 - use the sample built above
    text = asyncio.run(lib.catalog_text("机械臂 移动机器人"))
    assert text.splitlines()[0].startswith(("B-ARM-6R-S", "B-MOB-DIFF-S"))
    rec = asyncio.run(lib.copy_into(tmp_path, "C-LNK-4BAR-S"))
    assert {"entry.json", "default.glb", "default.svg", "motion.csv"} <= set(rec["files"])
    assert (tmp_path / "C-LNK-4BAR-S" / "LICENSE-ATTRIBUTION.txt").exists()


def test_a_lesson_uses_library_entries_and_lists_its_sources(client, tmp_path, monkeypatch):
    monkeypatch.setattr(main.state.settings, "data_dir", str(tmp_path / "data"))
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    assert [x["id"] for x in p["design_book"]["library"]] == ["B-ARM-6R-S", "B-MOB-DIFF-S"]
    les = p["outline"]["chapters"][0]["lessons"][0]
    assert les["assets"] == ["B-ARM-6R-S"]           # the lecturer listed none: the course's platform
    a = next(x for x in p["assets"] if x["id"] == "B-ARM-6R-S")
    assert a["used_in"] == ["1.1"] and a["license"] == "Apache-2.0" and a["thumb"]
    assert client.get(a["thumb"]).text.startswith("<svg")
    assert "素材来源" in les["content"]["zh"] and "B-ARM-6R-S" in les["content"]["zh"]
    # the teacher adds one from the library and takes one out
    lib = client.get("/api/v1/studio/library?q=四杆", headers=h).json()
    assert [x["id"] for x in lib["items"]] == ["C-LNK-4BAR-S"] and lib["sample"] is True
    p = client.post(f"/api/v1/studio/projects/{pid}/assets/C-LNK-4BAR-S", headers=h).json()
    assert {x["id"] for x in p["assets"]} == {"B-ARM-6R-S", "C-LNK-4BAR-S"}
    assert client.post(f"/api/v1/studio/projects/{pid}/assets/B-NOPE-S", headers=h).status_code == 404
    p = client.delete(f"/api/v1/studio/projects/{pid}/assets/B-ARM-6R-S", headers=h).json()
    assert {x["id"] for x in p["assets"]} == {"C-LNK-4BAR-S"}
    assert [x["id"] for x in p["design_book"]["library"]] == ["B-MOB-DIFF-S"]
