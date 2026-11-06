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

    def purgeTouched(self):
        pass


class Doc:
    def __init__(self):
        self.objs = []

    def addObject(self, kind, name):
        o = Obj(self)
        o.__dict__["Name"] = "{}{:03d}".format(name, len(self.objs))
        o.__dict__["Kind"] = kind
        self.objs.append(o)
        return o

    def removeObject(self, name):
        for o in list(self.objs):
            if o.Name == name:
                self.objs.remove(o)
                o.__dict__["Document"] = None

    def recompute(self):
        for o in self.objs:
            if hasattr(o, "Proxy"):
                o.Proxy.execute(o)


class Vec:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def __sub__(self, o):
        return Vec(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, k):
        return Vec(self.x * k, self.y * k, self.z * k)

    @property
    def Length(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5


class Shape:
    """假的 Part 形体：记下是什么、由几块组成（够测“零件生成了、动了的才重建”）"""
    made = 0

    def __init__(self, kind, n=1):
        Shape.made += 1
        self.kind, self.n = kind, n

    def extrude(self, *a):
        return Shape("solid")

    def cut(self, *a):
        return self

    def toShape(self):
        return self


def fake_part():
    P = types.ModuleType("Part")
    P.makeCylinder = lambda *a: Shape("cyl")
    P.makeBox = lambda *a: Shape("box")
    P.makeSphere = lambda *a: Shape("sphere")
    P.makeCircle = lambda *a: Shape("edge")
    P.makeCompound = lambda xs: Shape("compound", len(xs))
    P.LineSegment = lambda *a: Shape("edge")
    P.Arc = lambda *a: Shape("edge")
    P.Wire = lambda *a: Shape("wire")
    P.Face = lambda *a: Shape("face")
    P.__sortEdges__ = lambda e: e
    return P


@pytest.fixture
def feature(monkeypatch, tmp_path):
    app = types.ModuleType("FreeCAD")
    app.ActiveDocument = None
    app.newDocument = lambda name="": Doc()
    app.Console = types.SimpleNamespace(PrintError=print, PrintWarning=print)
    app.Vector = Vec
    monkeypatch.setitem(sys.modules, "FreeCAD", app)
    monkeypatch.setitem(sys.modules, "Part", fake_part())
    # 安装包里 sewcore 跟 wqsew_feature 同级；这里把网关的 app.sewcore 当成它
    from app import sewcore
    monkeypatch.setitem(sys.modules, "sewcore", sewcore)
    monkeypatch.setitem(sys.modules, "sewcore.cad", importlib.import_module("app.sewcore.cad"))
    monkeypatch.setitem(sys.modules, "sewcore.hotspot", importlib.import_module("app.sewcore.hotspot"))
    monkeypatch.setitem(sys.modules, "sewcore.cad_seq", importlib.import_module("app.sewcore.cad_seq"))
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


# ---------- 第 94 轮：六种机型都有零件、能转、标红、双击停到出问题的地方 ----------
from app.sewcore import cad as CAD  # noqa: E402
from app.sewcore import cad_seq as CSQ  # noqa: E402

BAD = {"lockstitch": {"n": 6000}, "overlock": {"n": 9000}, "cover": {"dphi": 40}, "pattern": {"n": 3000},
       "embroid": {"n": 1400}, "flatknit": {"sys": 2, "xfer": 4, "rack": 4, "dwell": 0.01}}


@pytest.mark.parametrize("m", list(BAD))
def test_parts_for_every_machine_and_spin(feature, m):
    doc = Doc()
    o = feature.add_design(doc, machine=m)
    names = [q["name"] for q in CAD.parts3d({}, 0.0, m)["parts"]]
    assert [x.SewKey for x in o.Parts] == names                     # 零件和网页版样机、讲解片同一套
    assert all(isinstance(x.Shape, Shape) for x in o.Parts)
    assert [h["key"] for h in json.loads(o.HotJson)] == [c["key"] for c in json.loads(o.ResultJson)["checks"] if c["state"] == "warn"]   # 默认参数只有黄灯（包缝机教材算例上弯针传动角）
    whole = feature.span(o)
    if m in feature.SEQ:
        assert whole == CSQ.cfg_of(m, o.Proxy.params(o))[0]["n"] * 360
        assert o.Progress.startswith("第 1 ")
    else:
        assert whole == 360
    # 转一格：只重建动了的零件
    p = o.Proxy.params(o)
    Shape.made = 0
    o.Proxy.update_parts(o, p, 0.0)
    assert Shape.made == 0                                          # 转角没变，一个也不重建
    o.Proxy.update_parts(o, p, 400.0 if m in feature.SEQ else 40.0)
    assert 0 < Shape.made
    assert [x.SewKey for x in o.Parts] == names
    if m in feature.SEQ:
        assert o.Progress.startswith("第 2 ")


@pytest.mark.parametrize("m", list(BAD))
def test_red_parts_and_goto_spot(feature, m):
    from app import sewcore
    from app.sewcore import hotspot as HS
    doc = Doc()
    o = feature.add_design(doc, params=BAD[m], machine=m)
    R = sewcore.get(m).analyze(sewcore.get(m).clean(BAD[m]))
    want = [c["key"] for c in R["checks"] if c["state"] == "bad"] + [c["key"] for c in R["checks"] if c["state"] == "warn"]
    hs = feature.hotspots(o)
    assert [h["key"] for h in hs] == want and want
    col = o.Proxy.hot_colors(o)
    assert col and set(col) <= {x.SewKey for x in o.Parts}
    for h in hs:
        for n in h["names"]:
            if h["whole"]:                                          # 整机的项不涂色
                continue
            assert col[n] == feature.RED or (h["state"] == "warn" and col[n] in (feature.RED, feature.ORANGE))
    if m == "lockstitch":                                           # 6000 r/min：针杆惯性力红，只有刺布机构红，机壳共振不把整台涂红
        assert set(col) == set(next(h for h in hs if h["key"] == "needle_force")["names"])
    assert hs == HS.hotspots(m, BAD[m])                              # 和计算核心（网页版讲解片用的）一致
    h = next((h for h in hs if h["phi"] is not None), None)
    if h:
        assert feature.hotspot_of(o, h["key"]) == h
        o.Proxy.update_parts(o, o.Proxy.params(o), h["phi"])
        if m in feature.SEQ:
            unit = "趟" if m == "flatknit" else "针"
            assert o.Progress.startswith("第 {} {}".format(h["index"] + 1, unit))


@pytest.mark.parametrize("m", ["pattern", "flatknit", "lockstitch"])
def test_progress_angle_beyond_360_survives_recompute(feature, m):
    """审读：FreeCAD 的角度属性夹在 360° 以内——花样、刺绣、横机的进度角另存一个数，重算后还停在那一针"""
    doc = Doc()
    o = feature.add_design(doc, params=BAD[m], machine=m)
    h = next(h for h in feature.hotspots(o) if h["phi"] is not None)
    feature.set_phi(o, h["phi"])
    assert o.Phi == pytest.approx(h["phi"] % 360)
    assert feature.get_phi(o) == pytest.approx(h["phi"])
    doc.recompute()
    assert feature.get_phi(o) == pytest.approx(h["phi"])
    if m in feature.SEQ:
        assert o.Progress.startswith("第 {} ".format(h["index"] + 1))
