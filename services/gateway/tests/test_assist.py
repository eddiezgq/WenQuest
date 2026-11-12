"""第 87 轮：问渠客服——考题（检索档前 3 条命中率）、接口、限流、国内站过滤。"""
from pathlib import Path

import yaml

from app.assist import FAQ_MIN, load_faq, load_index
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login

QS = yaml.safe_load((Path(__file__).parent / "data" / "assist_questions.yaml").read_text(encoding="utf-8"))


def score(region: str):
    """先看常见问答库有没有直接答上（faq:<编号>），没有再看检索前 3 条"""
    idx, faq, ok, miss = load_index(region), load_faq(region), 0, []
    qs = [x for x in QS if x.get("site", "both") in ("both", region)]
    for x in qs:
        fs, f = faq.match(x["q"])
        top = [f"faq:{f['id'].removeprefix('faq-')}"] if f is not None and fs >= FAQ_MIN else \
            [c["doc"] for _, c in idx.search(x["q"], k=3)]
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
    assert r["mode"] == "search" and r["answer"] and len(r["sources"]) <= 3   # 原文里摘一两句作直接回答
    log = client.get("/api/v1/admin/assist-log", headers=login(client)).json()
    assert log["count"] >= 2 and "ip" not in log["rows"][0]
    assert client.get("/api/v1/admin/assist-log", headers=login(client, "s")).status_code == 403


def test_rate_limit(client):  # noqa: F811
    codes = [client.post("/api/v1/public/assist", json={"q": "白板课", "ai": False},
                         headers={"X-Forwarded-For": "10.9.9.9"}).status_code for _ in range(22)]
    assert codes[:20] == [200] * 20 and codes[20] == 429


def test_cn_ai_switch(client, monkeypatch):  # noqa: F811
    """11-06 Eddie：国内站也开大模型（只用 DeepSeek）；WQ_ASSIST_CN_AI=0 可以关掉。出处不给链接、不含禁用词。"""
    from app.main import state
    monkeypatch.setattr(state.ai, "provider", "fake")
    s = state.settings
    old = s.region
    try:
        s.region = "cn"
        r = client.post("/api/v1/public/assist", json={"q": "凸轮怎么设计", "lang": "zh"}).json()
        assert r["mode"] == "ai" and r["ai_label"]
        monkeypatch.setenv("WQ_ASSIST_CN_AI", "0")
        r = client.post("/api/v1/public/assist", json={"q": "凸轮怎么设计", "lang": "zh"}).json()
        assert r["mode"] == "search" and r["sources"] and all(x["url"] is None for x in r["sources"])
        assert not any("wenquestrobotics" in x["snippet"] or "Claude" in x["snippet"] for x in r["sources"])
    finally:
        s.region = old


def test_faq_first_and_no_junk(client, monkeypatch):  # noqa: F811
    """返修（第 87 轮第十节）：常见问题直接给标准答案；对不上的不再堆不相干的片段。"""
    from app.main import state
    s = state.settings
    old = s.region
    try:
        s.region = "cn"
        r = client.post("/api/v1/public/assist", json={"q": "管理员能打开erp吗", "lang": "zh"}).json()
        assert r["mode"] == "faq" and "质量 ERP" in r["answer"] and r["sources"][0]["url"] == "/contact/"
        r = client.post("/api/v1/public/assist", json={"q": "How much does it cost?", "lang": "en"}).json()
        assert r["mode"] == "faq" and "price" in r["answer"].lower()
        for q in ("今天天气怎么样", "火星上有没有工厂"):
            r = client.post("/api/v1/public/assist", json={"q": q, "lang": "zh", "ai": False}).json()
            assert r["unsure"] and not r["sources"], (q, r)
    finally:
        s.region = old
    # 国内站的问答不含国内版官网禁用词，美国站的不提国内网址
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "site_cn"))
    from check_cn import BANNED
    for f in load_faq("cn").items:
        a = f[0]["a"]["zh"]
        assert not [w for w in BANNED if w in a], (f[0]["id"], a)


def test_every_site_page_has_the_assistant():
    """第 154 轮：官网每一页右下角都有问渠客服（Google 验证文件、离线版演示稿除外）；
    数字工业园各厂的网页也加载同一个 assist.js（前门把 /assist.js 和问答接口转给网关）。"""
    root = Path(__file__).resolve().parents[3]
    site = root / "site"
    skip = ("google", "演示稿-离线版")
    missing = [str(f.relative_to(site)) for f in sorted(site.rglob("*.html"))
               if f.relative_to(site).parts[0] not in ("cn", "vendor")
               and not any(k in f.name for k in skip)
               and "assist.js" not in f.read_text(encoding="utf-8")]
    assert not missing, f"这些页面没有 <script src=\"/assist.js\" defer></script>：{missing}"
    cn = [str(f.relative_to(site)) for f in sorted((site / "cn").rglob("*.html")) if "assist.js" not in f.read_text(encoding="utf-8")]
    assert not cn or cn == ["404.html"], f"国内官网缺：{cn}"
    assert '<script src="/assist.js" defer></script>' in (root / "factory/digital/web/index.html").read_text(encoding="utf-8")
    caddy = (root / "deploy/Caddyfile").read_text(encoding="utf-8")
    assert caddy.count("import assist_widget") >= 3
