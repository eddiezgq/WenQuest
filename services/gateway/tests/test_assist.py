"""第 87 轮：问渠客服——考题（检索档前 3 条命中率）、接口、限流、国内站过滤。"""
from pathlib import Path

import yaml

from app.assist import load_index
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login

QS = yaml.safe_load((Path(__file__).parent / "data" / "assist_questions.yaml").read_text(encoding="utf-8"))


def score(region: str):
    idx, ok, miss = load_index(region), 0, []
    qs = [x for x in QS if x.get("site", "both") in ("both", region)]
    for x in qs:
        top = [c["doc"] for _, c in idx.search(x["q"], k=3)]
        if set(top) & set(x["want"]):
            ok += 1
        else:
            miss.append((x["q"], top))
    return ok, len(qs), miss


def test_exam_us():
    ok, n, miss = score("us")
    assert n >= 50 and ok / n >= 0.9, miss


def test_exam_cn():
    ok, n, miss = score("cn")
    assert n >= 40 and ok / n >= 0.9, miss
    # 国内站只用不含禁用词的段落
    for c in load_index("cn").chunks:
        assert "Claude" not in c["text"] and "wenquestrobotics" not in c["text"]


def test_endpoint_and_log(client):  # noqa: F811
    r = client.post("/api/v1/public/assist", json={"q": "怎么出G代码", "page": "/", "lang": "zh"}).json()
    assert r["sources"] and any(x["url"] == "/help/" + x["url"][6:] for x in r["sources"])
    assert r["mode"] in ("ai", "search")
    r = client.post("/api/v1/public/assist", json={"q": "凸轮怎么设计", "lang": "zh", "ai": False}).json()
    assert r["mode"] == "search" and not r["answer"]
    log = client.get("/api/v1/admin/assist-log", headers=login(client)).json()
    assert log["count"] >= 2 and "ip" not in log["rows"][0]
    assert client.get("/api/v1/admin/assist-log", headers=login(client, "s")).status_code == 403


def test_rate_limit(client):  # noqa: F811
    codes = [client.post("/api/v1/public/assist", json={"q": "白板课", "ai": False},
                         headers={"X-Forwarded-For": "10.9.9.9"}).status_code for _ in range(22)]
    assert codes[:20] == [200] * 20 and codes[20] == 429


def test_cn_search_only_until_registered(client, monkeypatch):  # noqa: F811
    from app.main import state
    monkeypatch.setattr(state.ai, "provider", "fake")
    s = state.settings
    old = (s.region, s.ai_reg)
    try:
        s.region, s.ai_reg = "cn", ""
        r = client.post("/api/v1/public/assist", json={"q": "凸轮怎么设计", "lang": "zh"}).json()
        assert r["mode"] == "search" and r["sources"] and all(x["url"] is None for x in r["sources"])
        assert not any("wenquestrobotics" in x["snippet"] or "Claude" in x["snippet"] for x in r["sources"])
        s.ai_reg = "沪网信算备000000000000000号"
        r = client.post("/api/v1/public/assist", json={"q": "凸轮怎么设计", "lang": "zh"}).json()
        assert r["mode"] == "ai" and r["ai_label"]
    finally:
        s.region, s.ai_reg = old
