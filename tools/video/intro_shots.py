"""首页视频简介的截图（第 86 轮）：在本机把 site/ 当网站打开，按讲稿里的 shots 截真界面，中英各一张。

    python3 tools/video/intro_shots.py docs/课程视频/首页简介/17-评价与校情

讲稿.yaml 里：
  capture:
    - {name: eval-stu, url: /eval/, click: "[data-p=stu]", scroll: "#stu", wait: 800}
    - {name: xq-top, url: /xq/}
    - {name: sewing, file: tools/site_cn/assets/cam-ui.jpg}          # 现成截图（不分语言）
  输出：<讲稿目录>/课件/media/<name>-zh.jpg、<name>-en.jpg（1920×1080：浏览器 1280×720，放大 1.5 倍）
网站语言用 localStorage 的 wq-site-lang 切换（官网、评价、校情页都认）。
"""
from __future__ import annotations

import functools
import http.server
import shutil
import sys
import threading
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def serve(directory: Path) -> int:
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    h.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]


def main(d: str):
    lec = Path(d).resolve()
    spec = yaml.safe_load((lec / "讲稿.yaml").read_text(encoding="utf-8"))
    out = lec / "课件" / "media"
    out.mkdir(parents=True, exist_ok=True)
    port = serve(ROOT / "site")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for lang in ("zh", "en"):
            ctx = b.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5,
                                locale="zh-CN" if lang == "zh" else "en-US")
            ctx.add_init_script(f"try{{localStorage.setItem('wq-site-lang','{lang}')}}catch(e){{}}")
            ctx.route("**/assist.js", lambda r: r.fulfill(body="", content_type="text/javascript"))   # 画面里不要客服按钮
            p = ctx.new_page()
            for c in spec.get("capture") or []:
                dst = out / f"{c['name']}-{lang}.jpg"
                if "file" in c:
                    src = ROOT / (c.get(f"file_{lang}") or c["file"])
                    im = Image.open(src).convert("RGB")
                    im.save(dst, quality=88)
                    continue
                p.goto(f"http://127.0.0.1:{port}{c['url']}", wait_until="networkidle")
                for sel in ([c["click"]] if isinstance(c.get("click"), str) else c.get("click") or []):
                    p.click(sel)
                    p.wait_for_timeout(300)
                if c.get("js"):
                    p.evaluate(c["js"])
                if c.get("find"):                     # 按文字找标题，滚到它
                    p.evaluate("([t, off]) => { const e = [...document.querySelectorAll('h1,h2,h3,h4')].find((x) => x.textContent.includes(t)); if (e) window.scrollTo(0, e.getBoundingClientRect().top + scrollY - off) }",
                               [c["find"][0 if lang == "zh" else -1] if isinstance(c["find"], list) else c["find"], int(c.get("offset", 16))])
                if c.get("scroll"):
                    p.evaluate("([s, off]) => { const e = document.querySelector(s); window.scrollTo(0, e.getBoundingClientRect().top + scrollY - off) }",
                               [c["scroll"], int(c.get("offset", 16))])
                p.wait_for_timeout(int(c.get("wait", 700)))
                p.screenshot(path=str(dst), type="jpeg", quality=88)
                print(dst.relative_to(ROOT))
            ctx.close()
        b.close()


if __name__ == "__main__":
    main(sys.argv[1])
