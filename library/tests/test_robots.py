# -*- coding: utf-8 -*-
"""B 部分现成机器人（Menagerie）：节点按连杆命名、关节表字段齐全（附录 B.13、约定 R4）。
没有 Menagerie 源文件时跳过（CI 的发布流程会先克隆到固定提交）。"""
import io
import json

import pytest

import wqlib

mujoco = pytest.importorskip("mujoco")
trimesh = pytest.importorskip("trimesh")
from generators import b_robot  # noqa: E402

pytestmark = pytest.mark.skipif(not b_robot.MENAGERIE.exists(), reason="没有 Menagerie 源文件（WQ_MENAGERIE）")

CASES = {"B-ARM-UR5E": 6, "B-ARM-PANDA": 9}


def _entry(eid):
    return next(e for e in wqlib.entries(eid) if e["id"] == eid)


@pytest.mark.parametrize("eid,dof", CASES.items())
def test_joint_table_and_nodes(eid, dof):
    e = _entry(eid)
    part = b_robot.build(e, {})[0][1]
    robot = part["robot"]
    assert robot["dof"] == dof == len(robot["joints"])
    links = {l["name"] for l in robot["links"]}
    for j in robot["joints"]:
        assert j["type"] in ("revolute", "continuous", "prismatic")
        assert j["parent"] in links and j["child"] in links
        assert len(j["axis"]) == 3 and set(j["origin"]) == {"xyz", "rpy"}
        if j["type"] == "revolute":
            assert j["limit"]["lower"] < j["limit"]["upper"]
    sc = trimesh.load(io.BytesIO(b_robot.glb_bytes(part)), file_type="glb")
    nodes = set(sc.graph.nodes)
    assert "root" in nodes
    assert {j["child"] for j in robot["joints"]} <= nodes        # 网页按关节表找得到要转的节点
    json.dumps(robot)


def test_simplify_reaches_target():
    import numpy as np
    m = trimesh.creation.icosphere(subdivisions=5)                 # 20480 个三角形
    m.visual = trimesh.visual.ColorVisuals(m, face_colors=np.tile([200, 0, 0, 255], (len(m.faces), 1)))
    out = b_robot._simplify(m, 0.1)
    assert len(out.faces) <= 2048 * 1.3 and len(out.faces) > 100


def test_every_robot_entry_points_at_pinned_menagerie():
    import yaml
    pin = yaml.safe_load((wqlib.ROOT / "vendor" / "menagerie.yaml").read_text(encoding="utf-8"))["commit"]
    robots = [e for e in wqlib.entries("B-") if e["model"]["engine"].startswith("menagerie:")]
    assert len(robots) >= 60
    for e in robots:
        assert e["source"]["commit"] == pin
        assert (b_robot.MENAGERIE / e["model"]["engine"].split(":", 1)[1]).exists(), e["id"]


def test_rest_pose_from_keyframe():
    """学习平台 R7：有关键帧的模型带 robot.rest，关节名与关节表一致"""
    e = _entry("B-ARM-UR5E")
    r = b_robot.build(e, {})[0][1]["robot"]
    names = {j["name"] for j in r["joints"]}
    assert r["rest"] and set(r["rest"]) <= names and r["rest_source"]
    assert abs(r["rest"]["elbow_joint"] - 1.5708) < 1e-3
