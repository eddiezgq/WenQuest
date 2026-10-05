"""书中的三维图与三维动画（第 13 轮 8.3 R2）。

    from render3d import figure3d, Video
    figure3d("fig52_1_2", asm, camera={"dir": [1, -1.3, 0.8]}, labels=[...], explode=1.0)

asm 是 factory/digital/models3d 的 Assembly（零件用 build123d 造型）。渲染在无头 Chromium 里用 three.js 做：
浅色着色、黑色轮廓线与剪影，上面叠一层 SVG 标注（零件序号、文字、尺寸、箭头、点）。
图存为 <name>.svg（内嵌 PNG），和 bookout.figure 一样登记进本程序的输出；三维动画逐帧渲染后用 ffmpeg 合成 MP4。
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
THREE = HERE / "node_modules" / "three" / "build" / "three.module.js"
JS = HERE / "render3d.js"
PAGE = """<!doctype html><html><head><meta charset='utf-8'><style>
html,body{margin:0;padding:0;background:#fff} #box{position:relative;overflow:hidden}
</style></head><body><div id='box'></div><script>window.SCENE = __SCENE__;</script>
<script type='module' src='http://wq3d.local/render3d.js'></script></body></html>"""


def _scene(asm, width, height, scale, section, hide, tol, **opts):
    import sys
    repo = HERE.parents[1]
    for p in (repo / "factory" / "digital",):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    from models3d import core
    parts = core.mesh_parts(asm, tol=tol, section=section, hide=hide)
    return {"width": width, "height": height, "scale": scale, "parts": parts, **opts}


class Renderer:
    """一个浏览器页面渲染一个场景；可以连续调用 frame() 出多张图（动画）。"""

    def __init__(self, scene: dict):
        self._b = _browser()
        self.page = self._b.new_page(viewport={"width": scene["width"], "height": scene["height"]}, device_scale_factor=1)
        files = {"render3d.js": JS, "three.module.js": THREE}

        def route(r):
            name = r.request.url.rsplit("/", 1)[-1]
            if name == "index.html":
                r.fulfill(status=200, content_type="text/html", body=PAGE.replace("__SCENE__", json.dumps(scene)))
            elif name in files:
                r.fulfill(status=200, content_type="text/javascript", body=files[name].read_text(encoding="utf-8"))
            else:
                r.fulfill(status=404, body="")
        self.page.route("http://wq3d.local/**", route)
        errors = []
        self.page.on("pageerror", lambda e: errors.append(str(e)))
        self.page.goto("http://wq3d.local/index.html")
        try:
            self.page.wait_for_function("window.READY === true", timeout=120000)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError("三维渲染页出错：" + "; ".join(errors or [str(e)])) from e
        self.scene = scene

    def png(self, state: dict | None = None) -> bytes:
        if state is not None:
            self.page.evaluate("st => window.frame(st)", state)
        miss = self.page.evaluate("window.MISSES || []")
        for text, owner in miss:
            import sys
            print(f"render3d：标注“{text}”的指示点被“{owner}”挡住了", file=sys.stderr)
        self.misses = miss
        return self.page.locator("#box").screenshot(type="png", scale="device")

    def close(self):
        self.page.close()


_PW = {}


def _browser():
    """一个程序里的所有三维图共用一个浏览器（启动一次约几秒）。"""
    if "b" not in _PW:
        import atexit
        from playwright.sync_api import sync_playwright
        _PW["pw"] = sync_playwright().start()
        _PW["b"] = _PW["pw"].chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                                   "--ignore-gpu-blocklist"])

        def _close():
            try:
                _PW["b"].close()
                _PW["pw"].stop()
            except Exception:  # noqa: BLE001
                pass
        atexit.register(_close)
    return _PW["b"]


def render_png(asm, width=1400, height=900, scale=2, section=None, hide=(), tol=0.05, state=None, **opts) -> bytes:
    """渲染一张 PNG（字节）。opts：camera、labels、dims、arrows、points、texts、explode、edges、outline、background…"""
    st = dict(state or {})
    for k in ("camera", "labels", "dims", "arrows", "points", "texts", "explode", "parts", "fontSize"):
        if k in opts:
            st[k] = opts.pop(k)
    sc = _scene(asm, width, height, scale, section, hide, tol, **opts)
    sc["state"] = st
    # 要高清：视口按 scale 放大，SVG 标注的字号、线宽同比放大
    sc2 = dict(sc, width=width * scale, height=height * scale, scale=1, hatchPx=9.0 * scale, fontSize=(st.get("fontSize") or 15) * scale,
               outlinePx=opts.get("outlinePx", 1.1) * scale)
    sc2["state"] = _scale_state(st, scale)
    r = Renderer(sc2)
    try:
        return r.png()
    finally:
        r.close()


def _scale_state(st, s):
    st = json.loads(json.dumps(st))
    if "fontSize" in st:
        st["fontSize"] *= s
    else:
        st["fontSize"] = 15 * s
    for l in st.get("labels") or []:
        if "r" in l:
            l["r"] *= s
        else:
            l["r"] = 13 * s
        if "fontSize" in l:
            l["fontSize"] *= s
    if "labelGap" in st:
        st["labelGap"] *= s
    else:
        st["labelGap"] = 34 * s
    for a in st.get("arrows") or []:
        a["width"] = a.get("width", 3) * s
        a["head"] = a.get("head", 14) * s
        for k in ("dx", "dy"):
            if k in a:
                a[k] *= s
    for p in st.get("points") or []:
        p["r"] = p.get("r", 5) * s
        for k in ("dx", "dy"):
            if k in p:
                p[k] *= s
    for d in st.get("dims") or []:
        if "fontSize" in d:
            d["fontSize"] *= s
    return st


def _svg_wrap(png: bytes, width: int, height: int) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}"><image width="{width}" height="{height}" '
            f'href="data:image/png;base64,{base64.b64encode(png).decode()}"/></svg>')


def _small(png: bytes) -> bytes:
    """技术插图颜色少：转成 256 色调色板的 PNG，文件小三四倍，看不出差别。"""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB")
    q = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    buf = io.BytesIO()
    q.save(buf, "PNG", optimize=True)
    return buf.getvalue() if len(buf.getvalue()) < len(png) else png


def save_figure(name: str, png: bytes, width: int, height: int) -> None:
    """PNG 存成书里的图 <name>.svg，并登记进本程序的输出（与 bookout.figure 相同）。"""
    import bookout
    folder = os.environ.get("WQ_BOOK_FIGDIR")
    path = os.path.join(folder, f"{name}.svg") if folder else f"{name}.svg"
    Path(path).write_text(_svg_wrap(_small(png), width, height), encoding="utf-8")
    bookout._values.setdefault("_figures", []).append(name)
    bookout.out()


def save_svg(name: str, svg: str) -> None:
    """矢量图（工程图）直接存为书中的图 <name>.svg，并登记。"""
    import bookout
    folder = os.environ.get("WQ_BOOK_FIGDIR")
    Path(os.path.join(folder, f"{name}.svg") if folder else f"{name}.svg").write_text(svg, encoding="utf-8")
    bookout._values.setdefault("_figures", []).append(name)
    bookout.out()


def figure3d(name: str, asm, width=1400, height=900, **opts) -> None:
    """渲染并存为书中的图。"""
    png = render_png(asm, width=width, height=height, **opts)
    save_figure(name, png, width, height)


def compose(name: str, panels, cols: int = 2, width=1400, gap=12, titles=None) -> None:
    """几张 PNG 拼成一幅图（分图 (a)(b)…）。panels：PNG 字节列表；titles：每张的小标题。用 Pillow 拼。"""
    import io
    from PIL import Image, ImageDraw, ImageFont
    ims = [Image.open(io.BytesIO(p)).convert("RGB") for p in panels]
    w = (width * 2 - gap * 2 * (cols - 1)) // cols
    ims = [im.resize((w, int(im.height * w / im.width))) for im in ims]
    rows = (len(ims) + cols - 1) // cols
    th = 44 if titles else 0
    hs = [max(im.height for im in ims[r * cols:(r + 1) * cols]) for r in range(rows)]
    H = sum(hs) + (th + gap * 2) * rows
    canvas = Image.new("RGB", (width * 2, H), "white")
    dr = ImageDraw.Draw(canvas)
    font = None
    for f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"):
        if os.path.exists(f):
            font = ImageFont.truetype(f, 30)
            break
    y = 0
    for r in range(rows):
        x = 0
        for k in range(cols):
            i = r * cols + k
            if i >= len(ims):
                break
            if titles:
                dr.text((x + w / 2, y + 6), titles[i], fill="#1d2327", font=font, anchor="ma")
            canvas.paste(ims[i], (x, y + th))
            x += w + gap * 2
        y += hs[r] + th + gap * 2
    buf = io.BytesIO()
    canvas.save(buf, "PNG", optimize=True)
    save_figure(name, buf.getvalue(), width, H // 2)


class Video:
    """三维动画：逐帧渲染（每帧一个状态：零件位移、转动、显示、相机、标注），ffmpeg 合成 MP4，并取一帧作封面。

        v = Video(asm, width=1280, height=720)
        for t in ...: v.add(state)
        v.save("v52_1_1")             # 写 <WQ_ANIM_OUT>/v52_1_1.mp4 和 .png
    """

    def __init__(self, asm, width=1280, height=720, fps=24, section=None, hide=(), tol=0.08, **opts):
        self.sc = _scene(asm, width, height, 1, section, hide, tol, fontSize=22, outlinePx=1.0, **opts)
        self.sc["state"] = {}
        self.fps = fps
        self.r = Renderer(self.sc)
        self.dir = Path(tempfile.mkdtemp(prefix="wq3d-"))
        self.n = 0
        self.poster_at = None

    def add(self, state: dict, hold: float = 0.0, poster: bool = False):
        st = dict(state)
        st.setdefault("fontSize", 22)
        png = self.r.png(st)
        k = max(1, int(round(hold * self.fps))) if hold else 1
        for _ in range(k):
            (self.dir / f"f{self.n:05d}.png").write_bytes(png)
            self.n += 1
        if poster or self.poster_at is None:
            self.poster_at = png

    def save(self, name: str) -> tuple[str, str]:
        self.r.close()
        out = Path(os.environ.get("WQ_ANIM_OUT") or ".")
        out.mkdir(parents=True, exist_ok=True)
        mp4, png = out / f"{name}.mp4", out / f"{name}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(self.fps), "-i", str(self.dir / "f%05d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-movflags", "+faststart", str(mp4)], check=True)
        png.write_bytes(self.poster_at)
        shutil.rmtree(self.dir, ignore_errors=True)
        return str(mp4), str(png)


def lerp(a, b, t):
    return [x + (y - x) * t for x, y in zip(a, b)]


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)
