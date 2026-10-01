# -*- coding: utf-8 -*-
"""第 5 轮第 3 步第 3 批：ROS-Industrial 工业机械臂——固定提交与许可、xacro 展开、从动关节、模型与厂商参数互相核对。"""
import math

import pytest
import yaml

import wqlib

RD = wqlib.ROOT / "vendor_src" / "rd"
PIN = yaml.safe_load((wqlib.ROOT / "vendor" / "ros_industrial.yaml").read_text(encoding="utf-8"))
REPOS = yaml.safe_load((wqlib.ROOT / "vendor" / "rosi_repos.yaml").read_text(encoding="utf-8"))
have_src = all((RD / k / ".git").exists() for k in PIN["repos"])
need_src = pytest.mark.skipif(not have_src, reason="没有 ROS-Industrial 源仓库（tools/fetch_sources.py）")


def rosi_entries():
    return [e for e in wqlib.entries(["B-"]) if e["source"]["origin"] == "ros_industrial"]


def test_entries_pinned_and_licensed():
    es = rosi_entries()
    assert len(es) == len([o for o in PIN["robots"] if not o.get("dup_of")])
    for e in es:
        s = e["source"]
        key = e["model"]["engine"].split(":", 1)[1].split("/", 1)[0]
        assert e["model"]["engine"].startswith("xacro:")
        assert PIN["repos"][key]["commit"] == REPOS[key]["commit"] == s["commit"], e["id"]
        assert s["license"] in wqlib.ALLOWED_LICENSES, e["id"]
        assert "package.xml" in s["checked"]["note"]


def test_vendor_datasheets_attached():
    es = {e["id"]: e for e in rosi_entries()}
    with_sheet = [i for i, e in es.items() if e.get("datasheet")]
    assert len(with_sheet) >= 25
    gp7 = es["B-ARM-GP7"]["datasheet"]
    assert gp7["values"]["reach_mm"] == 927 and gp7["values"]["payload_kg"] == 7
    assert [a["speed_deg_s"] for a in gp7["axes"]] == [375, 315, 410, 550, 550, 1000]
    iiwa = next(e for e in wqlib.entries(["B-ARM-IIWA14"]) if e["id"] == "B-ARM-IIWA14")
    assert iiwa["model"]["engine"].startswith("menagerie:")                       # 已有条目只加链接与参数
    assert {a["format"] for a in iiwa["alt_models"]} >= {"urdf", "xacro"}


@need_src
def test_xacro_expands_with_mimic_joints():
    from generators import b_urdf
    e = next(x for x in rosi_entries() if x["id"] == "B-ARM-GP225")
    part = b_urdf.build(e, {"size": "default"})[0][1]
    rob = part["robot"]
    assert rob["dof"] == 6                                       # 两个平衡缸关节是从动的，不算自由度
    mimic = [j for j in rob["joints"] if "mimic" in j]
    assert {j["mimic"]["joint"] for j in mimic} == {"joint_2_l"}
    assert part["urdf"].lstrip().startswith("<?xml") and "package://motoman_gp225_support" in part["urdf"]


@need_src
@pytest.mark.parametrize("key", ["irb120_3_58", "gp7", "irb7600_150_350", "motomini"])
def test_model_matches_vendor_axes(key):
    """模型（ROS-Industrial）与厂商官方表两个独立来源：各轴范围、速度一致（±1.5°、±2°/s）"""
    import io

    import yourdfpy
    from import_rosi import arms, xacro_rel
    from xacro_util import expand
    o = next(x for x in PIN["robots"] if x["key"] == key)
    repo = RD / o["repo"]
    rb = yourdfpy.URDF.load(io.BytesIO(expand(repo, xacro_rel(repo, key)).encode()), load_meshes=False,
                            build_scene_graph=False).robot
    js = [j for j in rb.joints if j.type in ("revolute", "continuous", "prismatic") and j.mimic is None]
    r = arms()[key][1]
    for i, j in enumerate(js[:6]):
        lo, hi = r["joint_range_deg"][i]
        assert abs(math.degrees(j.limit.lower) - lo) <= 1.5 and abs(math.degrees(j.limit.upper) - hi) <= 1.5, (key, i)
        assert abs(math.degrees(j.limit.velocity) - r["joint_speed_deg_s"][i]) <= 2, (key, i)
