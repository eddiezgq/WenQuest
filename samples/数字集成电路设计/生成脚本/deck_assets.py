"""课件用图：实验台截图（每个实验一张整页、一张舞台区）与动画封面帧。运行：python deck_assets.py"""
import pathlib, subprocess
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAGE = ROOT / "labs/micro/dic-ch1/index.html"
OUT = HERE / "fig/media"; OUT.mkdir(parents=True, exist_ok=True)
VID = HERE.parent / "课程资料/第1章 CMOS反相器/动画"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
    pg.route("https://fonts.googleapis.com/**", lambda r: r.abort())
    pg.goto(PAGE.as_uri()); pg.evaluate("WQLab.reset()")
    for lab in "12345":
        pg.click(f'nav.tabs [data-lab="{lab}"]'); pg.wait_for_timeout(150)
        pg.screenshot(path=str(OUT / f"lab_{lab}.png"), clip={"x": 60, "y": 150, "width": 1160, "height": 725})
        pg.locator(f"#c{lab}").screenshot(path=str(OUT / f"robot_{lab}.png"))
    b.close()
for f in sorted(VID.glob("*.mp4")):
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * 0.6:.2f}", "-i", str(f), "-frames:v", "1", "-vf", "scale=1280:-1", str(OUT / f"poster_{f.stem.split('_', 1)[1]}.png")], check=True)
print("assets", sorted(x.name for x in OUT.iterdir()))
