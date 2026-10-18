# -*- coding: utf-8 -*-
"""设计软件接口（第 39 轮第 4 步 / 第 41 轮）：钥匙、单位隔离、每日用量、转交计算服务。
计算服务用假的 call 代替（真计算在 test_cae.py、test_mbd.py 里测）。"""
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hub import design_sw_api as D


class Fake:
    def __init__(self):
        self.jobs = {}
        self.calls = []

    def __call__(self, method, path, **kw):
        self.calls.append((method, path, kw))

        class R:
            def __init__(self, data):
                self.data = data

            def json(self):
                return self.data
        if path == "/jobs" and method == "GET":
            f = kw["params"]["factory"]
            return R({"jobs": [j for j in self.jobs.values() if j["factory"] == f]})
        if path in ("/jobs", "/mbd/jobs") and method == "POST":
            jid = "j{}".format(len(self.jobs) + 1)
            j = dict(kw["json"], id=jid, created=time.time(), status="queued")
            self.jobs[jid] = j
            return R(j)
        if path.startswith("/jobs/") and method == "GET":
            from fastapi import HTTPException
            jid = path.split("/")[2]
            if jid not in self.jobs:
                raise HTTPException(404, "没有这个任务")
            return R(self.jobs[jid])
        if path.endswith("/fatigue"):
            return R({"summary": {"life_h": 1e5}, "damage_b64": "AAAA"})
        return R({"ok": True, "path": path})


@pytest.fixture()
def env(monkeypatch):
    monkeypatch.setenv("WQ_FACTORY_CAE_KEY", "k" * 40)
    monkeypatch.setenv("WQ_DESIGN_SW_DAILY", "3")
    app = FastAPI()
    fake = Fake()
    D.mount(app, fake)
    return TestClient(app), fake


H = {"Authorization": "Bearer " + "k" * 40}


def test_key_required(env):
    c, _ = env
    assert c.get("/api/design-sw/materials").status_code == 401
    assert c.get("/api/design-sw/materials", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert c.get("/api/design-sw/materials", headers=H).status_code == 200


def test_submit_isolation_and_quota(env):
    c, fake = env
    body = {"app": "cam", "org": "示例机床厂", "user": "7", "user_name": "张工", "sha": "abc", "setup": {"x": 1}}
    r = c.post("/api/design-sw/fea", json=body, headers=H)
    assert r.status_code == 200
    j = r.json()
    assert j["factory"] == "wq_cam_saas" and j["owner"] == "示例机床厂/7"
    # another company cannot see it; the same company can
    assert c.get("/api/design-sw/jobs/" + j["id"], params={"org": "别的厂"}, headers=H).status_code == 404
    assert c.get("/api/design-sw/jobs/" + j["id"], params={"org": "示例机床厂"}, headers=H).status_code == 200
    # fatigue: the per-point damage stays in the factory
    f = c.post("/api/design-sw/jobs/{}/fatigue".format(j["id"]), params={"org": "示例机床厂"}, json={}, headers=H).json()
    assert "damage_b64" not in f and f["summary"]["life_h"] == 1e5
    # daily limit per company (3 in this test)
    c.post("/api/design-sw/mbd", json=dict(body, model={"source": "upload", "sha": "m"}), headers=H)
    c.post("/api/design-sw/fea", json=body, headers=H)
    r = c.post("/api/design-sw/fea", json=body, headers=H)
    assert r.status_code == 429
    assert c.post("/api/design-sw/fea", json=dict(body, org="别的厂"), headers=H).status_code == 200
    # the sewing software has its own factory number
    assert c.post("/api/design-sw/fea", json=dict(body, app="sewing"), headers=H).json()["factory"] == "wq_sewing_saas"
    assert c.post("/api/design-sw/fea", json=dict(body, app="erp"), headers=H).status_code == 400


def test_teaching_jobs_are_not_reachable(env):
    c, fake = env
    fake.jobs["t1"] = {"id": "t1", "factory": "wq_factory", "owner": "示例机床厂/7"}
    assert c.get("/api/design-sw/jobs/t1", params={"org": "示例机床厂"}, headers=H).status_code == 404


def test_table_coupling():
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
