#!/usr/bin/env bash
# 只读诊断（少量访问公开页面，不重试、不绕过）：看公共资源交易平台接口参数和一次查询结果、政府采购网列表页结构。
APP="$HOME/tender-crawler"; IMG=$(cat "$APP/image.txt")
docker run -i --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONPATH=/app/pylib -v "$APP":/app -w /app "$IMG" python - "$@" <<'PY'
import time, re, json, requests
UA = "Mozilla/5.0 (compatible; TenderWatch/1.0; public announcements only)"
s = requests.Session(); s.headers["User-Agent"] = UA
sq = lambda x: re.sub(r"\s+", " ", x)
API = "https://www.ggzy.gov.cn/information/pubTradingInfo/getTradList"
H = {"Referer": "https://www.ggzy.gov.cn/deal/dealList.html"}
for form in [{"SOURCE_TYPE": "1", "DEAL_TIME": "02", "PAGENUMBER": "1"},
             {"SOURCE_TYPE": "1", "DEAL_TIME": "02", "FINDTXT": "软件", "PAGENUMBER": "1"},
             {"SOURCE_TYPE": "1", "DEAL_TIME": "06", "TIMEBEGIN": "2026-11-06", "TIMEEND": "2026-11-09", "FINDTXT": "平台", "PAGENUMBER": "2"}]:
    r = s.post(API, data=form, headers=H, timeout=20)
    try:
        js = r.json(); d = js.get("data") or {}
        print("== ", form, "→ code", js.get("code"), "total", d.get("total"), "pages", d.get("pages"), "size", d.get("size"))
        for rec in (d.get("records") or [])[:2]: print("   记录:", json.dumps(rec, ensure_ascii=False)[:700])
    except Exception as e:
        print("== ", form, "非 JSON", r.status_code, sq(r.text[:300]))
    time.sleep(5)
for u in ["http://www.ccgp.gov.cn/cggg/dfgg/gkzb/index_1.htm", "http://www.ccgp.gov.cn/robots.txt", "https://www.ggzy.gov.cn/robots.txt"]:
    r = s.get(u, timeout=20); r.encoding = "utf-8"; t = r.text
    lis = re.findall(r"发布时间：<em>([^<]+)</em>", t)
    print("== ", u, "HTTP", r.status_code, "条目", len(lis), "首末", lis[:1], lis[-1:], "| 翻页:", re.findall(r"createPageHTML\([^)]*\)|countPage\s*=\s*\d+", t)[:3])
    if "robots" in u: print("   ", sq(t[:400]))
    time.sleep(5)
PY
