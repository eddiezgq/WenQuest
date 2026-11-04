# -*- coding: utf-8 -*-
"""第 75 轮：零件库 B-HUM-WQH1（问渠机器人厂 WQ-H1 轮式人形）——副本与原件一致；网页模型的节点链与 MuJoCo 正运动学一致；URDF、MJCF 齐全。"""
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest

import wqlib

trimesh = pytest.importorskip("trimesh")
from generators import b_wq, wqh1 as H  # noqa: E402
from test_wq_robots import chain  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def test_copy_is_identical_to_the_factory_original():
    orig = REPO / "factory" / "digital" / "cae" / "wqh1.py"
    assert (REPO / "library" / "generators" / "wqh1.py").read_bytes() == orig.read_bytes(), \
        "原件在 factory/digital/cae/wqh1.py：改原件后运行 python3 factory/digital/cae/wqh1.py --sync"


def test_node_chain_matches_mujoco_and_files_are_there():
    e = next(x for x in wqlib.entries(["B-HUM-WQH1"]) if x["id"] == "B-HUM-WQH1")
    pt = b_wq.build(e, wqlib.specs(e)[0])[0][1]
    names = [b["name"] for b in pt["bodies"]]
    assert names[0] == "base" and len(names) == 17 and len(pt["robot"]["joints"]) == 16
    root = ET.fromstring(pt["urdf"])
    assert len(root.findall("joint")) == 16
    m = ET.fromstring(pt["mjcf"])
    assert len(m.findall(".//joint")) == 16 and len(m.findall(".//actuator/position")) == 16
    assert pt["robot"]["dynamics"]["modules"] == {"WQJ-L": 2, "WQJ-M": 4, "WQJ-S": 10}
    assert all("armature" in j["dynamics"] for j in pt["robot"]["joints"])
    mujoco = pytest.importorskip("mujoco")
    mm = mujoco.MjModel.from_xml_string(pt["mjcf"])
    d = mujoco.MjData(mm)
    rng = np.random.default_rng(1)
    for _ in range(5):
        q = {j: rng.uniform(-1.0, 1.0) for j in H.JOINTS}
        for j, v in q.items():
            d.qpos[mm.joint(j).qposadr[0]] = v
        mujoco.mj_kinematics(mm, d)
        T = chain(pt, q)
        for n in ("head", "l_wrist", "r_wrist"):
            assert np.allclose(T[n][:3, 3], d.body(n).xpos, atol=1e-9)
