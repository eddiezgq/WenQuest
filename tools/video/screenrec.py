"""真页面录屏（第 127 轮）：首页视频里“看真东西”的镜头。本机起好数字工厂 / 问渠电子 / 官网，按 录屏.yaml 自动操作页面，
全屏 1920×1080 录下来，写成 <讲稿目录>/录屏/<name>.mp4（分语言时 <name>.zh.mp4、<name>.en.mp4），讲稿.yaml 的 rec 镜头引用它。

    python3 tools/video/screenrec.py docs/课程视频/首页简介/18-电子与芯片 [--only circuit,fct]

录法：Playwright 打开页面（输出 1920×1080；viewport 可以写小一点让页面放大，文字按设备像素渲染，不是放大图片），用 Chrome 的 screencast 收帧（JPEG 质量 95，
画面变了才来一帧，按时间戳排成 30 帧/秒的 H.264）。没用 Playwright 自带的 recordVideo：它的码率固定、很低，文字发糊。
正在讲的地方用黄色圈标出来（往页面里加一个浮层，不改页面本身）。

录屏.yaml：
  clips:
    - name: circuit
      hub: 8141            # 数字工厂（本机教学版，端口）：先用 /api/login 拿令牌（教学模式、厂长）；界面语言按录的语言固定（wq-factory-lang），--lang en 另录英文界面
      url: /circuit
      # site: true         # 或者：官网 site/ 当网站打开（WQ_PROXY="eda=8150" 把 /eda/ 转给本机服务），按语言各录一段
      viewport: [1440, 810]  # 可选：页面按这个大小排版，放大到 1920×1080 录（文字更大、照样是矢量渲染）；不写 = 1920×1080 原大
      wait: 6000           # 打开后等多久再开录（毫秒）
      setup: [...]         # 开录前先做的动作（同下，不写 at）
      dur: 12              # 录多长（秒）
      do:                  # 开录后第 at 秒做的动作
        - {at: 0.5, ring: "#sel", for: 3}            # 黄圈：Playwright 选择器（可用 :has-text）或 [x, y, w, h]（页面坐标）；for 秒后淡出
        - {at: 2, type: ["input.x", "16"]}           # 往输入框里填值（发 input、change）
        - {at: 3, click: "button:has-text('运行')"}  # 点（Playwright 选择器）；也可以 click: [x, y]；keep: true = 点完保持滚动位置
        - {at: 4, scroll: 600, dur: 1.5}             # 平滑滚到这个位置（像素，或 CSS 选择器、offset）
        - {at: 5, drag: [[900, 500], [1300, 520]], dur: 3}   # 按住拖动（三维视图转动）
        - {at: 6, js: "…"}                           # 页面里执行一段程序
        # ring / click / type / select / scroll 可以按语言分开写：{ring: {zh: "button:has-text('供应商')", en: "button:has-text('Suppliers')"}}
      langs: [zh, en]      # 官网、问渠电子这类有中英两版的页面
      cut: [[1.5, 4.6]]    # 可选：剪掉开录后这几段（秒），比如等服务器算结果的几秒；片子相应变短
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intro_shots  # noqa: E402  —— 复用它的 site/ 静态服务和 WQ_PROXY 转发

ROOT = Path(__file__).resolve().parents[2]
FPS = 30

OVERLAY = r"""
window.__wqRing = (target, ms, pad) => {
  let r
  if (Array.isArray(target)) r = {left: target[0], top: target[1], width: target[2], height: target[3]}
  else {
    const [sel, txt] = target.split('@@')
    let els = [...document.querySelectorAll(sel)]
    if (txt) els = els.filter((e) => e.textContent.includes(txt))
    if (!els.length) throw new Error('ring: no ' + target)
    const b = els[0].getBoundingClientRect(); r = {left: b.left, top: b.top, width: b.width, height: b.height}
  }
  pad = pad ?? 8
  const d = document.createElement('div')
  d.style.cssText = `position:absolute;left:${r.left + scrollX - pad}px;top:${r.top + scrollY - pad}px;width:${r.width + 2 * pad}px;` +
    `height:${r.height + 2 * pad}px;border:5px solid #f5c344;border-radius:14px;box-shadow:0 0 0 3px rgba(7,19,31,.35),0 0 28px rgba(245,195,68,.85);` +
    'pointer-events:none;z-index:2147483647;opacity:0;transform:scale(1.06);transition:opacity .35s ease,transform .35s ease'
  document.body.appendChild(d)
  requestAnimationFrame(() => requestAnimationFrame(() => { d.style.opacity = 1; d.style.transform = 'scale(1)' }))
  if (ms) setTimeout(() => { d.style.opacity = 0; setTimeout(() => d.remove(), 400) }, ms)
}
window.__wqScroll = (to, ms) => {
  const y0 = scrollY, t0 = performance.now()
  const step = (t) => { const u = Math.min(1, (t - t0) / ms), e = u < .5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2
    scrollTo(0, y0 + (to - y0) * e); if (u < 1) requestAnimationFrame(step) }
  requestAnimationFrame(step)
}
"""


def hub_token(port: int, role="manager"):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/login", method="POST", headers={"content-type": "application/json"},
                                 data=json.dumps({"name": "教师", "role": role, "mode": "teach"}).encode())
    s = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return {"token": s["token"], "user": s.get("user") or s}


def act(page, a: dict, lang: str = "zh"):
    a = {k: (v.get(lang, v.get("zh")) if isinstance(v, dict) and k in ("ring", "click", "type", "select", "scroll") else v) for k, v in a.items()}
    if "ring" in a:
        t = a["ring"]
        if isinstance(t, str):                       # Playwright 选择器（可以用 :has-text）→ 画面里的位置
            bb = page.locator(t).first.bounding_box()
            if not bb:
                raise RuntimeError("ring: 找不到 " + t)
            t = [bb["x"], bb["y"], bb["width"], bb["height"]]
        page.evaluate("([t, ms, pad]) => __wqRing(t, ms, pad)", [t, int(float(a.get("for", 0)) * 1000), a.get("pad")])
    if "type" in a:
        sel, v = a["type"]
        page.evaluate("""([sel, v]) => { const e = document.querySelector(sel); if (!e) throw new Error('type: no ' + sel)
            e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})) }""", [sel, str(v)])
    if "select" in a:
        sel, v = a["select"]
        page.select_option(sel, v)
    if "click" in a and a.get("keep"):           # 点了以后页面会重排、跳回顶上的：1.5 秒内把滚动位置拉回来
        page.evaluate("""() => { const y = scrollY, t0 = performance.now()
            const f = () => { if (scrollY !== y) scrollTo(0, y); if (performance.now() - t0 < 1500) requestAnimationFrame(f) }; requestAnimationFrame(f) }""")
    if "click" in a:
        c = a["click"]
        if isinstance(c, list):
            page.mouse.click(*c)
        else:
            page.click(c)
    if "scroll" in a:
        to = a["scroll"]
        if isinstance(to, str):
            to = page.evaluate("([s, off]) => { const e = document.querySelector(s); if (!e) throw new Error('scroll: no ' + s); "
                               "return e.getBoundingClientRect().top + scrollY - off }", [to, int(a.get("offset", 16))])
        page.evaluate("([y, ms]) => __wqScroll(y, ms)", [to, int(float(a.get("dur", 1.2)) * 1000)])
    if "js" in a:
        page.evaluate(a["js"])
    if "drag" in a:
        (x0, y0), (x1, y1) = a["drag"]
        n = max(2, int(float(a.get("dur", 2)) * 30))
        page.mouse.move(x0, y0)
        page.mouse.down()
        for i in range(1, n + 1):
            page.mouse.move(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n)
            page.wait_for_timeout(1000 / 30)
        page.mouse.up()
    if "wheel" in a:
        page.mouse.move(*a.get("at_xy", [960, 540]))
        for _ in range(int(abs(a["wheel"]) / 100)):
            page.mouse.wheel(0, 100 if a["wheel"] > 0 else -100)
            page.wait_for_timeout(40)


def record(b, c: dict, lang: str, site_port: int, out: Path):
    w, h = c.get("viewport") or (1920, 1080)          # 页面按多大的浏览器排版；输出总是 1920×1080（小视口 = 放大倍数 1920/w，文字照样清楚）
    ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1920 / w, locale="zh-CN" if lang == "zh" else "en-US")
    ctx.add_init_script(f"try{{for (const k of ['wq-site-lang','eda.lang','wq-factory-lang']) localStorage.setItem(k,'{lang}')}}catch(e){{}}")
    if c.get("hub"):
        tok = hub_token(c["hub"], c.get("role", "manager"))
        ctx.add_init_script("localStorage.setItem('wq-df-session', " + json.dumps(json.dumps(tok)) + ")")
        base = f"http://127.0.0.1:{c['hub']}"
    else:
        base = f"http://127.0.0.1:{site_port}"
    ctx.route("**/assist.js", lambda r: r.fulfill(body="", content_type="text/javascript"))   # 画面里不要客服按钮
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + c["url"])
    page.wait_for_timeout(int(c.get("wait", 4000)))
    page.add_script_tag(content=OVERLAY)
    for a in c.get("setup") or []:
        act(page, a, lang)
        page.wait_for_timeout(int(a.get("pause", 600)))
    page.wait_for_timeout(int(c.get("settle", 800)))

    frames = []                                   # (时间戳, jpeg)
    cdp = ctx.new_cdp_session(page)

    def on_frame(ev):
        frames.append((ev["metadata"]["timestamp"], ev["data"]))
        try:
            cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        except Exception:  # noqa: BLE001 —— 录完关掉时还在路上的帧
            pass
    cdp.on("Page.screencastFrame", on_frame)
    cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 95, "maxWidth": 1920, "maxHeight": 1080, "everyNthFrame": 1})
    t0 = time.time()
    page.wait_for_timeout(50)
    todo = sorted(c.get("do") or [], key=lambda a: float(a["at"]))
    dur = float(c["dur"])
    for a in todo:
        wait = float(a["at"]) - (time.time() - t0)
        if wait > 0:
            page.wait_for_timeout(wait * 1000)
        act(page, a, lang)
    rest = dur - (time.time() - t0)
    if rest > 0:
        page.wait_for_timeout(rest * 1000)
    cdp.send("Page.stopScreencast")
    page.wait_for_timeout(200)
    t_end = t0 + dur
    ctx.close()
    if errors:
        print(f"  （页面报错，照录：{'; '.join(errors[:2])}）", file=sys.stderr)
    if not frames:
        raise RuntimeError(f"{c['name']}：没有收到画面")
    tmp = Path(tempfile.mkdtemp(prefix="screenrec-"))
    lines = []
    frames.sort(key=lambda x: x[0])
    start = frames[0][0]
    cuts = sorted((float(x), float(y)) for x, y in (c.get("cut") or []))   # 剪掉的时段（例如等服务器算的几秒）：跳到那段结束时的画面
    if cuts:
        rel = [(ts - start, d) for ts, d in frames]
        out_f = []
        for t, d in rel:
            if any(x <= t < y for x, y in cuts):
                continue
            out_f.append((t - sum(y - x for x, y in cuts if y <= t), d))
        for x, y in cuts:                        # 剪口处放那段结束时的最后一帧
            last = [d for t, d in rel if t <= y]
            if last:
                out_f.append((x - sum(b - a for a, b in cuts if b <= x), last[-1]))
        out_f.sort(key=lambda z: z[0])
        dur -= sum(y - x for x, y in cuts)
        frames = [(start + t, d) for t, d in out_f]
    for i, (ts, data) in enumerate(frames):
        f = tmp / f"{i:05d}.jpg"
        f.write_bytes(base64.b64decode(data))
        nxt = frames[i + 1][0] if i + 1 < len(frames) else max(ts + 1 / FPS, start + dur)
        lines += [f"file '{f}'", f"duration {max(0.001, nxt - ts):.4f}"]
    lines.append(f"file '{tmp / f'{len(frames) - 1:05d}.jpg'}'")
    (tmp / "list.txt").write_text("\n".join(lines) + "\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                    "-vf", f"fps={FPS},scale=1920:1080:flags=lanczos,format=yuv420p", "-t", f"{dur:.2f}",
                    "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(tmp)
    print(out, f"{len(frames)} 帧", f"{t_end - t0:.1f} 秒")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--only", default="")
    ap.add_argument("--lang", default="", help="只录这种语言；数字工厂这类一段共用的，写成 <name>.<lang>.mp4（第 130 轮后数字工厂有英文界面）")
    a = ap.parse_args()
    lec = Path(a.dir).resolve()
    spec = yaml.safe_load((lec / "录屏.yaml").read_text(encoding="utf-8"))
    only = {x for x in a.only.split(",") if x}
    site_port = intro_shots.serve(ROOT / "site")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
                               if os.environ.get("WQ_GL_FLAGS", "1") == "1" else [])
        for c in spec["clips"]:
            if only and c["name"] not in only:
                continue
            langs = c.get("langs") or ["zh"]
            if a.lang:
                langs = [a.lang]
            for lang in langs:
                name = f"{c['name']}.{lang}.mp4" if len(langs) > 1 or a.lang else f"{c['name']}.mp4"
                record(b, c, lang, site_port, lec / "录屏" / name)
        b.close()


if __name__ == "__main__":
    main()
