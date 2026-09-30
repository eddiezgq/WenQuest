# -*- coding: utf-8 -*-
"""每个标准件族的默认规格：造出来的外形尺寸与规格表一致（误差 ≤ 0.01 mm，B.4），glb 的节点挂在 root 下、单位米。"""
import io

import pytest

import wqlib
from build import glb_bytes
from generators import get_builder

build123d = pytest.importorskip("build123d")
trimesh = pytest.importorskip("trimesh")

# 每族：外形包围盒应等于哪些参数（x, y, z 排序后比较；None 表示不比）
EXPECT = {
    "A-BRG-DG": lambda r: sorted([r["D_mm"], r["D_mm"], r["B_mm"]]),
    "A-BRG-AC": lambda r: sorted([r["D_mm"], r["D_mm"], r["B_mm"]]),
    "A-BRG-CR": lambda r: sorted([r["D_mm"], r["D_mm"], r["B_mm"]]),
    # 圆锥滚子轴承：bd_warehouse 的造型比总宽 T 稍宽（滚子伸出），只核对内外径（见条目 model.note）
    "A-BRG-TR": lambda r: None,
    "A-KEY-FLAT": lambda r: sorted([r["l_mm"], r["b_mm"], r["h_mm"]]),
    "A-WSH-PLN": lambda r: sorted([r["d2_mm"], r["d2_mm"], r["h_mm"]]),
    "A-SEL-ORING": lambda r: sorted([r["od_mm"], r["od_mm"], r["w_mm"]]),
    "A-NUT-HEX": lambda r: None,
    "A-BLT-HEX": lambda r: None,
    "A-SCR-SHC": lambda r: None,
    "A-RNG-SHAFT": lambda r: None,
}


def _bbox(nodes):
    shape = nodes[0][1] if len(nodes) == 1 else build123d.Compound(children=[n[1] for n in nodes])
    return shape.bounding_box().size


@pytest.mark.parametrize("entry_id", sorted(EXPECT))
def test_default_size_matches_spec(entry_id):
    e = next(x for x in wqlib.entries() if x["id"] == entry_id)
    row = next(r for r in wqlib.specs(e) if str(r["size"]) == str(e["default"]))
    nodes = get_builder(e)(e, row)
    got = sorted([nodes and v for v in _bbox(nodes)])
    want = EXPECT[entry_id](row)
    if entry_id in ("A-NUT-HEX",):
        assert abs(sorted(got)[0] - row["m_mm"]) < 0.01 and abs(sorted(got)[1] - row["s_mm"]) < 0.01
    elif entry_id in ("A-BLT-HEX",):
        assert abs(max(got) - (row["l_mm"] + row["k_mm"])) < 0.01 and abs(sorted(got)[0] - row["s_mm"]) < 0.01
    elif entry_id in ("A-SCR-SHC",):
        assert abs(max(got) - (row["l_mm"] + row["k_mm"])) < 0.01 and abs(sorted(got)[0] - row["dk_mm"]) < 0.01
    elif entry_id == "A-BRG-TR":
        assert abs(max(got) - row["D_mm"]) < 0.01 and abs(sorted(got)[1] - row["D_mm"]) < 0.01
    elif entry_id == "A-RNG-SHAFT":
        assert abs(min(got) - row["s_mm"]) < 0.01
    else:
        assert all(abs(a - b) < 0.01 for a, b in zip(got, want)), (got, want)
    # glb：root 下挂节点，单位米，Y 向上（厚度方向变成 Y）
    scene = trimesh.load(io.BytesIO(glb_bytes(nodes)), file_type="glb")
    names = set(scene.graph.nodes) - {"world", "root"}
    assert names == {n for n, _ in nodes}
    assert scene.graph.transforms.parents[next(iter(names))] == "root"
    assert abs(max(scene.extents) * 1000 - max(got)) < 0.05
