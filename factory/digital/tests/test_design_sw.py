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
