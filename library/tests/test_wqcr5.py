# -*- coding: utf-8 -*-
"""第 58 轮：零件库 B-ARM-WQCR5（问渠机器人厂 WQ-CR5）——副本与原件一致；网页模型的节点链与 DH 正运动学一致；URDF、MJCF 齐全。"""
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest

import wqlib

trimesh = pytest.importorskip("trimesh")
from generators import b_wq, wqcr5 as W  # noqa: E402
from test_wq_robots import chain  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def test_copy_is_identical_to_the_factory_original():
    orig = REPO / "factory" / "digital" / "cae" / "wqcr5.py"
    assert (REPO / "library" / "generators" / "wqcr5.py").read_bytes() == orig.read_bytes(), \
        "原件在 factory/digital/cae/wqcr5.py：改原件后运行 python3 factory/digital/cae/wqcr5.py --sync"


def _dh_fk(q):
    T = np.eye(4)
    for qi, d in zip(q, W.DH):
        ct, st, ca, sa = math.cos(qi), math.sin(qi), math.cos(d["alpha"]), math.sin(d["alpha"])
        T = T @ np.array([[ct, -st * ca, st * sa, d["a"] * ct], [st, ct * ca, -ct * sa, d["a"] * st], [0, sa, ca, d["d"]], [0, 0, 0, 1]])
    return T


def test_node_chain_matches_dh_and_files_are_there():
    e = next(x for x in wqlib.entries(["B-ARM-WQCR5"]) if x["id"] == "B-ARM-WQCR5")
    pt = b_wq.build(e, wqlib.specs(e)[0])[0][1]
    assert [b["name"] for b in pt["bodies"]] == ["base"] + ["link{}".format(i) for i in range(1, 7)]
    rng = np.random.default_rng(0)
    for _ in range(5):
        q = rng.uniform(-2.5, 2.5, 6)
        T = chain(pt, dict(zip(W.JOINTS, q)))
        # 节点 link6 的坐标系 = DH 坐标系 5 绕 z 转 θ6；法兰在它的 (0, 0, d6)
        flange = (T["link6"] @ np.array([0, 0, W.DH[5]["d"], 1]))[:3]
        assert np.allclose(flange, _dh_fk(q)[:3, 3], atol=1e-9)
    root = ET.fromstring(pt["urdf"])
    assert len(root.findall("joint")) == 6
    m = ET.fromstring(pt["mjcf"])
    assert len(m.findall(".//joint")) == 6 and len(m.findall(".//actuator/motor")) == 6
    assert pt["robot"]["dynamics"]["payload_kg"] == 5.0
    assert all("armature" in j["dynamics"] for j in pt["robot"]["joints"])
