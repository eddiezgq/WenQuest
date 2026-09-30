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
DONE = {"checked": 0, "failed": 0}

BLANK_JS = """(sel) => {
  const c = document.querySelector(sel);
  if (!c || !c.width || !c.height) return -1;
  const d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data;
  const seen = new Set();
  const step = Math.max(4, Math.floor(d.length / 4 / 4000)) * 4;
  for (let i = 0; i < d.length; i += step) { seen.add((d[i] >> 4) + "," + (d[i + 1] >> 4) + "," + (d[i + 2] >> 4) + "," + (d[i + 3] >> 5)); if (seen.size > 50) break; }
  return seen.size;
}"""


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


async def run(html: str, lab: str) -> dict:
    problems: list[str] = []
    errors: list[str] = []
    tasks: dict[str, bool] = {}
    shot = b""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--disable-dev-shm-usage", "--no-proxy-server"])
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
