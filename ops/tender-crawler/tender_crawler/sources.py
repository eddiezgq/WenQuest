"""抓取器。每个抓取器返回"列表项"字典：title, url, date, source, 以及能拿到的 region / buyer / type_text。
网站改版时只需改这里（或在 config.yaml 用 html_list 通用抓取器配置选择器）。"""
import json
import logging
from datetime import date, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .extract import normalize_date

log = logging.getLogger(__name__)


def _days(cfg):
    from .main import today_cst
    end = today_cst()
    return end - timedelta(days=int(cfg["run"].get("days_back", 2))), end


def ccgp_search(http, src, cfg, keyword):
    """中国政府采购网 全文检索（公开搜索页）。"""
    start, end = _days(cfg)
    for page in range(1, int(cfg["run"].get("max_pages_per_query", 3)) + 1):
        params = {"searchtype": 1, "page_index": page, "bidSort": 0, "pinMu": 0, "bidType": 0, "dbselect": "bidx",
                  "kw": keyword, "start_time": start.strftime("%Y:%m:%d"), "end_time": end.strftime("%Y:%m:%d"),
                  "timeType": 6, "displayZone": "", "zoneId": "", "pppStatus": 0, "agentName": ""}
        r = http.get(src["base_url"], params=params)
        items = list(parse_ccgp(r.text, src))
        yield from items
        if len(items) < 20:
            break


def parse_ccgp(html, src):
    soup = BeautifulSoup(html, "lxml")
    for li in soup.select("ul.vT-srch-result-list-bid li"):
        a = li.find("a")
        if not a or not a.get("href"):
            continue
        meta = li.find("span").get_text(" ", strip=True) if li.find("span") else ""
        strongs = [s.get_text(strip=True) for s in li.find_all("strong")]
        buyer = None
        for part in meta.split("|"):
            if "采购人" in part:
                buyer = part.split("：", 1)[-1].split(":", 1)[-1].strip()
        region = None
        for a2 in li.select("span a"):
            region = a2.get_text(strip=True) or region
        yield {"title": a.get_text(" ", strip=True), "url": urljoin(src["base_url"], a["href"]),
               "date": normalize_date(meta), "buyer": buyer, "region": region,
               "type_text": " ".join(strongs), "source": src["name"]}


def ggzy_deal(http, src, cfg, keyword):
    """全国公共资源交易平台 交易公开列表（公开查询接口）。"""
    start, end = _days(cfg)
    for page in range(1, int(cfg["run"].get("max_pages_per_query", 3)) + 1):
        data = {"TIMEBEGIN_SHOW": start.isoformat(), "TIMEEND_SHOW": end.isoformat(), "TIMEBEGIN": start.isoformat(),
                "TIMEEND": end.isoformat(), "SOURCE_TYPE": 1, "DEAL_TIME": "06", "DEAL_CLASSIFY": "00",
                "DEAL_STAGE": "0000", "DEAL_PROVINCE": 0, "DEAL_CITY": 0, "DEAL_PLATFORM": 0, "BID_PLATFORM": 0,
                "DEAL_TRADE": 0, "isShowAll": 1, "PAGENUMBER": page, "FINDTXT": keyword}
        r = http.post(src["base_url"], data=data)
        items, pages = parse_ggzy(r.text, src)
        yield from items
        if page >= pages:
            break


def parse_ggzy(text, src):
    try:
        js = json.loads(text)
    except ValueError:
        log.warning("%s 返回的不是 JSON，可能已改版", src["name"])
        return [], 0
    out = []
    for d in js.get("data") or []:
        url = d.get("url") or ""
        out.append({"title": (d.get("title") or "").strip(), "url": urljoin("http://www.ggzy.gov.cn/", url),
                    "date": normalize_date(d.get("timeShow") or ""), "region": d.get("districtShow"),
                    "buyer": None, "type_text": " ".join(filter(None, [d.get("stageShow"), d.get("classifyShow")])),
                    "source": src["name"]})
    return out, int(js.get("ttlpage") or 1)


def html_list(http, src, cfg, keyword=None):
    """通用列表页：按 CSS 选择器取标题、链接、日期。keyword 不用于请求（列表页不支持搜索），在本地过滤。"""
    for page in range(1, int(cfg["run"].get("max_pages_per_query", 3)) + 1):
        url = src["list_url"].format(page=page)
        r = http.get(url)
        items = list(parse_html_list(r.text, src, url))
        yield from items
        if not items or "{page}" not in src["list_url"]:
            break


def parse_html_list(html, src, page_url):
    soup = BeautifulSoup(html, "lxml")
    for it in soup.select(src["item"]):
        t = it.select_one(src["title"])
        link = it.select_one(src.get("link", src["title"]))
        if not t or not link or not link.get("href"):
            continue
        d = it.select_one(src["date"]) if src.get("date") else None
        yield {"title": (t.get("title") or t.get_text(" ", strip=True)).strip(),
               "url": urljoin(page_url, link["href"]), "date": normalize_date(d.get_text() if d else ""),
               "region": src.get("region"), "buyer": src.get("buyer"), "type_text": "", "source": src["name"]}


FETCHERS = {"ccgp_search": ccgp_search, "ggzy_deal": ggzy_deal, "html_list": html_list}
SEARCHABLE = {"ccgp_search", "ggzy_deal"}  # 支持按关键词搜索；其余为列表页，一次抓完本地过滤
