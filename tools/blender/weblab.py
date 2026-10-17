"""运动来源：已有的网页虚拟实验（第 37 轮）。在无界面浏览器里打开实验页，调用页面的 __api.dump(a)，
取主轴累计转角 a 时每个零件的世界矩阵、线的路径和读数——和学生在网页上看到的是同一套机构计算，视频与实验永远一致。

已接入的实验（页面要提供 __api.dump 与 __api.mesh）：
    sewing/proto-lockstitch   《缝纫机设计与制造》平缝机虚拟样机（第 20 轮；dump 在第 37 轮加）
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LABS = {"sewing/proto-lockstitch": (ROOT / "textbook/web-editions/sewing/src", "zh/labs/proto-lockstitch.html")}
VENDOR = ROOT / "site/vendor"                                   # 本地有；仓库里不放（.gitignore），three 取下面这份
THREE_R128 = ROOT / "tools/site_cases/assets/three.min.js"      # 与 site/vendor/three/r128/three.min.js 相同
TYPES = {".js": "application/javascript", ".html": "text/html", ".css": "text/css", ".json": "application/json",
         ".woff2": "font/woff2", ".png": "image/png", ".svg": "image/svg+xml"}


class Lab:
    """with Lab(name) as lab: lab.mesh() / lab.dump(a)"""

    def __init__(self, name):
        if name not in LABS:
            raise SystemExit(f"没有这个虚拟实验：{name}（已接入：{', '.join(LABS)}）")
        self.root, self.rel = LABS[name]

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._b = self._pw.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                                 "--enable-webgl", "--ignore-gpu-blocklist"])      # 没有显卡也能建 WebGL
        self.page = self._b.new_page(viewport={"width": 640, "height": 400})
        self.errors = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.route("**/*", self._serve)        # 页面从仓库里直接取（/vendor/ 取 site/vendor），不联网，结果不受网络影响
        self.page.goto(f"http://wq.local/{self.rel}", wait_until="domcontentloaded", timeout=120000)
        try:
            self.page.wait_for_function("window.__api && window.__api.dump", timeout=60000)
        except Exception:
            raise SystemExit("虚拟实验页没有就绪：" + " | ".join(self.errors[:5]))
        self.page.evaluate("__api.manual(true)")
        return self

    def _serve(self, route):
        from urllib.parse import unquote, urlparse
        u = urlparse(route.request.url)
        if u.hostname != "wq.local":
            return route.abort()
        path = unquote(u.path).lstrip("/")
        f = (VENDOR / path[len("vendor/"):]) if path.startswith("vendor/") else (self.root / path)
        if path == "vendor/three/r128/three.min.js" and not f.is_file():
            f = THREE_R128
        if not f.is_file():
            return route.fulfill(status=404, body="")
        route.fulfill(path=str(f), content_type=TYPES.get(f.suffix, "application/octet-stream"))

    def __exit__(self, *a):
        self._b.close()
        self._pw.stop()

    def mesh(self):
        return self.page.evaluate("__api.mesh()")

    def dump(self, a):
        return self.page.evaluate(f"__api.dump({float(a)})")

    def dumps(self, angles):
        js = "as => as.map(a => __api.dump(a))"
        out = []
        for i in range(0, len(angles), 60):
            out += self.page.evaluate(js, [float(a) for a in angles[i:i + 60]])
        return out


if __name__ == "__main__":
    with Lab("sewing/proto-lockstitch") as lab:
        d = lab.dump(206)
        print(sorted(d["parts"]), {k: (len(v) if v else 0) for k, v in d["tubes"].items()}, d["read"])
        print(json.dumps(lab.mesh()["meta"]))
