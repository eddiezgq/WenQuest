# -*- coding: utf-8 -*-
"""第 5 轮第 4 步：robot_descriptions 接入——许可核对、固定提交、URDF 读取（节点 = 连杆、关节表）、Collada 单位换算。"""
import pytest
import yaml

import wqlib

RD = wqlib.ROOT / "vendor_src" / "rd"
REPOS = yaml.safe_load((wqlib.ROOT / "vendor" / "rd_repos.yaml").read_text(encoding="utf-8"))


def rd_entries():
    return [e for e in wqlib.entries(["B-"]) if e["source"]["origin"] == "robot_descriptions"]


def test_entries_are_licensed_and_pinned():
    es = rd_entries()
    assert len(es) >= 35
    for e in es:
        s = e["source"]
        assert s["license"] in wqlib.ALLOWED_LICENSES, e["id"]
        key = e["model"]["engine"].split(":", 1)[1].split("/", 1)[0]
        assert REPOS[key]["commit"] == s["commit"], e["id"]
        assert "LICENSE 识别为" in s["checked"]["note"]
        assert not s["license"].startswith("GPL") and "NC" not in s["license"]


def test_duplicates_only_get_alt_link():
    e = next(x for x in wqlib.entries(["B-LEG-GO2"]) if x["id"] == "B-LEG-GO2")
    assert e["model"]["engine"].startswith("menagerie:")
    assert e["alt_models"][0]["format"] == "urdf" and e["alt_models"][0]["url"].startswith("https://")


needs_src = pytest.mark.skipif(not (RD / "eDO_description").exists(), reason="没有 robot_descriptions 的原仓库（fetch_sources.py rd）")


@needs_src
def test_urdf_robot_nodes_and_joints():
    pytest.importorskip("yourdfpy")
    trimesh = pytest.importorskip("trimesh")
    import io
    from generators import b_robot, b_urdf
    e = next(x for x in wqlib.entries(["B-ARM-EDO"]) if x["id"] == "B-ARM-EDO")
    part = b_urdf.build(e, {})[0][1]
    r = part["robot"]
    assert r["dof"] == 6
    names = {b["name"] for b in part["bodies"]}
    for j in r["joints"]:
        assert j["parent"] in names and j["child"] in names and len(j["axis"]) == 3
    sc = trimesh.load(io.BytesIO(b_robot.glb_bytes(part)), file_type="glb")
    assert {j["child"] for j in r["joints"]} <= set(sc.graph.nodes)


@needs_src
def test_collada_unit_is_applied():
    pytest.importorskip("yourdfpy")
    from generators import b_urdf
    e = next(x for x in wqlib.entries(["B-LEG-ALIENGO"]) if x["id"] == "B-LEG-ALIENGO")
    part = b_urdf.build(e, {})[0][1]
    calf = next(b for b in part["bodies"] if b["name"] == "FR_calf")
    assert 0.15 < max(calf["mesh"].extents) < 0.5          # 小腿约 0.3 m（文件单位为英寸 0.0254 m）
