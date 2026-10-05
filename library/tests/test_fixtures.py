# -*- coding: utf-8 -*-
"""第 13 轮 8.7：E 部分“工装夹具”——每个条目都能造出模型；零件表与节点一一对应、序号与爆炸方向齐全；
模型与教材、数字工厂用的是同一个函数（JJ-301-50 的尺寸与夹具设计数据一致）；编号能被各处识别。"""
import re

import pytest

import wqlib

pytest.importorskip("build123d")
from generators import e_fixture as F  # noqa: E402

E = [e for e in wqlib.entries() if e["id"].startswith("E-")]


def nodes(e):
    return F.build(e, next(iter(wqlib.specs(e))))


def test_part_e_registered():
    assert set(wqlib.CATEGORY_NAMES["E"]) == {"LOC", "CLP", "GDE", "BAS", "ACC", "ASM", "WKP"}
    assert len(E) >= 50
    for e in E:
        assert e["model"]["engine"].startswith("wqfix:")
        assert e["kind"] == ("case" if e["category"] in ("ASM", "WKP") else "product")
        assert "以所用标准为准" in e["model"]["note"]          # 尺寸不冒称标准表
        assert any(c["course"] == "机械制造技术" for c in e["teaching"]["courses"])


@pytest.mark.parametrize("eid", [e["id"] for e in E])
def test_every_entry_builds(eid):
    e = next(x for x in E if x["id"] == eid)
    ns = nodes(e)
    assert ns, eid
    metas = [s._wq["meta"] for _, s in ns]
    assert [m["node"] for m in metas] == [n for n, _ in ns] == [f"p{i + 1:02d}" for i in range(len(ns))]
    for _, s in ns:
        bb = s.bounding_box()
        assert bb.size.X > 0 and bb.size.Y > 0 and bb.size.Z > 0, eid
        assert len(s._wq["rgba"]) == 4
    for m in metas:
        assert m["name"] and not re.fullmatch(r"[a-z_]+", m["name"]), (eid, m["name"])   # 零件名用中文
        assert len(m["explode_mm"]) == 3


def test_assemblies_have_numbers_roles_and_explode():
    for e in E:
        if e["category"] != "ASM":
            continue
        metas = [s._wq["meta"] for _, s in nodes(e)]
        assert len(metas) >= 3, e["id"]
        assert any(m["role"] == "工件" for m in metas), e["id"]
        # 定位面常做在夹具体、钻模板里（盖板式、翻转式钻模，双向联动夹紧），不一定有单独的定位元件；至少有两类作用
        assert len({m["role"] for m in metas} - {"工件", "其他"}) >= 2, e["id"]
        assert sum(1 for m in metas if any(m["explode_mm"])) >= len(metas) // 2, e["id"]


def test_jj30150_same_model_as_book():
    """零件库的 JJ-301-50 与教材、数字工厂调用同一个函数，节点与装配体零件一一对应，几何相同"""
    from models3d import jj30150 as J
    e = next(x for x in E if x["id"] == "E-ASM-JJ30150")
    ns = nodes(e)
    asm = J.assembly("op40", with_work=True)
    assert [s._wq["meta"]["name"] for _, s in ns] == [p.name for p in asm.parts]
    for (_, s), p in zip(ns, asm.parts):
        assert abs(s.volume - p.shape.volume) < 1e-6 * max(1.0, p.shape.volume)
    roles = {s._wq["meta"]["name"]: s._wq["meta"]["role"] for _, s in ns}
    assert roles["V 形块"] == "定位" and roles["压板1"] == "夹紧" and roles["对刀块"] == "对刀导向"
    assert roles["定位键1"] == "夹具体" and roles["工件 SH-301"] == "工件"
    g = J.geometry()                                   # 工件轴线高度 = V 形块定位高度（夹具设计数据）
    vb = next(s for _, s in ns if s._wq["meta"]["name"] == "V 形块").bounding_box()
    work = next(s for _, s in ns if s._wq["meta"]["name"] == "工件 SH-301").bounding_box()
    assert abs((work.min.Z + work.max.Z) / 2 - g["zc"]) < 0.05
    assert abs(work.min.Z - (g["zc"] - g["d_g"] / 2)) < 0.05          # 齿轮位 Ø40.3 坐在 V 形块上
    assert vb.min.Z < work.min.Z


def test_sh301_states_carry_home_offsets_and_highlight():
    e = next(x for x in E if x["id"] == "E-WKP-SH301")
    ns = nodes(e)
    assert len(ns) == 5
    for _, s in ns:
        m = s._wq["meta"]
        bb = s.bounding_box()
        assert abs((bb.min.Y + bb.max.Y) / 2 + m["home_mm"][1]) < 0.5      # 加上 home_mm 回到 y = 0
    v, t, cols = ns[2][1]._wq["mesh"]()                  # 工序 40：有橙色的本工序加工面
    assert t and any(c[:3] != ns[2][1]._wq["rgba"][:3] for c in cols)


def test_ids_recognised_by_factory_and_gateway():
    sel = (wqlib.ROOT.parent / "factory" / "digital" / "hub" / "select.py").read_text(encoding="utf-8")
    ref = re.search(r'REF = re\.compile\(r"(.+?)"\)', sel).group(1)
    gw = (wqlib.ROOT.parent / "services" / "gateway" / "app" / "library.py").read_text(encoding="utf-8")
    for e in E:
        assert re.search(ref, e["id"]), e["id"]
    m = re.search(r'"(\^\[A-Z\][^"]+)"', gw)
    if m:
        for e in E:
            assert re.match(m.group(1), e["id"]), e["id"]


def test_variants_really_differ():
    """同一个函数的不同型式（圆柱销与菱形销、三种钻套、三种支承钉）确实造出不同的形体"""
    vol = {e["id"]: sum(s.volume for _, s in nodes(e)) for e in E if e["id"] in
           ("E-LOC-PIN", "E-LOC-DPIN", "E-GDE-BUSHFIX", "E-GDE-BUSHREN", "E-GDE-BUSHQC", "E-LOC-SPINA", "E-LOC-SPINB", "E-LOC-SPINC")}
    assert vol["E-LOC-DPIN"] < vol["E-LOC-PIN"] - 100
    assert len({round(vol[k]) for k in ("E-GDE-BUSHFIX", "E-GDE-BUSHREN", "E-GDE-BUSHQC")}) == 3
    assert len({round(vol[k]) for k in ("E-LOC-SPINA", "E-LOC-SPINB", "E-LOC-SPINC")}) == 3
