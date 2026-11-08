#!/usr/bin/env bash
# 只读诊断：每个来源各访问一次，看域名能否解析、返回什么页面。不重试、不绕过。
APP="$HOME/tender-crawler"; IMG=$(cat "$APP/image.txt")
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONPATH=/app/pylib -v "$APP":/app -w /app "$IMG" python - <<'PY'
import socket, time, re, requests
UA = "Mozilla/5.0 (compatible; TenderWatch/1.0; public announcements only)"
for h in ["search.ccgp.gov.cn", "www.ccgp.gov.cn", "deal.ggzy.gov.cn", "www.ggzy.gov.cn", "ggzy.gov.cn"]:
    try: print("DNS", h, socket.gethostbyname(h))
    except Exception as e: print("DNS", h, "失败", e)
def show(name, r):
    t = r.text
    print(f"== {name}: HTTP {r.status_code} 长度 {len(t)} 最终网址 {r.url}")
    print("   标题:", (re.search(r"<title>(.*?)</title>", t, re.S | re.I) or [None, ""])[1].strip()[:100])
    for m in ("验证码", "滑动验证", "安全验证", "访问过于频繁", "captcha", "请输入验证", "人机验证"):
        i = t.lower().find(m.lower())
        if i >= 0: print("   命中", m, "：", re.sub(r"\s+", " ", t[max(0, i-150):i+150]))
    print("   结果列表:", "vT-srch-result-list" in t, "| 前 300 字:", re.sub(r"\s+", " ", t[:300]))
s = requests.Session(); s.headers["User-Agent"] = UA
try:
    show("ccgp 检索", s.get("http://search.ccgp.gov.cn/bxsearch", params={"searchtype": 1, "page_index": 1, "kw": "智慧课堂", "timeType": 2, "dbselect": "bidx", "bidSort": 0, "pinMu": 0, "bidType": 0}, timeout=20))
except Exception as e: print("ccgp 失败", e)
time.sleep(5)
for u in ["http://www.ggzy.gov.cn/", "https://www.ggzy.gov.cn/"]:
    try: show(u, s.get(u, timeout=20))
    except Exception as e: print(u, "失败", e)
    time.sleep(5)
PY
