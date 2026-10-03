"""3b 验收：浏览器里跑 ngspice（WebAssembly）并与 JS 模型对照。
CDN 在测试环境不可达时，用本地 npm 包代替（--engine 路径）。记录启动时间：电脑、手机（CPU 降速 4 倍）。"""
import sys, pathlib, json
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[3]
PAGE = ROOT / "labs/micro/spice/index.html"
engine = pathlib.Path(sys.argv[sys.argv.index("--engine") + 1]) if "--engine" in sys.argv else None
shot = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None
out = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp, cpu in (("desktop", {"width": 1280, "height": 900}, 1), ("mobile_cpu4x", {"width": 390, "height": 844}, 4)):
        ctx = b.new_context(viewport=vp)
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        if engine:
            page.route("https://cdn.jsdelivr.net/npm/eecircuit-engine@1.8.0/**", lambda r: r.fulfill(path=str(engine), content_type="text/javascript", headers={"access-control-allow-origin": "*"}))
        page.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        if cpu > 1:
            cdp = ctx.new_cdp_session(page); cdp.send("Emulation.setCPUThrottlingRate", {"rate": cpu})
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300); page.evaluate("document.getElementById('run').click()")
        page.wait_for_function("window.SPICE_CHECK && window.SPICE_CHECK.runMs != null || document.getElementById('st').className.includes('err')", timeout=180000)
        r = page.evaluate("window.SPICE_CHECK"); r["errors"] = errs
        r["overflow"] = page.evaluate("document.documentElement.scrollWidth > innerWidth + 1")
        out[name] = r
        if shot and name == "desktop": page.screenshot(path=shot, full_page=True)
        ctx.close()
    b.close()
print(json.dumps(out, indent=1))
d = out["desktop"]
sys.exit(0 if d["maxErr"] is not None and d["maxErr"] < 1e-3 and not d["errors"] else 1)
