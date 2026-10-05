"""Record the platform's pages and virtual labs frame by frame for the promo video.

Playwright's fake clock drives the page (Date, timers, requestAnimationFrame, performance.now), so every frame is
exactly 1/30 s of page time no matter how slow the machine renders WebGL in software — the result is smooth.
Sliders are moved the way a student would (input events, eased); some tasks use the lab's own WQ.demo.

Usage: python3 record.py <work dir> [clip ...]
Needs:  python3 -m http.server 8701   (in textbook/build)      python3 -m http.server 8702   (in site/)
"""
from __future__ import annotations

import asyncio
import base64
import os
import shutil
import subprocess
import sys

from playwright.async_api import async_playwright

CHROME_ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
               "--no-proxy-server", "--autoplay-policy=no-user-gesture-required",
               "--disable-gpu-compositing"]   # software compositing: screenshots of WebGL pages take 0.3 s instead of 3 s
BOOK = os.environ.get("BOOK_URL", "http://127.0.0.1:8701")
SITE = os.environ.get("SITE_URL", "http://127.0.0.1:8702")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
MICRO = "file://" + os.path.join(REPO, "samples/数字集成电路设计/课程资料/第1章 CMOS反相器/虚拟实验/第1章虚拟实验（中英）.html")
FPS = 15          # page-time frames per second (each frame is shown twice in the 30 fps clip)


def ease(u: float) -> float:
    return u * u * (3 - 2 * u)


class Rec:
    def __init__(self, page, out_dir: str, lab: str | None, fake: bool):
        self.pg, self.dir, self.lab, self.n, self.cdp, self.fake = page, out_dir, lab, 0, None, fake
        self.fps = FPS if fake else 30
        self.times = []
        shutil.rmtree(out_dir, ignore_errors=True)
        os.makedirs(out_dir)

    async def frame(self, action=None):
        if action:
            await action()
        if self.fake == "slow":
            self.times.append(await self.pg.evaluate("() => performance.now() / 1000"))
        elif self.fake:
            await self.pg.clock.run_for(round(1000 / self.fps))
        else:   # stop motion: the state is set by the controls, wait until it is painted
            await self.pg.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
        if self.cdp is None:
            self.cdp = await self.pg.context.new_cdp_session(self.pg)
        # with software compositing the device scale factor is not applied to captures: ask for 1.5× explicitly
        # (the clip is in document coordinates)
        sx, sy = await self.pg.evaluate("() => [scrollX, scrollY]")
        shot = await self.cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": 92,
                                                              "clip": {"x": sx, "y": sy, "width": 1280, "height": 720, "scale": 1.5}})
        with open(f"{self.dir}/f{self.n:05d}.jpg", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        self.n += 1

    async def hold(self, sec: float):
        if self.fake == "slow":
            end = await self.pg.evaluate("() => performance.now() / 1000") + sec
            while await self.pg.evaluate("() => performance.now() / 1000") < end:
                await self.frame()
            return
        for _ in range(int(round(sec * self.fps))):
            await self.frame()

    async def set(self, vals: dict, lab=None):
        await self.pg.evaluate("""([lab, vals]) => { for (const [k, v] of Object.entries(vals)) {
            const i = document.querySelector(`#lab-${lab} input[data-param="${k}"]`) || document.querySelector(`input[data-param="${k}"]`);
            if (!i) continue; i.value = v; i.dispatchEvent(new Event('input', {bubbles: true})); } }""", [lab or self.lab, vals])

    async def slide(self, moves: dict, sec: float):
        n = max(2, int(round(sec * self.fps)))
        for i in range(1, n + 1):
            u = ease(i / n)
            vals = {k: a + (b - a) * u for k, (a, b) in moves.items()}
            await self.frame(lambda vals=vals: self.set(vals))

    async def chip(self, scene: str):
        await self.pg.evaluate("([lab, sc]) => { const b = document.querySelector(`#lab-${lab} [data-scene=\"${sc}\"]`); if (b) b.click(); }",
                               [self.lab, scene])

    async def press(self, action: str):
        await self.pg.evaluate("([lab, a]) => { const b = document.querySelector(`#lab-${lab} [data-action=\"${a}\"]`); if (b) b.click(); }",
                               [self.lab, action])

    async def demo(self, task: str):
        return await self.pg.evaluate(f"() => WQ.demo('{self.lab}', '{task}')")

    async def centre(self):
        return await self.pg.evaluate("(lab) => { const c = document.querySelector(`#lab-${lab} canvas`); const r = c.getBoundingClientRect(); return [r.x + r.width/2, r.y + r.height/2]; }", self.lab)

    async def zoom(self, clicks: int, dy=-120):
        x, y = await self.centre()
        await self.pg.mouse.move(x, y)
        for _ in range(clicks):
            await self.frame(lambda: self.pg.mouse.wheel(0, dy))

    async def orbit(self, dx: float, sec: float, dy: float = 0):
        x, y = await self.centre()
        await self.pg.mouse.move(x, y)
        await self.pg.mouse.down()
        n = int(round(sec * self.fps))
        for i in range(1, n + 1):
            u = ease(i / n)
            await self.frame(lambda u=u: self.pg.mouse.move(x + dx * u, y + dy * u))
        await self.pg.mouse.up()

    async def scroll_to(self, y1: float, sec: float):
        y0 = await self.pg.evaluate("() => window.scrollY")
        n = int(round(sec * self.fps))
        for i in range(1, n + 1):
            y = y0 + (y1 - y0) * ease(i / n)
            await self.frame(lambda y=y: self.pg.evaluate(f"() => window.scrollTo(0, {y})"))


# ---------- the clips ----------

async def ur5e(r: Rec):
    await r.pg.evaluate("() => window.scrollTo(0, 125)")     # so the task list (ticks) is in view too
    await r.zoom(5)
    await r.hold(1.0)
    await r.slide({"j1": (0, 90)}, 3.5)          # task 1: joint 1 to 90°  → auto tick
    await r.hold(1.5)
    await r.slide({"j1": (90, 0)}, 1.5)
    await r.slide({"j6": (0, 60)}, 2.5)          # task 2: only joint 6
    await r.hold(1.2)
    await r.slide({"j6": (60, 0)}, 1.2)
    await r.chip("lamp")
    await r.hold(0.8)
    await r.slide({"j2": (0, -90)}, 3.0)         # task 3: arm straight up
    await r.hold(1.5)
    await r.orbit(220, 4.0)
    await r.hold(1.0)


async def go2(r: Rec):
    await r.chip("go2")
    await r.hold(1.5)
    await r.zoom(3)
    await r.slide({"q2": (0, 60), "q3": (0, -90)}, 3.5)
    await r.orbit(260, 4.0)
    await r.slide({"q2": (60, 0), "q3": (-90, 0)}, 2.0)
    await r.hold(0.5)


async def gd(r: Rec):
    await r.chip("arm")
    await r.hold(0.8)
    await r.slide({"alpha": (1, 3)}, 1.2)
    await r.press("start")                     # task 1: α = 3 converges
    await r.hold(3.5)
    await r.press("reset")
    await r.slide({"alpha": (3, 4.5)}, 1.0)
    await r.press("start")                     # task 2: α = 4.5 overshoots
    await r.hold(3.5)
    await r.press("reset")
    await r.set({"method": 1})
    await r.press("start")                     # task 3: Newton's method
    await r.hold(3.0)


async def circuit(r: Rec):
    await r.chip("full")
    await r.hold(1.5)
    await r.slide({"F": (0, 100)}, 3.5)
    await r.hold(1.0)
    await r.slide({"rg": (500, 200)}, 3.0)
    await r.hold(2.0)


async def plc(r: Rec):
    """Load the book's program and run the five tests (the ticks), then work the station from its operator panel."""
    async def op(label, kind):    # the operator panel's own buttons
        await r.pg.evaluate("""([lab, label, kind]) => { const b = [...document.querySelectorAll(`#lab-${lab} .opbtn`)].find((x) => x.textContent.includes(label));
            if (!b) return; if (kind === 'click') b.click(); else b.dispatchEvent(new PointerEvent(kind, {bubbles: true, pointerId: 1})); }""", [r.lab, label, kind])
    await r.hold(0.6)
    await r.demo("good")
    await r.hold(1.8)
    await r.press("run")                          # PLC labs: the RUN button
    await op("自动", "click")
    await op("放上工件", "click")
    await r.hold(0.4)
    await op("复位", "pointerdown")
    await r.hold(0.3)
    await op("复位", "pointerup")
    await r.hold(2.0)
    await op("双手同时按住", "pointerdown")
    await r.hold(6.5)
    await op("双手同时按住", "pointerup")
    await r.hold(2.5)


async def gpu(r: Rec):
    await r.hold(0.8)
    await r.slide({"cond": (0, 2)}, 1.0)
    await r.hold(3.0)
    await r.slide({"cond": (2, 3)}, 0.6)
    await r.hold(2.5)
    await r.demo("few")
    await r.hold(4.0)


async def linalg(r: Rec):
    await r.hold(0.5)
    await r.demo("fwd")
    await r.hold(4.5)
    await r.demo("up")
    await r.hold(4.5)


async def micro(r: Rec):
    async def rng(a, b, sec):
        n = int(sec * r.fps)
        for k in range(1, n + 1):
            v = a + (b - a) * ease(k / n)
            await r.frame(lambda v=v: r.pg.evaluate("(v) => { const e = document.querySelectorAll('input[type=range]')[1]; e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); }", v))
    await r.pg.get_by_text("传输特性", exact=False).first.click()
    await r.hold(1.0)
    lo, hi, v0 = await r.pg.evaluate("() => { const e = document.querySelectorAll('input[type=range]')[1]; return [+e.min, +e.max, +e.value]; }")
    await rng(v0, lo + (hi - lo) * 0.9, 3.5)
    await r.hold(0.6)
    await rng(lo + (hi - lo) * 0.9, lo + (hi - lo) * 0.3, 3.0)
    await r.hold(1.0)


async def site(r: Rec):
    await r.pg.evaluate("() => { document.documentElement.style.scrollBehavior = 'auto'; }")   # the site scrolls smoothly by itself
    await r.hold(2.5)
    h = await r.pg.evaluate("() => document.documentElement.scrollHeight - innerHeight")
    await r.scroll_to(min(h, 2600), 12.0)
    await r.hold(1.0)


# WebGL pages are far too slow under the fake clock: the purely kinematic 3D labs are shot stop-motion instead
REAL = {"lab_ur5e", "lab_go2", "lab_linalg"}
# WebGL and driven by time (a PLC program running the machine): the page runs in slow motion (SLOWMO× slower) in real
# time, every screenshot is stamped with the page's own clock, and the clip is rebuilt at those times.
SLOW = {"lab_plc"}
SLOWMO = 12
SLOW_JS = """(() => { const k = %d, pn = performance.now.bind(performance), p0 = pn(), d0 = Date.now();
  performance.now = () => p0 + (pn() - p0) / k;  Date.now = () => d0 + (pn() - p0) / k;
  const raf = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = (cb) => raf(() => cb(performance.now()));
  const st = window.setTimeout.bind(window), si = window.setInterval.bind(window);
  window.setTimeout = (f, d, ...a) => st(f, (d || 0) * k, ...a); window.setInterval = (f, d, ...a) => si(f, (d || 0) * k, ...a); })();""" % SLOWMO
CLIPS = {   # name: (url, lab id or None, scenario)
    "lab_ur5e": (f"{BOOK}/robotics/lab/ch12.html", "12-1", ur5e),
    "lab_go2": (f"{BOOK}/robotics/lab/ch01.html", "1-6", go2),
    "lab_gd": (f"{BOOK}/robotics/lab/ch08.html", "8-1", gd),
    "lab_circuit": (f"{BOOK}/robotics/lab/ch39.html", "39-2", circuit),
    "lab_plc": (f"{BOOK}/plc/lab/ch15.html", "15-3", plc),
    "lab_gpu": (f"{BOOK}/ai/lab/ch03.html", "3-6", gpu),
    "lab_linalg": (f"{BOOK}/linalg/lab/ch01.html", "1-6", linalg),
    "lab_micro": (MICRO, None, micro),
    "site": (f"{SITE}/index.html", None, site),
}


async def tick(pg, fake, ms=100):
    if fake is True:
        await pg.clock.run_for(ms)
    else:
        await asyncio.sleep(ms / 1000)


async def record(b, work, name):
    url, lab, fn = CLIPS[name]
    fake = "slow" if name in SLOW else name not in REAL
    ctx = await b.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5, locale="zh-CN")
    if fake == "slow":
        await ctx.add_init_script(SLOW_JS)
    elif fake:
        await ctx.clock.install()
    pg = await ctx.new_page()
    await pg.goto(url, wait_until="domcontentloaded")
    for _ in range(30):                      # let the page load: real time for the network, page time for its timers
        await tick(pg, fake)
        await asyncio.sleep(0.05)
    if lab:
        await pg.evaluate(f"() => {{ WQ.show('{lab}'); WQ.reset('{lab}'); window.scrollTo(0, 0); }}")
        for _ in range(600):
            await tick(pg, fake)
            await asyncio.sleep(0.05)
            s = await pg.evaluate(f"() => {{ const s = WQ.status().labs['{lab}']; return s.ready || s.broken; }}")
            if s:
                break
    for _ in range(20):
        await tick(pg, fake)
        await asyncio.sleep(0.05)
    if fake is not True:
        await asyncio.sleep(3)
    r = Rec(pg, f"{work}/rec_{name}", lab, fake)
    await fn(r)
    if r.times:                                   # slow motion: frames at their page times
        lst = f"{r.dir}/list.txt"
        with open(lst, "w") as f:
            f.write("ffconcat version 1.0\n")
            for i in range(r.n):
                d = (r.times[i + 1] - r.times[i]) if i + 1 < r.n else 0.1
                f.write(f"file 'f{i:05d}.jpg'\nduration {max(d, 0.001):.4f}\n")
        src = ["-f", "concat", "-safe", "0", "-i", lst]
    else:
        src = ["-framerate", str(r.fps), "-i", f"{r.dir}/f%05d.jpg"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src,
                    "-vf", "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                    f"{work}/{name}.mp4"], check=True)
    print(name, r.n, "frames", flush=True)
    await ctx.close()


async def main():
    work = sys.argv[1]
    names = sys.argv[2:] or list(CLIPS)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=CHROME_ARGS)
        for n in names:
            await record(b, work, n)
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
