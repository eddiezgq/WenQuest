"""第 39 轮第 6 步：问渠凸轮的 AI 起草接口——要登录、每天限次、每次留记录、凸轮服务回填校验结论。
模型用替身（不联网、不调真模型）；判定、校验、核对数字在凸轮服务里，见 services/cam/tests/test_ai.py。"""
import sqlite3
from pathlib import Path

from app import main
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login

DRAFT = {"segments": [{"kind": "rise", "deg": 100, "h": 40, "law": "cycloidal", "why": "平稳"},
                      {"kind": "dwell", "deg": None, "h": None, "law": None, "why": ""}],
         "advance_deg": None, "assumptions": [], "questions": ["停多久？"]}


def test_draft_needs_login_quota_and_log(client, monkeypatch):  # noqa: F811
    calls = []

    async def fake_json(**kw):
        calls.append(kw)
        return DRAFT if "Requirement sentence" in kw["prompt"] else {"sentences": ["压力角 39.05° 未超许用值。"]}

    monkeypatch.setattr(main.state.ai, "json", fake_json)
    monkeypatch.setattr(main.state.ai, "provider", "fake")
    monkeypatch.setattr(main.state.settings, "cam_ai_daily", 3)
    body = {"sentence": "前 100° 推出 40 mm，停一会儿，再退回", "follower": "translating", "laws": ["cycloidal", "poly345"]}
    assert client.post("/api/v1/cam/ai/draft", json=body).status_code == 401
    h = login(client, "s")
    r = client.post("/api/v1/cam/ai/draft", json=body, headers=h).json()
    assert r["draft"] == DRAFT and r["left_today"] == 2 and r["run"]
    # the schema limits the laws to the allowed list, the prompt carries the sentence and the follower
    seg = calls[0]["schema"]["properties"]["segments"]["items"]["properties"]
    assert seg["law"]["enum"] == ["cycloidal", "poly345", None]
    assert "前 100° 推出 40 mm" in calls[0]["prompt"] and "translating" in calls[0]["prompt"]
    r_id = r["run"]
    assert client.post(f"/api/v1/cam/ai/runs/{r_id}", json={"passed": False, "note": "空两处"}, headers=h).json()["ok"]
    t = client.post("/api/v1/cam/ai/explain", json={"title": "凸轮", "checks": [{"id": "pressure", "value": 39.05}]},
                    headers=h).json()
    assert t["sentences"] == ["压力角 39.05° 未超许用值。"] and t["left_today"] == 1
    client.post("/api/v1/cam/ai/describe", json={"title": "凸轮"}, headers=h)
    r = client.post("/api/v1/cam/ai/draft", json=body, headers=h)
    assert r.status_code == 429                                   # 3 a day in this test
    with sqlite3.connect(str(Path(main.state.settings.data_dir) / "cam_ai.db")) as c:
        rows = c.execute("select kind, input, ok, passed, note from runs order by id").fetchall()
    assert [x[0] for x in rows] == ["draft", "explain", "describe"]
    assert rows[0][1].startswith("前 100°") and rows[0][2] == 1 and rows[0][3] == 0 and rows[0][4] == "空两处"
    # someone else cannot set the verdict of this run
    other = login(client)
    assert client.post(f"/api/v1/cam/ai/runs/{r_id}", json={"passed": True}, headers=other).status_code == 404


def test_cookie_login_works_too(client, monkeypatch):  # noqa: F811
    async def fake_json(**kw):
        return DRAFT

    monkeypatch.setattr(main.state.ai, "json", fake_json)
    monkeypatch.setattr(main.state.ai, "provider", "fake")
    h = login(client, "s")
    tok = h["Authorization"].split(" ", 1)[1]
    client.cookies.set("wq_sso", tok)
    try:
        r = client.post("/api/v1/cam/ai/draft", json={"sentence": "转一圈升 10 mm 再回"})
        assert r.status_code == 200
    finally:
        client.cookies.clear()
