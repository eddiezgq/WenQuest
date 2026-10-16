"""高清录虚拟实验（飞行实验.html 的 SEEK 演示）→ _lab.webm（1920×900，录屏 Chromium 解不了 H.264，所以用 WebM）。
    python3 rec_lab.py"""
import json, subprocess, sys  # noqa: E401
from pathlib import Path
from playwright.sync_api import sync_playwright
here = Path(__file__).resolve().parent
# 三次悬停：300 bar / 700 bar / 700 bar 减重 500 kg；快放让三次都落在讲解的 4 句话里
DEMO = [{"at": 0.8, "p": 300, "m": 2000, "mode": "hover", "len": 7.4, "speed": 1.6},
        {"at": 7.6, "p": 700, "m": 2000, "mode": "hover", "len": 13.0, "speed": 2.2},
        {"at": 15.6, "p": 700, "m": 1500, "mode": "hover", "len": 13.6, "speed": 2.2}]
LEN, FPS = 23.0, 30
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                       "-vf", "scale=1920:900", "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "24", "-row-mt", "1", "-deadline", "good",
                       "-cpu-used", "4", str(here / "_lab.webm")], stdin=subprocess.PIPE)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 600}, device_scale_factor=2)
    pg.add_init_script(f"window.DEMO_OVERRIDE = {json.dumps(DEMO)};")
    pg.goto((here / "飞行实验.html").as_uri())
    pg.wait_for_function("window.READY === true")
    for i in range(int(LEN * FPS)):
        pg.evaluate(f"SEEK({i / FPS})")
        ff.stdin.write(pg.screenshot(type="png"))
    b.close()
ff.stdin.close()
sys.exit(ff.wait())
