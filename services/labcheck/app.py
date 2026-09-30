"""WenQuest lab checker (round 3, A3): try an AI-written virtual lab in headless Chromium.

POST /check {html, lab: "2-1"} opens the lab page (built with the WenQuest lab kit), then checks:
  1. no script errors while loading, switching scenes, moving every slider and running the tasks;
  2. every scene actually draws something (the canvas is not blank);
  3. every task's demo (the "示范做法") really ticks the task;
and returns {ok, problems, tasks, screenshot (PNG, base64), seconds}. One check at a time.
The service holds no secrets and has no internet; every network request the page tries is aborted.
"""
from __future__ import annotations

import asyncio
import base64
import time

from fastapi import FastAPI
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright

app = FastAPI(title="WenQuest lab checker")
LOCK = asyncio.Lock()
SPEED = 4          # physics steps per frame while checking (labs run 4x faster)
LIMIT = 100.0      # seconds for one whole check
RENDER_LIMIT = 900.0   # seconds for one 3D animation
DONE = {"checked": 0, "failed": 0}

BLANK_JS = """(sel) => {
  // Copy the canvas (2D or WebGL) into a small 2D canvas and count distinct colours.
  const c = document.querySelector(sel);
  if (!c || !c.width || !c.height) return -1;
  const t = document.createElement("canvas");
  t.width = Math.min(c.width, 400); t.height = Math.max(1, Math.round(t.width * c.height / c.width));
  const x = t.getContext("2d");
  x.drawImage(c, 0, 0, t.width, t.height);
  const d = x.getImageData(0, 0, t.width, t.height).data;
  const seen = new Set();
  const step = Math.max(4, Math.floor(d.length / 4 / 4000)) * 4;
  for (let i = 0; i < d.length; i += step) { seen.add((d[i] >> 4) + "," + (d[i + 1] >> 4) + "," + (d[i + 2] >> 4) + "," + (d[i + 3] >> 5)); if (seen.size > 50) break; }
  return seen.size;
}"""


class RenderIn(BaseModel):
    html: str = Field(min_length=10, max_length=40_000_000)
    duration: float = Field(gt=0, le=90)
    fps: int = Field(default=30, ge=10, le=30)
    width: int = Field(default=1280, ge=320, le=1920)
    height: int = Field(default=720, ge=240, le=1080)


class CheckIn(BaseModel):
    html: str = Field(min_length=10, max_length=2_000_000)
    lab: str = Field(pattern=r"^\d{1,2}-\d{1,2}$")


@app.get("/health")
async def health():
    return {"ok": True, "busy": LOCK.locked(), **DONE}


@app.post("/check")
async def check(body: CheckIn):
    async with LOCK:
        t0 = time.monotonic()
        try:
            out = await asyncio.wait_for(run(body.html, body.lab), LIMIT)
        except asyncio.TimeoutError:
            out = {"ok": False, "problems": [f"the check took longer than {int(LIMIT)} s (the lab is too slow or never finishes)"],
                   "tasks": {}, "screenshot": ""}
        out["seconds"] = round(time.monotonic() - t0, 1)
        DONE["checked"] += 1
        DONE["failed"] += 0 if out["ok"] else 1
        return out


@app.post("/render3d")
async def render3d(body: RenderIn):
    """A 3D scene page (engine + models + script, from the gateway) stepped frame by frame into an MP4."""
    async with LOCK:
        t0 = time.monotonic()
        try:
            out = await asyncio.wait_for(record(body), RENDER_LIMIT)
        except asyncio.TimeoutError:
            out = {"ok": False, "error": f"3D render took longer than {int(RENDER_LIMIT)} s", "stage": "render"}
        out["render_seconds"] = round(time.monotonic() - t0, 1)
        return out


async def record(body: RenderIn) -> dict:
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path
    work = Path(tempfile.mkdtemp(prefix="wq3d-"))
    errors: list[str] = []
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(args=["--disable-dev-shm-usage", "--no-proxy-server", "--use-gl=angle",
                                                     "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
            try:
                page = await browser.new_page(viewport={"width": body.width, "height": body.height})

                async def block(route):
                    if route.request.url.startswith("data:") or route.request.url == "about:blank":
                        await route.continue_()
                    else:
                        errors.append(f"the scene tried to load {route.request.url[:120]} (not allowed)")
                        await route.abort()
                await page.route("**/*", block)
                page.on("pageerror", lambda e: errors.append(f"script error: {e}"))
                await page.set_content(body.html, wait_until="load", timeout=60000)
                try:
                    await page.wait_for_function("() => window.READY || window.FAIL", timeout=60000)
                except Exception:
                    return {"ok": False, "error": "the scene did not start: " + "; ".join(errors[:3]), "stage": "render"}
                fail = await page.evaluate("() => window.FAIL || ''")
                if fail:
                    return {"ok": False, "error": f"the scene failed to load: {fail[:1500]}", "stage": "render"}
                n = max(1, int(body.duration * body.fps))
                video = work / "scene.mp4"
                ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(body.fps),
                                       "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "veryfast",
                                       "-movflags", "+faststart", str(video)], stdin=subprocess.PIPE)
                keys = {int(n * f): None for f in (0.2, 0.45, 0.5, 0.8)}
                for i in range(n):
                    await page.evaluate(f"() => window.SEEK({i / body.fps})")
                    shot = await page.screenshot(type="jpeg", quality=90)
                    ff.stdin.write(shot)
                    if i in keys:
                        keys[i] = shot
                ff.stdin.close()
                ff.wait(timeout=120)
                if ff.returncode != 0 or not video.exists():
                    return {"ok": False, "error": "encoding the video failed", "stage": "render"}
                if errors:
                    return {"ok": False, "error": "; ".join(errors[:5]), "stage": "render"}
                shots = [keys[k] for k in sorted(keys) if keys[k]]
                return {"ok": True, "seconds": round(n / body.fps, 2), "video": base64.b64encode(video.read_bytes()).decode(),
                        "poster": base64.b64encode(shots[1] if len(shots) > 1 else shots[0]).decode() if shots else "",
                        "frames": [base64.b64encode(s).decode() for i, s in enumerate(shots) if i != 2]}
            finally:
                await browser.close()
    finally:
        shutil.rmtree(work, ignore_errors=True)


async def run(html: str, lab: str) -> dict:
    problems: list[str] = []
    errors: list[str] = []
    tasks: dict[str, bool] = {}
    shot = b""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--disable-dev-shm-usage", "--no-proxy-server", "--use-gl=angle",
                                                 "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        try:
            ctx = await browser.new_context(viewport={"width": 1280, "height": 860}, device_scale_factor=1.5,
                                            locale="zh-CN", java_script_enabled=True)
            page = await ctx.new_page()

            async def block(route):
                if route.request.url.startswith("data:") or route.request.url == "about:blank":
                    await route.continue_()
                else:
                    errors.append(f"the lab tried to load {route.request.url[:120]} (not allowed)")
                    await route.abort()
            await page.route("**/*", block)
            page.on("pageerror", lambda e: errors.append(f"script error: {e}"))
            page.on("console", lambda m: errors.append(f"console error: {m.text}") if m.type == "error" else None)
            await page.set_content(html, wait_until="load", timeout=15000)
            await page.wait_for_timeout(600)
            status = await page.evaluate("() => window.WQ ? WQ.status() : null")
            if not status or lab not in status["labs"]:
                problems.append("the lab did not start (WQ.lab was not called, or threw an error before it finished)")
                return result(problems, errors, tasks, shot)
            info = status["labs"][lab]
            if not info.get("ready", True) and not info["broken"]:   # a 3D lab: wait for its models
                try:
                    await page.wait_for_function(f"() => {{ const s = WQ.status().labs[{lab!r}]; return s.ready || s.broken; }}", timeout=30000)
                except Exception:
                    problems.append("the 3D lab's models did not load within 30 s")
                    return result(problems, errors, tasks, shot)
                info = (await page.evaluate("() => WQ.status()"))["labs"][lab]
            if info["broken"]:
                problems.append("the lab stopped with an error while starting")
            sec = f"#lab-{lab}"
            await page.evaluate(f"() => {{ WQ.speed = {SPEED}; WQ.show('{lab}'); WQ.reset('{lab}'); }}")
            # 1-2. every scene draws; every slider can move
            for sc in info["scenes"]:
                await page.click(f'{sec} [data-scene="{sc}"]')
                await page.wait_for_timeout(350)
                colours = await page.evaluate(BLANK_JS, f"{sec} canvas")
                if colours < 3:
                    problems.append(f"scene '{sc}': the picture is blank")
                for pid in info["params"]:
                    visible = await page.is_visible(f'{sec} [data-param="{pid}"]')
                    if not visible:
                        continue
                    for end in ("min", "max"):
                        await page.evaluate(f"""() => {{ const i = document.querySelector('{sec} [data-param="{pid}"]');
                            i.value = i.{end}; i.dispatchEvent(new Event('input')); }}""")
                        await page.wait_for_timeout(120)
                await page.click(f'{sec} [data-action="start"]') if await page.query_selector(f'{sec} [data-action="start"]') else None
                await page.wait_for_timeout(500)
            # 3. every task's demo ticks the task
            await page.evaluate(f"() => WQ.reset('{lab}')")
            for tid, demo in info["demos"].items():
                if not demo:
                    problems.append(f"task '{tid}' has no demo (how to complete it)")
                    tasks[tid] = False
                    continue
                wait = await page.evaluate(f"() => WQ.demo('{lab}', {tid!r})")
                deadline = time.monotonic() + min(30.0, float(wait or 5) / SPEED + 3.0)
                ok = False
                while time.monotonic() < deadline:
                    await page.wait_for_timeout(250)
                    st = await page.evaluate("() => WQ.status()")
                    if st["labs"][lab]["tasks"].get(tid):
                        ok = True
                        break
                tasks[tid] = ok
                if not ok:
                    problems.append(f"task '{tid}': after its demo {demo} the task was not ticked (it cannot be completed as written)")
            # the picture for the slides: the first task's demo at normal speed; keep the busiest frame
            first = next(iter(info["demos"].items()), (None, None))
            canvas = page.locator(f"{sec} canvas")
            best = -1
            await page.evaluate("() => { WQ.speed = 1; }")
            if first[0]:
                await page.evaluate(f"() => WQ.reset('{lab}')")
                wait = float(await page.evaluate(f"() => WQ.demo('{lab}', {first[0]!r})") or 4)
                for _ in range(10):
                    await page.wait_for_timeout(int(min(wait, 4.0) / 10 * 1000))
                    colours = await page.evaluate(BLANK_JS, f"{sec} canvas")
                    if colours > best:
                        best, shot = colours, await canvas.screenshot(type="png")
            if not shot:
                shot = await canvas.screenshot(type="png")
            st = await page.evaluate("() => WQ.status()")
            errors.extend(e for e in st["errors"] if e not in errors)
        finally:
            await browser.close()
    return result(problems, errors, tasks, shot)


def result(problems: list[str], errors: list[str], tasks: dict, shot: bytes) -> dict:
    seen, uniq = set(), []
    for e in errors:
        k = e[:200]
        if k not in seen:
            seen.add(k)
            uniq.append(e[:600])
    problems = problems + uniq[:10]
    return {"ok": not problems, "problems": problems, "tasks": tasks,
            "screenshot": base64.b64encode(shot).decode() if shot else ""}
