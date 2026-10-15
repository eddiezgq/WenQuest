"""问渠白板讲课（第 35 轮）：本机出片与看样。核心在 services/gateway/app/production/whiteboard/（网关也用它）。

    python3 tools/whiteboard/wb.py <课目录>            # 读 <课目录>/lesson.json，写 board.excalidraw、data.json、白板课.html
    python3 tools/whiteboard/wb.py <课目录> --scene    # 从（老师改过的）board.excalidraw 编译
    python3 tools/whiteboard/wb.py <课目录> --mp4      # 另出 白板课.mp4（1920×1080，30 帧/秒）
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "services" / "gateway"))
from app.production.whiteboard.core import *  # noqa: E402,F401,F403
from app.production.whiteboard.core import compile_lesson, compile_scene, excalidraw, page, W, H  # noqa: E402

HERE = Path(__file__).resolve().parent   # (the star import above brought core's HERE)
HAND = HERE / "assets"   # Eddie's hand photo, kept out of the public repository


REPO = HERE.parent.parent


def local_media(src: str):
    """Media frames for local samples: lab:<书>/<章.节> → the built textbook's lab page; video:<file> → the file inline."""
    kind, _, ref = src.partition(":")
    if kind == "lab":
        book, _, no = ref.partition("/")
        ch = no.split(".")[0]
        p = REPO / "textbook" / "build" / book / "lab" / f"ch{int(ch):02d}.html"
        if p.exists():
            return {"kind": "page", "html": p.read_text(encoding="utf-8"), "hash": "lab-" + no.replace(".", "-"), "zoom": 1.0}
    if kind == "video":
        p = Path(ref)
        if p.exists():
            return {"kind": "video", "url": "data:video/mp4;base64," + base64.b64encode(p.read_bytes()).decode()}
    print("media not found:", src)
    return None


def build(lesson_dir, mp4=False):
    d = Path(lesson_dir)
    L = json.loads((d / "lesson.json").read_text())
    data, ex = compile_lesson(L, local_media)
    (d / "data.json").write_text(json.dumps(data, ensure_ascii=False))
    (d / "board.excalidraw").write_text(json.dumps(excalidraw(L, ex), ensure_ascii=False))
    audio = d / L["audio"]
    web_audio = d / "_web.mp3"   # MP3: every browser plays it (open-source Chromium has no AAC)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-vn", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k", str(web_audio)], check=True)
    b64 = base64.b64encode(web_audio.read_bytes()).decode()
    (d / "白板课.html").write_text(page(data, L["title"], b64, "audio/mpeg", hand_dir=HAND))
    (d / "_render.html").write_text(page(data, L["title"], render=True, hand_dir=HAND))
    print(f"{len(L['boards'])} boards, {len(data['items'])} strokes, {data['total']} s → {d / '白板课.html'}")
    if mp4:
        render_mp4(d, data, audio)


def build_scene(lesson_dir, mp4=False):
    """lesson.json (segments, audio) + board.excalidraw (edited) → web page / MP4."""
    d = Path(lesson_dir)
    L = json.loads((d / "lesson.json").read_text())
    scene = json.loads((d / "board.excalidraw").read_text())
    data = compile_scene(scene, L["segments"], L.get("duration", 0))
    (d / "data.json").write_text(json.dumps(data, ensure_ascii=False))
    (d / "_render.html").write_text(page(data, L["title"], render=True, hand_dir=HAND))
    print(f"scene: {len(data['boards'])} boards, {len(data['items'])} strokes, {data['total']} s")
    if mp4:
        render_mp4(d, data, d / L["audio"])
    return data


def render_mp4(d, data, audio, fps=30, start=0.0, end=None, progress=None):
    from playwright.sync_api import sync_playwright
    end = end or data["total"]
    out = d / "白板课.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                           "-ss", str(start), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                           "-crf", "21", "-preset", "medium", "-c:a", "aac", "-b:a", "128k", "-shortest", str(out)], stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": W, "height": H})
        p.goto((d / "_render.html").resolve().as_uri())
        n = int((end - start) * fps)
        for i in range(n):
            p.evaluate(f"WB.seek({start + i / fps})")
            ff.stdin.write(p.screenshot(type="jpeg", quality=90))
            if i % 900 == 0:
                print(f"  frame {i}/{n}", flush=True)
            if progress and i % 30 == 0:
                progress(round(100 * i / n))
        b.close()
    ff.stdin.close()
    ff.wait()
    print("→", out)


if __name__ == "__main__":
    if "--scene" in sys.argv:
        build_scene(sys.argv[1], "--mp4" in sys.argv)
    else:
        build(sys.argv[1], "--mp4" in sys.argv)
