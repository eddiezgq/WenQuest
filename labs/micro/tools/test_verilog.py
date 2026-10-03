"""3c 验收：Yosys（WebAssembly）综合＋DigitalJS 门级仿真，两个样例自动测试通过。
测试环境不能访问 CDN 时，用 --node-modules 指向本地 npm 包目录代替 unpkg。"""
import sys, pathlib, json, mimetypes
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[3]
PAGE = ROOT / "labs/micro/verilog/index.html"
nm = pathlib.Path(sys.argv[sys.argv.index("--node-modules") + 1]) if "--node-modules" in sys.argv else None
shot = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None
MAP = {"@yowasp/yosys@0.70.62-dev.1236/": "@yowasp/yosys/", "digitaljs@0.14.2/": "digitaljs/"}

def serve(route):
    url = route.request.url.split("https://unpkg.com/", 1)[1]
    for k, v in MAP.items():
        if url.startswith(k):
            f = nm / (v + url[len(k):])
            ct = "application/wasm" if f.suffix == ".wasm" else (mimetypes.guess_type(str(f))[0] or "application/octet-stream")
            if f.suffix in (".js", ".mjs"): ct = "text/javascript"
            return route.fulfill(path=str(f), content_type=ct, headers={"access-control-allow-origin": "*"})
    return route.abort()

out = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp, cpu in (("desktop", {"width": 1280, "height": 900}, 1), ("mobile_cpu4x", {"width": 390, "height": 844}, 4)):
        ctx = b.new_context(viewport=vp); page = ctx.new_page(); errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        if nm: page.route("https://unpkg.com/**", serve)
        page.route("https://cdn.jsdelivr.net/**", lambda r: r.abort())
        page.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        if cpu > 1:
            cdp = ctx.new_cdp_session(page); cdp.send("Emulation.setCPUThrottlingRate", {"rate": cpu})
        page.goto(PAGE.as_uri()); page.wait_for_timeout(300)
        page.evaluate("WQLab.reset()")
        page.evaluate("document.getElementById('run').click()")
        page.wait_for_function("window.VERILOG_CHECK && window.VERILOG_CHECK.synthMs != null || document.getElementById('st').className.includes('err')", timeout=300000)
        page.evaluate("document.querySelector('[data-ex=pwm]').click()")
        page.evaluate("window.VERILOG_CHECK.synthMs = null; document.getElementById('run').click()")
        page.wait_for_function("window.VERILOG_CHECK && window.VERILOG_CHECK.synthMs != null || document.getElementById('st').className.includes('err')", timeout=300000)
        page.wait_for_timeout(500)
        r = page.evaluate("window.VERILOG_CHECK"); r["status"] = page.inner_text("#st"); r["errors"] = errs
        r["overflow"] = page.evaluate("document.documentElement.scrollWidth > innerWidth + 1")
        out[name] = r
        if shot and name == "desktop": page.screenshot(path=shot, full_page=True)
        ctx.close()
    b.close()
print(json.dumps(out, indent=1, ensure_ascii=False))
d = out["desktop"]
sys.exit(0 if all(ok for _, ok in d["tasks"]) and not d["errors"] else 1)
