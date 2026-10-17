"""三维仿真视频（第 38 轮）：谁能用（老师、管理员开通的账号；学生不能）、场景检查、从样片开始、AI 写和改、
关键画面（blender 容器）、租机出小样和高清（Mock 机器）、记账、取消、白板课插入。"""
import asyncio
import base64
import json
import time
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main, video3d as v3
from app.ai import ModelGateway
from app.moodle import MoodleClient
from tests.test_materials import BASE, fake_moodle, login

SCENE = """slug: demo
name: 示例
title: {zh: 平缝机一针, en: One stitch}
duration: 12
floor: false
models:
  - id: m
    use: "weblab:sewing/proto-lockstitch"
    colors: {frame: shell, needle: needle}
motion:
  - {drive: weblab, model: m, angle: [[0, 0], [12, 360]]}
camera:
  - {t: 0, look: [0.1, 0, 0.08], az: -35, el: 18, dist: 0.95}
  - {t: 6, look: [-0.017, 0, 0.0], az: -60, el: 10, dist: 0.2}
  - {t: 12, look: [0.1, 0, 0.08], az: -35, el: 18, dist: 0.95}
effects:
  - {kind: cutaway, t: [2, 12], hide: [m.face, m.top], show: [m.body_cut]}
labels:
  - {t: [0, 12], zh: 平缝机一针, en: One stitch}
"""
PNG = base64.b64encode(b"\x89PNG\r\n\x1a\nfake").decode()
CALLS: list[str] = []


def blender(request: httpx.Request) -> httpx.Response:
    path = urlparse(str(request.url)).path
    CALLS.append(path)
    if path == "/samples":
        return httpx.Response(200, json={"samples": [{"id": "缝纫机一针", "title": {"zh": "平缝机一针", "en": "One stitch"},
                                                      "duration": 12, "scene": SCENE}]})
    if path == "/format":
        return httpx.Response(200, json={"text": "# 场景格式"})
    if path == "/bundle":
        return httpx.Response(200, content=b"tgz")
    if path == "/run.sh":
        return httpx.Response(200, content=b"#!/bin/bash\n")
    if path == "/stills":
        body = json.loads(request.content)
        assert "name: video" in body["scene"] and "slug" not in body["scene"]
        return httpx.Response(200, json={"ok": True, "seconds": 3.0, "stills": [PNG] * len(body["times"])})
    return httpx.Response(404)


def moodle(request: httpx.Request) -> httpx.Response:
    q = parse_qs(urlparse(str(request.url)).query)
    fn, tok = (q.get("wsfunction") or [""])[0], (q.get("wstoken") or [""])[0]
    if fn == "local_wenquest_get_permissions":
        return httpx.Response(200, json={"cancreatecourses": tok == "teacher", "issiteadmin": tok == "teacher"})
    if fn == "core_user_get_users_by_field":
        return httpx.Response(200, json=[{"id": 6, "username": "s", "fullname": "企业用户"}])
    return fake_moodle(request)


@pytest.fixture
def v3c(tmp_path):
    with TestClient(main.app) as c:
        st = main.state.settings
        saved = {k: getattr(st, k) for k in ("data_dir", "public_url", "video3d_blender_url")}
        st.data_dir, st.public_url, st.video3d_blender_url = str(tmp_path / "data"), "https://learn.test", "http://blender.test"
        main.state.http = httpx.AsyncClient(transport=httpx.MockTransport(moodle))
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        main.state.video3d_transport = httpx.MockTransport(blender)
        main.state.video3d_provider = v3.Mock()
        main.state.video3d = None
        CALLS.clear()
        yield c
        main.state.video3d_provider = None
        main.state.video3d_transport = None
        main.state.video3d = None
        for k, v in saved.items():
            setattr(st, k, v)


def settle(c, h, vid, ok=lambda d: True, n=100):
    for _ in range(n):
        d = c.get(f"/api/v1/video3d/{vid}", headers=h).json()
        if ok(d):
            return d
        time.sleep(0.05)
    raise AssertionError(d)


def tick():
    asyncio.run(main.state.video3d.tick())


def test_check_catches_what_would_break_the_render():
    spec, errs = v3.check(SCENE)
    assert errs == [] and spec["duration"] == 12
    bad = SCENE.replace('use: "weblab:sewing/proto-lockstitch"', 'use: "gen:spaceship"').replace("az: -35, el: 18, dist: 0.95}\n  - {t: 6", "az: -35, el: 18}\n  - {t: 6")
    _, errs = v3.check(bad)
    assert any("gen:spaceship" in e for e in errs) and any("camera 第 1" in e for e in errs)
    _, errs = v3.check(SCENE.replace("zh: 平缝机一针, en: One stitch}\n", "zh: " + "很长" * 30 + ", en: x}\n"))
    assert any("出框" in e for e in errs)
    _, errs = v3.check("a: [")
    assert errs and "YAML" in errs[0]
    assert "name: video" in v3.normalized(SCENE)
    assert v3.still_times(spec) and all(0 < t < 12 for t in v3.still_times(spec))


def test_students_cannot_use_it_until_an_admin_enables_the_account(v3c):
    s, t = login(v3c, "s"), login(v3c, "t")
    assert v3c.get("/api/v1/video3d/access", headers=s).json()["allowed"] is False
    assert v3c.get("/api/v1/video3d", headers=s).status_code == 403
    assert v3c.post("/api/v1/video3d", headers=s, json={"sample": "缝纫机一针"}).status_code == 403
    assert v3c.get("/api/v1/video3d/admin/overview", headers=s).status_code == 403
    a = v3c.get("/api/v1/video3d/access", headers=t).json()
    assert a["allowed"] and a["teacher"]
    r = v3c.post("/api/v1/video3d/admin/grants", headers=t, json={"username": "s", "note": "某缝纫机厂"})
    assert r.status_code == 200 and r.json()["user_id"] == 6
    assert v3c.get("/api/v1/video3d/access", headers=s).json() == {"allowed": True, "admin": False, "teacher": False, "granted": True}
    assert v3c.get("/api/v1/video3d", headers=s).status_code == 200
    assert v3c.delete("/api/v1/video3d/admin/grants/6", headers=t).status_code == 200
    assert v3c.get("/api/v1/video3d", headers=s).status_code == 403


def test_sample_stills_draft_and_hd_with_machine_ledger(v3c):
    t = login(v3c, "t")
    idx = v3c.get("/api/v1/video3d", headers=t).json()
    assert idx["samples"][0]["id"] == "缝纫机一针" and idx["render_on"] and idx["stills_on"]
    d = v3c.post("/api/v1/video3d", headers=t, json={"sample": "缝纫机一针"}).json()
    vid = d["id"]
    assert d["title"]["zh"] == "平缝机一针" and "weblab" in d["scene"] and d["version"] == 1
    # 别人看不到
    assert v3c.get(f"/api/v1/video3d/{vid}", headers=login(v3c, "s")).status_code == 403
    # 关键画面
    r = v3c.post(f"/api/v1/video3d/{vid}/stills", headers=t)
    assert r.status_code == 200
    d = settle(v3c, t, vid, lambda d: d["stills"].get("state") == "done")
    assert len(d["stills"]["urls"]) == 6 and not d["stills"]["stale"]
    png = v3c.get(urlparse(d["stills"]["urls"][0]).path)
    assert png.status_code == 200 and png.headers["content-type"] == "image/png"
    # 小样：排队 → 开机 → 传文件、启动 → 读进度 → 取回 → 关机
    d = v3c.post(f"/api/v1/video3d/{vid}/render", headers=t, json={"quality": "draft"}).json()
    assert d["renders"]["draft"]["state"] == "queued"
    assert v3c.post(f"/api/v1/video3d/{vid}/render", headers=t, json={"quality": "draft"}).status_code == 409
    prov = main.state.video3d_provider
    states = []
    for _ in range(8):
        tick()
        states.append(v3c.get(f"/api/v1/video3d/{vid}", headers=t).json()["renders"]["draft"]["state"])
    assert states[0] == "starting" and "rendering" in states and states[-1] == "done"
    assert prov.box["files"]["wq3d/bundle.tgz"] == b"tgz" and "name: video" in prov.box["files"]["wq3d/job/scene.yaml"]
    assert json.loads(prov.box["files"]["wq3d/job/job.json"]) == {"quality": "draft"}
    assert all(not mm["on"] for mm in prov.machines.values())                       # 出完就关机
    d = v3c.get(f"/api/v1/video3d/{vid}", headers=t).json()
    mp4 = v3c.get(urlparse(d["renders"]["draft"]["urls"]["mp4"]).path)
    assert mp4.status_code == 200 and mp4.headers["content-type"] == "video/mp4"
    # 高清出 MP4 和 WebM
    v3c.post(f"/api/v1/video3d/{vid}/render", headers=t, json={"quality": "hd"})
    for _ in range(8):
        tick()
    d = v3c.get(f"/api/v1/video3d/{vid}", headers=t).json()
    assert d["renders"]["hd"]["state"] == "done" and set(d["renders"]["hd"]["urls"]) == {"mp4", "webm"}
    ov = v3c.get("/api/v1/video3d/admin/overview", headers=t).json()
    assert [r["state"] for r in ov["runs"]] == ["done", "done"] and all(r["kind"] == "gpu_1x_a10" for r in ov["runs"])
    # 白板课“插入”里能选到
    assert main.video3d_wb_list(5)[0]["src"] == f"video3d:{vid}/hd"
    assert main.video3d_wb_file(5, f"{vid}/hd").name == "hd.mp4" and main.video3d_wb_file(6, f"{vid}/hd") is None


def test_ai_writes_and_revises_and_bad_scene_edits_are_refused(v3c):
    t = login(v3c, "t")
    d = v3c.post("/api/v1/video3d", headers=t, json={"prompt": "讲清楚平缝机怎样缝一针"}).json()
    vid = d["id"]
    d = settle(v3c, t, vid, lambda d: not d["busy"])
    assert d["version"] == 1 and d["chat"][-1]["who"] == "ai" and "weblab" in d["scene"]
    d = v3c.post(f"/api/v1/video3d/{vid}/say", headers=t, json={"text": "镜头再近一点"}).json()
    d = settle(v3c, t, vid, lambda d: not d["busy"])
    assert d["version"] == 2 and [c["who"] for c in d["chat"]] == ["me", "ai", "me", "ai"]
    r = v3c.put(f"/api/v1/video3d/{vid}/scene", headers=t, json={"scene": SCENE.replace("duration: 12", "duration: 999")})
    assert r.status_code == 422 and "duration" in r.json()["detail"]
    r = v3c.put(f"/api/v1/video3d/{vid}/scene", headers=t, json={"scene": SCENE.replace("平缝机一针, en", "改过的标题, en")})
    assert r.status_code == 200 and r.json()["title"]["zh"] == "改过的标题" and r.json()["version"] == 3


def test_no_machine_waits_then_gives_up_and_cancel_stops_the_machine(v3c):
    t = login(v3c, "t")
    vid = v3c.post("/api/v1/video3d", headers=t, json={"sample": "缝纫机一针"}).json()["id"]
    main.state.video3d_provider = v3.Mock(capacity=False)
    main.state.video3d = None
    v3c.post(f"/api/v1/video3d/{vid}/render", headers=t, json={"quality": "draft"})
    tick()
    d = v3c.get(f"/api/v1/video3d/{vid}", headers=t).json()["renders"]["draft"]
    assert d["state"] == "queued" and d["stage"] == "waiting_machine"
    svc = main.state.video3d
    svc.wait = 0
    run = svc.store.live_runs()[0]
    svc.store.update_run(run["id"], queued_at=run["queued_at"] - 5)
    tick()
    d = v3c.get(f"/api/v1/video3d/{vid}", headers=t).json()["renders"]["draft"]
    assert d["state"] == "failed" and "空闲机器" in d["error"]
    # 有机器了：开机后取消，机器关掉
    prov = svc.provider = v3.Mock()
    v3c.post(f"/api/v1/video3d/{vid}/render", headers=t, json={"quality": "draft"})
    tick()
    assert any(mm["on"] for mm in prov.machines.values())
    d = v3c.post(f"/api/v1/video3d/{vid}/render/draft/cancel", headers=t).json()
    assert d["renders"]["draft"]["state"] == "cancelled"
    tick()
    assert all(not mm["on"] for mm in prov.machines.values())
    assert [r["state"] for r in svc.store.runs()][0] == "cancelled"


def test_render_error_on_the_machine_is_shown_and_the_machine_stopped(v3c):
    t = login(v3c, "t")
    vid = v3c.post("/api/v1/video3d", headers=t, json={"sample": "缝纫机一针"}).json()["id"]
    prov = main.state.video3d_provider
    prov.box["fail"] = True
    v3c.post(f"/api/v1/video3d/{vid}/render", headers=t, json={"quality": "draft"})
    for _ in range(5):
        tick()
    d = v3c.get(f"/api/v1/video3d/{vid}", headers=t).json()["renders"]["draft"]
    assert d["state"] == "failed" and "boom" in d["error"]
    assert all(not mm["on"] for mm in prov.machines.values())


def test_lambda_picks_a_machine_with_capacity_and_registers_a_key():
    seen = []

    def lam(request: httpx.Request) -> httpx.Response:
        p = urlparse(str(request.url)).path
        seen.append((request.method, p, request.content and json.loads(request.content)))
        assert request.headers["authorization"] == "Bearer K"
        if p.endswith("/instance-types"):
            return httpx.Response(200, json={"data": {
                "gpu_1x_a10": {"instance_type": {"price_cents_per_hour": 86}, "regions_with_capacity_available": []},
                "gpu_1x_a6000": {"instance_type": {"price_cents_per_hour": 92},
                                 "regions_with_capacity_available": [{"name": "asia-south-1"}, {"name": "us-west-1"}]}}})
        if p.endswith("/ssh-keys"):
            return httpx.Response(200, json={"data": [] if request.method == "GET" else {"name": "wenquest-video3d"}})
        if p.endswith("/instance-operations/launch"):
            return httpx.Response(200, json={"data": {"instance_ids": ["i-1"]}})
        if p.endswith("/instances/i-1"):
            return httpx.Response(200, json={"data": {"status": "active", "jupyter_url": "https://j.lambda/?token=x", "jupyter_token": "x"}})
        return httpx.Response(200, json={"data": {}})

    async def go():
        lm = v3.Lambda(httpx.AsyncClient(transport=httpx.MockTransport(lam)), "K", "https://cloud.lambda.ai/api/v1",
                       "gpu_1x_a10,gpu_1x_a6000")
        m = await lm.launch("wq-video3d-x")
        st = await lm.status("i-1")
        await lm.stop("i-1")
        return m, st
    m, st = asyncio.run(go())
    assert m == {"pid": "i-1", "kind": "gpu_1x_a6000", "region": "us-west-1", "price_hour": 0.92}
    assert st == {"state": "running", "url": "https://j.lambda", "token": "x"}
    launch = next(b for meth, p, b in seen if p.endswith("/launch"))
    assert launch["ssh_key_names"] == ["wenquest-video3d"] and launch["instance_type_name"] == "gpu_1x_a6000"
    assert ("POST", "/api/v1/ssh-keys", {"name": "wenquest-video3d"}) in seen
    assert any(p.endswith("/terminate") and b == {"instance_ids": ["i-1"]} for _, p, b in seen)


def test_jupyter_files_go_up_as_base64_and_status_comes_back():
    put = {}

    def jup(request: httpx.Request) -> httpx.Response:
        p = urlparse(str(request.url)).path
        assert request.headers["authorization"] == "token T"
        if request.method == "PUT":
            put[p] = json.loads(request.content)
            return httpx.Response(201, json={})
        if p == "/api/contents/wq3d/status.json":
            return httpx.Response(200, json={"content": '{"stage": "render"}'})
        return httpx.Response(404)

    async def go():
        j = v3.Jupyter(httpx.AsyncClient(transport=httpx.MockTransport(jup)), "https://j.lambda", "T")
        await j.put("wq3d/bundle.tgz", b"\x00\x01")
        await j.put("wq3d/job/job.json", "{}")
        return await j.read_text("wq3d/status.json"), await j.read_text("wq3d/none.json")
    got, none = asyncio.run(go())
    assert put["/api/contents/wq3d"] == {"type": "directory"} and put["/api/contents/wq3d/job"] == {"type": "directory"}
    assert put["/api/contents/wq3d/bundle.tgz"] == {"type": "file", "format": "base64", "content": "AAE="}
    assert put["/api/contents/wq3d/job/job.json"]["format"] == "text"
    assert got == '{"stage": "render"}' and none is None
