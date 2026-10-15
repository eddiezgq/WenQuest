"""Screenshots of a built lesson at given times (seconds) or at the end of every board:  snap.py <课目录> [t ...]"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
d = Path(sys.argv[1]); data = json.loads((d / "data.json").read_text())
ts = [float(x) for x in sys.argv[2:]]
if not ts:
    ends = {}
    for it in data["items"]:
        ends[it["b"]] = max(ends.get(it["b"], 0), it["start"] + it["dur"])
    ts = [round(v + 0.2, 2) for _, v in sorted(ends.items())]
with sync_playwright() as pw:
    b = pw.chromium.launch(); p = b.new_page(viewport={"width": 1920, "height": 1080})
    p.goto((d / "_render.html").resolve().as_uri())
    for t in ts:
        p.evaluate(f"WB.seek({t})"); p.screenshot(path=str(d / f"_snap_{t}.png"))
        print(t)
    b.close()
