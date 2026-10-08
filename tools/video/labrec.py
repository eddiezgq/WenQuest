"""虚拟实验录屏（第 22 轮）：用无头浏览器打开教材实验页，按讲稿的时间点改参数，逐帧截图，得到与配音对齐的画面。

浏览器时钟用 Playwright 的虚拟时钟（page.clock）推进，每帧 1/30 秒，实验里的动画和计时与真实播放一样快，
不受截图快慢影响。操作通过学生用的同一个滑块（input 事件），正在调的滑块加一圈橙色提示。

步骤（讲稿 steps，第 i 个 “>” 执行第 i 步）：
  {set: {q1: 0, phi: 270}}                      立即设定
  {sweep: {phi: [270, 200]}, dur: 6}             在 dur 秒内从起点平滑调到终点（可同时调几个）
  {press: start}                                 按按钮（start / reset 或实验自定义的按钮）
  {demo: soft}                                   执行某个任务的演示（只在讲稿明确需要时用；默认不报答案）

独立实验页（网页版教材，第 23 轮，standalone=True）：页面自己就是一个实验，没有 WQ 对象。
  {set: {d: 0.9}}            按元素 id 设定：滑块发 input，下拉框发 change，勾选框改勾选
  {sweep: {phi: [0, 360]}, dur: 6}
  {press: "#play"}           点按钮（CSS 选择器；不带 # 时按 id；可以是列表，依次点）
  {js: "__api.setCfg({psi: -20})"}   调页面自己的接口（虚拟样机、综合调机都有 __api）
  {click: [640, 360]}        在画面坐标处点一下（三维页点零件）
  {drag: [[x0, y0], [x1, y1]], dur: 3}   按住拖动（三维页转视角）
"""
from __future__ import annotations

import asyncio
import base64
import math
import os
import shutil
import subprocess
from pathlib import Path

FPS = 30
CSS = """
.wq-vid-focus { outline: 4px solid #f0883e !important; outline-offset: 6px; border-radius: 10px; transition: none; }
html { scroll-behavior: auto !important; }
"""


async def _set(page, lab, pid, v, focus=True):
    await page.evaluate(
        """([lab, pid, v, focus]) => {
          const sec = document.querySelector('#lab-' + lab) || document;
          const inp = sec.querySelector('input[data-param="' + pid + '"]') || sec.querySelector('[data-param="' + pid + '"] input')
                   || [...sec.querySelectorAll('input[type=range]')].find(e => (e.id || '').endsWith(pid) || e.name === pid);
          if (!inp) throw new Error('no slider for ' + pid);
          inp.value = v; inp.dispatchEvent(new Event('input', {bubbles: true}));
          const box = inp.closest('.ctl') || inp.parentElement;
          document.querySelectorAll('.wq-vid-focus').forEach(e => { if (e !== box) e.classList.remove('wq-vid-focus'); });
          if (focus) box.classList.add('wq-vid-focus'); else box.classList.remove('wq-vid-focus');
        }""", [lab, pid, v, focus])


async def _set_any(page, pid, v, focus=True):
    await page.evaluate(
        """([pid, v, focus]) => {
          const e = document.getElementById(pid) || document.querySelector(pid);
          if (!e) throw new Error('no control ' + pid);
          if (e.type === 'checkbox') { e.checked = !!v; e.dispatchEvent(new Event('change', {bubbles: true})); }
          else { e.value = v; e.dispatchEvent(new Event(e.tagName === 'SELECT' ? 'change' : 'input', {bubbles: true})); }
          const box = e.parentElement;
          document.querySelectorAll('.wq-vid-focus').forEach(x => { if (x !== box) x.classList.remove('wq-vid-focus'); });
          if (focus && e.type === 'range') box.classList.add('wq-vid-focus'); else box.classList.remove('wq-vid-focus');
        }""", [pid, v, focus])


async def record(url: str, lab: str, steps: list[dict], step_times: list[float], total: float, out: Path,
                 width=1280, height=720, scale=1.5, standalone=False, viewport=None, manual=False, fps=FPS, gl=False) -> Path:
    """manual=True（第 23 轮）：页面有 __api.manual / __api.step（三维页）。不用虚拟时钟，每帧调 step(1/fps) 渲染一帧再截图：
    软件渲染下虚拟时钟会让三维页每帧渲染好几遍、越来越慢。三维镜头用 fps=15，合成时补成 30 帧。"""
    from playwright.async_api import async_playwright
    frames = out.with_suffix("")
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir(parents=True)
    async with async_playwright() as p:
        if viewport:
            width, height = viewport
            scale = 1920 / width
        args = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] if ((manual or gl) and os.environ.get("WQ_GL_FLAGS", "1") == "1") else []   # 只有三维页需要 WebGL
        b = await p.chromium.launch(args=args)
        ctx = await b.new_context(viewport={"width": width, "height": height}, device_scale_factor=scale)
        page = await ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        three = os.environ.get("WQ_THREE")       # 本地没有外网时用本地的 three.min.js（与 CDN 同版本 r128）
        if three:
            await page.route("**/three.min.js", lambda r: r.fulfill(path=three, content_type="application/javascript"))
        if manual:
            await page.goto(url)
            await page.add_style_tag(content=CSS)
            for _ in range(240):
                if await page.evaluate("!!(window.__api && window.__api.step)"):
                    break
                await asyncio.sleep(0.5)
            else:
                raise RuntimeError("三维页没有 __api.step：" + "; ".join(errors[:3]))
            await page.evaluate("__api.manual(true)")
            cdp = await ctx.new_cdp_session(page)

            async def advance():
                await page.evaluate(f"__api.step({1 / fps})")

            async def capture(fr):
                r = await cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": 90,
                                                               "clip": {**(await page.evaluate("({x: scrollX, y: scrollY})")),
                                                                            "width": width, "height": height, "scale": scale}})
                (frames / f"{fr:05d}.jpg").write_bytes(base64.b64decode(r["data"]))
        else:
            await page.clock.install()
            await page.goto(url)
            await page.add_style_tag(content=CSS)
            await page.clock.run_for(2500)
            if not standalone:               # the lab's own reset first, so tasks and readouts start clean
                await page.evaluate(f"WQ.reset('{lab}')")
                await page.clock.run_for(200)

            async def advance():
                await page.clock.run_for(int(1000 / fps))

            if standalone:                   # 网页版教材的页面：CDP 直接截图，比 page.screenshot 快
                cdp = await ctx.new_cdp_session(page)

                async def capture(fr):
                    r = await cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": 90,
                                                                   "clip": {**(await page.evaluate("({x: scrollX, y: scrollY})")),
                                                                            "width": width, "height": height, "scale": scale}})
                    (frames / f"{fr:05d}.jpg").write_bytes(base64.b64decode(r["data"]))
            else:
                async def capture(fr):
                    await page.screenshot(path=str(frames / f"{fr:05d}.jpg"), type="jpeg", quality=90)
        setter = (lambda pid, v, focus=True: _set_any(page, pid, v, focus)) if standalone else \
                 (lambda pid, v, focus=True: _set(page, lab, pid, v, focus))
        n = int(round(total * fps))
        plan = []                        # (frame_from, frame_to, step)
        for i, st in enumerate(steps):
            if i >= len(step_times):
                break
            f0 = int(step_times[i] * fps)
            f1 = f0 + int(float(st.get("dur", 0)) * fps)
            plan.append((f0, f1, st))
        done = set()
        for fr in range(n):
            for k, (f0, f1, st) in enumerate(plan):
                if fr < f0:
                    continue
                once = k not in done         # 一步里的几个动作（set、js、press…）在这一帧一起做，只做一次
                done.add(k)
                if "set" in st and once:
                    for pid, v in st["set"].items():
                        await setter(pid, v, focus=False)
                if standalone and "press" in st and once:
                    for sel in (st["press"] if isinstance(st["press"], list) else [st["press"]]):
                        await page.click(sel if sel[:1] in "#.[" else "#" + sel)
                if "js" in st and once:
                    await page.evaluate(st["js"])
                if "click" in st and once:
                    await page.mouse.click(*st["click"])
                if "drag" in st and fr <= f1:
                    (x0, y0), (x1, y1) = st["drag"]
                    u = 1.0 if f1 == f0 else min(1.0, (fr - f0) / (f1 - f0))
                    if fr == f0:
                        await page.mouse.move(x0, y0)
                        await page.mouse.down()
                    await page.mouse.move(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)
                    if fr == f1 or f1 == f0:
                        await page.mouse.up()
                if not standalone and "press" in st and once:
                    await page.evaluate("""([lab, a]) => { const s = document.querySelector('#lab-' + lab) || document;
                        const b = s.querySelector('[data-action="' + a + '"]'); if (b) b.click(); }""", [lab, st["press"]])
                if "demo" in st and once:
                    await page.evaluate(f"WQ.demo('{lab}', '{st['demo']}')")
                if "sweep" in st and fr <= f1:
                    u = 1.0 if f1 == f0 else min(1.0, (fr - f0) / (f1 - f0))
                    u = 0.5 - 0.5 * math.cos(math.pi * u)   # ease in and out
                    for pid, (a, bnd) in st["sweep"].items():
                        await setter(pid, round(a + (bnd - a) * u, 3), focus=fr < f1)
            await advance()
            if standalone and not manual:    # 课件里预录的三维画面：按虚拟时间换到这一帧（第 25 轮）
                await page.evaluate(f"window.__wqFrame ? __wqFrame({fr / fps}) : 0")
            await capture(fr)
        await b.close()
        if errors:
            raise RuntimeError("实验页出错：" + "; ".join(errors[:3]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "%05d.jpg"),
                    "-vf", f"scale=1920:1080:flags=lanczos,fps={FPS},format=yuv420p", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    str(out)], check=True)
    shutil.rmtree(frames)
    return out


def run(*a, **k):
    return asyncio.run(record(*a, **k))
