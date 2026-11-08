"""离线测试：用页面样本验证解析、规则提取、过滤、去重和输出。运行：python -m pytest -q tests"""
import json
from datetime import date
from pathlib import Path

import pytest
import yaml

from tender_crawler import extract, main, sources
from tender_crawler.http import BlockedError, PoliteSession
from tender_crawler.store import Store

FX = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).parent.parent


class Resp:
    def __init__(self, text):
        self.text = text


class FakeHttp:
    """按网址返回样本页面；记录请求次数。"""
    def __init__(self, routes, blocked=()):
        self.routes, self.blocked, self.requests = routes, blocked, 0

    def _pick(self, url):
        self.requests += 1
        for k in self.blocked:
            if k in url:
                raise BlockedError("HTTP 403 " + url)
        for k, v in self.routes.items():
            if k in url:
                return Resp(v)
        raise AssertionError("unexpected url " + url)

    def get(self, url, **kw):
        return self._pick(url)

    def post(self, url, **kw):
        return self._pick(url)


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    c = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    c["output"]["dir"] = str(tmp_path)
    c["run"]["max_pages_per_query"] = 1
    c["keywords"] = {"engineering": ["MES"], "education": ["虚拟仿真实验", "智慧课堂", "数字教材", "教学平台"]}
    c["sources"] = [
        {"name": "中国政府采购网", "type": "ccgp_list", "enabled": True, "max_pages": 5,
         "lists": ["http://www.ccgp.gov.cn/cggg/dfgg/gkzb/"]},
        {"name": "全国公共资源交易平台", "type": "ggzy_deal", "enabled": True,
         "base_url": "https://www.ggzy.gov.cn/information/pubTradingInfo/getTradList"},
        {"name": "中国政府采购网检索", "type": "ccgp_search", "enabled": True, "base_url": "http://search.ccgp.gov.cn/bxsearch"},
        {"name": "示例高校", "type": "html_list", "enabled": True,
                         "list_url": "https://u.example.edu.cn/list{page}.htm", "item": "ul.news-list li",
                         "title": "a", "link": "a", "date": "span.date", "region": "上海", "buyer": "示例大学"}]
    monkeypatch.setattr(main, "today_cst", lambda: date(2026, 11, 8))
    return c


def routes():
    return {"search.ccgp.gov.cn": (FX / "ccgp.html").read_text(encoding="utf-8"),
            "cggg/dfgg/gkzb/index": (FX / "ccgp_list.html").read_text(encoding="utf-8"),
            "pubTradingInfo/getTradList": (FX / "ggzy.json").read_text(encoding="utf-8"),
            "u.example.edu.cn": (FX / "list.html").read_text(encoding="utf-8"),
            "ccgp.gov.cn/cggg": (FX / "detail.html").read_text(encoding="utf-8")}


def test_extract_rules():
    t = (FX / "detail.html").read_text(encoding="utf-8")
    assert extract.budget_cny(t) == pytest.approx(3865000)
    assert extract.budget_cny("最高限价：1,200,000元") == 1200000
    assert extract.deadline(t) == "2026-11-28 09:30"
    assert extract.buyer(t) == "上海理工大学"
    assert extract.notice_type("某某中标公告") == "result"
    assert extract.notice_type("竞争性磋商公告") == "negotiation"
    assert extract.notice_type("2026年采购意向公开") == "intention"
    assert extract.keyword_hits("采购mes系统", {"e": ["MES"]}) == (["e"], ["MES"])


def test_run_end_to_end(cfg, monkeypatch):
    http = FakeHttp(routes())
    monkeypatch.setattr(main, "PoliteSession", lambda c: http)
    feed = main.cmd_run(cfg)
    titles = [r["title"] for r in feed["items"]]
    assert "上海理工大学虚拟仿真实验教学平台建设项目公开招标公告" in titles
    assert "浙江工业大学智能制造MES实训平台采购项目" in titles
    assert "示例大学数字教材建设项目询价公告" in titles          # 列表页抓取器
    hd = next(r for r in feed["items"] if r["title"] == "华东理工大学智慧课堂建设项目公开招标公告")  # 政府采购网公告列表
    assert (hd["region"], hd["buyer"], hd["notice_type"], hd["publish_date"]) == ("上海", "华东理工大学", "tender", "2026-11-08")
    assert "华东理工大学" in hd["focus"]
    assert not any("某学院教学平台" in t for t in titles)         # 列表里超出时间窗口的
    mes = next(r for r in feed["items"] if "MES" in r["title"])
    assert mes["region"] == "浙江" and mes["url"].startswith("https://www.ggzy.gov.cn/information/deal/")
    assert not any("保洁" in t or "施工" in t for t in titles)  # 排除词
    assert not any("ERP系统" in t for t in titles)              # 超出时间窗口
    top = feed["items"][0]
    assert top["title"].startswith("华东理工大学")               # 重点高校 + 新增 + 招标类 + 最新发布排第一
    assert top["focus"] and top["is_new"] and not top["is_result"]
    top = next(r for r in feed["items"] if r["title"].startswith("上海理工大学"))
    assert (top["budget_cny"], top["deadline"], top["buyer"]) == (3865000, "2026-11-28 09:30", "上海理工大学")
    assert "上海理工大学" in top["focus"] and top["is_new"]
    res = [r for r in feed["items"] if r["is_result"]]
    assert res and res[-1] is feed["items"][-1]                 # 结果公告排最后
    assert all(s["status"] == "ok" for s in feed["sources"] if s["status"] != "disabled")
    out = Path(cfg["output"]["dir"])
    assert json.loads((out / "latest.json").read_text(encoding="utf-8"))["schema"] == "tender-feed/1"
    assert "新增（招标 / 采购类）" in (out / "latest.md").read_text(encoding="utf-8")
    # 同一天重跑：结果一致（"新增"按首次发现日期计算，跨天去重见 test_store_dedup）
    feed2 = main.cmd_run(cfg)
    assert feed2["summary"]["total"] == feed["summary"]["total"]


def test_blocked_source_does_not_stop_others(cfg, monkeypatch):
    http = FakeHttp(routes(), blocked=("search.ccgp.gov.cn",))
    monkeypatch.setattr(main, "PoliteSession", lambda c: http)
    feed = main.cmd_run(cfg)
    st = {s["name"]: s for s in feed["sources"]}
    assert st["中国政府采购网检索"]["status"] == "blocked"
    assert st["中国政府采购网检索"]["requests"] == 1            # 被拦后不再重试
    assert st["全国公共资源交易平台"]["status"] == "ok"
    assert st["中国政府采购网"]["status"] == "ok"
    assert st["中国政府采购网"]["requests"] == 1                # 第一页已翻到窗口之前，不再翻页
    assert feed["summary"]["total"] >= 2


def test_politeness_detects_captcha(monkeypatch):
    s = PoliteSession({"politeness": {"min_interval_seconds": 0, "jitter_seconds": 0, "respect_robots_txt": False}})

    class R:
        status_code, encoding, text = 200, "utf-8", "<html>请输入验证码</html>"

        def raise_for_status(self):
            pass
    monkeypatch.setattr(s.s, "request", lambda *a, **k: R())
    with pytest.raises(BlockedError):
        s.get("https://example.gov.cn/")


def test_store_dedup(tmp_path):
    st = Store(str(tmp_path / "s.db"))
    it = {"url": "http://a/1", "title": "t"}
    assert st.first_seen(it, "2026-11-07")[1] == "2026-11-07"
    assert st.first_seen(it, "2026-11-08")[1] == "2026-11-07"


def test_config_check():
    assert main.main(["-c", str(ROOT / "config.yaml"), "check"]) == 0


def test_ggzy_captcha_is_blocked():
    with pytest.raises(BlockedError):
        sources.parse_ggzy('{"code": 829, "captchaToken": "x", "captchaImage": ""}', {"name": "交易平台"})


def test_ccgp_list_section_error_keeps_others(cfg):
    class H(FakeHttp):
        def get(self, url, **kw):
            if "/jzxcs/" in url:
                self.requests += 1
                raise ConnectionError("boom")
            return super().get(url, **kw)
    src = {"name": "中国政府采购网", "type": "ccgp_list", "max_pages": 3,
           "lists": ["http://www.ccgp.gov.cn/cggg/dfgg/jzxcs/", "http://www.ccgp.gov.cn/cggg/dfgg/gkzb/"]}
    got = []
    with pytest.raises(RuntimeError, match="jzxcs"):
        for it in sources.ccgp_list(H(routes()), src, cfg):
            got.append(it)
    assert len(got) == 3 and got[0]["type_text"] == "公开招标"
