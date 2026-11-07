"""第 105 轮：问渠电子的 AI 起草接口——要登录、每天限次、每次留记录、服务回填校验结论；单元类型限在目录里。
模型用替身（不联网、不调真模型）；校验和判定在问渠电子（eda/wqeda/ai），见 eda/tests/test_ai.py。"""
import sqlite3
from pathlib import Path

from app import main
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login

CATALOG = {"spec": [{"key": "bus_voltage_v", "required": True}],
           "units": [{"type": "gate_drive", "params": [{"key": "RG_OHM"}]}],
           "fixed_units": [{"type": "mcu_core"}]}
DRAFT = {"spec": [{"key": "bus_voltage_v", "value": 48, "source": "requirement", "quote": "48 V", "why": ""}],
         "units": [], "questions": [], "unsupported": []}


def test_draft_needs_login_quota_and_log(client, monkeypatch):  # noqa: F811
    calls = []

    async def fake_json(**kw):
        calls.append(kw)
        return DRAFT

    monkeypatch.setattr(main.state.ai, "json", fake_json)
    monkeypatch.setattr(main.state.ai, "provider", "fake")
    monkeypatch.setattr(main.state.settings, "eda_ai_daily", 2)
    body = {"requirement": "48 V 的关节驱动板", "catalog": CATALOG}
    assert client.post("/api/v1/eda/ai/draft", json=body).status_code == 401
    h = login(client, "s")
    r = client.post("/api/v1/eda/ai/draft", json=body, headers=h).json()
    assert r["draft"] == DRAFT and r["left_today"] == 1 and r["run"]
    unit = calls[0]["schema"]["properties"]["units"]["items"]["properties"]
    assert unit["type"]["enum"] == ["gate_drive", "mcu_core"]                   # 单元类型只能是目录里的
    assert "48 V 的关节驱动板" in calls[0]["prompt"] and "RG_OHM" in calls[0]["prompt"]
    assert "Never invent a number" in calls[0]["system"]
    rid = r["run"]
    assert client.post(f"/api/v1/eda/ai/runs/{rid}", json={"passed": True, "note": "ok"}, headers=h).json()["ok"]
    body2 = dict(body, feedback={"fails": [{"name": "母线电容耐压"}]})
    client.post("/api/v1/eda/ai/draft", json=body2, headers=h)
    assert "母线电容耐压" in calls[1]["prompt"]
    assert client.post("/api/v1/eda/ai/draft", json=body, headers=h).status_code == 429
    with sqlite3.connect(str(Path(main.state.settings.data_dir) / "eda_ai.db")) as c:
        rows = c.execute("select kind, input, ok, passed from runs order by id").fetchall()
    assert [x[0] for x in rows] == ["draft", "revise"] and rows[0][3] == 1
    other = login(client)
    assert client.post(f"/api/v1/eda/ai/runs/{rid}", json={"passed": False}, headers=other).status_code == 404


def test_catalog_must_have_units(client, monkeypatch):  # noqa: F811
    async def fake_json(**kw):
        return DRAFT

    monkeypatch.setattr(main.state.ai, "json", fake_json)
    h = login(client, "s")
    r = client.post("/api/v1/eda/ai/draft", json={"requirement": "随便一块板", "catalog": {}}, headers=h)
    assert r.status_code == 400


def test_issues_cite_only_open_results_and_log_no_files(client, monkeypatch):  # noqa: F811
    """第 112 轮：工厂端问题单——只把未通过的检查结果交给模型，引用编号限在这些结果里；记录里不记结果内容"""
    calls = []

    async def fake_json(**kw):
        calls.append(kw)
        return {"issues": [{"cites": ["R1"], "question": "C47 要不要贴？", "options": ["贴", "不贴"],
                            "reply_required": True}]}

    monkeypatch.setattr(main.state.ai, "json", fake_json)
    monkeypatch.setattr(main.state.ai, "provider", "fake")
    results = [{"id": "R1", "key": "D1", "name": "位号对上", "status": "fail", "refs": ["C47"], "detail": "C47 只在坐标里"},
               {"id": "R2", "key": "F1", "name": "最小线宽", "status": "pass", "refs": []}]
    body = {"results": results, "factory": "示例贴片厂"}
    assert client.post("/api/v1/eda/ai/issues", json=body).status_code == 401
    h = login(client, "s")
    r = client.post("/api/v1/eda/ai/issues", json=body, headers=h).json()
    assert r["draft"]["issues"][0]["cites"] == ["R1"]
    cites = calls[0]["schema"]["properties"]["issues"]["items"]["properties"]["cites"]["items"]["enum"]
    assert cites == ["R1"] and "R2" not in calls[0]["prompt"] and "C47 只在坐标里" in calls[0]["prompt"]
    assert "Never mention a problem that is not in the results" in calls[0]["system"]
    with sqlite3.connect(str(Path(main.state.settings.data_dir) / "eda_ai.db")) as c:
        kind, inp = c.execute("select kind, input from runs order by id desc limit 1").fetchone()
    assert kind == "issues" and "C47" not in inp and "1 条结果" in inp
    only_pass = {"results": [results[1]]}
    assert client.post("/api/v1/eda/ai/issues", json=only_pass, headers=h).status_code == 400
