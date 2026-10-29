"""第 42 轮：FreeCAD 工作台的参数化对象——用一个假的 FreeCAD 模块把五种机型都建一遍、算一遍、导出导入一遍。"""
import importlib
import json
import sys
import types
from pathlib import Path

import pytest

FC = Path(__file__).resolve().parents[1] / "app" / "sewcore" / "freecad"


class Obj:
    def __init__(self, doc):
        self.__dict__["_p"] = {}
        self.__dict__["Document"] = doc
        self.__dict__["Label"] = ""

    def addProperty(self, kind, name, grp="", tip=""):
        self._p[name] = kind
        self.__dict__[name] = 0.0 if kind in ("App::PropertyFloat", "App::PropertyAngle") else ([] if kind == "App::PropertyLinkList" else "")

    def setEditorMode(self, *a):
        pass


class Doc:
    def __init__(self):
        self.objs = []

    def addObject(self, kind, name):
        o = Obj(self)
        self.objs.append(o)
        return o

    def recompute(self):
        for o in self.objs:
            if hasattr(o, "Proxy"):
                o.Proxy.execute(o)


@pytest.fixture
def feature(monkeypatch, tmp_path):
    app = types.ModuleType("FreeCAD")
    app.ActiveDocument = None
    app.newDocument = lambda name="": Doc()
    app.Console = types.SimpleNamespace(PrintError=print)
    monkeypatch.setitem(sys.modules, "FreeCAD", app)
    # 安装包里 sewcore 跟 wqsew_feature 同级；这里把网关的 app.sewcore 当成它
    from app import sewcore
    monkeypatch.setitem(sys.modules, "sewcore", sewcore)
    monkeypatch.setitem(sys.modules, "sewcore.cad", importlib.import_module("app.sewcore.cad"))
    monkeypatch.syspath_prepend(str(FC))
    sys.modules.pop("wqsew_feature", None)
    return importlib.import_module("wqsew_feature")


@pytest.mark.parametrize("m", ["cover", "pattern", "embroid", "flatknit"])
def test_build_compute_export_import(feature, tmp_path, m):
    doc = Doc()
    o = feature.add_design(doc, machine=m)
    assert o.Machine == m and o.Status == "全部合格"
    assert json.loads(o.ResultJson)["machine"] == m
    path = tmp_path / "p.json"
    feature.export_params(o, path)
    d = json.loads(path.read_text(encoding="utf-8"))
    assert d["machine"] == m
    if m == "pattern":
        d["params"].update(pat="csv", pts=[[0, 0], [3, 0], [6, 0], [16, 0], [19, 0]])
        path.write_text(json.dumps(d), encoding="utf-8")
        feature.import_params(o, path)
        assert o.P_pat == "csv" and json.loads(o.PatternPoints)[3] == [16.0, 0.0]
        assert json.loads(o.ResultJson)["params"]["pts"][3] == [16.0, 0.0]
    if m == "embroid":
        d["params"]["n"] = 800
        path.write_text(json.dumps(d), encoding="utf-8")
        feature.import_params(o, path)
        assert o.Status.startswith("不合格")
    other = feature.add_design(doc, machine="cover" if m != "cover" else "pattern")
    with pytest.raises(ValueError):
        feature.import_params(other, path)
