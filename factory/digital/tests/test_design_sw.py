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
