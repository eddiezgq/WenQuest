# -*- coding: utf-8 -*-
"""第 5 轮第 2 步：厂商目录（UR、Harmonic Drive 试做）——出处齐全、表内自洽、DH 模型与正运动学一致、Menagerie 叠加。"""
import csv
import math

import numpy as np
import pytest

import wqlib


def entry(eid):
    return next(e for e in wqlib.entries([eid]) if e["id"] == eid)


def test_hd_csf_table_is_consistent_and_sourced():
    e = entry("D-RDC-HD-CSF")
    assert e["kind"] == "product" and e["source"]["origin"] == "vendor" and e["source"]["data_sources"]
    rows = list(csv.DictReader(open(wqlib.CATALOG / "D" / "D-RDC-HD-CSF" / "specs.csv", encoding="utf-8")))
    assert len(rows) == 27 and all(r["src_page"] for r in rows)
    r = {x["size"]: x for x in rows}
    assert (r["20-100"]["T_rated_Nm"], r["20-100"]["T_momentary_Nm"]) == ("40", "147")
    assert (r["32-160"]["T_repeat_Nm"], r["14-30"]["T_avg_Nm"]) == ("372", "6.8")
    for x in rows:                      # 样本里转矩的大小关系：额定 ≤ 平均允许 ≤ 启停峰值 ≤ 瞬时峰值
        tr, ta, tp, tm = (float(x[k]) for k in ("T_rated_Nm", "T_avg_Nm", "T_repeat_Nm", "T_momentary_Nm"))
        assert tr <= ta <= tp <= tm, x["size"]
        assert float(x["n_avg_grease_rpm"]) <= float(x["n_max_grease_rpm"]) <= float(x["n_max_oil_rpm"])


@pytest.mark.parametrize("eid,reach", [("B-ARM-UR3E", 500), ("B-ARM-UR16E", 900), ("B-ARM-UR20", 1750), ("B-ARM-UR30", 1300)])
def test_dh_model_matches_forward_kinematics(eid, reach):
    pytest.importorskip("trimesh")
    from generators import b_dh
    e = entry(eid)
    assert e["datasheet"]["values"]["reach_mm"] == reach
    part = b_dh.build(e, {})[0][1]
    bodies = {b["name"]: b for b in part["bodies"]}
    joints = {j["child"]: j for j in part["robot"]["joints"]}
    rng = np.random.default_rng(1)
    for _ in range(5):
        q = rng.uniform(-math.pi, math.pi, 6)
        T = np.eye(4)
        for i in range(1, 7):                              # 按节点链与关节表算
            b = bodies["link{}".format(i)]
            w, x, y, z = b["quat"]
            R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                          [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                          [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
            M = np.eye(4)
            M[:3, :3], M[:3, 3] = R, b["pos"]
            c, s = math.cos(q[i - 1]), math.sin(q[i - 1])
            Rz = np.eye(4)
            Rz[:2, :2] = [[c, -s], [s, c]]
            assert joints["link{}".format(i)]["axis"] == [0.0, 0.0, 1.0]
            T = T @ M @ Rz
        tool = np.eye(4)
        tool[:3, 3] = part["robot"]["tool"]["xyz"]
        p6 = e["dh"]["params"][-1]
        tool[:3, :3] = b_dh._T(p6[1], p6[0], p6[2])[:3, :3]
        assert np.allclose(T @ tool, b_dh.fk(e["dh"]["params"], q), atol=1e-6)
    # 伸直时法兰离肩关节的距离 ≈ 样本工作半径（UR 的工作半径按腕部中心算，允许 ±15%）
    flange = b_dh.fk(e["dh"]["params"], [0] * 6)[:3, 3]
    assert 0.85 * reach / 1000 < np.linalg.norm(flange[:2]) < 1.15 * reach / 1000


def test_menagerie_entries_get_vendor_overlay():
    e = entry("B-ARM-UR5E")
    assert e["model"]["engine"].startswith("menagerie:")                # 可动模型仍用 Menagerie
    assert e["datasheet"]["values"]["payload_kg"] == 5 and e["vendor"]["model"] == "UR5e"
    urls = [d["url"] for d in e["source"]["data_sources"]]
    assert any("UR5e_techsheet" in u for u in urls) and any("dh-parameters" in u for u in urls)


def test_vendor_files_regenerate_identically(tmp_path, monkeypatch):
    import import_vendor
    before = {p: p.read_text(encoding="utf-8") for p in (wqlib.CATALOG / "D").rglob("*") if p.is_file()}
    import_vendor.main()
    after = {p: p.read_text(encoding="utf-8") for p in (wqlib.CATALOG / "D").rglob("*") if p.is_file()}
    assert before == after


def _rows(eid):
    return list(csv.DictReader(open(wqlib.CATALOG / "D" / eid / "specs.csv", encoding="utf-8")))


@pytest.mark.parametrize("eid", ["D-ACT-ROBOTIS-X", "D-FTS-ATI-FT", "D-GRP-ROBOTIQ", "D-CAM-REALSENSE-D400", "D-LDR-OUSTER", "D-RDC-HD-CSF"])
def test_every_vendor_row_has_source_and_proxy_dims(eid):
    e = entry(eid)
    rows = _rows(eid)
    assert rows and all(r["src_url"].startswith("https://") for r in rows)
    urls = {d["url"] for d in e["source"]["data_sources"]}
    assert all(set(r["src_url"].split(" ; ")) <= urls for r in rows)
    for r in rows:
        for k, col in e["model"]["dims"].items():
            if r.get(col):
                assert float(r[col]) > 0, (eid, r["size"], col)


def test_vendor_tables_sanity():
    for r in _rows("D-FTS-ATI-FT"):
        assert float(r["Fxy_overload_N"]) > float(r["Fxy_range_N"]) and float(r["Fz_overload_N"]) > float(r["Fz_range_N"])
    for r in _rows("D-ACT-ROBOTIS-X"):
        assert float(r["voltage_min_V"]) <= float(r["stall_torque_at_V"]) <= float(r["voltage_max_V"])
    for r in _rows("D-LDR-OUSTER"):
        if r["range_10pct_m"]:
            assert float(r["range_10pct_m"]) < float(r["range_max_m"])
    for r in _rows("D-GRP-ROBOTIQ"):
        assert float(r["grip_force_min_N"]) < float(r["grip_force_max_N"])
    xm = {r["size"]: r for r in _rows("D-ACT-ROBOTIS-X")}["XM540-W270"]          # 抽查值（官方 e-Manual）
    assert (xm["stall_torque_Nm"], xm["no_load_speed_rpm"], xm["weight_g"]) == ("10.6", "30", "165")
