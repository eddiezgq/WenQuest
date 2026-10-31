# -*- coding: utf-8 -*-
"""设计软件接口（学习平台第 41 轮）：钥匙、单位隔离、每日上限、转交计算服务。"""
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.test_cae import beam_step, face_at


@pytest.fixture
def ds(tmp_path, monkeypatch):
    from cae import service
    from hub import cae_api, design_sw_api
    monkeypatch.setattr(service, "DATA", str(tmp_path))
    monkeypatch.setenv("WQ_FACTORY_CAE_KEY", "k" * 40)
    monkeypatch.setenv("WQ_DESIGN_SW_DAILY", "2")
    app = FastAPI()
    design_sw_api.mount(app)
    with TestClient(service.app) as cae:
        monkeypatch.setattr(cae_api, "CLIENT", cae)
        with TestClient(app) as c:
            yield c


H = {"Authorization": "Bearer " + "k" * 40}


def wait(c, jid, org):
    for _ in range(240):
        j = c.get("/api/design-sw/jobs/" + jid, params={"org": org}, headers=H).json()
        if j["status"] in ("done", "failed"):
            return j
        time.sleep(0.5)
    raise AssertionError("timeout")


def test_key_org_quota_and_fea(ds):
    c = ds
    assert c.get("/api/design-sw/health").status_code == 401
    assert c.get("/api/design-sw/health", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert c.get("/api/design-sw/health", headers=H).json()["ok"]
    assert any(m["id"] == "45-QT" for m in c.get("/api/design-sw/materials", headers=H).json()["materials"])
    assert c.get("/api/design-sw/motors", headers=H).json()["motors"][0]["rated_nm"] > 0
    g = c.post("/api/design-sw/geometry", content=beam_step(), headers=H).json()
    fix, tip = face_at(g["faces"], 0, 0.0), face_at(g["faces"], 0, 100.0)
    setup = {"material_id": "45-QT", "mesh": {"size_mm": 5},
             "loads": [{"type": "fixed", "faces": [fix]}, {"type": "force", "faces": [tip], "vector_n": [0, -100, 0]}]}
    assert c.post("/api/design-sw/jobs", json={"org": "", "kind": "fea", "step_sha": g["sha"], "setup": setup}, headers=H).status_code == 400
    j = c.post("/api/design-sw/jobs", json={"org": "甲厂", "user": "7", "user_name": "张工", "kind": "fea", "step_sha": g["sha"],
                                           "setup": setup, "title": "连杆"}, headers=H).json()
    assert j["factory"] == "wq_sewing_saas" and j["owner"] == "甲厂::7"
    j = wait(c, j["id"], "甲厂")
    assert j["status"] == "done" and abs(j["stats"]["u_max_mm"] - 0.1905) / 0.1905 < 0.03
    # 别的单位看不到
    assert c.get("/api/design-sw/jobs/" + j["id"], params={"org": "乙厂"}, headers=H).status_code == 404
    assert c.get("/api/design-sw/jobs", params={"org": "乙厂"}, headers=H).json()["jobs"] == []
    lst = c.get("/api/design-sw/jobs", params={"org": "甲厂"}, headers=H).json()
    assert lst["used_today"] == 1 and lst["daily_limit"] == 2
    # 疲劳、模态、报告、云图
    f = c.post(f"/api/design-sw/jobs/{j['id']}/fatigue", params={"org": "甲厂"}, json={"ref_load": 1, "series": [5, -5]}, headers=H).json()
    assert f["summary"]["cycles_per_block"] == 1
    m = c.post(f"/api/design-sw/jobs/{j['id']}/modal", params={"org": "甲厂"}, headers=H).json()
    assert m["freqs"][0]["hz"] > 0
    assert c.post(f"/api/design-sw/jobs/{j['id']}/report", params={"org": "甲厂"}, json={}, headers=H).content[:2] == b"PK"
    assert c.get(f"/api/design-sw/jobs/{j['id']}/surface.bin", params={"org": "甲厂"}, headers=H).content[:4] == b"WQS1"
    # 每日上限（测试里设为 2）
    assert c.post("/api/design-sw/jobs", json={"org": "甲厂", "kind": "fea", "step_sha": g["sha"], "setup": setup}, headers=H).status_code == 200
    r = c.post("/api/design-sw/jobs", json={"org": "甲厂", "kind": "fea", "step_sha": g["sha"], "setup": setup}, headers=H)
    assert r.status_code == 429


def test_mbd_slider_crank(ds):
    c = ds
    w = 2 * 3.141592653589793 * 3000 / 60
    j = c.post("/api/design-sw/jobs", headers=H, json={
        "org": "甲厂", "user": "7", "kind": "mbd", "title": "刺布机构",
        "model": {"source": "mech", "id": "C-LNK-SLIDER", "params": {"crank_m": 0.0155, "rod_m": 0.055}},
        "setup": {"duration_s": 0.06, "drives": [{"joint": "crank", "kind": "speed", "value": w}],
                  "payloads": [{"body": "slider", "mass": 0.12}]}}).json()
    j = wait(c, j["id"], "甲厂")
    assert j["status"] == "done", j.get("error")
    s = c.get(f"/api/design-sw/mbd/jobs/{j['id']}/joint-series", params={"org": "甲厂", "joint": "crank"}, headers=H).json()
    assert s["peak"] > 0
    b = c.get(f"/api/design-sw/jobs/{j['id']}/series.bin", params={"org": "甲厂"}, headers=H).content
    assert b[:4] == b"WQC1"
    assert c.get(f"/api/design-sw/jobs/{j['id']}/series.bin", params={"org": "乙厂"}, headers=H).status_code == 404


def test_cam_app_has_its_own_factory_and_model_upload(ds):
    """第 39 轮第 4 步：问渠凸轮用同一接口，任务记在 wq_cam_saas 下；整机模型是凸轮服务自己生成的 MJCF，先上传"""
    c = ds
    g = c.post("/api/design-sw/geometry", content=beam_step(), headers=H).json()
    fix, tip = face_at(g["faces"], 0, 0.0), face_at(g["faces"], 0, 100.0)
    setup = {"material_id": "45-QT", "mesh": {"size_mm": 8},
             "loads": [{"type": "fixed", "faces": [fix]}, {"type": "force", "faces": [tip], "vector_n": [0, -100, 0]}]}
    body = {"app": "cam", "org": "示例机床厂", "user": "7", "kind": "fea", "step_sha": g["sha"], "setup": setup}
    j = c.post("/api/design-sw/jobs", json=body, headers=H).json()
    assert j["factory"] == "wq_cam_saas" and j["owner"] == "示例机床厂::7"
    assert c.post("/api/design-sw/jobs", json=dict(body, app="erp"), headers=H).status_code == 400
    # 两个软件各算各的用量；本单位能看到自己的任务，别的单位看不到
    assert c.get("/api/design-sw/jobs", params={"org": "示例机床厂"}, headers=H).json()["jobs"] == []
    assert len(c.get("/api/design-sw/jobs", params={"org": "示例机床厂", "app": "cam"}, headers=H).json()["jobs"]) == 1
    assert c.get("/api/design-sw/jobs/" + j["id"], params={"org": "别的厂"}, headers=H).status_code == 404
    wait(c, j["id"], "示例机床厂")
    xml = b"""<mujoco><worldbody><body name="b"><joint name="q" type="hinge" axis="0 0 1"/>
      <geom type="box" size=".1 .02 .02" mass="1"/></body></worldbody><actuator><motor joint="q"/></actuator></mujoco>"""
    m = c.post("/api/design-sw/mbd/model", params={"name": "cam-system.xml"}, content=xml, headers=H).json()
    assert m["ref"]["source"] == "upload"
    assert c.post("/api/design-sw/mbd/model", content=xml).status_code == 401


def test_table_coupling():
    """第 39 轮第 4 步：凸轮的位置表（含每转净分度）做成耦合函数"""
    import math

    import numpy as np

    from cae import mech_mjcf as MC
    deg = np.arange(0, 360, 2.0)
    val = np.radians(deg) / 2 + 0.1 * np.sin(np.radians(2 * deg))
    f = MC.coupling_fn("table", {"deg": deg.tolist(), "value": val.tolist(), "advance": math.pi})
    for q in (0.3, 2.0, 5.5, 2 * math.pi + 0.3, 4 * math.pi + 2.0):
        assert abs(f(q) - (q / 2 + 0.1 * math.sin(2 * q))) < 1e-5
    with pytest.raises(ValueError):
        MC.coupling_fn("table", {"deg": [0, 10], "value": [0, 1]})


def _rod_plate():
    from shapely.geometry import Point
    from shapely.ops import unary_union
    d = unary_union([Point(0, 0).buffer(9, 32), Point(0, -55).buffer(8, 32)]).convex_hull
    return {"domain": [list(q) for q in d.exterior.coords[:-1]], "solid": [[0, 0, 6.5], [0, -55, 5.5]], "holes": [[0, 0, 3.5], [0, -55, 3]],
            "support": [0, 0, 3.5], "load": {"at": [0, -55, 3], "f": [400, -650]}, "thickness_mm": 6}


def test_topo_plate_step_and_cam(ds):
    """第 41 轮第二批：两孔平板拓扑优化 → 减重零件 STEP 与轮廓 → 铣削程序；单位隔离、每日上限照样"""
    c = ds
    assert c.post("/api/design-sw/topo", headers=H, json={"org": "甲厂", "spec": {"plate": {"domain": [[0, 0], [1, 0]]}}}).status_code == 400
    j = c.post("/api/design-sw/topo", headers=H, json={"org": "甲厂", "user": "7", "title": "连杆减重", "spec": {"plate": _rod_plate(), "volfrac": 0.5}}).json()
    assert j["factory"] == "wq_sewing_saas" and j["kind"] == "topo"
    j = wait(c, j["id"], "甲厂")
    assert j["status"] == "done", j.get("error")
    assert c.get(f"/api/design-sw/topo/{j['id']}/result", params={"org": "乙厂"}, headers=H).status_code == 404
    r = c.get(f"/api/design-sw/topo/{j['id']}/result", params={"org": "甲厂"}, headers=H).json()
    assert r["preset"] == "plate" and r["converged"] and 0.3 < r["mass_ratio"] < 0.9
    s = c.post(f"/api/design-sw/topo/{j['id']}/to-step", params={"org": "甲厂"}, headers=H).json()
    assert len(s["inner"]) >= 2 and s["area_mm2"] > 100                                   # 两个孔还在
    cyl = [f for f in s["geometry"]["faces"] if f["kind"] == "cylinder"]
    assert any(abs(f["radius_mm"] - 3.5) < 0.05 for f in cyl) and any(abs(f["radius_mm"] - 3.0) < 0.05 for f in cyl)
    assert c.get(f"/api/design-sw/geometry/{s['geometry']['sha']}/step", headers=H).content.startswith(b"ISO-10303-21")
    m = c.post("/api/design-sw/cam", headers=H, json={"org": "甲厂", "user": "7", "sha": s["geometry"]["sha"], "name": "针杆连杆", "material": "45"}).json()
    assert m["status"] == "done", m.get("error")
    assert m["programs"] and m["features"]["holes"] >= 2 and m["features"]["narrow"] == 0
    nc = c.get(f"/api/design-sw/cam/{m['id']}/0.nc", params={"org": "甲厂"}, headers=H).text
    assert "G0" in nc and ("M30" in nc or "M02" in nc)
    assert c.get(f"/api/design-sw/cam/{m['id']}/0.nc", params={"org": "乙厂"}, headers=H).status_code == 404
    # 每日上限（测试里设为 2）：拓扑优化算一个，数控编程单独计数（不占这 2 个）
    lst = c.get("/api/design-sw/jobs", params={"org": "甲厂"}, headers=H).json()
    assert lst["used_today"] == 1 and lst["cam_used_today"] == 1 and lst["cam_daily_limit"] == 100
    assert c.post("/api/design-sw/topo", headers=H, json={"org": "甲厂", "spec": {"plate": _rod_plate()}}).status_code == 200
    assert c.post("/api/design-sw/topo", headers=H, json={"org": "甲厂", "spec": {"plate": _rod_plate()}}).status_code == 429


def test_ebox_geometry_and_cfd_kind(ds):
    """学习平台第 62 轮：电控箱参数化外壳读入（面分组、热载荷）；流体分析也能从设计软件提交（自然对流要表面比空气热）"""
    pytest.importorskip("build123d")
    c = ds
    g = c.post("/api/design-sw/ebox/geometry", json={"params": {"fins": 4, "p_ipm": 20, "p_aux": 8, "t_air": 38}}, headers=H).json()
    ex = g["example"]
    assert g["sha"] and len(ex["groups"]["ipm"]) == 5 and ex["formula"]["loss_w"] == 28
    assert c.post("/api/design-sw/ebox/geometry", json={"params": {"L": 50}}, headers=H).status_code == 400
    bad = {"org": "甲厂", "kind": "cfd", "step_sha": g["sha"], "setup": {"flow": {"mode": "natural", "air_t_c": 38}, "heat": {"wall_t_c": 38.5}}}
    assert c.post("/api/design-sw/jobs", json=bad, headers=H).status_code == 400
    assert c.post("/api/design-sw/jobs", json=dict(bad, kind="cfx"), headers=H).status_code == 400
