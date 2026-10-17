"""运动来源：已有的网页虚拟实验（第 37 轮）。在无界面浏览器里打开实验页，调用页面的 __api.dump(a)，
取主轴累计转角 a 时每个零件的世界矩阵、线的路径和读数——和学生在网页上看到的是同一套机构计算，视频与实验永远一致。

已接入的实验（页面要提供 __api.dump 与 __api.mesh）：
    sewing/proto-lockstitch   《缝纫机设计与制造》平缝机虚拟样机（第 20 轮；dump 在第 37 轮加）
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LABS = {"sewing/proto-lockstitch": ROOT / "textbook/web-editions/sewing/src/zh/labs/proto-lockstitch.html"}
THREE = ROOT / "site/vendor/three/r128/three.min.js"


class Lab:
    """with Lab(name) as lab: lab.mesh() / lab.dump(a)"""

    def __init__(self, name):
        if name not in LABS:
            raise SystemExit(f"没有这个虚拟实验：{name}（已接入：{', '.join(LABS)}）")
        self.page_path = LABS[name]

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._b = self._pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        self.page = self._b.new_page(viewport={"width": 640, "height": 400})
        self.page.route("http*://**", lambda r: r.abort())          # 不联网：字体、统计等外部资源一律不取，结果不受网络影响
        self.page.route("**/vendor/three/r128/three.min.js",
                        lambda r: r.fulfill(path=str(THREE), content_type="application/javascript"))
        self.page.goto(self.page_path.as_uri(), wait_until="domcontentloaded")
        self.page.wait_for_function("window.__api && window.__api.dump", timeout=60000)
        self.page.evaluate("__api.manual(true)")
        return self

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
