#!/usr/bin/env bash
# 只读诊断（少量访问公开页面，不重试、不绕过）：看公共资源交易平台接口参数和一次查询结果、政府采购网列表页结构。
APP="$HOME/tender-crawler"; IMG=$(cat "$APP/image.txt")
docker run -i --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONPATH=/app/pylib -v "$APP":/app -w /app "$IMG" python - "$@" <<'PY'
import time, re, json, requests
UA = "Mozilla/5.0 (compatible; TenderWatch/1.0; public announcements only)"
s = requests.Session(); s.headers["User-Agent"] = UA
sq = lambda x: re.sub(r"\s+", " ", x)
r = s.get("https://www.ggzy.gov.cn/deal/dealList.html", timeout=20); r.encoding = "utf-8"; t = r.text
i = t.find("formObject"); print("== 参数代码:", sq(t[i-200:i+1800]))
time.sleep(5)
form = {"SOURCE_TYPE": "1", "DEAL_TIME": "02", "DEAL_CLASSIFY": "00", "DEAL_STAGE": "0000", "DEAL_PROVINCE": "0", "DEAL_CITY": "0",
        "DEAL_PLATFORM": "0", "BID_PLATFORM": "0", "DEAL_TRADE": "0", "isShowAll": "1", "PAGENUMBER": "1", "FINDTXT": "智慧"}
r = s.post("https://www.ggzy.gov.cn/information/pubTradingInfo/getTradList", data=form, timeout=20,
           headers={"Referer": "https://www.ggzy.gov.cn/deal/dealList.html", "X-Requested-With": "XMLHttpRequest"})
print("== 查询: HTTP", r.status_code, sq(r.text[:2500]))
time.sleep(5)
for u in ["http://www.ccgp.gov.cn/cggg/zygg/", "http://www.ccgp.gov.cn/cggg/dfgg/gkzb/"]:
    r = s.get(u, timeout=20); r.encoding = "utf-8"; t = r.text
    for m in re.finditer(r'<ul[^>]*class="[^"]*(?:list|lst)[^"]*"[^>]*>', t):
        print("== ", u, "列表:", sq(t[m.start():m.start()+1200]))
    print("   翻页:", sq(" ".join(re.findall(r"index_\d+\.htm|createPageHTML\([^)]*\)", t)[:5])))
    time.sleep(5)
PY
