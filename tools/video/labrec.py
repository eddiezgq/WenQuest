"""虚拟实验录屏（第 22 轮）：用无头浏览器打开教材实验页，按讲稿的时间点改参数，逐帧截图，得到与配音对齐的画面。

浏览器时钟用 Playwright 的虚拟时钟（page.clock）推进，每帧 1/30 秒，实验里的动画和计时与真实播放一样快，
不受截图快慢影响。操作通过学生用的同一个滑块（input 事件），正在调的滑块加一圈橙色提示。

步骤（讲稿 steps，第 i 个 “>” 执行第 i 步）：
  {set: {q1: 0, phi: 270}}                      立即设定
  {sweep: {phi: [270, 200]}, dur: 6}             在 dur 秒内从起点平滑调到终点（可同时调几个）
  {press: start}                                 按按钮（start / reset 或实验自定义的按钮）
  {demo: soft}                                   执行某个任务的演示（只在讲稿明确需要时用；默认不报答案）
"""
from __future__ import annotations

import asyncio
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


async def record(url: str, lab: str, steps: list[dict], step_times: list[float], total: float, out: Path,
                 width=1280, height=720, scale=1.5) -> Path:
    from playwright.async_api import async_playwright
    frames = out.with_suffix("")
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir(parents=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": width, "height": height}, device_scale_factor=scale)
        page = await ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.clock.install()
        await page.goto(url)
        await page.add_style_tag(content=CSS)
        await page.clock.run_for(2500)
        # the lab's own reset first, so tasks and readouts start clean
        await page.evaluate(f"WQ.reset('{lab}')")
        await page.clock.run_for(200)
        n = int(round(total * FPS))
        plan = []                        # (frame_from, frame_to, step)
        for i, st in enumerate(steps):
            if i >= len(step_times):
                break
            f0 = int(step_times[i] * FPS)
            f1 = f0 + int(float(st.get("dur", 0)) * FPS)
            plan.append((f0, f1, st))
        done = set()
        for fr in range(n):
            for k, (f0, f1, st) in enumerate(plan):
                if fr < f0:
                    continue
                if "set" in st and k not in done:
                    for pid, v in st["set"].items():
                        await _set(page, lab, pid, v, focus=False)
                    done.add(k)
                if "press" in st and k not in done:
                    await page.evaluate("""([lab, a]) => { const s = document.querySelector('#lab-' + lab) || document;
                        const b = s.querySelector('[data-action="' + a + '"]'); if (b) b.click(); }""", [lab, st["press"]])
                    done.add(k)
                if "demo" in st and k not in done:
                    await page.evaluate(f"WQ.demo('{lab}', '{st['demo']}')")
                    done.add(k)
                if "sweep" in st and fr <= f1:
                    u = 1.0 if f1 == f0 else min(1.0, (fr - f0) / (f1 - f0))
                    u = 0.5 - 0.5 * __import__("math").cos(__import__("math").pi * u)   # ease in and out
                    for pid, (a, bnd) in st["sweep"].items():
                        await _set(page, lab, pid, round(a + (bnd - a) * u, 3), focus=fr < f1)
            await page.clock.run_for(int(1000 / FPS))
            await page.screenshot(path=str(frames / f"{fr:05d}.jpg"), type="jpeg", quality=90)
        await b.close()
        if errors:
            raise RuntimeError("实验页出错：" + "; ".join(errors[:3]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "%05d.jpg"),
                    "-vf", "scale=1920:1080:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    str(out)], check=True)
    shutil.rmtree(frames)
    return out


def run(*a, **k):
    return asyncio.run(record(*a, **k))
