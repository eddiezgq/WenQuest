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


class Handler(http.server.SimpleHTTPRequestHandler):
    """静态文件 + 转发：环境变量 WQ_PROXY="cam=8301,bearing=8302" 把 /cam/… 转到本机 8301（去掉前缀），
    和线上 Caddy 的 handle_path 一样——这样凸轮、轴承这类自带页面的服务也能按 /cam/ 截图。"""
    def log_message(self, *a):
        pass

    def _proxy(self):
        import os
        import urllib.request
        for item in filter(None, os.environ.get("WQ_PROXY", "").split(",")):
            pre, port = item.split("=")
            if self.path.startswith(f"/{pre}/") or self.path == f"/{pre}":
                n = int(self.headers.get("content-length") or 0)
                body = self.rfile.read(n) if n else None
                req = urllib.request.Request(f"http://127.0.0.1:{port}" + (self.path[len(pre) + 1:] or "/"), data=body, method=self.command,
                                             headers={k: v for k, v in self.headers.items() if k.lower() in ("content-type", "accept")})
                try:
                    r = urllib.request.urlopen(req, timeout=120)
                    code, data, ct = r.status, r.read(), r.headers.get("content-type", "")
                except urllib.error.HTTPError as e:
                    code, data, ct = e.code, e.read(), e.headers.get("content-type", "")
                self.send_response(code)
                self.send_header("content-type", ct)
                self.send_header("content-length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return True
        return False

    def do_GET(self):
        if not self._proxy():
            super().do_GET()

    def do_POST(self):
        if not self._proxy():
            self.send_error(404)


def serve(directory: Path) -> int:
    h = functools.partial(Handler, directory=str(directory))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]


def hub_shot(b, c, dst):
    """数字工厂的页面：先用本机工厂的 /api/login 拿令牌（教学模式、厂长），放进 localStorage 再打开。
    本机工厂怎么起来见 docs/课程视频/首页简介/README.md。"""
    import json
    import urllib.request
    base = f"http://127.0.0.1:{c['hub']}"
    req = urllib.request.Request(base + "/api/login", method="POST", headers={"content-type": "application/json"},
                                 data=json.dumps({"name": "教师", "role": c.get("role", "manager"), "mode": "teach"}).encode())
    s = json.loads(urllib.request.urlopen(req, timeout=30).read())
    ctx = b.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5, locale="zh-CN")
    ctx.add_init_script("([k, v]) => localStorage.setItem(k, v)".join(["(", ")(" + json.dumps(["wq-df-session", json.dumps({"token": s["token"], "user": s.get("user") or s})]) + ")"]))
    p = ctx.new_page()
    p.goto(base + c["url"])
    p.wait_for_timeout(int(c.get("wait", 5000)))
    for sel in ([c["click"]] if isinstance(c.get("click"), str) else c.get("click") or []):
        p.click(sel)
        p.wait_for_timeout(800)
    if c.get("wheel"):                                 # 三维页：滚轮推近
        p.mouse.move(*c.get("at", [760, 380]))
        for _ in range(int(abs(c["wheel"]) / 100)):
            p.mouse.wheel(0, 100 if c["wheel"] > 0 else -100)
            p.wait_for_timeout(60)
    if c.get("drag"):
        (x0, y0), (x1, y1) = c["drag"]
        p.mouse.move(x0, y0); p.mouse.down(); p.mouse.move(x1, y1, steps=20); p.mouse.up()
    if c.get("tap"):                                   # 在画面坐标处点一下（三维页点设备）
        p.mouse.click(*c["tap"])
        p.wait_for_timeout(1500)
    if c.get("js"):
        p.evaluate(c["js"])
    p.wait_for_timeout(1500)
    p.screenshot(path=str(dst), type="jpeg", quality=88)
    ctx.close()


def learn_shot(b, c, lang, dst):
    """学习平台的页面：用测试账号（teacher1 / student1，密码 Test#2026）登录本机网页端，界面语言跟视频语言。"""
    import json
    ctx = b.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5, locale="zh-CN" if lang == "zh" else "en-US")
    ctx.add_init_script("localStorage.setItem('wq.locale', " + json.dumps(json.dumps({"type": "string", "data": lang})) + ")")
    p = ctx.new_page()
    base = c.get("base", "http://localhost:8088")
    p.goto(base + "/")
    p.wait_for_timeout(2000)
    p.fill("input[type=text]", c.get("user", "teacher1"))
    p.fill("input[type=password]", "Test#2026")
    p.keyboard.press("Enter")
    p.wait_for_timeout(3500)
    if c["learn"] != "/":
        p.goto(base + c["learn"])
        p.wait_for_timeout(int(c.get("wait", 4000)))
    for sel in ([c["click"]] if isinstance(c.get("click"), str) else c.get("click") or []):
        p.click(sel)
        p.wait_for_timeout(1200)
    if c.get("js"):
        p.evaluate(c["js"])
        p.wait_for_timeout(800)
    p.screenshot(path=str(dst), type="jpeg", quality=88)
    ctx.close()


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
            ctx.add_init_script(f"try{{for (const k of ['wq-site-lang','wqcam-lang','wqbearing-lang']) localStorage.setItem(k,'{lang}')}}catch(e){{}}")
            ctx.route("**/assist.js", lambda r: r.fulfill(body="", content_type="text/javascript"))   # 画面里不要客服按钮
            p = ctx.new_page()
            for c in spec.get("capture") or []:
                dst = out / f"{c['name']}-{lang}.jpg"
                if c.get("hub"):                     # 数字工厂（本机测试环境，界面只有中文）：中文版截一次，英文版用同一张
                    if lang == "en":
                        shutil.copy(out / f"{c['name']}-zh.jpg", dst)
                    else:
                        hub_shot(b, c, dst)
                        print(dst)
                    continue
                if c.get("learn"):                   # 学习平台（本机完整环境 tools/local/setup.sh，网页端 :8088），按语言切界面
                    learn_shot(b, c, lang, dst)
                    print(dst)
                    continue
                if "file" in c:
                    src = ROOT / (c.get(f"file_{lang}") or c["file"])
                    im = Image.open(src).convert("RGB")
                    im.save(dst, quality=88)
                    continue
                p.goto(f"http://127.0.0.1:{port}{c['url']}", wait_until="networkidle")
                if c.get("select"):                   # [下拉框, 第几项]：比如凸轮、轴承软件里选一个示例
                    p.select_option(c["select"][0], index=int(c["select"][1]))
                    p.wait_for_timeout(int(c.get("wait_select", 2500)))
                ck = c.get(f"click_{lang}", c.get("click"))     # 按钮文字分中英时写 click_en
                for sel in ([ck] if isinstance(ck, str) else ck or []):
                    p.click(sel)
                    p.wait_for_timeout(int(c.get("wait_click", 600)))
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
                print(dst)
            ctx.close()
        b.close()


if __name__ == "__main__":
    main(sys.argv[1])
