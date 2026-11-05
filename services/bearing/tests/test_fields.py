"""FreeCAD form spec, drawings and operation sketches (round 64, step 6): the same fields and words as the web editor;
the drawings come from the same profiles as the solids. These run without FreeCAD."""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from bearingkit import drawing as D
from bearingkit import fields as FL
from bearingkit import process as P
from bearingkit.analyze import analyse, geometry_of

HERE = Path(__file__).resolve().parents[1]
WEB = HERE.parents[1] / "apps" / "bearing" / "src"
EX = HERE / "examples"
EXAMPLES = sorted(EX.glob("*.json"))


def web_paths():
    f = (WEB / "components" / "Fields.vue").read_text(encoding="utf-8")
    s = (WEB / "components" / "Scenario.vue").read_text(encoding="utf-8")
    paths = set(re.findall(r'v-model(?:\.\w+)?="project\.([\w.]+)"', f))
    paths |= {"scenario." + p for p in re.findall(r'v-model(?:\.\w+)?="s\.([\w.]+)"', s)}
    # fields the web editor sets without v-model: the type buttons, the crown table, the scenario picker and cases
    assert "project.type = k" in f and "project.profile.points" in f and "pick($event.target.value)" in s
    assert "project.flex.points" in f  # the cam point table (plan section 十八)
    return paths | {"type", "profile.points", "flex.points", "scenario.kind", "scenario.cases"}


def test_the_form_has_exactly_the_web_fields():
    spec = {f["path"] for _g, _w, fs in FL.GROUPS for f in fs}
    assert spec == web_paths()


def test_blank_and_fresh_scenarios_match_the_web():
    store = (WEB / "store.js").read_text(encoding="utf-8")
    for group, val in FL.BLANK.items():
        if isinstance(val, dict) and group != "title":
            line = re.search(rf"\b{group}: \{{([^}}]*)\}}", store).group(1)
            assert set(re.findall(r"(\w+):", line)) == set(val), group
    scen = (WEB / "components" / "Scenario.vue").read_text(encoding="utf-8")
    for kind, fresh in FL.FRESH.items():
        body = re.search(rf"\b{kind}: \(\) => \(\{{(.*)\}}\),?\n", scen).group(1)
        assert set(re.findall(r"\b(\w+):", body)) >= set(fresh), kind


def test_labels_are_the_web_words_and_up_to_date():
    run = subprocess.run([sys.executable, str(HERE / "tools" / "labels.py"), "--check"])
    assert run.returncode == 0, "run tools/labels.py: labels.json is behind apps/bearing/src/i18n.js"
    for _g, _w, fs in FL.GROUPS:
        for f in fs:
            assert f["key"] in FL.LABELS, f["key"]
            for _v, k in f["options"] or []:
                assert k is None or k in FL.LABELS, k
    assert FL.label("sk_hub") == "汽车轮毂" and FL.label("sk_hub", "en") == "Wheel hub"


def test_visibility_follows_the_web_editor():
    p = FL.blank()
    paths = lambda: {f["path"] for _g, fs in FL.visible(p) for f in fs}  # noqa: E731
    assert "inner.Pd" in paths() and "inner.alpha0_deg" not in paths() and "loads.Fr" in paths()
    p["type"] = "angular"
    assert "inner.alpha0_deg" in paths() and "pair.preload" not in paths() and "fits.shaft_I" not in paths()
    p["pair"]["arrangement"] = "DT"
    assert "pair.spacing" in paths() and "pair.preload" not in paths()
    p["type"] = "tapered"
    assert {"inner.alpha_o_deg", "inner.R_end", "profile.kind"} <= paths() and "inner.fi" not in paths()
    p["profile"]["kind"] = "partial"
    assert {"profile.R", "profile.flat"} <= paths()
    FL.set_scene(p, "joint")
    assert "loads.Fr" not in paths() and "scenario.x" in paths() and "scenario.r" not in paths()
    assert "scenario.fp" not in paths()
    p["scenario"]["axis"] = "vertical"
    assert "scenario.r" in paths() and "scenario.x" not in paths()
    FL.set_scene(p, "gearbox")
    assert p["scenario"] == FL.FRESH["gearbox"] and "scenario.cases" in paths()


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_files_round_trip_and_compute_the_same(path, tmp_path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    p = FL.normalise(raw)
    FL.save(p, tmp_path / "x.wqbearing.json")
    q = FL.load(tmp_path / "x.wqbearing.json")
    assert q == p
    a, b = analyse(raw), analyse(q)
    assert [(c["id"], c["status"], c["value"]) for c in a["checks"]] == [
        (c["id"], c["status"], c["value"]) for c in b["checks"]
    ]
    for _g, fs in FL.visible(p):  # every field the form shows can be read and written back unchanged
        for f in fs:
            v = FL.get(p, f["path"])
            FL.put(q, f["path"], v)
    assert q == p


def test_crown_points_text():
    rows = FL.parse_points("-5, 0.002\n0 0\n5; 0.002\nbad line\n")
    assert rows == [[-5.0, 0.002], [0.0, 0.0], [5.0, 0.002]]
    assert FL.parse_points(FL.points_text(rows)) == rows


@pytest.mark.parametrize("name", ["demo-deep-groove", "demo-angular", "scene-cylindrical", "scene-tapered"])
def test_part_sheets(name):
    g = geometry_of(json.loads((EX / f"{name}.json").read_text(encoding="utf-8")))
    for which in ("inner", "outer", "element"):
        svg = D.part_sheet(g, which, name)
        assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
        assert "未知" in svg and "技术要求" in svg
    inner = D.part_sheet(g, "inner")
    assert f"φ{g['d']:g}" in inner and f">{g['B']:g}<" in inner  # bore and width dimensions


def test_feature_segments_pick_the_right_surfaces():
    for name, kinds in (
        ("demo-deep-groove", {"race": 1}),
        ("scene-cylindrical", {"race": 1}),
        ("scene-tapered", {"race": 1}),
    ):
        g = geometry_of(json.loads((EX / f"{name}.json").read_text(encoding="utf-8")))
        from bearingkit import parts as PT

        pr = PT.parts(g)
        for ring, feats in P.features(g).items():
            segs = pr[ring]
            for f in feats:
                idx = D.feature_segments(segs, ring, f["id"], g["type"])
                assert idx, (name, ring, f["id"])
                if f["id"] == "width":
                    assert len(idx) == 2
                    continue
                s = segs[idx[0]]
                if f["id"] == "race" and s.get("arc"):  # groove bottom diameter
                    rc, rho = s["arc"]["c"][0], s["arc"]["rho"]
                    assert 2 * (rc - rho if ring == "inner" else rc + rho) == pytest.approx(f["size"])
                elif f["id"] == "race" and g["type"] == "tapered":
                    assert s["a"][0] + s["b"][0] == pytest.approx(f["size"])
                else:
                    assert 2 * s["a"][0] == pytest.approx(f["size"]), (name, ring, f["id"])
        assert kinds


def test_operation_sketches_follow_the_process():
    g = geometry_of(json.loads((EX / "demo-deep-groove.json").read_text(encoding="utf-8")))
    t = json.loads((EX / "process" / "demo-deep-groove.json").read_text(encoding="utf-8"))
    r = P.run(g, t)
    sk = dict(D.sketches(g, r, "demo"))
    cut_ops = [
        c
        for ring in r["rings"].values()
        for c in ring["cards"]
        if c["kind"] in ("grind", "superfinish", "cut") and c["lines"]
    ]
    assert len(sk) == len(cut_ops) == 9
    race = sk["inner-op50-sketch.svg"]
    line = next(x for c in r["rings"]["inner"]["cards"] if c["no"] == 50 for x in c["lines"])
    assert f"{line['size']['size']:.4f}" in race and "虚构" in race and "#c0392b" in race


def test_freecad_pack_and_workbench_registration(tmp_path, monkeypatch):
    """The download: the shared workbench files, the bearing page and form, bearingkit with labels.json, examples, a
    readme; and the workbench, run the way FreeCAD runs InitGui.py (separate globals and locals, no __file__), shows
    the bearing button next to the cam button and the button opens the bearing page."""
    import io
    import types
    import zipfile

    from fastapi.testclient import TestClient

    import app as A

    r = TestClient(A.app).get("/api/freecad.zip")
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip"
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(z.namelist())
    root = "wenquest-bearing-freecad/Mod/WenQuest/"
    for f in (
        "InitGui.py",
        "wq_workbench.py",
        "wq_bearing.py",
        "wq_bearing_form.py",
        "bearingkit/__init__.py",
        "bearingkit/labels.json",
        "bearingkit/fields.py",
        "bearingkit/drawing.py",
        "examples/scene-tapered.wqbearing.json",
        "examples/demo-deep-groove.wqprocess.json",
    ):
        assert root + f in names, f
    assert {root + "bearingkit/" + f.name for f in (HERE / "bearingkit").glob("*.py")} <= names
    assert not any("__pycache__" in n for n in names) and "wenquest-bearing-freecad/使用说明.txt" in names
    ignore = (HERE / "Dockerfile.dockerignore").read_text(encoding="utf-8")
    docker = (HERE / "Dockerfile").read_text(encoding="utf-8")
    assert "!services/bearing/freecad" in ignore and "wq_workbench.py" in ignore and "wq_workbench.py" in docker
    assert A.workbench_dirs(Path("/srv")) == [Path("/srv/freecad/workbench")]

    mod = tmp_path / "Mod" / "WenQuest"
    mod.mkdir(parents=True)
    for f in ("InitGui.py", "wq_workbench.py"):
        (mod / f).write_bytes(z.read(root + f))
    for m in ("wq_cam", "wq_bearing"):
        (mod / f"{m}.py").write_text("CALLED = []\ndef run_dialog():\n    CALLED.append(1)\n", encoding="utf-8")
    reg = {"cmds": {}, "wb": []}

    class Workbench:
        def appendToolbar(self, name, cmds):
            reg["toolbar"] = list(cmds)

        def appendMenu(self, name, cmds):
            reg["menu"] = list(cmds)

    gui = types.SimpleNamespace(
        Workbench=Workbench,
        addCommand=lambda n, c: reg["cmds"].__setitem__(n, c),
        addWorkbench=lambda w: reg["wb"].append(w),
    )
    monkeypatch.setitem(sys.modules, "FreeCADGui", gui)
    monkeypatch.setitem(sys.modules, "FreeCAD", types.SimpleNamespace())
    for m in ("wq_workbench", "wq_cam", "wq_bearing"):
        monkeypatch.delitem(sys.modules, m, raising=False)
    monkeypatch.setattr(sys, "path", [str(mod)] + list(sys.path))
    exec(
        compile((mod / "InitGui.py").read_text(encoding="utf-8"), "InitGui.py", "exec"),
        {"__builtins__": __builtins__},
        {},
    )
    assert list(reg["cmds"]) == ["WQ_Cam", "WQ_Bearing"] and len(reg["wb"]) == 1
    reg["wb"][0].Initialize()
    assert reg["toolbar"] == ["WQ_Cam", "WQ_Bearing"]
    reg["cmds"]["WQ_Bearing"].Activated()
    assert sys.modules["wq_bearing"].CALLED == [1]
