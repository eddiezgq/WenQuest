"""第 64 轮第 7 步（7c）：问渠轴承的 AI 起草接口——只给开通企业授权的单位（Eddie 11-04 定）；每天限次；每次留记录（含单位）；
轴承服务回填检查结论；别人改不了这条记录。模型用替身（不联网）；字段与数字的检查在轴承服务里，见 services/bearing/tests/test_ai.py。"""
import sqlite3
from pathlib import Path

from app import main
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login
from tests.test_sewing_api import UID, sc  # noqa: F401

DRAFT = {"kind": "gearbox", "values": [{"path": "scenario.mn", "value": 3, "quote": "法向模数 3"}],
         "assumptions": [], "questions": ["齿轮离 A 轴承多远？"]}
KINDS = {"gearbox": {"fields": [{"path": "scenario.mn", "label": "法向模数 mn", "unit": "mm"}]}}


def test_only_licensed_companies_quota_and_log(sc, monkeypatch):  # noqa: F811
    c = sc
    calls = []

    async def fake_json(**kw):
        calls.append(kw)
        return DRAFT if "Sentence:" in kw["prompt"] else {"sentences": ["外圈最大接触应力 1850 MPa。"]}

    monkeypatch.setattr(main.state.ai, "json", fake_json)
    monkeypatch.setattr(main.state.ai, "provider", "fake")
    monkeypatch.setenv("WQ_BEARING_AI_DAILY", "3")
    body = {"sentence": "减速器斜齿轮轴，法向模数 3，齿数 34", "kinds": KINDS, "bearing": "deep_groove"}
    assert c.post("/api/v1/bearing/ai/draft", json=body).status_code == 401
    s = login(c, "s")
    assert c.post("/api/v1/bearing/ai/draft", json=body, headers=s).status_code == 403     # 登录了、没开通
    admin = login(c)
    UID["s"] = c.get("/api/v1/me", headers=s).json()["id"]
    assert c.post("/api/v1/admin/sewing/licenses", json={"username": "s", "org": "甲轴承厂"}, headers=admin).json()["ok"]
    r = c.post("/api/v1/bearing/ai/draft", json=body, headers=s).json()
    assert r["draft"] == DRAFT and r["left_today"] == 2 and r["run"]
    assert "法向模数 3" in calls[0]["prompt"] and "scenario.mn" in calls[0]["prompt"] and "deep_groove" in calls[0]["prompt"]
    assert "Never invent a number" in calls[0]["system"] and "catalogue number" in calls[0]["system"]
    rid = r["run"]
    assert c.post(f"/api/v1/bearing/ai/runs/{rid}", json={"passed": False, "note": "缺 x"}, headers=s).json()["ok"]
    t = c.post("/api/v1/bearing/ai/explain", json={"title": "6206", "checks": [{"id": "p_outer", "value": 1850}]},
               headers=s).json()
    assert t["sentences"] == ["外圈最大接触应力 1850 MPa。"] and t["left_today"] == 1
    c.post("/api/v1/bearing/ai/describe", json={"title": "6206"}, headers=s)
    assert c.post("/api/v1/bearing/ai/draft", json=body, headers=s).status_code == 429
    with sqlite3.connect(str(Path(main.state.settings.data_dir) / "bearing_ai.db")) as db:
        rows = db.execute("select kind, input, org, ok, passed, note from runs order by id").fetchall()
    assert [x[0] for x in rows] == ["draft", "explain", "describe"]
    assert rows[0][1].startswith("减速器") and rows[0][2] == "甲轴承厂" and rows[0][4] == 0 and rows[0][5] == "缺 x"
    # the admin (问渠) is licensed too, but cannot set the verdict of 张工's run
    assert c.post(f"/api/v1/bearing/ai/runs/{rid}", json={"passed": True}, headers=admin).status_code == 404
