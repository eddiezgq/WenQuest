"""抓取器。每个抓取器返回"列表项"字典：title, url, date, source, 以及能拿到的 region / buyer / type_text。
网站改版时只需改这里（或在 config.yaml 用 html_list 通用抓取器配置选择器）。"""
import json
import logging
import re
from datetime import date, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import requests

from .extract import normalize_date
from .http import BlockedError

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
    """全国公共资源交易平台 交易公开查询接口（2026 年新版 www.ggzy.gov.cn，按标题关键词 + 日期范围）。
    接口要求输入验证码（code 829）时当天停止，不绕过。"""
    start, end = _days(cfg)
    for page in range(1, int(cfg["run"].get("max_pages_per_query", 3)) + 1):
        data = {"SOURCE_TYPE": "1", "DEAL_TIME": "06", "TIMEBEGIN": start.isoformat(), "TIMEEND": end.isoformat(),
                "FINDTXT": keyword, "PAGENUMBER": str(page)}
        r = http.post(src["base_url"], data=data,
                      headers={"Referer": src.get("referer", "https://www.ggzy.gov.cn/deal/dealList.html")})
        items, pages = parse_ggzy(r.text, src)
        yield from items
        if page >= pages:
            break


_PROV_SUFFIX = re.compile(r"(省|市|壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区)$")


def parse_ggzy(text, src):
    try:
        js = json.loads(text)
    except ValueError:
        raise RuntimeError(f"{src['name']} 返回的不是 JSON，可能已改版")
    code = js.get("code")
    if code == 829:
        raise BlockedError("接口要求输入验证码")
    if code not in (200, None):
        raise RuntimeError(f"接口返回 {code}：{js.get('message')}")
    d = js.get("data") or {}
    out = []
    for rec in d.get("records") or []:
        out.append({"title": (rec.get("title") or "").strip(),
                    "url": urljoin("https://www.ggzy.gov.cn/", rec.get("url") or ""),
                    "date": normalize_date(rec.get("publishTime") or ""),
                    "region": _PROV_SUFFIX.sub("", rec.get("provinceText") or "") or None, "buyer": None,
                    "type_text": " ".join(filter(None, [rec.get("businessTypeText"), rec.get("informationTypeText")])),
                    "source": src["name"]})
    return out, int(d.get("pages") or 1)


CCGP_SECTION_TYPES = {"gkzb": "公开招标", "jzxcs": "竞争性磋商", "jzxtp": "竞争性谈判", "xjgg": "询价",
                      "dylygg": "单一来源", "yqzbgg": "邀请招标", "gzgg": "更正公告"}


def ccgp_list(http, src, cfg, keyword=None):
    """中国政府采购网 公告列表页（www.ccgp.gov.cn/cggg/...，静态页，index.htm、index_1.htm…）。
    列表不支持搜索：按日期往回翻到时间窗口之前为止，关键词在本地过滤。某个栏目出错不影响其他栏目。"""
    start = _days(cfg)[0].isoformat()
    failed = []
    for base in src["lists"]:
        try:
            for page in range(int(src.get("max_pages", 30))):
                url = urljoin(base, "index.htm" if page == 0 else f"index_{page}.htm")
                try:
                    r = http.get(url)
                except requests.HTTPError as e:
                    if e.response is not None and e.response.status_code == 404:
                        break  # 翻到最后一页之后
                    raise
                items = list(parse_ccgp_list(r.text, src, url))
                yield from items
                dates = [i["date"] for i in items if i["date"]]
                if not items or (dates and min(dates) < start):
                    break
        except BlockedError:
            raise
        except Exception as e:  # noqa: BLE001
            log.warning("%s 栏目 %s 出错：%s", src["name"], base, e)
            failed.append(base.rstrip("/").rsplit("/", 2)[-1] or base)
    if failed:
        raise RuntimeError("这些栏目出错：" + "、".join(failed))


def parse_ccgp_list(html, src, page_url):
    soup = BeautifulSoup(html, "lxml")
    sec = next((v for k, v in CCGP_SECTION_TYPES.items() if f"/{k}/" in page_url), "")
    for li in soup.select("ul.c_list_bid li"):
        a = li.find("a", href=True)
        if not a:
            continue
        text = li.get_text(" ", strip=True)
        bx = li.find("em", attrs={"rel": "bxlx"})
        reg = re.search(r"地域：\s*([^\s：:]+)(?=\s|$)", text)
        buyer = re.search(r"采购人：\s*(.+)$", text)
        m = re.search(r"发布时间：\s*([0-9-]+)", text)
        yield {"title": (a.get("title") or a.get_text(" ", strip=True)).strip(), "url": urljoin(page_url, a["href"]),
               "date": normalize_date(m.group(1) if m else ""), "region": reg.group(1) if reg and not reg.group(1).startswith("采购人") else None,
               "buyer": buyer.group(1).strip() if buyer else None,
               "type_text": (bx.get_text(strip=True) if bx else "") or sec, "source": src["name"]}


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


FETCHERS = {"ccgp_search": ccgp_search, "ccgp_list": ccgp_list, "ggzy_deal": ggzy_deal, "html_list": html_list}
SEARCHABLE = {"ccgp_search", "ggzy_deal"}  # 支持按关键词搜索；其余为列表页，一次抓完本地过滤
