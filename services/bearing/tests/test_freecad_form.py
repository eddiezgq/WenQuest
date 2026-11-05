"""The FreeCAD form itself (round 64, step 6a′), driven with Qt off screen. Skipped where PySide6 is not installed
(CI); run locally with the Python that comes with FreeCAD:  QT_QPA_PLATFORM=offscreen <freecad>/bin/python -m pytest
tests/test_freecad_form.py"""

import json
import os
import sys
from pathlib import Path

import pytest

QtWidgets = pytest.importorskip("PySide6.QtWidgets")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

HERE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HERE), str(HERE / "freecad")]

from bearingkit import fields as FL  # noqa: E402
from bearingkit.analyze import analyse  # noqa: E402

import wq_bearing_form as WF  # noqa: E402

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
EX = HERE / "examples"


def settle():
    for _ in range(3):
        app.processEvents()


def shown_paths(form):
    return {path for path, _key in form.widgets}


@pytest.mark.parametrize("path", sorted(EX.glob("*.json")), ids=lambda p: p.stem)
def test_open_example_shows_its_fields_and_the_same_checks(path, tmp_path):
    form = WF.Form()
    form.open_file(str(path))
    settle()
    want = {f["path"] for _g, fs in FL.visible(form.project) for f in fs}
    assert shown_paths(form) == want
    raw = json.loads(path.read_text(encoding="utf-8"))
    res = analyse(raw)
    assert form.table.rowCount() == len(res["checks"])
    assert form.table.item(0, 0).text() == res["checks"][0]["zh"]
    form.save_file(str(tmp_path / "a.wqbearing.json"))
    assert FL.load(str(tmp_path / "a.wqbearing.json")) == FL.normalise(raw)


def test_design_from_scratch_in_the_form(tmp_path):
    form = WF.Form()
    settle()
    vals = {"size.d": "30", "size.D": "58", "size.B": "16", "inner.Dw": "9", "inner.Z": "10", "inner.fi": "0.515",
            "inner.fo": "0.525", "inner.Pd": "0.012", "inner.h_i": "1.8", "inner.h_o": "1.8", "loads.Fr": "4000",
            "loads.n": "3000"}
    for (path, _key), w in list(form.widgets.items()):
        if path in vals:
            w.setText(vals[path])
            w.editingFinished.emit()
    settle()
    assert form.project["size"]["d"] == 30 and form.project["inner"]["Z"] == 10
    assert isinstance(form.project["inner"]["Z"], int)
    res = form.calculate()
    assert res and res["status"] in ("pass", "unknown", "fail") and form.table.rowCount() == len(res["checks"])
    # the same project typed into the web editor's store: identical result
    p = FL.blank()
    for k, v in vals.items():
        FL.put(p, k, float(v) if k != "inner.Z" else int(v))
    assert [c["value"] for c in analyse(p)["checks"]] == [c["value"] for c in res["checks"]]
    form.save_file(str(tmp_path / "b.wqbearing.json"))
    saved = json.loads((tmp_path / "b.wqbearing.json").read_text(encoding="utf-8"))
    assert saved["size"] == {"d": 30.0, "D": 58.0, "B": 16.0} and saved["type"] == "deep_groove"


def test_switching_type_and_scenario_rebuilds_the_form():
    form = WF.Form()
    settle()
    combo = form.widgets[("type", "type")]
    combo.setCurrentIndex(combo.findData("tapered"))
    settle()
    assert form.project["type"] == "tapered" and ("inner.alpha_o_deg", "cupAngle") in form.widgets
    scen = form.widgets[("scenario.kind", "sceneKind")]
    scen.setCurrentIndex(scen.findData("spindle"))
    settle()
    assert form.project["scenario"] == FL.FRESH["spindle"]
    assert ("scenario.cases", "cases") in form.widgets and ("loads.Fr", "Fr") not in form.widgets
    form._add_case()
    settle()
    assert len(form.project["scenario"]["cases"]) == 2 and form.cases_table.rowCount() == 2
    form.cases_table.item(1, 1).setText("1500")
    assert form.project["scenario"]["cases"][1]["Fr"] == 1500
    bad = form.widgets[("scenario.a", "overhang")]
    bad.setText("abc")
    bad.editingFinished.emit()
    assert bad.text() == "" and form.project["scenario"]["a"] is None  # not a number: refused, nothing stored


def test_a_model_from_the_company_catalogue(tmp_path):
    """产品库：选一个型号，外形尺寸填好、内部尺寸清空，说明里写出出处（虚构目录）。"""
    from test_catalog import series

    form = WF.Form(json.loads((EX / "scene-tapered.json").read_text(encoding="utf-8")))
    cat = {"name": "示范厂目录（虚构）", "version": 1, "rows": series()}
    form.use_catalog(cat, series()[2])
    settle()
    assert form.project["size"]["d"] == 30.0 and form.project["inner"]["Dw"] is None
    assert "88002" in form.note.text() and "算不出来" in form.verdict.text()
    assert form.title.text() == "88002"
