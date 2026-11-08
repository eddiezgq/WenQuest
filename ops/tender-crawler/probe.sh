#!/usr/bin/env bash
# 只读诊断：少量访问公开页面，看域名、页面结构。不重试、不绕过。用法：probe.sh [网址 ...]
APP="$HOME/tender-crawler"; IMG=$(cat "$APP/image.txt")
docker run -i --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONPATH=/app/pylib -v "$APP":/app -w /app "$IMG" python - "$@" <<'PY'
import sys, time, re, requests
from urllib.parse import urljoin
UA = "Mozilla/5.0 (compatible; TenderWatch/1.0; public announcements only)"
s = requests.Session(); s.headers["User-Agent"] = UA
urls = sys.argv[1:] or ["https://www.ggzy.gov.cn/"]
for u in urls:
    try:
        r = s.get(u, timeout=20); r.encoding = r.apparent_encoding
        t = r.text
        print(f"== {u}: HTTP {r.status_code} 长度 {len(t)} 最终 {r.url}")
        print("   标题:", (re.search(r"<title>(.*?)</title>", t, re.S | re.I) or [None, ""])[1].strip()[:80])
        links = set()
        for m in re.finditer(r'(?:href|src|url)\s*[:=]\s*["\']([^"\']+)["\']', t):
            h = m.group(1)
            if re.search(r"deal|search|list|jyxx|information|query|\.do|\.jsp|api", h, re.I) and not h.endswith((".css", ".png", ".jpg", ".gif")):
                links.add(urljoin(r.url, h))
        for h in sorted(links)[:60]: print("   ", h)
        if len(t) < 6000: print("   正文:", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))[:800])
    except Exception as e:
        print(u, "失败", e)
    time.sleep(5)
PY
