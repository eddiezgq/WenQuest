"""第 17 轮附 4e 验收：手机宽度下 Verilog 页走服务器综合（真实 micro-synth 服务 + 本机 Yosys），两个样例自动测试通过。
页面只下载 DigitalJS（约 1 MB），不下载 WebAssembly 版 Yosys。
用法：python labs/micro/tools/test_verilog_server.py --node-modules <含 digitaljs 的 node_modules>"""
import json, pathlib, socket, subprocess, sys, time, urllib.request
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[3]
PAGE = ROOT / "labs/micro/verilog/index.html"
nm = pathlib.Path(sys.argv[sys.argv.index("--node-modules") + 1])
SYNTH = "https://learn.test/api/v1/micro-synth/token"

s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--port", str(port)], cwd=ROOT / "services/micro-synth",
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(50):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1); break
    except Exception:
        time.sleep(0.2)

fetched, posted = [], []


def synth(route):
    posted.append(1)
    req = urllib.request.Request(f"http://127.0.0.1:{port}/synth", data=route.request.post_data.encode(), headers={"Content-Type": "application/json"})
    body = urllib.request.urlopen(req, timeout=30).read()
    route.fulfill(body=body, content_type="application/json")


def cdn(route):
    url = route.request.url; fetched.append(url)
    if "digitaljs@0.14.2/" in url:
        f = nm / "digitaljs" / url.split("digitaljs@0.14.2/", 1)[1]
        return route.fulfill(path=str(f), content_type="text/javascript")
    return route.abort()


out = {}
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
        page = ctx.new_page(); errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.route("https://learn.test/**", synth)
        page.route("https://unpkg.com/**", cdn); page.route("https://cdn.jsdelivr.net/**", cdn)
        page.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        page.goto(PAGE.as_uri() + "#synth=" + SYNTH); page.wait_for_timeout(300)
        page.evaluate("WQLab.reset()")
        for ex in ("counter", "pwm"):
            page.evaluate(f"document.querySelector('[data-ex={ex}]').click()")
            page.evaluate("window.VERILOG_CHECK && (window.VERILOG_CHECK.synthMs = null); document.getElementById('run').click()")
            page.wait_for_function("window.VERILOG_CHECK && window.VERILOG_CHECK.synthMs != null || document.getElementById('st').className.includes('err')", timeout=60000)
            page.wait_for_timeout(300)
        r = page.evaluate("window.VERILOG_CHECK")
        out = {"mode": r["mode"], "tasks": r["tasks"], "synth_ms": round(r["synthMs"]), "status": page.inner_text("#st"),
               "posted": len(posted), "yosys_wasm_fetched": any("yowasp" in u for u in fetched), "errors": errs,
               "overflow": page.evaluate("document.documentElement.scrollWidth > innerWidth + 1")}
        if "--shot" in sys.argv:
            page.screenshot(path=sys.argv[sys.argv.index("--shot") + 1], full_page=True)
        b.close()
finally:
    srv.terminate()
print(json.dumps(out, ensure_ascii=False, indent=1))
ok = out.get("mode") == "server" and all(t for _, t in out["tasks"]) and out["posted"] == 2 and not out["yosys_wasm_fetched"] and not out["errors"] and not out["overflow"]
sys.exit(0 if ok else 1)
