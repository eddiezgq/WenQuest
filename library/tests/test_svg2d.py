# -*- coding: utf-8 -*-
"""第 5 轮第 6 步：二维图（R3）——三种图都能出、是合法 SVG、有中英文标题栏与比例；A 部分剖视有剖面线。"""
import xml.etree.ElementTree as ET

import pytest

import wqlib

pytest.importorskip("build123d")
import svg2d  # noqa: E402
from generators import get_builder  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"


def entry(eid):
    return next(e for e in wqlib.entries([eid]) if e["id"] == eid)


def texts(svg):
    root = ET.fromstring(svg.encode("utf-8"))
    assert root.get("viewBox") == "0 0 297 210"
    return " ".join(t.text or "" for t in root.iter(NS + "text"))


@pytest.mark.parametrize("eid,size", [("A-BRG-DG", "6207"), ("A-BLT-HEX", "M12x110"), ("A-LGD-RAIL", "HGH20CA"),
                                      ("A-SPR-CMP", "1.6x12x32"), ("A-PUL-HTD", "GT2-20-6")])
def test_standard_part_two_views(eid, size):
    e = entry(eid)
    row = next(r for r in wqlib.specs(e) if str(r["size"]) == size)
    svg = svg2d.drawing(e, row, nodes=get_builder(e)(e, row))
    t = texts(svg)
    assert "主视图" in t and ("俯视图" in t or "侧视图" in t)
    assert "{}/{}".format(eid, size) in t and "比例 Scale" in t and e["name"]["zh"] in t and e["name"]["en"] in t
    assert "主要尺寸" in t
    if e["category"] in svg2d.SECTION_CATS:
        assert "url(#hatch)" in svg and "剖视" in t


@pytest.mark.parametrize("eid", ["C-LNK-4BAR", "C-GER-TRAIN", "C-CAM-DISC", "C-GNV-GENEVA", "C-SCN-LEAD"])
def test_mechanism_diagram(eid):
    e = entry(eid)
    part = get_builder(e)(e, {})[0][1]
    t = texts(svg2d.drawing(e, {}, part=part))
    assert "机构运动简图" in t and eid in t


@pytest.mark.parametrize("eid", ["B-SCA-WQ4", "B-PAR-STEWART", "B-EDU-2R"])
def test_robot_joint_diagram(eid):
    e = entry(eid)
    part = get_builder(e)(e, wqlib.specs(e)[0])[0][1]
    t = texts(svg2d.drawing(e, {}, part=part))
    assert "关节示意图" in t and "J1" in t and eid in t


def test_scale_picker():
    assert svg2d.pick_scale(1.3) == ("1:1", 1.0)
    assert svg2d.pick_scale(0.3)[1] == 0.25 and svg2d.pick_scale(6)[1] == 5
